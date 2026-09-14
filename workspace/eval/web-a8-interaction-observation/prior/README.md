# 선행 교정 시도 자료(이관본)

원 위치: `/tmp/dddjango-web-a8-interactions-20260913/`(실행·플러그인 스냅샷·build 사본·raw transcript)와 `/tmp/a8-interaction-evaluator-20260913/`(평가자 oracle). 이 폴더에는 프롬프트·호출 인자·판정·oracle만 옮겼다. 기록 시점 2026-09-13.

| 원 디렉터리 | 크기 | 이관 | 미이관 사유 |
|---|---|---|---|
| activation-probe |  40K | prompt.txt·invocation.json·판정 md | raw.jsonl·build 사본·캡처는 대용량·재현 자료라 원 위치 참조 |
| baseline-plugin | 1.9M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| baseline | 6.3M | prompt.txt·invocation.json·판정 md | raw.jsonl·build 사본·캡처는 대용량·재현 자료라 원 위치 참조 |
| candidate-coordinator-v2 |  48M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| candidate-coordinator |  48M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| candidate-plugin | 2.5M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| candidate-review | 6.3M | prompt.txt·invocation.json·판정 md | raw.jsonl·build 사본·캡처는 대용량·재현 자료라 원 위치 참조 |
| candidate-v2-plugin | 2.5M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| chrome-live | 112M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| coordinator-browser |  48M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| coordinator-final |  48M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| coordinator-live |  65M | prompt.txt·invocation.json·판정 md | raw.jsonl·build 사본·캡처는 대용량·재현 자료라 원 위치 참조 |
| coordinator-repair |  16M | prompt.txt·invocation.json·판정 md | raw.jsonl·build 사본·캡처는 대용량·재현 자료라 원 위치 참조 |
| dedicated-chrome | 488K | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| discovery-first-plugin | 2.5M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| final-plugin | 2.5M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| g0-normal-negative | 6.4M | prompt.txt·invocation.json·판정 md | raw.jsonl·build 사본·캡처는 대용량·재현 자료라 원 위치 참조 |
| g0-observed-review |  21M | prompt.txt·invocation.json·판정 md | raw.jsonl·build 사본·캡처는 대용량·재현 자료라 원 위치 참조 |
| mode-split-plugin | 2.5M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| review-final-plugin | 2.5M | 없음 | 플러그인 스냅샷/브라우저 프로필/임시 산출 — 저장소 밖 유지 |
| review-final | 6.4M | prompt.txt·invocation.json·판정 md | raw.jsonl·build 사본·캡처는 대용량·재현 자료라 원 위치 참조 |
| a8-interaction-evaluator-20260913 |  16K | oracle.json·oracle.sha256 | — |

판정 요약(선행 계획 memo §실행 관찰 기준): baseline fail(다른 사유·Select 열림 nit) · g0-normal-negative fail(발견 누락) · coordinator-live 33 case·86 로그(전수 아님) · g0-observed-review fail · coordinator-repair native-review-r3 **pass = 거짓 통과**(같은 핸들러 변이 면제). oracle = 조작군 30·관계 8·시 12·시·도 17·시·군 153.
