#!/usr/bin/env python3
"""게이트 반송 프로토콜 검사 — 세션 jsonl 결정적 파생 (T2-3 · 동결 §1 ② 의무 산출물).

**이 도구는 A/B 판정에 산입되지 않는다.** 실런 판형이 «무수정 승인 고정»(t2-plan §2 T2-0a)
이라 게이트 반송은 **구조상 0이 기대값**이다. 따라서 이것은 측정기가 아니라 **프로토콜
불변식 검사기**다 — 비0이면 실런 프로토콜이 깨진 것이므로 invalid run 경보다. 암별 «수리
노력» 비교는 재생성 루프의 회전 레코드가 소유한다(별도 계상 — 동결 §1 ② 문면).

조작적 정의(설계 판단표 v2 §4 B1~B13 — 선행 적대 리뷰 통과분):

- **반송 단위** = `AskUserQuestion` 왕복 1건. `requested`(사용자가 «승인»이 아닌 답을 줌)와
  `effectuated`(그 뒤 같은 G단계가 실제 재진입)를 **분리 계상**하고, 공식 반송은 후자다.
- **게이트 식별** = 배너 1행 정규식이 **같은 논리 completion**(`message.id`+`requestId`)의
  tool_use 앞 text 블록에 있을 때만 `gate`. assistant 응답이 text/thinking/tool_use 레코드로
  쪼개지고(실측: 동일 message.id 분할 최대 9·분할률 72%) 「가장 가까운 텍스트」 휴리스틱은
  **다른 completion**의 배너를 붙일 수 있어 폐기했다.
- **판정** = `toolUseResult.answers` 의 답이 그 질문의 `options[].label` 과 **정확 일치**할
  때만 결정적. 자유 입력은 `freeform` 으로 분리하고 **추정하지 않는다**(실측: 사용자가 label
  대신 산문으로 답한 사례가 실재).
- **결합키** = `tool_use.id == tool_result.tool_use_id` 단일 규칙(문면 매칭 금지 — 중복 문면·
  interleave 에서 깨진다).
- **세션 경계** = 파일 단위 추정 폐기. 사건을 global identity 로 dedupe 한다(실측: 동일 Ask
  ID 가 두 파일에, tool_result 88건이 복제 — resume 계열). 같은 ID·다른 내용은 오류 중단.
- **사람 메시지** = provenance 와 태그의 **결합** 판정(실측: provenance 단독은 하네스 주입
  85건을 못 거르고, 태그 단독은 `[Image:]` 캡션을 못 거른다). 판정 불능은 human 으로 강제하지
  않고 `suspect` 로 노출한다.
- **내부 루프 회전 제외**: 계수기는 회전 레코드를 읽지 않는다. 루프는 `AskUserQuestion` 을
  쓰지 않으므로 구조적으로 분리돼 있고, 배너 앵커 요구가 루프발 질문을 gate 에서 떨어뜨린다.

exit 0 = 프로토콜 정상 / 3 = 미분류·반송 존재(invalid run 경보) / 1 = 사용 오류·재료 결손·ID 충돌.

사용: python3 session_bounce_counter.py <jsonl|디렉터리> [...] [--self-test]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
FIXTURES: Path = REPO_ROOT / "workspace" / "eval" / "fixtures" / "bounce_counter"

# 배너 1행 — `dddjango.md` 게이트 배너 형식의 고정 문면(`{…}` 만 치환된다).
BANNER_RE: "re.Pattern[str]" = re.compile(
    r"^dddjango · (G0 스코프|G1 설계|G2 구현) 승인$", re.MULTILINE)
APPROVE_PREFIX: str = "승인"
BOUNCE_PREFIX: str = "수정 요청"
APPROVE_WORD: str = "승인"

# 하네스 주입 접두(실측 관측분만 — 추측으로 늘리지 않는다).
HARNESS_TAGS: "tuple[str, ...]" = (
    "<local-command-caveat>", "<command-name>", "<local-command-stdout>",
    "<task-notification>", "<system-reminder>", "[Image:",
    "This session is being continued from a previous conversation",
)


class UsageError(Exception):
    """사용 오류·재료 결손·ID 충돌 — exit 1."""


def _load(path: Path) -> "list[dict]":
    rows: "list[dict]" = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # 관측 부산물 — 파싱 불가 줄은 건너뛴다(도구가 죽지 않는다)
    return rows


def _blocks(rec: dict) -> "list[dict]":
    content = (rec.get("message") or {}).get("content")
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def _completion_key(rec: dict) -> "tuple":
    msg = rec.get("message") or {}
    return (rec.get("sessionId"), msg.get("id"), rec.get("requestId"))


def _classify_message(rec: dict, text: str) -> str:
    """사람 / 하네스 / 슬래시 명령 / suspect — provenance 와 태그의 결합 판정."""
    stripped: str = text.lstrip()
    if rec.get("isMeta"):
        return "harness"
    if any(stripped.startswith(t) for t in HARNESS_TAGS):
        return "harness"
    if rec.get("promptSource") is not None or rec.get("origin") is not None:
        return "human"
    if stripped.startswith("/"):
        return "slash"          # 사람 행위지만 대화 요구가 아니다 — 별도 분류
    if stripped.startswith("<"):
        return "suspect"        # 미지 주입 태그의 조기 경보
    return "suspect"


class Session:
    """한 세션(sessionId)의 사건 열 — 파일 간 복제는 identity 로 dedupe 된다."""

    def __init__(self, sid: str) -> None:
        self.sid: str = sid
        self.events: "list[tuple[int, str, dict]]" = []   # (순번, 종류, payload)
        self._seen_tool_use: "dict[str, object]" = {}
        self._seen_result: "dict[str, object]" = {}
        self._seen_text: "set[tuple]" = set()
        self._seen_msg: "set[tuple]" = set()
        self._n: int = 0

    def _next(self) -> int:
        self._n += 1
        return self._n

    def add_text(self, rec: dict, text: str) -> None:
        key = (_completion_key(rec), text)
        if key in self._seen_text:
            return
        self._seen_text.add(key)
        self.events.append((self._next(), "text",
                            {"completion": _completion_key(rec), "text": text}))

    def add_ask(self, rec: dict, block: dict) -> None:
        tid = block.get("id")
        payload = json.dumps(block.get("input"), ensure_ascii=False, sort_keys=True)
        if tid in self._seen_tool_use:
            if self._seen_tool_use[tid] != payload:
                raise UsageError(f"같은 tool_use.id {tid!r} 에 다른 내용 — 입력 파일이 충돌한다")
            return
        self._seen_tool_use[tid] = payload
        self.events.append((self._next(), "ask",
                            {"completion": _completion_key(rec), "id": tid,
                             "questions": (block.get("input") or {}).get("questions") or []}))

    def add_result(self, rec: dict, tool_use_id: str) -> None:
        tur = rec.get("toolUseResult")
        if not isinstance(tur, dict) or "answers" not in tur:
            return
        payload = json.dumps(tur.get("answers"), ensure_ascii=False, sort_keys=True)
        if tool_use_id in self._seen_result:
            if self._seen_result[tool_use_id] != payload:
                raise UsageError(
                    f"같은 tool_use_id {tool_use_id!r} 에 다른 답 — 입력 파일이 충돌한다")
            return
        self._seen_result[tool_use_id] = payload
        self.events.append((self._next(), "answer",
                            {"id": tool_use_id, "answers": tur.get("answers") or {},
                             "questions": tur.get("questions") or []}))

    def add_message(self, rec: dict, text: str) -> None:
        key = (rec.get("uuid"), text)
        if key in self._seen_msg:
            return
        self._seen_msg.add(key)
        self.events.append((self._next(), "msg",
                            {"kind": _classify_message(rec, text)}))


def collect(paths: "list[Path]") -> "dict[str, Session]":
    sessions: "dict[str, Session]" = {}
    for path in paths:
        file_sids: "set[str]" = set()
        for rec in _load(path):
            sid = rec.get("sessionId")
            if rec.get("type") not in ("assistant", "user") or rec.get("isSidechain"):
                continue
            if sid is None:
                continue
            file_sids.add(sid)
            sess = sessions.setdefault(sid, Session(sid))
            if rec.get("type") == "assistant":
                for b in _blocks(rec):
                    if b.get("type") == "text":
                        sess.add_text(rec, b.get("text") or "")
                    elif b.get("type") == "tool_use" and b.get("name") == "AskUserQuestion":
                        sess.add_ask(rec, b)
                continue
            content = (rec.get("message") or {}).get("content")
            if isinstance(content, str):
                if rec.get("toolUseResult") is None:
                    sess.add_message(rec, content)
                continue
            for b in _blocks(rec):
                if b.get("type") == "tool_result":
                    sess.add_result(rec, b.get("tool_use_id"))
        if len(file_sids) > 1:
            raise UsageError(
                f"{path.name}: 한 파일에 sessionId {len(file_sids)}개 — 런 manifest 가 "
                f"canonical 파일을 지정해야 한다")
    return sessions


def _banner_stage(text: str) -> "str | None":
    m = BANNER_RE.search(text)
    return m.group(1) if m else None


def _has_approve_word(questions: "list") -> bool:
    for q in questions:
        if APPROVE_WORD in (q.get("question") or ""):
            return True
        for o in q.get("options") or []:
            if APPROVE_WORD in (o.get("label") or ""):
                return True
    return False


def _verdict(questions: "list", answers: dict) -> str:
    """왕복 판정 — label 정확 일치만 결정적. 하나라도 bounced 면 왕복이 bounced."""
    kinds: "list[str]" = []
    for q in questions:
        qtext: str = q.get("question") or ""
        if qtext not in answers:
            continue
        given: str = answers[qtext]
        labels: "list[str]" = [o.get("label") or "" for o in (q.get("options") or [])]
        if given not in labels:
            kinds.append("freeform")
        elif given.startswith(BOUNCE_PREFIX):
            kinds.append("bounced")
        elif given.startswith(APPROVE_PREFIX):
            kinds.append("approved")
        else:
            kinds.append("other_label")
    if not kinds:
        return "freeform"
    for k in ("bounced", "freeform", "other_label"):
        if k in kinds:
            return k
    return "approved"


def analyze(sess: Session) -> dict:
    out = {"gate": 0, "requested": 0, "effectuated": 0, "approved": 0, "other_label": 0,
           "freeform": 0, "ambiguous": 0, "post_approval": 0, "suspect": 0}
    # completion → 그 안에서 tool_use 앞에 나온 배너 단계
    banner_by_completion: "dict[tuple, str]" = {}
    stage_seen_after: "list[tuple[int, str]]" = []   # (순번, 배너 단계) 전체 열
    asks: "dict[str, dict]" = {}
    for seq, kind, payload in sess.events:
        if kind == "text":
            stage = _banner_stage(payload["text"])
            if stage is not None:
                banner_by_completion.setdefault(payload["completion"], stage)
                stage_seen_after.append((seq, stage))
        elif kind == "ask":
            asks[payload["id"]] = {"seq": seq, "completion": payload["completion"],
                                   "questions": payload["questions"]}

    pending_bounce: "list[tuple[int, str]]" = []
    last_approved_seq: "int | None" = None
    gate_seqs: "list[int]" = []

    for seq, kind, payload in sess.events:
        if kind != "answer":
            continue
        ask = asks.get(payload["id"])
        if ask is None:
            out["ambiguous"] += 1       # 결합 실패 — 추정하지 않는다
            continue
        questions = ask["questions"] or payload["questions"]
        stage = banner_by_completion.get(ask["completion"])
        if stage is None:
            if _has_approve_word(questions):
                out["ambiguous"] += 1   # 배너 누락 의심 — fail-loud
            continue
        out["gate"] += 1
        gate_seqs.append(seq)
        verdict = _verdict(questions, payload["answers"])
        if verdict == "bounced":
            out["requested"] += 1
            pending_bounce.append((seq, stage))
        elif verdict == "approved":
            out["approved"] += 1
            last_approved_seq = seq
        else:
            out[verdict] += 1

    # effectuated — 반송 뒤 같은 G단계 배너가 다시 나왔는가(단계 재진입)
    for bseq, bstage in pending_bounce:
        if any(s > bseq and stage == bstage for s, stage in stage_seen_after):
            out["effectuated"] += 1

    # post_approval — 마지막 승인 뒤, 다음 게이트 왕복 전까지의 사람 메시지
    if last_approved_seq is not None:
        nxt = min([s for s in gate_seqs if s > last_approved_seq], default=None)
        for seq, kind, payload in sess.events:
            if kind != "msg" or seq <= last_approved_seq:
                continue
            if nxt is not None and seq >= nxt:
                continue
            if payload["kind"] == "human":
                out["post_approval"] += 1
    for _seq, kind, payload in sess.events:
        if kind == "msg" and payload["kind"] == "suspect":
            out["suspect"] += 1
    return out


def render(results: "list[tuple[str, dict]]") -> int:
    print("# session_bounce_counter — 게이트 반송 프로토콜 검사")
    print("# 동결 §1 ② 보조 지표 · **A/B 판정 산입 금지** · 기대값 0(무수정 승인 고정)")
    print("# post_approval·suspect 는 하네스 문면 의존(fragile) — 태그 목록 변경 시 값이 바뀐다")
    head = ("| session | gate | requested | effectuated | approved | other_label | "
            "freeform | ambiguous | post_approval | suspect |")
    print(head)
    print("|" + "---|" * 10)
    bad = 0
    for sid, r in results:
        print(f"| {sid[:8]} | {r['gate']} | {r['requested']} | {r['effectuated']} | "
              f"{r['approved']} | {r['other_label']} | {r['freeform']} | {r['ambiguous']} | "
              f"{r['post_approval']} | {r['suspect']} |")
        bad += r["requested"] + r["freeform"] + r["ambiguous"] + r["suspect"]
    print(f"\n판정: {'프로토콜 정상' if not bad else 'invalid run 경보 — 미분류·반송 존재'}")
    return 0 if not bad else 3


def _expand(args: "list[str]") -> "list[Path]":
    paths: "list[Path]" = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            paths.extend(sorted(p.glob("*.jsonl")))
        elif p.is_file():
            paths.append(p)
        else:
            raise UsageError(f"입력 없음: {a}")
    if not paths:
        raise UsageError("jsonl 입력이 없다")
    return paths


def self_test() -> int:
    """픽스처 대조 — 기대값은 구현 «전에» 저작돼 고정돼 있다(픽스처 선행 규율)."""
    expected = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
    failed: "list[str]" = []
    for case in sorted(expected):
        want = expected[case]
        try:
            sessions = collect(_expand([str(FIXTURES / case)]))
            got_exit = render_silent(sessions)
        except UsageError:
            got_exit = 1
            sessions = {}
        if want.get("exit") != got_exit:
            failed.append(f"{case}: exit {got_exit} ≠ 기대 {want.get('exit')}")
            continue
        if got_exit == 1:
            continue
        merged = {k: 0 for k in ("gate", "requested", "effectuated", "approved",
                                 "other_label", "freeform", "ambiguous", "post_approval",
                                 "suspect")}
        for sess in sessions.values():
            for k, v in analyze(sess).items():
                merged[k] += v
        for key, exp in want.items():
            if key == "exit":
                continue
            if merged.get(key) != exp:
                failed.append(f"{case}.{key}: {merged.get(key)} ≠ 기대 {exp}")
    if failed:
        print(f"[self-test] 불일치 {len(failed)}건", file=sys.stderr)
        for f in failed:
            print(f"  {f}", file=sys.stderr)
        return 2
    print(f"[self-test] 픽스처 {len(expected)}/{len(expected)} 일치")
    return 0


# 픽스처 «검출력» 증명용 변이 — 핵심 판정 5지점을 망가뜨리면 self-test 가 red 여야 한다.
# (2026-08-20 실측 교훈: 첫 변이 설계 3종이 «중복 방어» 지점을 못 건드려 GREEN 이었다 —
#  픽스처 통과는 검출력이 아니다. 아래는 실제 방어 지점을 정확히 겨눈 판이다.)
_MUTATIONS: "tuple[tuple[str, str, str], ...]" = (
    ("논리 completion 무시(다른 completion 배너 채택)",
     '        stage = banner_by_completion.get(ask["completion"])',
     '        stage = banner_by_completion.get(ask["completion"]) or '
     'next(iter(banner_by_completion.values()), None)'),
    ("freeform 을 승인으로 추정",
     '            kinds.append("freeform")',
     '            kinds.append("approved")'),
    ("answer dedupe 제거(파일 간 복제 이중 계수)",
     '        if tool_use_id in self._seen_result:',
     '        if False:'),
    ("isMeta provenance 무시",
     '    if rec.get("isMeta"):\n        return "harness"',
     '    if False:\n        return "harness"'),
    ("effectuated 를 requested 와 동일시(재진입 미확인)",
     '        if any(s > bseq and stage == bstage for s, stage in stage_seen_after):',
     '        if True:'),
)


def mutation_test() -> int:
    """변이 주입 self-test — 원본 파일은 건드리지 않고 임시 사본으로 돌린다."""
    import subprocess
    import tempfile

    src: str = Path(__file__).read_text(encoding="utf-8")
    survived: "list[str]" = []
    for name, old, new in _MUTATIONS:
        if old not in src:
            survived.append(f"{name}: 변이 지점 소실 — 변이 표를 코드에 맞춰 갱신하라")
            continue
        with tempfile.TemporaryDirectory() as td:
            mutant = Path(td) / "mutant.py"
            mutant.write_text(src.replace(old, new, 1), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(mutant), "--self-test"],
                                  capture_output=True, text=True)
        if proc.returncode == 0:
            survived.append(f"{name}: 변이가 살아남음(픽스처가 못 잡는다)")
    if survived:
        print(f"[mutation] 생존 변이 {len(survived)}건 — 픽스처 검출력 부족", file=sys.stderr)
        for s in survived:
            print(f"  {s}", file=sys.stderr)
        return 2
    print(f"[mutation] 변이 {len(_MUTATIONS)}종 전건 red — 픽스처 검출력 확인")
    return 0


def render_silent(sessions: "dict[str, Session]") -> int:
    bad = 0
    for sess in sessions.values():
        r = analyze(sess)
        bad += r["requested"] + r["freeform"] + r["ambiguous"] + r["suspect"]
    return 0 if not bad else 3


def main(argv: "list[str]") -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] == ["--mutation-test"]:
        return mutation_test()
    if not argv:
        print(__doc__)
        return 1
    try:
        sessions = collect(_expand(argv))
    except UsageError as exc:
        print(f"사용 오류: {exc}", file=sys.stderr)
        return 1
    results = [(sid, analyze(sess)) for sid, sess in sorted(sessions.items())]
    return render(results)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
