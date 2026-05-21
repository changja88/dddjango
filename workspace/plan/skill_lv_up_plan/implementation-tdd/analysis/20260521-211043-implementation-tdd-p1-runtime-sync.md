수정 대상: runtime-sync
원인 분류: cache drift after source skill deduplication

# implementation-tdd P1 runtime sync 분석

## 평가 범위

- source skill: `dddjango/skills/implementation-tdd/`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/`

## 현재 판정

`dddjango/skills/implementation-tdd/SKILL.md`의 boundary guidance 중복을 줄인 뒤 runtime cache와 source skill이 달라졌다.

확인 명령:

```bash
diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd
```

확인 결과:

```text
Files dddjango/skills/implementation-tdd/SKILL.md and /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/SKILL.md differ
```

## 수정 필요성

- 수정 이유: source `SKILL.md` 변경이 runtime cache에 반영되어야 실제 runtime에서 같은 instruction을 사용한다.
- 수정 범위: runtime cache의 `SKILL.md`만 source와 동일하게 동기화한다.
- 수정하지 말아야 할 범위: source reference, bundled references, agents metadata, eval files는 이 runtime-sync 수정 대상이 아니다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent 리뷰 결과를 반영한 skill 수정 뒤 발생한 cache drift다. 현재 상태는 위 `diff -qr` 결과를 기준으로 판단한다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

- Major 1: source `SKILL.md` 수정 후 runtime cache가 stale 상태다.

## 완료 조건

- runtime cache `SKILL.md`가 source `SKILL.md`와 동일하다.
- 동기화 후 source skill과 runtime cache 사이에 diff가 없다.
