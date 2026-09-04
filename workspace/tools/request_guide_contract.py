#!/usr/bin/env python3
"""사람용 요청 가이드의 설치·발견·미러 계약 검사(표준 라이브러리, 네트워크 없음).

기본: 현재 저장소 읽기 전용 검사. --self-test: 임시 fixture의 정상·독립 변이 검사.
링크 검사는 README exact source token과 guide의 상대 목적지 구문 drift로 한정한다.
CommonMark 문맥이나 실제 rendered/clickable 동작은 판정하지 않는다.
Guide의 코드·주석·예시에도 상대 목적지 구문을 허용하지 않는다.
exit 0 = 계약 충족 / exit 1 = self-test 실패 / exit 2 = 배포 계약 위반.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile


def guide_section_source(text: str) -> str:
    """정확한 source heading부터 다음 level-2 source heading 전까지 읽는다."""
    match = re.search(r"(?ms)^## 작업 요청 가이드\n(.*?)(?=^## |\Z)", text)
    return match[1] if match is not None else ""


def source_link_targets(text: str) -> list[str]:
    """문맥을 해석하지 않고 목적지처럼 보이는 raw source 구문을 수집한다.

    Inline/image는 `](` 뒤, reference definition은 `[label]:` 뒤를 읽는다.
    href/src는 tag 여부나 주변 문맥을 판정하지 않는다. 코드·주석·escape도 예외가 없다.
    """
    patterns = (
        r"\]\(\s*(?:<([^>\r\n]*)>|([^\s)]*))",
        r"\[[^\]\r\n]+\]:\s*(?:<([^>\r\n]*)>|([^\s]*))",
        r'''(?i)(?<![\w:-])(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]*))''',
    )
    return [
        next(value for value in match.groups() if value is not None)
        for pattern in patterns for match in re.finditer(pattern, text)
    ]


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
    section = guide_section_source(readme) if readme is not None else ""
    for plugin in plugins:
        canonical = f"{plugin}/REQUEST_GUIDE.md"
        mirror = f"codex-{plugin}/REQUEST_GUIDE.md"
        token = f"[{plugin} 작업 요청 가이드]({canonical})"
        if readme is not None and (section.count(token) != 1 or readme.count(token) != 1):
            errors.append(f"[readme-link] README.md: expected exactly one {token!r} "
                          "in '## 작업 요청 가이드' and in full README source")
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
            for target in source_link_targets(text):
                if not target.startswith("#") and not re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
                    errors.append(f"[guide-link] {path}: relative destination-like source {target!r}")

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
        "README.md": (
            "# 플러그인\n\n## 작업 요청 가이드\n\n"
            "[dddjango 작업 요청 가이드](dddjango/REQUEST_GUIDE.md)\n"
            "[dddjango-web 작업 요청 가이드](dddjango-web/REQUEST_GUIDE.md)\n"
            "\n## 업데이트\n\n설치본 갱신 방법\n"
        ),
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
        token = f"[{plugin} 작업 요청 가이드]({canonical})"
        cases.append((f"{plugin}: README same path with wrong label", {
            "README.md": fixtures["README.md"].replace(token, f"[다른 이름]({canonical})"),
        }, "readme-link"))
        cases.append((f"{plugin}: README exact token outside intended section", {
            "README.md": fixtures["README.md"].replace(token, "") + token + "\n",
        }, "readme-link"))
        for label, suffix in (
            ("fenced Markdown source", "```markdown\n[root](../README.md)\n```\n"),
            ("fenced HTML source", '```html\n<a href="../README.md">root</a>\n```\n'),
            ("inline Markdown source", "`[root](../README.md)`\n"),
            ("inline HTML source", '`<img src="../image.png">`\n'),
            ("comment Markdown source", "<!-- [root](../README.md) -->\n"),
            ("comment HTML source", '<!-- <a href="../README.md">root</a> -->\n'),
            ("nested relative Markdown source", "[![preview](https://example.com/image.png)](../README.md)\n"),
        ):
            cases.append((f"{plugin}: {label} rejected", {
                canonical: fixtures[canonical] + suffix, mirror: fixtures[mirror] + suffix,
            }, "guide-link"))
        cases.append((f"{plugin}: mirror 1-byte drift", {mirror: fixtures[mirror] + "x"}, "mirror"))
        for path in (canonical, mirror):
            cases.append((f"{path}: missing guide", {path: None}, "guide-missing"))
            cases.append((f"{path}: relative source checked independently", {
                path: fixtures[path] + "[root](../README.md)\n",
            }, "guide-link"))
        cases.append((f"{plugin}: README link typo", {
            "README.md": fixtures["README.md"].replace(canonical, canonical + "x"),
        }, "readme-link"))
        for label, source in (
            ("duplicate token in section", fixtures["README.md"].replace(token, token + "\n" + token)),
            ("duplicate token after section", fixtures["README.md"] + token + "\n"),
            ("wrong section heading", fixtures["README.md"].replace("## 작업 요청 가이드", "## 다른 섹션")),
            ("reference syntax replacing token", fixtures["README.md"].replace(token, f"[guide][g]\n\n[g]: {canonical}")),
            ("HTML syntax replacing token", fixtures["README.md"].replace(token, f'<a href="{canonical}">guide</a>')),
        ):
            cases.append((f"{plugin}: README {label}", {"README.md": source}, "readme-link"))
        for label, source in (
            ("fenced token", f"```markdown\n{token}\n```"),
            ("inline-code token", f"`{token}`"),
            ("comment token", f"<!-- {token} -->"),
        ):
            cases.append((f"{plugin}: README source count accepts {label}", {
                "README.md": fixtures["README.md"].replace(token, source),
            }, ""))
        for label, suffix in (
            ("inline image", "![root](../image.png)\n"),
            ("unused reference definition", "[root]: ../README.md\n"),
            ("comment reference definition", "<!-- [root]: ../README.md -->\n"),
            ("angle-wrapped inline destination", "[root](<../README.md>)\n"),
            ("angle-wrapped reference destination", "[root]: <../README.md>\n"),
            ("multiline inline destination", "[root](\n../README.md)\n"),
            ("HTML double-quoted href", '<a href="../README.md">root</a>\n'),
            ("HTML single-quoted src", "<img src='../image.png'>\n"),
            ("HTML unquoted href", "<a href=../README.md>root</a>\n"),
            ("HTML unquoted src", "<img src=../image.png>\n"),
            ("HTML multiline uppercase href", '<a\n HREF="../README.md">root</a>\n'),
            ("indented code", "\n    [root](../README.md)\n"),
            ("escaped source", "\\[root](../README.md)\n"),
            ("root-relative destination", "[root](/README.md)\n"),
            ("scheme-relative destination", "[root](//example.com/guide)\n"),
            ("empty inline destination", "[root]()\n"),
            ("empty HTML destination", '<a href="">root</a>\n'),
        ):
            cases.append((f"{plugin}: relative {label} source rejected", {
                canonical: fixtures[canonical] + suffix, mirror: fixtures[mirror] + suffix,
            }, "guide-link"))
        for label, suffix in (
            ("inline schemes and fragments", "[public](https://example.com/guide) [start](#start)\n"),
            ("image schemes and fragments", "![image](https://example.com/image.png) ![icon](#icon)\n"),
            ("reference schemes and fragments", "[public]: <https://example.com/guide>\n[start]: #start\n"),
            ("quoted HTML schemes and fragments", '<a href="https://example.com/guide">public</a> <img src=\'#icon\'>\n'),
            ("unquoted HTML schemes and fragments", "<a href=mailto:user@example.com>mail</a> <img src=#icon>\n"),
            ("schemes and fragments in code and comments", "```markdown\n[app](app://guide)\n[ref]: #start\n```\n`<img src=\"data:image/png;base64,AA==\">`\n<!-- [start](#start) -->\n"),
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
