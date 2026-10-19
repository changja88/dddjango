# dddjango — 시험 기다림 줄이기(개선 ④): 전체 suite 는 G2 앞 한 번 · 슬라이스 시험은 BC 경로와 소비자 경로 (10-19 설계 · 10-20 구현)

## 바탕
- 바탕: main `f8613a88`(dddjango 2.23.1 · dddjango-web 2.6.1). 바뀌는 것은 Coordinator · coder · design-architect 의 규범(그래프)뿐이다 — 검사기 · 스크립트 · `rulepack.py` 는 바이트 그대로이고, `rulepack.json` 만 재소성된다.
- 판: minor 를 제안한다(새 규범 3 · 개정 3). 매니페스트 판은 `make release` 가 올린다.
- 날짜: 설계 · 작은 시험 10-19 ~ 10-20 · 구현 10-20(ISSUED · Expression 날짜 `2026-10-20`).

## 왜 — 진단
- 진행 레인 아홉의 기록을 다시 셌다. 일한 시간의 약 13% 가 시험 기다림이고, 그중 큰 몫이 프로젝트 전체 suite 한 벌이다(46 번).
- 전체 한 벌 46 번 가운데 퇴행을 실제로 잡은 것은 1 번뿐이었다 — 앞 슬라이스가 루트 conftest 가 싣는 시험 재료(흉내)를 바꿔 다른 BC 의 시험이 붉어졌고, 그 슬라이스의 BC 범위 시험은 놓쳤으며 다음 슬라이스의 전체 실행이 잡았다. G2 앞 전체가 처음 잡은 퇴행은 0 번이었다.
- 규칙끼리 부딪혔다: 명세의 슬라이스 완료 조건(R-3610)에는 범위 제한이 없어 «전체 시험 녹색»을 적을 수 있었고, coder 의 BC 범위 규칙(R-2527)과 어느 쪽이 먼저인지 글이 없었다. 그래서 coder 가 슬라이스 안에서 전체를 여러 번 돌거나, 코디네이터가 슬라이스마다 · 감사 뒤마다 전체를 돌았다.

## 무엇을 바꿨나(그래프 정본 → 재투영 · Codex 짝 손 미러)

| 규범 | 바뀐 것 |
|---|---|
| R-3610 rev2(amendment · design-architect s005/b39) | 완료 조건의 시험 = 그 슬라이스가 바꾸는 BC 의 시험 경로 · 인수 행 시험 · 까닭을 단 소비자 시험 경로(coder 래칫 예외와 같은 찾기 + 리뷰 · 설계가 근거 줄로 짚은 길). 전체 suite 한 벌은 소비자가 곧 전체일 때만. 다른 영역 붉음을 이 명세 밖에서 고치기로 사용자가 정했으면 `## G2 전체 확인` 절(시험 id · 예외 타입과 실패 줄 · 처분 · 사용자 답 출처). 리팩토링 명세에는 두지 않는다. |
| R-2527 rev2(amendment · coder s004/b10) | 전역 판정은 G2 앞 Coordinator 의 전체 suite 와 게이트 몫. 명세가 까닭과 함께 적은 소비자 경로는 돌고, 까닭 없는 «전체 suite» 완료 조건 · Coordinator 입력의 전역 실행만으로는 돌지 않으며 완료 보고에 `전역 스위트 — G2 앞 Coordinator 몫(돌리지 않음)` 을 적는다. |
| R-2528 rev2(amendment · coder s004/b10) | 소비자 찾기 넷: ⑴ BC 폴더 밖 ⑵ 타 BC 소비 표면 ⑶ BC 밖 시험 쪽이 싣는 길(conftest · conftest 가 import 하는 모듈 포함 — 고정물이 깔리는 시험 전부) ⑷ 다른 BC 시험이 경로 글자 · URL 이름으로 부르는 API 의 라우트 · 컨트롤러 · 요청/응답 꼴(그 아래 유스케이스 · 도메인 · 저장소 코드만 바꾼 것은 ⑷ 아님). ⑶ 의 길은 두 꼴뿐이다 — BC 밖 시험 쪽 파일이 이 BC 모듈을 직접 import 하거나, BC 밖 conftest 가 직접 import 하는 모듈(다른 BC 제품 모듈 · `scripts/` 같은 그 밖 모듈이어도 됨 · 배선 모듈은 아님)이 이 BC 모듈을 직접 import 한다. 그 밖 사슬과 제품 코드 · 배선에서 시작하는 길은 ⑶ 도 «불명확»도 아니다. 소비자 실행은 그 파견의 마지막 바꿈 뒤 한 번 · 목록과 같은 붉음은 고치지 않고 보고 · 시험 쪽 파일의 주석 · docstring 만이면 소비자를 더하지 않는다. |
| **R-3664 신설**(command s007/b9) | 전체 suite 의 때 — G2 로 가는 마지막 슬라이스 보고 뒤 홀리스틱(수정 모드 focused) 감사 앞 한 번 · 첫 실패에서 멈추지 않는 꼴 · 슬라이스 끝(슬라이스 0 포함)과 경량 감사 뒤에는 돌지 않음(슬라이스 0 끝 관련 테스트가 전역이면 G2 앞 한 번으로 미루고, G2 배너의 «그 시점의 관련 테스트 결과»는 coder 가 그 슬라이스에서 돈 전역 1회 보고를 옮겨 적음) · 옛 꼴 지시의 까닭 없는 «전체»는 이 한 번이 채움 · 코드가 그대로면 이 한 번이 G2 증거(설치 · git 밖 시험 자원을 바꿨으면 다시). |
| **R-3665 신설**(command s007/b9) | 전체 suite 뒤 바뀐 코드 — 관련 실패를 고치면 전체를 한 번 더(관련 실패가 0 이 될 때까지 — G2 전체 확인 목록과 같은 붉음은 셈 밖 · 뒤 감사가 그 고침을 본다) · 감사 반영은 고친 역할의 래칫 범위와 붉었던 시험만 다시 · G2 배너 · Phase 3 에 전체 결과(그 실행의 HEAD)와 그 뒤 확인. |
| **R-3666 신설**(command s007/b9) | G2 전체 확인 목록 대조 — 사용자 답 출처가 있고 같은 시험 · 같은 까닭이면 반송하지 않고 G2 배너에 따로 적음 · 출처 없음 · 목록 밖 · 까닭 다름은 관련/무관 규칙 그대로 · 전체 green 주장 금지 · 리팩토링 모드 밖. |

