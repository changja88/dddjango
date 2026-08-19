# 선행 설계 리뷰 레인 V — 열린 스코프 (적용 전)

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only)에서 T2-1 보강 설계 묶음이 **적용되기 전에** 결함을 찾아라. **열린 스코프다** — 아래 목록은 출발점일 뿐이고, 지정 밖 결함을 찾는 것이 네 존재 이유다(직전 리뷰의 최대 발견도 지정 밖에서 나왔다). 칭찬·요약 금지.

## 리뷰 대상

- `workspace/design/2026-08-19-ontology-t2-1-attribution-map.md` (귀속 매핑표 — 91행+부속)
- `workspace/design/2026-08-19-ontology-t2-1-formatter-contract.md` (공용 포매터 이행 표)
- 맥락: `workspace/design/2026-08-19-ontology-t2-1-adversarial/MEDIATION.md`(직전 검증 31건 중재+개정 5 기각 부록 — 이 설계가 갚아야 할 빚 목록이다)

## 출발점 (얽매이지 마라)

1. **중재 채택분 누락**: MEDIATION의 «수정 예정» 표 전건이 두 설계 문서 어딘가에 착지했는가 — 착지 안 한 채택 항목을 전부 적출하라(예: regen severity 고정·계수 골든 레인 픽스처·git 레인·multiset 정명·--scripts-dir·record payload 전건 단언·stdout↔record 대응).
2. **포매터 이행 표의 실물 충돌**: 이행 표가 «byte 동일»이라 주장하는 A형 레인이 정말 동일한지(2-space 복원 판형), B형 콜론 추가·ⓓ#511 분해가 소비자(registry_gate 정규화·anchor debt_match 부분문자열·backstop fragment)를 깨는 경우, 계약 레인 존치가 E8과 재충돌하는지.
3. **적용 순서·과도기**: SliceFindings 제거 시점, 매핑 적용과 포매터 이행을 한 커밋에 섞으면 안 되는 이유/괜찮은 이유, EXPECTED 갱신이 두 번 일어나는 낭비 여부.
4. **검증 계획의 구멍**: formatter-contract §검증 계획이 놓친 회귀 표면(코퍼스 미러? corpus_lint? checker_lint 낱말 규율? codex 쌍둥이 byte-diff? spec_lint owner-map 재생성?).
5. **그 밖의 무엇이든**: 두 문서의 내부 모순, 규약(`2026-08-19-ontology-autonomous-protocol.md`)과의 충돌, T2-2 이후 단계에 미치는 부작용, 지금 안 잡으면 비싸지는 것.

## 출력 형식

| # | 심각도(blocker/major/minor) | 결함 | 근거(파일:행 인용·실측) | 수정 제안 |

결함 없는 영역은 «반증 실패» 한 줄. 저장소 수정 금지(read-only).
