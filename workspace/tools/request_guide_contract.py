#!/usr/bin/env python3
"""사람용 요청 가이드의 설치·발견·미러 계약 검사(표준 라이브러리, 네트워크 없음).

기본: 현재 저장소 읽기 전용 검사. --self-test: 임시 fixture의 정상·독립 변이 검사.
exit 0 = 계약 충족 / exit 1 = self-test 실패 / exit 2 = 배포 계약 위반.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import string
import tempfile


ATX_HEADING = re.compile(r" {0,3}#{1,6}(?:[ \t]|$)")


class HTMLLinkTargets(HTMLParser):
    """따옴표 유무와 무관하게 HTML 링크·이미지 목적지를 수집한다."""

    def __init__(self, clickable_only: bool) -> None:
        super().__init__()
        self.clickable_only = clickable_only
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.targets.extend(
            value for name, value in attrs if name in {"href", "src"} and value is not None
            and (not self.clickable_only or (tag == "a" and name == "href"))
        )


def fence_marker(line: str) -> str | None:
    """한 줄에서 fence 시작자만 읽는다(backtick info string의 backtick은 금지)."""
    match = re.match(r" {0,3}(`{3,}|~{3,})([^\r\n]*)", line)
    if match is None or (match[1][0] == "`" and "`" in match[2]):
        return None
    return match[1]


def inline_limit(lines: list[str], offsets: list[int], line_index: int) -> int:
    """Inline 후보는 soft newline만 넘고 다음 block 시작 전에서 끝난다."""
    for index in range(line_index + 1, len(lines)):
        line = lines[index]
        if (not line.strip() or fence_marker(line) or ATX_HEADING.match(line)
                or re.match(r" {0,3}<!--", line)):
            return offsets[index]
    return offsets[-1]


def backtick_end(text: str, start: int) -> int:
    end = start + 1
    while end < len(text) and text[end] == "`":
        end += 1
    return end


def code_span_end(text: str, start: int, limit: int) -> int | None:
    """같은 문단 안에서 길이가 같은 backtick run만 닫는 delimiter다."""
    opening_end = backtick_end(text, start)
    width = opening_end - start
    position = text.find("`", opening_end, limit)
    while position != -1:
        end = backtick_end(text, position)
        if end - position == width:
            return end
        position = text.find("`", end, limit)
    return None


def html_tag_end(text: str, start: int) -> int | None:
    """HTML tag의 quote 상태를 따라 속성 안 Markdown 표식을 문자로 보존한다."""
    name = re.match(r"</?[A-Za-z][A-Za-z0-9-]*", text[start:])
    if name is None:
        return None
    attributes_start = start + name.end()
    if text.startswith(">", attributes_start):
        return attributes_start + 1
    if text.startswith("/>", attributes_start):
        return attributes_start + 2
    if attributes_start == len(text) or not text[attributes_start].isspace():
        return None
    quote: str | None = None
    for position in range(attributes_start, len(text)):
        character = text[position]
        if quote is not None:
            if character == quote:
                quote = None
        elif character in "\"'":
            quote = character
        elif character == ">":
            return position + 1
        elif character == "<":
            return None
    return None


def blank_source(text: str) -> str:
    """범위를 가리되 줄 경계와 source offset은 유지한다."""
    return "".join(character if character in "\r\n" else " " for character in text)


def source_visibility(text: str) -> tuple[str, list[tuple[int, int]]]:
    """Block·inline 상태로 코드/주석 mask와 확인된 HTML tag 범위를 한 번 만든다."""
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    visible = list(text)
    tags: list[tuple[int, int]] = []
    fence: str | None = None
    paragraph_open = False
    context: str | None = None
    context_end = 0
    for line_index, line in enumerate(lines):
        position, line_end = offsets[line_index:line_index + 2]
        # 확인된 HTML tag와 줄 시작 comment만 내부의 fence 모양을 소유한다.
        if context not in {"tag", "block-comment"}:
            if fence is not None:
                if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*", line.rstrip("\r\n")):
                    fence = None
                visible[position:line_end] = blank_source(line)
                continue
            marker = fence_marker(line)
            if marker is not None:
                fence = marker
                paragraph_open = False
                visible[position:line_end] = blank_source(line)
                continue
            if line.startswith(("    ", "\t")) and not paragraph_open:
                visible[position:line_end] = blank_source(line)
                continue
        heading = context is None and ATX_HEADING.match(line) is not None
        line_content = False
        while position < line_end:
            if context is not None:
                end = min(context_end, line_end)
                if context != "tag":
                    visible[position:end] = blank_source(text[position:end])
                if context in {"code", "tag"}:
                    line_content = True
                position = end
                if position == context_end:
                    context = None
                continue
            character = text[position]
            if character == "\\" and position + 1 < line_end and text[position + 1] in string.punctuation:
                line_content = True
                position += 2
                continue
            if text.startswith("<!--", position):
                block_comment = re.fullmatch(r" {0,3}", text[offsets[line_index]:position]) is not None
                limit = len(text) if block_comment else inline_limit(lines, offsets, line_index)
                closing = text.find("-->", position + 4, limit)
                if closing != -1 or block_comment:
                    context = "block-comment" if block_comment else "inline-comment"
                    context_end = closing + 3 if closing != -1 else len(text)
                    continue
            if character == "<":
                end = html_tag_end(text, position)
                if end is not None:
                    tags.append((position, end))
                    context, context_end = "tag", end
                    continue
            if character == "`":
                end = code_span_end(text, position, inline_limit(lines, offsets, line_index))
                if end is not None:
                    context, context_end = "code", end
                else:
                    line_content = True
                    position = backtick_end(text, position)
                continue
            line_content = line_content or not character.isspace()
            position += 1
        # 가린 code span도 문단 content다. 주석만 있는 줄은 문단을 열지 않는다.
        paragraph_open = line_content and not heading
    return "".join(visible), tags


def without_markdown_code(text: str) -> str:
    """코드와 주석을 가리고 HTML 속성 및 원문의 줄 경계는 보존한다."""
    return source_visibility(text)[0]


def is_escaped(text: str, position: int) -> bool:
    backslashes = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        backslashes += 1
        position -= 1
    return backslashes % 2 == 1


def link_targets(text: str, *, clickable_only: bool = False) -> list[str]:
    """코드 예시를 제외한 Markdown 링크와 HTML href/src의 목적지를 읽는다."""
    text, tags = source_visibility(text)
    html = HTMLLinkTargets(clickable_only)
    markdown = list(text)
    for start, end in tags:
        html.feed(text[start:end])
        markdown[start:end] = blank_source(text[start:end])
    html.close()
    text = "".join(markdown)
    definitions: dict[str, str] = {}

    def reference_label(label: str) -> str:
        return " ".join(label.split()).casefold()

    def collect_definition(match: re.Match[str]) -> str:
        definitions.setdefault(reference_label(match[1]), match[2])
        return "\n"

    text = re.sub(r"(?m)^ {0,3}\[([^\]\n]+)\]:[ \t]*<?([^\s>]+)[^\n]*", collect_definition, text)
    targets: list[str] = []
    markdown_link = re.compile(
        r"(?P<image>!?)\[(?P<label>[^\]\n]*)\]"
        r"(?:\(\s*<?(?P<inline>[^\s)>]+)[^\n)]*\)|\[(?P<reference>[^\]\n]*)\])?",
    )
    for paragraph in re.split(r"\n[ \t\r]*\n", text):
        for match in markdown_link.finditer(paragraph):
            if is_escaped(paragraph, match.start("label") - 1):
                continue
            if clickable_only and match["image"] and not is_escaped(paragraph, match.start()):
                continue
            if match["inline"] is not None:
                targets.append(match["inline"])
            else:
                target = definitions.get(reference_label(match["reference"] or match["label"]))
                if target is not None:
                    targets.append(target)
    targets += html.targets
    return targets


def validate(root: Path) -> list[str]:
    """저장소의 배포 계약 위반을 수집한다."""
    errors: list[str] = []
    repository = "https://github.com/changja88/dddjango"
    plugins = ("dddjango", "dddjango-web")

    def read_text(relative: str, code: str) -> str | None:
        try:
            return (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"[{code}] {relative}: {exc}")
            return None

    def read_json(relative: str, code: str) -> dict:
        text = read_text(relative, code)
        if text is None:
            return {}
        try:
            data = json.loads(text)
        except ValueError as exc:
            errors.append(f"[json] {relative}: {exc}")
            return {}
        if not isinstance(data, dict):
            errors.append(f"[json] {relative}: expected object")
            return {}
        return data

    readme = read_text("README.md", "readme-link")
    for plugin in plugins:
        canonical = f"{plugin}/REQUEST_GUIDE.md"
        mirror = f"codex-{plugin}/REQUEST_GUIDE.md"
        if readme is not None and canonical not in link_targets(readme, clickable_only=True):
            errors.append(f"[readme-link] README.md: missing exact canonical link {canonical}")
        texts = [read_text(path, "guide-missing") for path in (canonical, mirror)]
        if all(text is not None for text in texts):
            if (root / canonical).read_bytes() != (root / mirror).read_bytes():
                errors.append(f"[mirror] {canonical} != {mirror} (byte drift)")
        for path, text in zip((canonical, mirror), texts):
            if text is None:
                continue
            introduction = re.split(r"(?m)^##\s", text, maxsplit=1)[0]
            if not re.search(r"설치된[^\n]*`REQUEST_GUIDE\.md`[^\n]*해당 runtime[^\n]*권위 있는 가이드", introduction):
                errors.append(f"[guide-authority] {path}: missing installed-copy authority in introduction")
            for target in link_targets(text):
                if not target.startswith("#") and not re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
                    errors.append(f"[guide-link] {path}: external relative link {target!r}")

    for prefix, manifest_dir, market in (
        ("", ".claude-plugin", ".claude-plugin/marketplace.json"),
        ("codex-", ".codex-plugin", ".agents/plugins/marketplace.json"),
    ):
        marketplace = read_json(market, "marketplace-missing")
        entries = marketplace.get("plugins")
        if not isinstance(entries, list):
            entries = []
        names = [entry.get("name") for entry in entries if isinstance(entry, dict)]
        if len(entries) != 2 or len(names) != 2 or any(names.count(plugin) != 1 for plugin in plugins):
            errors.append(f"[marketplace-name] {market}: expected exactly one entry each for {plugins}")
        for plugin in plugins:
            directory = prefix + plugin
            expected_source = {
                "source": "git-subdir", "url": repository + ".git",
                "path": "./" + directory if prefix else directory, "ref": "main",
            }
            entry = next((entry for entry in entries if isinstance(entry, dict) and entry.get("name") == plugin), {})
            source = entry.get("source")
            if not isinstance(source, dict) or any(source.get(key) != value for key, value in expected_source.items()):
                errors.append(f"[marketplace-source] {market}: {plugin} expected {expected_source!r}")
            # 미신뢰 path는 순회하지 않는다. exact 매핑된 설치 경계에서 내용 존재를 검사한다.
            manifest_path = f"{directory}/{manifest_dir}/plugin.json"
            manifest = read_json(manifest_path, "manifest-missing")
            url = f"{repository}/blob/main/{plugin}/REQUEST_GUIDE.md"
            for key, expected in (("name", plugin), ("homepage", url), ("repository", repository)):
                if manifest.get(key) != expected:
                    code = "manifest-name" if key == "name" else key
                    errors.append(f"[{code}] {manifest_path}: expected {key}={expected!r}")
            if prefix:
                interface = manifest.get("interface")
                if not isinstance(interface, dict):
                    interface = {}
                if interface.get("websiteURL") != url:
                    errors.append(f"[websiteURL] {manifest_path}: expected {url!r}")
                prompts = interface.get("defaultPrompt")
                name_pattern = rf"(?<![A-Za-z0-9_-]){re.escape(plugin)}(?![A-Za-z0-9_-])"
                if not isinstance(prompts, list) or not prompts or any(
                    not isinstance(prompt, str) or not prompt.strip() or not re.search(name_pattern, prompt)
                    for prompt in prompts
                ):
                    errors.append(f"[defaultPrompt] {manifest_path}: expected nonempty string array; each prompt must name {plugin}")
    return errors


def self_test() -> int:
    """각 fixture 변이는 지정된 계약 검사가 빠지면 반드시 실패한다."""
    repository = "https://github.com/changja88/dddjango"
    authority = "설치된 플러그인 루트의 이 `REQUEST_GUIDE.md`가 해당 runtime에 대한 권위 있는 가이드 사본입니다."
    fixtures: dict[str, str] = {
        "README.md": "[backend](dddjango/REQUEST_GUIDE.md)\n[web](dddjango-web/REQUEST_GUIDE.md)\n",
    }
    for prefix, manifest_dir, market in (
        ("", ".claude-plugin", ".claude-plugin/marketplace.json"),
        ("codex-", ".codex-plugin", ".agents/plugins/marketplace.json"),
    ):
        entries = []
        for plugin in ("dddjango", "dddjango-web"):
            directory = prefix + plugin
            url = f"{repository}/blob/main/{plugin}/REQUEST_GUIDE.md"
            fixtures[f"{directory}/REQUEST_GUIDE.md"] = (
                f"# {plugin}\n\n{authority}\n\n## 시작\n"
                "[시작](#시작) [공개 문서](https://example.com/guide)\n"
            )
            manifest = {"name": plugin, "homepage": url, "repository": repository}
            if prefix:
                manifest["interface"] = {"websiteURL": url, "defaultPrompt": [f"{plugin}로 작업해줘."]}
            fixtures[f"{directory}/{manifest_dir}/plugin.json"] = json.dumps(manifest)
            entries.append({"name": plugin, "source": {
                "source": "git-subdir", "url": repository + ".git",
                "path": "./" + directory if prefix else directory, "ref": "main",
            }})
        fixtures[market] = json.dumps({"plugins": entries})

    cases: list[tuple[str, dict[str, str | None], str]] = []

    def change_json(path: str, keys: tuple[str | int, ...], value: object) -> dict[str, str]:
        data = json.loads(fixtures[path])
        target = data
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
        return {path: json.dumps(data)}

    for plugin in ("dddjango", "dddjango-web"):
        canonical = f"{plugin}/REQUEST_GUIDE.md"
        mirror = f"codex-{plugin}/REQUEST_GUIDE.md"
        cases.append((f"{plugin}: mirror 1-byte drift", {mirror: fixtures[mirror] + "x"}, "mirror"))
        readme_without_link = "".join(
            line for line in fixtures["README.md"].splitlines(keepends=True)
            if canonical not in line
        )
        for path in (canonical, mirror):
            cases.append((f"{path}: missing guide", {path: None}, "guide-missing"))
        cases.append((f"{plugin}: README link typo", {
            "README.md": fixtures["README.md"].replace(canonical, canonical + "x"),
        }, "readme-link"))
        for label, example in (
            ("fenced backticks", f"```markdown\n[guide]({canonical})\n```\n"),
            ("fence after unmatched backtick", f"`\n```\n` [guide]({canonical})\n```\n"),
            ("fenced tildes", f"~~~markdown\n[guide]({canonical})\n~~~\n"),
            ("code span", f"`[guide]({canonical})`\n"),
            ("HTML comment", f"<!-- [guide]({canonical}) -->\n"),
            ("indented code", f"\n    [guide]({canonical})\n"),
            ("indented code after consecutive comments", f"\n<!-- a --> <!-- b -->\n    [guide]({canonical})\n"),
            ("unused reference definition", f"[guide]: {canonical}\n"),
            ("reference use in code span", f"`[guide][g]`\n\n[g]: {canonical}\n"),
            ("Markdown image", f"![guide]({canonical})\n"),
            ("reference image", f"![guide][g]\n\n[g]: {canonical}\n"),
            ("HTML image", f'<img src="{canonical}">\n'),
            ("non-anchor HTML href", f'<div href="{canonical}">guide</div>\n'),
            ("Markdown text in HTML attribute", f'<span title="[guide]({canonical})">guide</span>\n'),
            ("escaped Markdown opener (one backslash)", f"\\[guide]({canonical})\n"),
            ("link destination across blank paragraph", f"[guide](\n\n{canonical})\n"),
            ("link destination across fence", f"[guide](\n```\n```\n{canonical})\n"),
        ):
            cases.append((f"{plugin}: README link only in {label}", {
                "README.md": readme_without_link + example,
            }, "readme-link"))
        for label, link in (
            ("inline link", f"[guide]({canonical})"),
            ("full reference link", f"[guide][g]\n\n[g]: {canonical}"),
            ("collapsed reference link", f"[guide][]\n\n[guide]: {canonical}"),
            ("shortcut reference link", f"[guide]\n\n[guide]: {canonical}"),
            ("HTML anchor", f'<a href="{canonical}">guide</a>'),
            ("HTML anchor with attribute backticks", f'<a title="`" href="{canonical}" data-note="`">guide</a>'),
            ("indented paragraph continuation", f"guide\n    [guide]({canonical})"),
            ("multiline HTML anchor", f'<a\n    href="{canonical}">guide</a>'),
            ("indented continuation after code span", f"`code`\n    [guide]({canonical})"),
            ("fence ending inline comment candidate", f"text <!--\n```\n```\n[guide]({canonical})\n-->"),
            ("blank paragraph separating backticks", f"`\n\n[guide]({canonical})\n\n`"),
            ("escaped backslash before link (two backslashes)", f"\\\\[guide]({canonical})"),
            ("angle-wrapped inline destination", f"[guide](<{canonical}>)"),
            ("angle-wrapped reference destination", f"[guide][g]\n\n[g]: <{canonical}>"),
            ("inline destination after soft newline", f"[guide](\n{canonical})"),
        ):
            cases.append((f"{plugin}: README discoverable through {label}", {
                "README.md": readme_without_link + link + "\n",
            }, ""))
        for label, prefix in (
            ("inline-code comment opener", "`<!--`\n\n"),
            ("fenced-code comment opener", "```html\n<!--\n```\n\n"),
            ("indented-code comment opener", "\n    <!--\n\n"),
            ("HTML attribute comment opener", '<span title="<!--">example</span>\n\n'),
            ("real comment containing backtick", "<!-- ` -->\n\n"),
            ("real comment containing fence", "<!--\n```html\n-->\n\n"),
        ):
            cases.append((f"{plugin}: README canonical link after {label} accepted", {
                "README.md": readme_without_link + prefix + f"[guide]({canonical})\n\n`\n",
            }, ""))
            suffix = prefix + "[root](../README.md)\n\n`\n"
            cases.append((f"{plugin}: guide relative link after {label} rejected", {
                canonical: fixtures[canonical] + suffix, mirror: fixtures[mirror] + suffix,
            }, "guide-link"))
        for label, suffix in (
            ("inline relative link", "[root](../README.md)\n"),
            ("relative link after fence preceded by unmatched backtick", "`\n```\n`\n```\n[root](../README.md)\n"),
            ("relative link after multiline code span", "`code\n[root](../README.md)\n`\n[root](../README.md)\n"),
            ("reference relative link", "[root][r]\n[r]: ../README.md\n"),
            ("HTML relative link", '<a href="../README.md">root</a>\n'),
            ("HTML unquoted href", "<a href=../README.md>root</a>\n"),
            ("HTML unquoted src", "<img src=../image.png>\n"),
            ("Markdown relative image", "![root](../image.png)\n"),
            ("reference relative image", "![root][r]\n[r]: ../image.png\n"),
            ("HTML attribute backticks", '<a title="`" href="../README.md" data-note="`">root</a>\n'),
            ("HTML image attribute backticks", '<img title="`" src="../image.png" data-note="`">\n'),
            ("multiline HTML href", '<a\n    href="../README.md">root</a>\n'),
            ("indented continuation after code span", "`code`\n    [root](../README.md)\n"),
            ("fence ending inline comment candidate", "text <!--\n```\n```\n[root](../README.md)\n-->\n"),
            ("blank paragraph separating backticks", "`\n\n[root](../README.md)\n\n`\n"),
            ("escaped backslash before link (two backslashes)", "\\\\[root](../README.md)\n"),
            ("angle-wrapped inline destination", "[root](<docs/README.md>)\n"),
            ("angle-wrapped reference destination", "[root][r]\n\n[r]: <docs/README.md>\n"),
            ("inline destination after soft newline", "[root](\n../README.md)\n"),
        ):
            cases.append((f"{plugin}: {label}", {
                canonical: fixtures[canonical] + suffix, mirror: fixtures[mirror] + suffix,
            }, "guide-link"))
        for label, suffix in (
            ("inline Markdown code example", "`[root](../README.md)`\n"),
            ("multiline Markdown code example", "`code\n[root](../README.md)\n`\n"),
            ("inline HTML code example", '`<a href="../README.md">root</a>`\n'),
            ("double-backtick HTML code example", '``<a title="`" href="../README.md" data-note="`">root</a>``\n'),
            ("backtick fenced code example", '```html\n<a href="../README.md">root</a>\n```\n'),
            ("tilde fenced code example", '~~~html\n<a href="../README.md">root</a>\n~~~\n'),
            ("indented code after consecutive comments", "\n<!-- a --> <!-- b -->\n    [root](../README.md)\n"),
            ("absolute reference link", "[public][p]\n\n[p]: https://example.com/guide\n"),
            ("HTML absolute URL", '<a href="https://example.com/guide">public</a>\n'),
            ("HTML fragment", '<a href="#start">start</a>\n'),
            ("escaped Markdown opener (one backslash)", "\\[root](../README.md)\n"),
            ("link destination across blank paragraph", "[root](\n\n../README.md)\n"),
            ("link destination across fence", "[root](\n```\n```\n../README.md)\n"),
        ):
            cases.append((f"{plugin}: {label} accepted", {
                canonical: fixtures[canonical] + suffix, mirror: fixtures[mirror] + suffix,
            }, ""))
        cases.append((f"{plugin}: authority line deleted", {
            path: fixtures[path].replace(authority, "") for path in (canonical, mirror)
        }, "guide-authority"))
        for prefix, manifest_dir in (("", ".claude-plugin"), ("codex-", ".codex-plugin")):
            manifest = f"{prefix}{plugin}/{manifest_dir}/plugin.json"
            cases.append((f"{manifest}: subdir manifest missing", {manifest: None}, "manifest-missing"))
            for key, value in (("homepage", repository), ("repository", repository + f"/blob/main/{plugin}/REQUEST_GUIDE.md")):
                cases.append((f"{manifest}: {key} confusion", change_json(manifest, (key,), value), key))
            cases.append((f"{manifest}: name corrupted", change_json(manifest, ("name",), "other"), "manifest-name"))
            if prefix:
                cases.append((f"{plugin}: websiteURL corrupted", change_json(manifest, ("interface", "websiteURL"), repository), "websiteURL"))
                for label, value in (
                    ("wrong type", "dddjango"), ("empty list", []), ("non-string", [1]),
                    ("blank string", ["   "]), ("plugin-name omission", ["기능을 만들어줘."]),
                    ("other plugin name", ["dddjango로 작업해줘." if plugin.endswith("-web") else "dddjango-web으로 작업해줘."]),
                ):
                    cases.append((f"{plugin}: defaultPrompt {label}", change_json(manifest, ("interface", "defaultPrompt"), value), "defaultPrompt"))

    for market in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
        for index in (0, 1):
            for key, value in (("path", "../wrong"), ("ref", "old"), ("source", "git"), ("url", "https://example.com/wrong.git")):
                cases.append((f"{market}[{index}]: {key} corrupted", change_json(market, ("plugins", index, "source", key), value), "marketplace-source"))
            cases.append((f"{market}[{index}]: name corrupted", change_json(market, ("plugins", index, "name"), "wrong"), "marketplace-name"))

    failures = 0
    for label, changes, expected in [("normal fixture", {}, "")] + cases:
        with tempfile.TemporaryDirectory(prefix="request-guide-contract-") as directory:
            root = Path(directory)
            for relative, content in (fixtures | changes).items():
                if content is not None:
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")
            errors = validate(root)
        passed = not errors if not expected else any(error.startswith(f"[{expected}]") for error in errors)
        if not passed:
            failures += 1
        print(f"[self-test] {'PASS' if passed else 'FAIL'} {label}: "
              f"{'accepted' if not expected else 'expected [' + expected + '] rejection'}"
              + (f"; got {errors!r}" if not passed else ""))
    print(f"[self-test] {len(cases) + 1 - failures}/{len(cases) + 1} passed")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    errors = validate(Path(__file__).resolve().parents[2])
    for error in errors:
        print(f"[request-guide] {error}")
    print(f"[request-guide] {'FAIL: ' + str(len(errors)) + ' violations' if errors else 'PASS: installation, discovery and mirror contracts'}")
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
