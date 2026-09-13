"""Run a tool-free native Claude decision probe; this is not the plugin pipeline."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys


root = Path(__file__).resolve().parents[3]
destination = Path(__file__).resolve().parent / sys.argv[1]
destination.mkdir(exist_ok=False)
paths = [
    "dddjango-web/commands/dddjango-web.md",
    "dddjango-web/agents/design-review-web.md",
    "dddjango-web/skills/architecture-web/references/final.md",
    "dddjango-web/skills/implementation-ui/references/final.md",
    "dddjango-web/skills/implementation-ui/references/design-acquisition.md",
]
sources = {path: (root / path).read_text() for path in paths}
scenario = (Path(__file__).parent / "scenarios.md").read_text()
prompt = (
    "다음은 dddjango-web 역할의 모의 판단 작업이다. 실제 파이프라인 실행이나 파일 변경은 요청하지 않는다. "
    "각 상황의 해당 역할로 현재 판정과 이어서 실행할 작업을 반환하라. 실행하지 않은 관찰을 완료했다고 쓰지 마라. "
    "현재 배포 지침의 실제 본문을 아래에 제공한다. 도구는 이 판정 시험에서 사용할 수 없다. "
    "상황 R1~R4 각각에 답하고, 반송/완료 범위와 다음 작업을 구체적으로 설명하라.\n\n"
    + scenario
    + "\n\n# 제공된 지침 원문\n"
    + "\n\n".join(f"## {path}\n{text}" for path, text in sources.items())
)
(destination / "input.txt").write_text(prompt)
command = [
    "claude", "--print", "--safe-mode", "--tools", "",
    "--no-session-persistence", "--output-format", "json",
]
metadata = {
    "command": command,
    "cwd": str(root),
    "source_sha256": {path: hashlib.sha256(text.encode()).hexdigest() for path, text in sources.items()},
    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
    "scenario_sha256": hashlib.sha256(scenario.encode()).hexdigest(),
    "kind": "tool-free native decision probe, not full plugin execution",
}
with (destination / "output.json").open("w") as stdout, (destination / "stderr.txt").open("w") as stderr:
    result = subprocess.run(command, input=prompt, text=True, cwd=root, stdout=stdout, stderr=stderr, timeout=600)
metadata["exit_code"] = result.returncode
(destination / "invocation.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"trial": destination.name, "exit_code": result.returncode}))
sys.exit(result.returncode)