- 그대로인 것: G2 앞 Coordinator 전체 suite · 관련 테스트(R-0293) · 기준선 실측 · 인수 시험 전부 · 리팩토링 모드 suite · 6번 registry_gate · 슬라이스 0 끝 관련 테스트(R-3488 — 전역이면 G2 앞으로) · 6′ · 검사기 · 스크립트.
- 설계 3판 뒤 덧붙임 한 구(R-2528 rev2 ⑶ · 정식 문면에만): 사전 확인에서 «conftest 가 import 하는 모듈» 갈래와 «다른 BC 제품 코드가 import 하는 길은 ⑶ 아님»이 부딪히는 실례가 나왔다(한 BC 의 integration conftest → 그 BC 의 ACL 어댑터 → 바뀌는 BC 모듈). 그 시험은 실제로 깨질 수 있는 소비자라 넣는 쪽으로 정했다. 첫 문면(«시험 쪽에서 시작하면 중간에 다른 BC 제품 모듈을 지나도 ⑶»)은 단 수에 한도가 없어 넓게 읽혔다(구현 의미 검토 차단 — 넓게 읽으면 찾기에 안 나오는 사슬 → «불명확 → 전역 1회»가 다시 열림). 그래서 두 꼴(시험 쪽 파일의 직접 import · conftest 가 직접 import 하는 모듈의 직접 import)로 좁히고, 그 밖 사슬은 ⑶ 도 «불명확»도 아니라고 적었다 — 비용 셈(약 124 ~ 140 분)이 쓴 뜻과 같다. 작은 시험판에는 이 구가 없었고, 시험한 조각은 이 길과 무관했다.

## 구현 검토(Claude 둘)와 고침 한 바퀴
| 검토 | 결과 | 처분 |
|---|---|---|
| 충실도(설계 · 시험판 대비) | 차단 0 · 중요 0 · nit 4 | nit 은 다음 후보 |
| 런타임 의미 · 규범 정합 | 차단 1 · 중요 1 · 사소 5 · nit 6 | 받음: 차단(⑶ 두 꼴로 좁힘) · 중요(⑷ 는 API 겉만) · 사소 둘(R-3665 «0 이 될 때까지»에서 목록 붉음 셈 밖 · 슬라이스 0 끝 G2 배너 결과는 coder 의 전역 1회 보고) — 같은 Expression · 같은 블록 · 같은 명칭을 그 자리에서 고침(새 판 없음 · 계수 무변). 나머지는 다음 후보 |

