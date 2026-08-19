너는 적대 검증자다. dddjango 저장소의 온톨로지 센서스(절 유형 분류)에서 **서사성(NAR) 판정을 반증**하는 것이 과업이다 — NAR 오분류는 이후 전량 이관에서 그 절이 통째로 누락되므로, 규범을 «찾아내려는» 자세로 읽어라.

## 판정 기준 (이 정의가 유일한 기준)
규범 문장 = «에이전트·파이프라인·생성 코드의 행동을 구속하는 지시·금지·조건 문장». 설명·예제·이유·교과 지식·일반론은 규범이 아니다. 애매하면 «애매-포함 후보»로 별도 표기. 코드 펜스 안 텍스트는 규범이 아니다(단 그 코드를 강제하는 산문이 있으면 그 산문이 규범). 표 셀·리스트 항이라도 행동을 구속하면 규범이다. 주의: «~해야 한다»가 있어도 교과 설명(예: 일반 원칙 서술, 타 도구 소개)이면 규범이 아니다 — 구속 대상(이 파이프라인의 에이전트/생성 코드)이 있는지 보라.

## 대상 절 42개 (파일 경로는 저장소 루트 기준, 행 범위는 1-indexed 원문 행)
아래 각 절의 원문 스팬을 직접 읽어라(sed -n '<start>,<end>p' <파일> 활용).

[신호어 보유 — 최우선 재판정 7건]
- dddjango/skills/discipline-cleancode/references/final.md 756-818 (s060-7.2)
- dddjango/skills/discipline-cleancode/references/final.md 1690-1715 (s099)
- dddjango/skills/discipline-cleancode/references/final.md 2018-2048 (s115)
- dddjango/skills/architecture-db/references/final.md 84-95 (s011-2.5)
- dddjango/skills/architecture-db/references/final.md 213-222 (s026-6.4)
- dddjango/skills/architecture-api/references/final.md 69-76 (s010-2.2)
- dddjango/skills/implementation-test/references/final.md 86-99 (s006-1.3)

[층화 표본 35건]
- dddjango/skills/architecture-ddd/references/final.md 463-464 (s015-3) · 34-35 (s006-2) · 446-462 (s014-2.8) · 821-837 (s020)
- dddjango/skills/discipline-cleancode/references/final.md 2271-2272 (s124-16) · 1759-1780 (s102-13.2) · 22-44 (s002) · 2143-2167 (s120)
- dddjango/skills/implementation-python/references/final.md 1512-1539 (s075-12.3) · 452-478 (s021-2.4) · 1070-1099 (s055-9.1) · 1444-1485 (s073-12.1)
- dddjango/skills/implementation-test/references/final.md 466-506 (s025-5.2) · 1221-1264 (s052-9.4) · 2245-2278 (s087-17.4)
- dddjango/skills/implementation-django/references/final.md 530-531 (s031-5) · 1668-1669 (s080-17) · 3-24 (s002) · 1786-1789 (s093)
- dddjango/skills/discipline-tdd/references/final.md 17-26 (s004-1.2) · 616-617 (s039-9) · 816-817 (s048-11) · 253-256 (s016-4.3)
- dddjango/skills/implementation-django-ninja/references/final.md 901-902 (s027-9) · 373-374 (s015-4) · 33-34 (s003-1) · 1001-1019 (s032-12)
- dddjango/skills/architecture-api/references/final.md 436-442 (s046-10.2) · 620-638 (s067-15)
- dddjango/skills/architecture-db/references/final.md 673-693 (s065-13.3) · 354-362 (s040-9.3)
- dddjango/skills/discipline-houserules/references/final.md 222-223 (s012-4) · 181-182 (s005-2)
- dddjango/skills/discipline-houserules/SKILL.md 69-70 (s010-6)
- dddjango/skills/implementation-django-web/SKILL.md 7-8 (s002)

## 출력 형식 (최종 메시지로만 — 파일 쓰기 금지)
```
# L-A NAR 반증 결과
검토 절: 42
## 발견 (REF 오분류 주장)
| # | 절(파일/절키) | 규범 문장 verbatim 인용 | 행 | 심각도(확실/애매-포함 후보) |
(발견 0이면 «발견 0» 명시)
## 판정 유지 (NAR 타당)
간단 집계 + 신호어 7건 각각의 비규범 사유 한 줄
```
