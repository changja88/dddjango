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
import tempfile


class HTMLLinkTargets(HTMLParser):
    """따옴표 유무와 무관하게 HTML 링크·이미지 목적지를 수집한다."""

    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.targets.extend(value for name, value in attrs if name in {"href", "src"} and value is not None)


def without_markdown_code(text: str) -> str:
    """코드 fence와 같은 길이의 backtick으로 감싼 code span은 링크가 아니다."""
    lines: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        if fence is not None:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*", line.rstrip("\r\n")):
                fence = None
            lines.append("\n")
            continue
        opener = re.match(r" {0,3}(`{3,}|~{3,})(.*)", line)
        if opener and not (opener[1].startswith("`") and "`" in opener[2]):
            fence = opener[1]
            lines.append("\n")
        else:
            lines.append(line)
    return re.sub(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)", " ", "".join(lines), flags=re.DOTALL)


def link_targets(text: str) -> list[str]:
    """코드 예시를 제외한 Markdown 링크와 HTML href/src의 목적지를 읽는다."""
    text = without_markdown_code(text)
    targets = re.findall(r"\]\(\s*<?([^\s)>]+)", text)
    targets += re.findall(r"(?m)^\s{0,3}\[[^\]]+\]:\s*<?([^\s>]+)", text)
    html = HTMLLinkTargets()
    html.feed(text)
    html.close()
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
        if readme is not None and canonical not in link_targets(readme):
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
        for path in (canonical, mirror):
            cases.append((f"{path}: missing guide", {path: None}, "guide-missing"))
        cases.append((f"{plugin}: README link typo", {
            "README.md": fixtures["README.md"].replace(canonical, canonical + "x"),
        }, "readme-link"))
        for label, example in (
            ("fenced backticks", f"```markdown\n[guide]({canonical})\n```\n"),
            ("fenced tildes", f"~~~markdown\n[guide]({canonical})\n~~~\n"),
            ("code span", f"`[guide]({canonical})`\n"),
        ):
            cases.append((f"{plugin}: README link only in {label}", {
                "README.md": "".join(
                    line for line in fixtures["README.md"].splitlines(keepends=True)
                    if canonical not in line
                ) + example,
            }, "readme-link"))
        for label, suffix in (
            ("inline relative link", "[root](../README.md)\n"),
            ("reference relative link", "[root][r]\n[r]: ../README.md\n"),
            ("HTML relative link", '<a href="../README.md">root</a>\n'),
            ("HTML unquoted href", "<a href=../README.md>root</a>\n"),
            ("HTML unquoted src", "<img src=../image.png>\n"),
        ):
            cases.append((f"{plugin}: {label}", {
                canonical: fixtures[canonical] + suffix, mirror: fixtures[mirror] + suffix,
            }, "guide-link"))
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
