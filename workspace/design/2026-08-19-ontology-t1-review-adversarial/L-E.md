# L-E Work 정합 반증 결과

검토 Work: 117

## 발견

| # | Work(R-NNNN)·블록 | 유형(오판/왜곡/누락/과채번) | 문장 인용 | 주장 |
|---:|---|---|---|---|
| 1 | 미채번 · `implementation-django-ninja/s022-6.1/b17` | 누락 | “Django Ninja validation error의 default status·body는 framework-owned 응답이다.” | 오류 응답의 소유 경계를 구속하는 문장이다. 뒤의 R-0006~R-0008은 각각 전역 변환 금지·계약 주장 금지·G1 승인에 대응하므로 이 선행 소유 규범을 맡는 Work가 없다. |
| 2 | R-0010 · `architecture-ddd/s051-8/b4` | 오판 | “CQRS 적용 범위 … 보조 패턴으로 선택적 적용” | `선택적 적용`은 CQRS 사용을 의무화하지 않고 선택 가능성을 연다. `Obligation`이 아니라 `Permission`이다. |
| 3 | R-0014 · `architecture-ddd/s051-8/b8` | 오판 | “전략 vs 전술 우선순위 … 전략 설계 우선” | 전략 설계가 전술 설계보다 앞선다는 명시적 우선 규칙이다. `Obligation`이 아니라 `Override`다. |
| 4 | R-0026 · `architecture-ddd/s017-3.2/b9` | 오판 | “항-(2) 판정을 다른 컨텍스트가 소유하고 이 코드는 단순 상류 데이터 소스 … 면 도메인 판정 실내용만 비운다.” | 일반적인 도메인 구현 이주에서 단순 데이터소스를 조건부로 갈라내는 대안 분기다. `Obligation`이 아니라 `Exception`이다. |
| 5 | R-0030 · `architecture-ddd/s017-3.2/b9` | 오판 | “`test` 의미군은 … 실제 테스트가 승인된 경우에만 패키지와 레이아웃을 만든다.” | `경우에만`으로 생성 가능 범위를 제한한다. 무조건적 생성 의무가 아니라 승인 조건부 한정이므로 `Exception`이다. |
| 6 | R-0048 · `implementation-django-ninja/s023-6.2/b3` | 오판 | “`add/update`일 때만 §8–§9의 mount 경계 recipe로 검증한다.” | 핵심 양상은 검증 의무 자체가 아니라 `add/update`에만 적용한다는 조건부 한정이다. `Obligation`이 아니라 `Exception`이다. |
| 7 | R-0049 · `implementation-django-ninja/s023-6.2/b3` | 오판 | “API와 discipline reviewer가 기존 shape 무변경을 확인한 경우에만 Coordinator가 `RESOLVED_DYNAMIC_ERROR_SHAPE_ANALYSIS`로 해소한다.” | marker 해소를 양 리뷰어 확인 조건에 한정한다. `Obligation`이 아니라 `Exception`이다. |
| 8 | R-0052 · `implementation-django-ninja/s023-6.2/b3` | 왜곡 | “선택 module의 직접 mutation과 직접 import한 module-level callable 경로는 owning controller checker가 차단한다.” | prefLabel의 “module-level callable 경로 차단”은 원문의 핵심 범위인 `직접 import한`을 누락한다. 바로 다음 문장이 2-hop·dynamic dispatch 등을 AST 증명 밖으로 돌리므로, 현 라벨은 checker 차단 범위를 과대 표시한다. |
| 9 | R-0059 · `implementation-django-ninja/s023-6.2/b7` | 오판 | “기존 공용 경로가 있으면 승인된 동등 계약을 우선 재사용한다.” | 새 경로보다 기존 승인 경로를 먼저 택하는 명시적 우선 규칙이다. `Obligation`이 아니라 `Override`다. |
| 10 | 미채번 · `implementation-django-ninja/s023-6.2/b15` | 누락 | “이것은 concrete를 인자와 함께 생성하는 우회가 아니다.” | 직전의 BC-base 직접 채움 허용 범위를 제한하고 concrete-with-arguments 우회를 배제한다. R-0069는 허용, R-0070은 keyword 범위에 대응하므로 그 사이의 이 금지·한정 문장이 미채번됐다. |
| 11 | R-0074 · `implementation-django-ninja/s023-6.2/b16` | 오판 | “짧은 반복 mapping은 의도적인 지역 중복이며, 다음 순서를 10번 slot이 승인한 한 path로 보인다.” | 짧은 지역 중복과 해당 mapping path를 인정하는 허용 규범이다. 중복을 반드시 만들라는 의무가 아니므로 `Obligation`이 아니라 `Permission`이다. |
| 12 | 미채번 · `implementation-django-ninja/s023-6.2/b29` | 누락 | “controller가 짧은 exception→concrete mapping과 `Status` 반환을 직접 소유해야 runtime 직렬화와 `response=` 선언이 한눈에 대응한다.” | `직접 소유해야`라는 명시적 의무 문장이다. R-0093은 앞 문장의 raw 응답 금지에, R-0094는 뒤 문장의 반복 허용에 대응하므로 이 문장을 맡는 Work가 없다. |
| 13 | R-0114 · `implementation-django-ninja/s023-6.2/b36` | 오판 | “기존 범위가 RFC 9457 Problem Details를 이미 공개하고 소비자·테스트가 승인된 wire contract에 의존한다면 … 그대로 보존한다.” | 신규 code-profile 기본 규칙에 대한 소비자 의존 조건부 carveout이며 같은 블록도 이를 명시적으로 “carveout”이라 부른다. `Obligation`이 아니라 `Exception`이다. |

## 집계

현행 그래프 유형 분포 확인: Obligation 68 · Prohibition 39 · Permission 6 · Exception 4 · Override 0 = 117.

반증 분포: 오판 9 · 왜곡 1 · 누락 3 · 과채번 0. 기존 Work 판정 유지 수는 **107/117**이며, 미채번 3문장은 이 분모 밖이다.

Serena: skipped — 저장소에 `.serena/project.yml` opt-in 표식이 없어 기본 읽기 도구로 전수 대조했다.