## 작은 A/B(옛 판 2.23.1 vs 새 판 · 실제 레인 조각을 사본에서 다시 돌림 · 확인은 Claude)
| 시험 | 본 것 | 결과 |
|---|---|---|
| ① 슬라이스 안 «전체» 명세 | 전체 한 벌 수 · 사후 실행 결과 | 1 → 0 · 사후 실행 붉음 다섯 이름 · 통과 수 같음 → 통과 |
| ② S5 → 새 G2 | 전체 한 벌 수 · G2 수치 · 감사 지적 | (기준선 빼고) 2 → 1 · 통과 수 · 타입 · lint · 게이트 · 감사 blocker/important 같음 → 통과 |
| ③ ⑶ 루트 conftest 길(새 판만 · 2 회) | coder 가 BC 밖 시험 쪽 찾기로 루트 conftest → autouse 읽기 → 그 표식 시험 전부를 돌아 붉음을 보고 | 2 회 모두 섰다(옛 레인은 다음 슬라이스에서야 잡음) → 통과 |
| ④ 심은 결함 둘(새 판만) | ㉮ 전체 붉음 → 관련 가름 → 고친 뒤 전체 다시 → 감사가 고침을 봄 · ㉯ 명세가 까닭과 함께 적은 소비자 경로를 coder 가 돎 | 둘 다 섰다 → 통과 |

- 효과 [추정]: 아홉 레인 기준 전체 한 벌 46 → 19, 덧붙임 반영 뒤 약 124 ~ 140 분(일한 시간의 약 2.2 ~ 2.4%). 시간 밖 이득 — 루트 conftest 꼴 퇴행이 한 슬라이스 일찍 선다 · 전체 붉음 고침을 감사가 본다.

## 계수(실측 = 설계)
| 계수 | 앞 | 뒤 |
|---|---|---|
| NormShape · WorkShape | 3672 | 3675 |
| ExpressionShape | 4017 | 4023(새 3 + 개정 3) |
| BlockShape · SectionShape | 2992 · 553 | 그대로 |
| q4 `distinct_works` · `rows` | 3663 | 3666 |
| ISSUED 끝 | R-3663 | R-3666 |
| LEDGER 행 | 1815 | 1818(재기준선 3: command-dddjango s007 · agent-coder s004 · agent-design-architect s005) |
| wiring | — | `delegatedTo command-dddjango` 셋(R-3664 ~ R-3666) |

## 파일(17)
- 정본: `ontology/rules/command-dddjango.ttl` · `agent-coder.ttl` · `agent-design-architect.ttl` · `ontology/wiring/command-dddjango.ttl` · `ontology/ISSUED` · `ontology/LEDGER.tsv`.
- 재투영: `dddjango/commands/dddjango.md` · `dddjango/agents/coder.md` · `dddjango/agents/design-architect.md`.
- 소성물 · 골든: `dddjango/scripts/rulepack.json` · Codex `rulepack.json`(byte 같음) · `workspace/eval/fixtures/ontology_gate/target-counts.json` · `workspace/eval/fixtures/rulepack/query-golden.json`(q4).
- Codex 손 미러 셋(아래) · 이 기록.
- 봉인: `workspace/eval/ab/T2-0b-manifest.json`(`manifest_seal.py --write` — 커밋 뒤 봉인 재발행 chore 로 다시 맞춘다).

## Codex 손 미러(parity 대조 절 밖 — 검사기가 못 잡으므로 손 대조)
| Claude | Codex | 넣은 글 · 대조 |
|---|---|---|
| `commands/dddjango.md:165` | `codex-dddjango/skills/dddjango/SKILL.md:184` | 찾을 글 · 바꿀 글이 글자까지 같다 → 두 줄 `cmp` 같음 |
| `agents/coder.md:47` | `codex-dddjango/skills/dddjango-coder/SKILL.md:39` | 같은 글 · «Coordinator» → «코디네이터»(그 파일 관례 — 조사 붙임: «코디네이터의» · 명사 앞은 띄움: «코디네이터 입력» · «코디네이터 몫»). 낱말 대조: 앞부터 있던 차이(«Bash로» ↔ «네이티브 셸로») 밖은 이 바꿈뿐 |
| `agents/design-architect.md:99` | `codex-dddjango/skills/dddjango-design-architect/SKILL.md:93` | 같은 글 · «Coordinator 가» → «코디네이터가». 낱말 대조: 앞부터 있던 «코디네이터가» 한 곳 밖은 이 바꿈뿐 |

