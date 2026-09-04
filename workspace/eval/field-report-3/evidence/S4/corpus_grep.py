"""코퍼스 전수 — dict/Mapping[…, Any|object] 류 줄을 코드 펜스/산문 구분해 file:line 으로."""
import re, sys, glob
PAT = re.compile(r'(dict|Dict|Mapping|MutableMapping)\[[^\]]*, *(object|Any)\]')
KW = re.compile(r'TypedDict|TypeAdapter|JsonValue|RootModel|model_validate')
files = sorted(glob.glob("dddjango/skills/*/SKILL.md") + glob.glob("dddjango/skills/*/references/final.md")
               + glob.glob("dddjango/agents/*.md") + ["dddjango/commands/dddjango.md"])
mode = sys.argv[1]
rx = PAT if mode == "dict" else KW
for f in files:
    fence = False
    for i, line in enumerate(open(f, encoding="utf-8"), 1):
        if line.lstrip().startswith("```"):
            fence = not fence; continue
        if rx.search(line):
            kind = "FENCE" if fence else "PROSE"
            print(f"{kind}\t{f}:{i}\t{line.rstrip()[:160]}")
