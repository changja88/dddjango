# Phase 0 — 에피소드 마스터 리스트 (동결)

> 근본원인 분석의 분석 단위. "수정 에피소드" = 변경을 처방한 DR 또는 발견/규칙항목 하나.
> 소스 = DEVLOG §2 DR-16~45 · §3 DO-NOT-RETRY · REMAINING-ISSUES. 코퍼스 동결 2026-06-06.
> 이후 Phase 1~3은 이 리스트를 공유 입력으로 받는다. 라벨 규율: 진단 문서에선 DR/루브릭 코드로 환원.

## A. 하드닝 DR 에피소드 (DR-16~45)

| episode_id | 제목(짧게) | 처방 요약 | 소스 앵커 | 알려진 후속 결과 |
|---|---|---|---|---|
| DR-16 | BC 판정-소유 ③ + API 스택 ④ 승격 | 이주 기준=판정·불변식 소유·ninja 1급 설계결정 | DEVLOG:83 | DR-17 동적검증·③ 비결정 잔존 |
| DR-17 | 동적검증 Tier2/3 + ④ 보강 | design-architect "무설치≠plain" 2미러 | DEVLOG:93 | ④ 수렴 달성·③ 비결정 미해소(N≥5) |
| DR-18 | 최종 스모크 → 갭 4건 발견·구현 | P1a~P4 처방 1차 | DEVLOG:110 | DR-19 라이브 재테스트 |
| DR-19 | 라이브 재테스트(smoke2) | P1b/P2/P3 라이브 확정·P1a Codex 재발 | DEVLOG:119 | DR-20 P1a 백스톱 착수 |
| DR-20 | P1a 백스톱 v1 (reviewer 중앙화 규율) | discipline-reviewer blocker 항목 | DEVLOG:137 | DR-21이 신뢰도 정정 |
| DR-21 | P1a 백스톱 라이브-파이어 재현율 약함 | (관측만) blocker→권고 강등 발견 | DEVLOG:144 | 문구 강화 v2로 |
| DR-22 | P1a 강화 v2 + 사전시뮬 0/3 | (실패) 문구강화만으론 부족 확정 | DEVLOG:152 | v3 구조적 개입으로 |
| DR-23 | P1a v3 결정적 백스톱 + 생산자 예방 | ②check-error-centralization.py + architect 명세 | DEVLOG:159 | B트랙 "준수"→DR-24 정정 |
| DR-24 | C 트랙 심층감사 (B트랙 "완전준수" 정정) | (감사) C1~C9·L1~L4 인벤토리 | DEVLOG:167 | P1a 릴리스 보류 재개 |
| DR-25 | 평가 시스템 재구조화 | rubric/·results/ 분리·관리 규약 | DEVLOG:179 | (인프라) |
| DR-26 | catalog 컨테이너 §0-1 회귀 3-leg | 예방·백스톱⑦·감사 3중 | DEVLOG:190 | DR-34서 ⑦ 라이브 예방 확정 |
| DR-27 | NJ-경계 가이드+백스톱 1.0.4 | §6.3·백스톱⑧⑨ P-α/P-β | DEVLOG:202 | P-α/P-β 라이브 예방·C3 재현(미해결) |
| DR-28 | C3 멱등성 스코프크립 백스톱 ⑩ | 코드-탐지 백스톱 + salience | DEVLOG:211 | DR-30 라이브 배선 검증 |
| DR-29 | 백스톱 10종 발화 매트릭스(스크립트) | 실5+합성5 발화 확인 | DEVLOG:219 | 라이브 배선 미검증 잔여 |
| DR-30 | 라이브 배선 dual 검증 (exit2 차단) | (검증) 주입→exit2→반송 양 런타임 | DEVLOG:225 | 부수=G0 plain 발견 |
| DR-31 | G0 plain-추천 예방 1.0.6 | G0 절 음성경계 2미러 | DEVLOG:233 | DR-34서 before/after 확정 |
| DR-32 | C4 빈혈 SQL 백스톱 ⑪ (C형) | domain_layer 부재 탐지 + reviewer | DEVLOG:240 | DR-34서 ⑪ 라이브 배선 확정 |
| DR-33 | C1 과대평가·스킵 / C6 N=1 reviewer | (재검증) 반복된 것만 보강 원칙 | DEVLOG:248 | C4만 N=3 진짜 갭 |
| DR-34 | 라이브 검증 dual (G0·C4⑪·⑦) | (검증) + 정식채점 Claude NJ-2 FAIL | DEVLOG:254 | major-1=NJ-2 후속 |
| DR-35 | NJ-2 §6.3 협상 레시피 교체 | ninja 1.6.x parse_body→400 버그·view 데코레이터 | DEVLOG:267 | DR-36 라이브 효과검증 |
| DR-36 | DR-35 라이브 + 33항목 채점 | (검증) 양 NJ-2 PASS·Codex FC-2 FAIL | DEVLOG:276 | 부수=BC FK 발견 |
| DR-37 | BC 경계 ORM FK 금지 (규칙3 확장) | 텍스트 16미러·백스톱 보류 | DEVLOG:284 | 라이브 미검증·underdetermined |
| DR-38 | NJ-1 협상 over-impl 추적 (기각) | Q-1 경미·결정적집행 구조적 불가 | DEVLOG:293 | 채점지/RUBRIC Q-1 미세보정만 |
| DR-39 | 변수 어노테이션 공개표면 + 백스톱 ⑫ | §4 권장→공개표면 필수 | DEVLOG:304 | 커밋 6fc850f·라이브 미검증 |
| DR-40 | 산출물 폴더 규약 1.1.0 | .dddjango/<날짜>-<slug>·재빌드 선택 | DEVLOG:313 | 커밋 012cb5f·라이브 미검증 |
| DR-41 | 네이밍 규약 + 포트/어댑터 헥사고날 | DR-05/37 번복·16미러·백스톱 무변경 | DEVLOG:323 | 라이브 미검증 |
| DR-42 | pytest 테스트 표준 + 백스톱 ⑬ | 생태계-우선·하니스 이주·부트스트랩 | DEVLOG:335 | 라이브 미검증 |
| DR-43 | R/C/Q 응용 명명 | Request/Command/Query 인터랙터·SH-3 반영 | DEVLOG:347 | 라이브 미검증 |
| DR-44 | ACL 예외 전수성 1.5.0 | houserules 전수번역+포트앵커E+reviewer C1/C2 | DEVLOG:359 | DR-45 라이브=부분미완 |
| DR-45 | aclex 라이브 + 심층감사 | (감사) ACL 부분미완·major 4 적출 | DEVLOG:369 | 표준 빈틈 #1 미해결 |

