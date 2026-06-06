# Lens L3 — 백스톱 맹점 (결정적 게이트 exit0인데 변종 통과·부재·저recall)

> 정의: 결정적 백스톱(①~⑬)이 exit0인데 의미 변종 통과, 원리상 못 보는 변종, 또는 부재/저-recall. 고정밀·저recall의 대가. 캐논 앵커 = DO-NOT-RETRY #11.

| episode_id | mode | evidence_anchor | severity | is_open | note |
|---|---|---|---|---|---|
| DR-24 | L3 | DEVLOG:169 "exit0이 자기 텍스트 계약상 정확(status:int plain dataclass라 신호 0)…v3 3중 방어망의 의미적 커버리지 갭"; REMAINING:62 | critical | no | 캐논: ②check-error-centralization exit0인데 멱등성 status:int 변종이 죽은코드로 통과 |
| DR-45 | L3 | DEVLOG:376 "백스톱 13종+단일정독 못 본 major 4"; :383 "표준 자체 빈틈"; aclex-claude:12 | critical | yes | 캐논: 13종 exit0인데 인프라-예외 500 누수·sequential이라 영구 green |
| ACL-EX | L3 | DEVLOG:404 DNR-14; aclex-claude:21 "포트 도메인 예외 집합에 앵커링…인프라 transient 범위 밖" | critical | yes | 표준 빈틈 #1: 백스톱 부재(전파-도달성 정적분석 FP불가로 DR-44 보류)+포트 도메인-예외만 앵커 |
| pytest-MISS | L3 | DEVLOG:384④ "백스톱 ⑬ 맹점=pytest *무설정*은 못 봄, 깨진설정만" | major | yes | ⑬은 깨진 설정만·pytest 자체 미채택(manage.py test)은 원리상 못 봄 |
| C3 | L3 | DEVLOG:213 "9종 백스톱에 C3 검사 0(좁은 텍스트 계약=DR-24)"; :216 "이름-위장 저-recall" | major | no | ⑩ 신설 전 백스톱 0·신설 후에도 이름-위장 저recall |
| C4 | L3 | DEVLOG:246 "저-recall(도메인 메서드 application service에·이름-위장→reviewer 위임)"; :199 "leg-1.5 미작성" | major | no | ⑪은 C형(domain_layer 0개)만·B형 복제·이름위장 사각 |
| P2 | L3 | DEVLOG:114 "고정밀·저-recall(7회피는 ②③ 위임)"; :66 "결정적 grep도 신기루" | minor | no | ①은 7 회피경로 중 좁은 1형태만·나머지 reviewer 위임(설계상 저recall) |
| 깨진JSON | L3 | DEVLOG:377 "415 데코는 CT만 봄"; aclex-claude:13 | major | yes | DR-35 view 데코레이터가 content-type만 검사·깨진 본문 problem+json 미중앙화 사각 |
| 위장-oversell | L3 | DEVLOG:378 "CAS 무력화해도 통과"; aclex-claude:14 | major | yes | 백스톱·mutation 둘 다 못 본 위장 green(순차 테스트라 CAS 미실행) |
| 위장-constraint | L3 | DEVLOG:379 "산출물 삭제해도 false green"; aclex-claude:15 | major | yes | 명명 제약 약화/삭제해도 green(암묵 CHECK)·테스트 진정성 백스톱 부재 |
| DNR-11 | L3 | DEVLOG:401 "백스톱 침묵(exit0)은 좁은 텍스트 계약 통과일 뿐…전면 준수로 일반화 금지" | critical | n/a | 캐논 교훈 박제·DR-23 exit0→DR-24 변종이 직접 증거 |
| DNR-14 | L3 | DEVLOG:404 "백스톱 13종 exit0+단일정독 clean을 전면 준수로 일반화 금지" | critical | yes | 캐논 교훈·DR-45 인프라-예외 누수 일반화 |

NEW (L3 아님): NJ-4=NEW:backstop-live-unfired(백스톱 정상 발화 exit2·FP0·라이브 미stress만) · SD-7=NEW:backstop-live-unfired(동일) · DR-21=NEW:reviewer-recall-downgrade(LLM reviewer 백스톱, 결정적-스크립트 아님·앵커 DNR-10) · DR-22=NEW:reviewer-recall-downgrade · DR-37=NEW:backstop-deferred-undetected(cross-BC FK 백스톱 보류·텍스트만).

핵심: 결정적 백스톱 exit0은 "자기 스크립트의 좁은 텍스트 계약 통과"만 보증, "구조적/의미적 준수"는 아님 — DR-23→DR-24(status:int)·DR-44→DR-45(infra leak) 두 번 이 오독 발생, DNR-11/14가 박제. ACL-EX는 결정적 백스톱이 *원리상 불가*(전파-도달성 정적분석 FP-무한)라 열림.
