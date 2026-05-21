수정 대상: runtime-sync
원인 분류: cache drift after source skill metadata update

# implementation-tdd P1 runtime sync 분석

## 평가 범위

- source skill: `dddjango/skills/implementation-tdd/`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/`

## 현재 판정

`dddjango/skills/implementation-tdd/agents/openai.yaml`를 P1 metadata 반영도 보강으로 수정한 뒤 runtime cache와 source skill이 달라졌다.

확인 명령:

```bash
diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd
```

확인 결과:

```text
Files dddjango/skills/implementation-tdd/agents/openai.yaml and /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/agents/openai.yaml differ
```

## 수정 필요성

- 수정 이유: source skill과 runtime cache가 다르면 실제 Codex runtime에서 P1 수정 내용이 반영되지 않는다.
- 수정 범위: runtime cache의 `agents/openai.yaml`만 source와 동일하게 동기화한다.
- 수정하지 말아야 할 범위: source reference, source skill body, bundled references, eval files는 이 runtime-sync 수정 대상이 아니다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent 2개를 실행했다. P1 독립 리뷰는 metadata 수정 전에는 runtime cache가 source와 일치한다고 보고했지만, source metadata 수정 이후에는 해당 결과가 현재 상태를 증명하지 못한다. 현재 상태는 위 `diff -qr` 결과를 우선한다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

- Major 1: source metadata 수정 후 runtime cache가 stale 상태다.

## 완료 조건

- runtime cache `agents/openai.yaml`이 source `agents/openai.yaml`과 동일하다.
- 동기화 후 `diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd`가 차이를 출력하지 않는다.