## B. 횡단 발견 — 여러 DR에 걸쳐 고쳐지거나 회귀한 것 (실패 추적의 핵)

| episode_id | 제목 | 처방/관측 궤적 | 소스 앵커 | 현 상태 |
|---|---|---|---|---|
| P1a | ninja 오류 중앙화 | DR-18 레시피→DR-20 v1→DR-21 강등→DR-22 0/3→DR-23 v3→DR-24 변종 적발 | DEVLOG:112·137~174·REMAINING-ISSUES P1a | 🟡 5회 반복·릴리스 보류 |
| P1b | 의존성 버전 stale | DR-18 houserules §6.2→DR-19 라이브 1.6.2 교정 | DEVLOG:113·126 | ✅ 라이브 해결 |
| P2 | 코더 메커니즘-소유권 | DR-18 4수(백스톱①)→DR-19 라이브 exit0 | DEVLOG:114·127 | ✅ 라이브 해결 |
| P3 | §9.6 Risky Write 집행 | DR-18 4스테이지→DR-19 Codex catch 라이브 발화 | DEVLOG:115·128 | ✅ 라이브 해결 |
| P4③ | 판정-소유 이주 비결정 | DR-16/18/24/34/45 반복 관측(Claude 리치↔Codex 평면/함수) | DEVLOG:116·133·260·374 | ⚪ N≥5 보류·반복 비결정 |
| NJ-2 | operation raw 파싱 | DR-24 Codex FAIL→DR-34 Claude FAIL(반전)→DR-35 §6.3 교체→DR-36 양 PASS | DEVLOG:207·262·267~279 | 🔄 런간 반전·DR-35로 PASS |
| C3 | 멱등성 스코프크립 | DR-24 뿌리 적발→DR-27 라이브 재현→DR-28 백스톱⑩(가드는 이미 있었으나 architect 번복) | DEVLOG:169·207·211 | 🔧 백스톱⑩·라이브 발화 미검증 |
| C4 | 빈혈 SQL 복제 | DR-24 적발(Codex 3픽스처)→DR-32 백스톱⑪(C형)→DR-34 라이브 배선 | DEVLOG:170·240·257 | 🔧 C형 집행·B형 보류·저recall |
| C1 | 약속 테스트 파일 부재 | DR-24 Critical→DR-33 과대평가·스킵(파일명 무해) | DEVLOG:170·250 | ⚪ 스킵(표준 갭 아님) |
| C5/C6/C7 | G1 미상정 / 포트 오배치 / 죽은 핸들러 | DR-24 Major→DR-33 N=1 캐스케이드 분류 | DEVLOG:170·251~252 | ⚪ N=1·reviewer 위임 |
| catalog-회귀 | catalog 루트 방치 §0-1 | smoke4/6 반복·poc 펄럭→DR-26 3-leg→DR-34 라이브 예방 | DEVLOG:190~200·258 | 🔧 예방·B-1 reviewer-only |
| BC-FK | 경계 ORM FK | DR-36 부수발견→DR-37 규칙3 확장(백스톱 보류) | DEVLOG:280·284~291 | 🔧 텍스트·underdetermined·라이브 미검증 |
| G0-plain | coordinator plain 추천 | DR-30 부수→DR-31 예방→DR-34 before/after 확정 | DEVLOG:231·233·256 | ✅ 라이브 미띄움 확정 |
| NJ-1/협상 | 협상 over-impl | DR-38 추적→"막을 위반 아님"(§6.3 허용 Q-1 경미) | DEVLOG:293~302 | ⏸️ 기각·미세보정만 |