## 검증
- 렌더 결과 ↔ 작은 시험판: `agents/design-architect.md` byte 같음 · `agents/coder.md` 는 ⑶ 덧붙임 문장과 ⑷ 정의 두 자리 · `commands/dddjango.md` 는 R-3665 괄호 · 슬라이스 0 끝 문장 두 자리만 다름(시험판에 이 넷을 넣으면 byte 같음).
- 금지 낱말(G12 라벨 드리프트 — `rulepack_smoke.py`): 새 · 고친 명칭 여섯 적중 0 → `DRIFT_REVIEWED` · `scope-limit-norms.md` 무변. `corpus_lint` 위반 0.
- `make verify` · `make verify-mutation` — 수치는 커밋 직전 마지막 실행 로그의 것만 커밋 메시지에 적는다.

## 다음(운영자)
- Claude 검토 둘 → 커밋 → 봉인 재발행 chore → `make verify` 다시 → `make release`(minor). pre-gate 실행 트리 digest 는 `rulepack.json` 을 빼므로 진행 중 레인의 재예보는 필요 없다.
- 다음 후보(이번 판 밖): 역할이 돌린 시험을 코디네이터가 다시 돌지 않기 · 같은 트리 기계 판단 · 구현 시작 기준선 전체 실행 줄이기 · 사건 구독 · in-process HTTP 소비 길의 기계 찾기.

## 다음 후보 — 구현 검토에서 넘긴 것(이번에 고치지 않음)
- (의미 m1) architect «까닭이 붙은 경로만 coder 가 돈다»를 coder 글이 받지 않는다 — 까닭 없이 적힌 BC 밖 개별 경로를 coder 가 돌지 · 보고만 할지 한쪽으로 정한다.
- (의미 m4) 인계 메모 · 발주 글의 «까닭»이 정해져 있지 않다 — «회귀 확인» 같은 일반 목적은 까닭이 아님 · 사용자 원문 지시가 때를 정했으면 게이트 답처럼 따름을 적는다.
- (의미 m5) 수정 모드 3번이 «전체 suite 의 때»를 가리키지 않고, focused 감사가 없을 때 기준점이 비어 있다 — 수정 모드 절에서 Phase 2 5번을 가리키고 감사가 없으면 6번 백스톱 앞으로.
- (의미 n1) architect «그 밖의 길(… 루트 autouse 고정물 …)»이 coder ⑶ 과 겹쳐 읽힌다 — «import 없이 실행되는 길»로 좁히고, 설계 리뷰어 점검 목록에 이 길이 없는 것도 본다.
- (의미 n2) ⑶ 진입이 공용 도움 모듈(conftest · `test_*.py` 아님)이면 소비자가 무엇인지 글이 없다 — «그것을 import 하는 시험» 한 구.
- (의미 n3) `from <상위 패키지> import <BC>` 꼴은 점 경로 grep 에 걸리지 않는다 — 따로 찾는다는 한 구.
- (의미 n4) R-3665 고침으로 트리가 바뀌면 ⓓ 용 registry_gate 를 «감사 직전 트리»로 다시 도는지 한 구.
- (의미 n5) 홀리스틱 갈음이 서지 않아 전체 suite 뒤에 돈 마지막 슬라이스 경량 감사의 반영도 R-3665 가 받게 넓힌다.
- (의미 n6) 주석 · docstring 면제가 coder(⑶ ⑷ 만)와 코디네이터(시험 쪽 파일 전부)에서 다르다 — «⑴ 의 시험 쪽 파일 · ⑶ · ⑷»로 맞춘다.
- (충실도 nit 1) 기록 파일 이름을 선례대로 판을 단 이름(`plan-<판>.md`)으로.
- (충실도 nit 2) 위 «파일(17)» 목록에 봉인 부수 파일(t2-0b 설계 문서의 사실 블록 한 줄)을 더한다 — 커밋 때 매니페스트와 함께 스테이지.
- (충실도 nit 3) R-2528 명칭이 «⑶» 을 정의 없이 쓴다 — 명칭만 읽는 소비자를 위해 번호 없는 글로.
- (충실도 nit 4) Codex coder 보고 글자(«코디네이터 몫»)가 Claude(«Coordinator 몫»)와 다르다 · 두 런타임 머리 구 있음 대조 시험이 없다 — 대조 한 건을 시험에 더한다(봉인 대상이라 재봉인 따름).
- (충실도 관찰) R-3665 · R-3666 의 G2 배너 · Phase 3 줄이 5번 하위 글에만 있다 — 7번 G2 배너 · Phase 3 절에 가리킴 문장(restates)을 더할지.
