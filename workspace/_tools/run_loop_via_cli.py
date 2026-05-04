#!/usr/bin/env python3
"""dddjango 트리거 정확도 최적화 — skill-creator 메커니즘을 dddjango plugin 환경에 맞춰 패치.

기존 skill-creator의 run_eval은 .claude/commands/<unique-name>.md 임시 파일에
description을 포장해 그 unique-name이 자발적으로 호출되는지 측정. 그러나
Claude 4.x에서 슬래시 명령은 자발적 호출되지 않아 항상 0이 나옴.

패치 방식:
1. iter 시작 시 SKILL.md frontmatter description을 직접 갱신
2. claude -p --plugin-dir <dddjango>로 query 실행 (진짜 스킬이 자발적 트리거됨)
3. stream-json에서 Skill 도구의 인자가 target_skill_name과 일치하는지 측정
4. iter 끝에 SKILL.md 원본 복원
5. improve_description은 anthropic.Anthropic monkey-patch로 claude -p 호출
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic


_original_popen = subprocess.Popen


def _update_skill_md_description(skill_md_path: Path, new_description: str) -> str:
    """SKILL.md frontmatter description을 갱신하고 원본 content 반환."""
    content = skill_md_path.read_text()

    fm_match = re.match(r'^(---\n)(.*?)(\n---\n)', content, re.DOTALL)
    if not fm_match:
        raise ValueError(f"No frontmatter in {skill_md_path}")

    fm_open = fm_match.group(1)
    fm = fm_match.group(2)
    fm_close = fm_match.group(3)
    rest = content[fm_match.end():]

    indented = '\n'.join('  ' + line for line in new_description.split('\n'))
    new_block = f'description: |\n{indented}'

    new_fm = re.sub(
        r'(?ms)^description:.*?(?=^[a-zA-Z_][a-zA-Z0-9_-]*:|\Z)',
        new_block + '\n',
        fm,
        count=1,
    )

    new_content = fm_open + new_fm.rstrip('\n') + fm_close + rest
    skill_md_path.write_text(new_content)
    return content


def _restore_skill_md(skill_md_path: Path, original_content: str):
    skill_md_path.write_text(original_content)


def _run_single_query(query: str, plugin_dir: str, target_skill_name: str, model: str | None, timeout: int) -> int:
    """단일 query 실행. trigger되면 1, 아니면 0."""
    cmd = [
        "claude", "-p",
        "--plugin-dir", plugin_dir,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
    ]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    proc = _original_popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        env=env,
    )
    try:
        proc.stdin.write(query)
        proc.stdin.close()
    except Exception:
        proc.kill()
        return 0

    triggered = False
    pending_skill = False
    accumulated_json = ""

    start = time.time()
    while time.time() - start < timeout:
        if proc.poll() is not None and not pending_skill:
            remaining = proc.stdout.read() if proc.stdout else ""
            for line in remaining.split('\n'):
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("type") == "stream_event":
                    se = e.get("event", {})
                    if se.get("type") == "content_block_delta":
                        delta = se.get("delta", {})
                        if delta.get("type") == "input_json_delta":
                            accumulated_json += delta.get("partial_json", "")
            if target_skill_name in accumulated_json:
                triggered = True
            break

        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue

        if e.get("type") == "stream_event":
            se = e.get("event", {})
            st = se.get("type", "")
            if st == "content_block_start":
                cb = se.get("content_block", {})
                if cb.get("type") == "tool_use" and cb.get("name") == "Skill":
                    pending_skill = True
                    accumulated_json = ""
            elif st == "content_block_delta" and pending_skill:
                delta = se.get("delta", {})
                if delta.get("type") == "input_json_delta":
                    accumulated_json += delta.get("partial_json", "")
                    if target_skill_name in accumulated_json:
                        triggered = True
                        break
            elif st in ("content_block_stop", "message_stop"):
                if pending_skill and target_skill_name in accumulated_json:
                    triggered = True
                if st == "message_stop":
                    break

    try:
        proc.kill()
    except Exception:
        pass
    try:
        proc.wait(timeout=5)
    except Exception:
        pass

    return 1 if triggered else 0


def patched_run_eval(
    eval_set,
    skill_name,
    description,
    num_workers,
    timeout,
    project_root,
    runs_per_query,
    trigger_threshold,
    model=None,
    **kwargs,
):
    skill_path = Path(os.environ["DDDJANGO_SKILL_PATH"])
    plugin_dir = os.environ["DDDJANGO_PLUGIN_DIR"]
    skill_md_path = skill_path / "SKILL.md"

    sys.stderr.write(f"[patched_run_eval] iter eval: {len(eval_set)} queries × {runs_per_query} runs (skill={skill_name})\n")
    sys.stderr.flush()

    original = _update_skill_md_description(skill_md_path, description)

    try:
        triggers_per_query = {q["query"]: 0 for q in eval_set}
        with ThreadPoolExecutor(max_workers=num_workers) as ex:
            futures = {}
            for q in eval_set:
                for run_idx in range(runs_per_query):
                    fut = ex.submit(_run_single_query, q["query"], plugin_dir, skill_name, model, timeout)
                    futures[fut] = q["query"]

            done = 0
            total = len(futures)
            for fut in as_completed(futures):
                q_str = futures[fut]
                try:
                    t = fut.result()
                except Exception as e:
                    sys.stderr.write(f"[patched_run_eval] worker error: {e}\n")
                    t = 0
                triggers_per_query[q_str] += t
                done += 1
                if done % 10 == 0:
                    sys.stderr.write(f"[patched_run_eval] {done}/{total}\n")
                    sys.stderr.flush()

        results = []
        for q in eval_set:
            triggers = triggers_per_query[q["query"]]
            trigger_rate = triggers / runs_per_query
            actually_triggered = trigger_rate >= trigger_threshold
            passed = (actually_triggered == q["should_trigger"])
            results.append({
                "query": q["query"],
                "should_trigger": q["should_trigger"],
                "trigger_rate": trigger_rate,
                "triggers": triggers,
                "runs": runs_per_query,
                "pass": passed,
            })

        passed_count = sum(1 for r in results if r["pass"])
        return {
            "results": results,
            "summary": {"passed": passed_count, "failed": len(results) - passed_count, "total": len(results)},
            "description": description,
        }
    finally:
        _restore_skill_md(skill_md_path, original)


class _FakeContentText:
    type = "text"
    def __init__(self, text: str):
        self.text = text


class _FakeContentThinking:
    type = "thinking"
    def __init__(self, text: str):
        self.thinking = text


class _FakeResponse:
    def __init__(self, text: str, thinking: str = ""):
        blocks = []
        if thinking:
            blocks.append(_FakeContentThinking(thinking))
        blocks.append(_FakeContentText(text))
        self.content = blocks


class _FakeMessages:
    def create(self, model, max_tokens, thinking, messages, **kwargs):
        prompt_parts = []
        for m in messages:
            role = m.get("role", "user").upper()
            content = m.get("content", "")
            if isinstance(content, list):
                content = "\n".join(
                    c.get("text", "") if isinstance(c, dict) else str(c)
                    for c in content
                )
            prompt_parts.append(f"=== {role} ===\n{content}")
        prompt = "\n\n".join(prompt_parts)

        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        cmd = [
            "claude", "-p",
            "--output-format", "json",
            "--model", model,
        ]

        sys.stderr.write(f"[improve] claude -p (model={model}, prompt_chars={len(prompt)})\n")
        sys.stderr.flush()
        t0 = time.time()
        proc = _original_popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
        )
        try:
            stdout, stderr = proc.communicate(input=prompt, timeout=600)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            raise RuntimeError("claude -p timeout (improve)")

        sys.stderr.write(f"[improve] done in {time.time()-t0:.1f}s, rc={proc.returncode}\n")
        sys.stderr.flush()

        if proc.returncode != 0:
            raise RuntimeError(f"claude -p failed (rc={proc.returncode}): {stderr[:1000]}")

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"claude -p output not JSON: {e}; head: {stdout[:500]}")

        if data.get("is_error"):
            raise RuntimeError(f"claude -p returned error: {data}")

        text = data.get("result", "")
        return _FakeResponse(text=text)


class _FakeAnthropic:
    def __init__(self, *args, **kwargs):
        self.messages = _FakeMessages()


def main():
    preparser = argparse.ArgumentParser(add_help=False)
    preparser.add_argument("--skill-path", default=None)
    pre_args, _ = preparser.parse_known_args()
    if pre_args.skill_path:
        sp = Path(pre_args.skill_path).resolve()
        os.environ["DDDJANGO_SKILL_PATH"] = str(sp)
        os.environ["DDDJANGO_PLUGIN_DIR"] = str(sp.parent.parent)
        sys.stderr.write(f"[setup] skill={sp.name} plugin_dir={sp.parent.parent}\n")
        sys.stderr.flush()

    anthropic.Anthropic = _FakeAnthropic

    SKILL_CREATOR_DIR = "/Users/hyun/.claude/plugins/cache/claude-plugins-official/skill-creator/unknown/skills/skill-creator"
    sys.path.insert(0, SKILL_CREATOR_DIR)
    os.chdir(SKILL_CREATOR_DIR)

    import scripts.run_eval as _re_module
    _re_module.run_eval = patched_run_eval

    import scripts.run_loop as _rl_module
    _rl_module.run_eval = patched_run_eval

    _rl_module.main()


if __name__ == "__main__":
    main()