## C. 열린 발견 (현 미해결 — 진단의 매핑 대상)

| episode_id | 제목 | 무엇 | 소스 앵커 | 현 상태 |
|---|---|---|---|---|
| ACL-EX | ACL 인프라-예외 누수 | 포트 *도메인* 예외만 앵커→raw OperationalError/IntegrityError 통과→500 | DEVLOG:376·404·REMAINING-ISSUES ACL-EX | 🔴 표준 빈틈 #1·DR-44 부분미완 |
| 깨진JSON | problem+json 중앙화 갭 | 깨진 본문→400 plain(problem+json 아님) | DEVLOG:377·aclex-claude #2 | 🔴 DR-35 변종 |
| 위장-oversell | 동시성 테스트 진정성 | 순차 테스트라 CAS 충돌 0·무력화해도 green | DEVLOG:378·aclex-claude #3 | 🔴 위장 green |
| 위장-constraint | 제약 테스트 오귀속 | 명명 제약 아닌 필드 암묵 CHECK가 차단 | DEVLOG:379·aclex-claude #4 | 🔴 위장 green |
| NJ-4 | openapi error 선언 | 오류 status를 openapi_extra로만(response= 누락) | REMAINING-ISSUES NJ-4 | 🔧 백스톱·라이브 발화 N≥1 |
| SD-7 | 컨텍스트 격리 | ACL 밖이 타 BC 도메인 예외 직접 import | REMAINING-ISSUES SD-7 | 🔧 백스톱·라이브 발화 N≥1 |
| pytest-MISS | Codex pytest 미채택 | manage.py test+unittest(백스톱⑬ 무설정은 못 봄) | DEVLOG:373·384④ | 🔴 Codex N=2·맹점 |

## D. §3 DO-NOT-RETRY (검증된 헛다리 — 실패모드 직접 증거)

| episode_id | 헛다리 | 소스 앵커 |
|---|---|---|
| DNR-1~9 | 모델 다운그레이드·grep 신기루·다양한 1차진단 오류 | DEVLOG §3:389~ |
| DNR-10 | N=9 텍스트-판별 통과를 "라이브 발화"로 간주 | DEVLOG §3:400 |
| DNR-11 | 백스톱 exit0을 "구조적 준수"로 해석 | DEVLOG §3:401 |
| DNR-12 | 협상(406)에 결정적 백스톱 시도 | DEVLOG §3:402 |
| DNR-13 | 변수 어노테이션 "전부 의무화" | DEVLOG §3:403 |
| DNR-14 | ACL 전수성을 포트 도메인 예외만 앵커 | DEVLOG §3:404 |

> 참고: DNR-1~9 정확 본문은 Phase 1 L5 렌즈가 DEVLOG §3 전수로 확정(여기선 위치 앵커만).
