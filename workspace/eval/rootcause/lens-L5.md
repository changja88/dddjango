# Lens L5 — 1차 진단 오류 (진단 철회·번복·헛다리·자기-정정)

> 정의: 첫 진단이 철회·번복되거나 처방이 틀린 진단 위에 세워졌다가 정정된 사례. DO-NOT-RETRY 14항 전수 포함.

가장 농밀한 군집: P1a 사슬(DR-18→24 진단·신뢰도 4~5회 연쇄 정정)·DR-44/45(1차 진단 3개 철회+조정자 자기-정정)·§3 DNR 14항(본질적으로 L5 박제).

| episode_id | mode | evidence_anchor | severity | is_open | note |
|---|---|---|---|---|---|
| P2 | L5 | REMAINING:66 "적대검증으로 방향 2번 뒤집힘"; DEVLOG:114 | major | no | 1차 진단(settings 부재)→번복(금지 무시+집행 부재)+grep 신기루 |
| P1a | L5 | DR-18:112→DR-21(신뢰도 정정)→DR-22(0/3)→DR-24(완전준수 정정) | critical | no | 진단·신뢰도 5회 연쇄 정정된 L5 원형 |
| P4③ | L5 | DEVLOG:91 "DR-24 보강: G1 에스컬레이션 비결정으로 재진단" | minor | no | 1차 "underdetermined 허용"→"G1 에스컬레이션 비결정" 재정의 |
| NJ-2 | L5 | DEVLOG:269 "묻힌 가드가 아니라 표준 처방이 실제 버그…차단 백스톱은 함정" | major | no | 1차 "코더가 §6.3 안 따름"→근본 "§6.3 자체가 ninja 버그" |
| catalog-회귀 | L5 | DEVLOG:194 "진단 절반 정정"; DNR-7 번복 | major | no | 1차 동인 절반 정정+DNR-7 자체가 번복된 규칙 |
| BC-FK | L5 | DEVLOG:288 "규칙4 내부 반론→underdetermined(과한 단정 회피)" | minor | no | 1차 "명백 위반" 단정→"underdetermined" 격하 |
| NJ-1/협상 | L5 | DEVLOG:302 "곁길 3회…매번 N=1 비대칭을 공통패턴 승격→적대리뷰 정정"; :296 "415 3회 진동" | major | no | 곁길 3회+415 3회 진동. 최종 "막을 위반 아님" 기각 |
| DR-32(C4) | L5 | DEVLOG:243 "내 (나-3) 추천 인과가 거짓"; REMAINING "DR-06근거 거짓 폭로→(B) 선회" | major | no | 조정자 자신의 추천 근거가 거짓 폭로→(B) 선회 |
| DR-33(C1) | L5 | DEVLOG:250 "C1=과대평가·스킵" | minor | yes | DR-24 1차 Critical을 "과대평가" 철회 |
| DR-40(B1) | L5 | DEVLOG:319 "1차 '무조건 선행'을 구현시 조건부로 약화→복원" | minor | no | 1차 처방→구현서 자기-약화(자기-회귀)→재검증 복원 |
| DR-31(G0) | L5 | DEVLOG:237 "보강 권고를 N=0 가상 FP로 기각" | minor | no | 적대리뷰 권고를 근거부족으로 기각한 진단 결정(약한 L5) |
| ACL-EX | L5 | DEVLOG:361 "1차 진단 3개 철회…'코더 무죄' 철회"; :382 "carve-out 정당은 오판" | major | yes | DR-44 1차 진단 3개 철회+DR-45 조정자 자기-정정 |
| 깨진JSON | L5 | aclex-claude:13; DEVLOG:377 | major | yes | DR-35 "중앙화 해결" 진단 사각이 감사로 드러남 |
| 위장-oversell | L5 | aclex-claude:14; DEVLOG:378 | major | yes | 1차 채점 green을 mutation 감사가 위장 green으로 정정 |
| 위장-constraint | L5 | aclex-claude:15; DEVLOG:379 | major | yes | 1차 채점 green을 감사가 오귀속 false green으로 정정 |
| pytest-MISS | L5 | DEVLOG:384④ | major | yes | DR-42 백스톱⑬가 잡는다는 가정의 맹점(무설정) |
| DNR-1 | L5 | DEVLOG:391 모델 다운그레이드 헛다리(DR-09) | minor | no | 다운그레이드가 빠를 것이란 가설 반증 |
| DNR-2 | L5 | DEVLOG:392 코더 메커니즘 대체 33분 토끼굴(DR-06) | major | no | P2 뿌리·"관찰성 향상" 판단 헛다리 |
| DNR-3 | L5 | DEVLOG:393 "오케스트레이션 서술 줄여 비용절감" 헛다리 | minor | no | 비용 1위 오진(서술→output) |
| DNR-4 | L5 | DEVLOG:394 커밋 타임스탬프로 코드 추론 헛다리 | minor | no | 타임스탬프 인과 추론 헛다리 |
| DNR-5 | L5 | DEVLOG:395 machine-time 정의 자체가 버그 | minor | no | 측정 정의 오진 |
| DNR-6 | L5 | DEVLOG:396 "선택 제거=결정론" 번복(DR-07) | major | no | 방향 역전(표면화로) |
| DNR-7 | L5 | DEVLOG:397 "조치 없음"→"(DR-26 정정: touched 앱은 이주)" | major | no | 규칙이 명시 번복된 박제 |
| DNR-8 | L5 | DEVLOG:398 긍정레시피만으로 차단 기대→라이브 재발(DR-19) | critical | no | P1a 보류 결정이 라이브 반례로 헛다리 확정 |
| DNR-9 | L5 | DEVLOG:399 캐시 신선화 없이 라이브 검증(14커밋 stale) | major | no | 캐시=워킹트리 가정 헛다리 |
| DNR-10 | L5 | DEVLOG:400 N=9 텍스트판별을 라이브 발화로 간주 | critical | no | DR-20 "9/9 검증"을 DR-21/22가 연쇄 정정 |
| DNR-11 | L5 | DEVLOG:401 exit0을 구조적 준수로 해석 | critical | yes | DR-23 "dual 완전준수"를 DR-24가 정정한 박제 |
| DNR-12 | L5 | DEVLOG:402 협상(406)에 결정적 백스톱 시도 | major | no | DR-38 곁길 박제(구조적 불가) |
| DNR-13 | L5 | DEVLOG:403 변수 어노테이션 "전부 의무화" | minor | no | 1차 "전부 의무화"가 적대4렌즈로 기각 |
| DNR-14 | L5 | DEVLOG:404 ACL 전수번역을 도메인 예외만 앵커 | major | yes | DR-44 처방 자체가 박힌 헛다리. ACL-EX 동일 축 |

NEW: DR-26(§632)=NEW:eval-측-버그(채점자 루브릭 오독이 산출물 오판). 제외(L5 아님): P1b·P3(reframe이나 본질 재명명·정정 아님)·DR-34/36의 "🔄 반전"(런간 *비결정*이지 진단 *철회* 아님 — DEVLOG가 "우열 아님" 명시).

경계: DR-34/36 반전은 같은 표적이 런타임 간 갈린 비결정(L1)이라 L5(진단 철회)와 구분.
