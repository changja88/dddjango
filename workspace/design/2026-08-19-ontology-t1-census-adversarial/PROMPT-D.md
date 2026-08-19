너는 적대 검증자다. 온톨로지 센서스의 **규범 문장 계수 잔차 판정 4건**(T1 계수 3,225 vs P0 3,217)을 재심하라 — 각 판정이 P0 계수 규약과 T1 규약 문면으로 정당화되는지, 판정이 틀렸다면 올바른 계수는 무엇인지.

## 규약 (판정의 유일 기준)
- P0 규약: 규범 문장 = «에이전트·파이프라인·생성 코드의 행동을 구속하는 지시·금지·조건 문장(설명·예제·이유 제외, 애매하면 포함+비고)».
- T1 추가 규약: 코드 펜스 안 텍스트는 규범 계수 밖(단 그 코드를 강제하는 산문이 있으면 그 산문이 규범). 표·체크리스트의 구속 항목은 포함.

## 재심 대상 4건
1. **E03 −11**: `workspace/design/2026-08-19-ontology-t1-census/E03-recon.md` §4가 «코드 펜스 내 지시 주석 11건 제외»를 주장(§1.2·1.7·1.8·3.5·4.5·8.9·9.5·10.8·16.1·17.3·27.1). 원문 `dddjango/skills/implementation-python/references/final.md`에서 이 11곳을 실측하라 — 정말 펜스 안인가? 그 코드를 강제하는 산문이 밖에 있는가(있다면 제외가 아니라 산문 계수여야 한다)?
2. **E08 +1**: `E08-recon.md` — architecture-api final의 «의존 항목 명시 기록» 지시 1문장 신규 계수. 원문에서 해당 문장을 찾아 규범성 판정.
3. **E09 +10**: `E09-recon.md` — 두 SKILL.md frontmatter 계상(web 4·houserules 6). frontmatter(description 등)의 문장들이 «행동 구속»인지, 4/6 배분이 실제 문면과 맞는지 원문 실측(`dddjango/skills/implementation-django-web/SKILL.md`·`dddjango/skills/discipline-houserules/SKILL.md` 선두).
4. **E10 +8**: `E10-recon.md` — 8문서 frontmatter description 각 1문 계수. `dddjango/commands/dddjango.md`+`dddjango/agents/*.md` 선두를 실측해 8건이 실제로 각 1문인지, 규범성 판정이 규약에 맞는지.

추가: E05의 h4 접힘 절 P0 계수 재배분(«§4.2: s026=1·s027=2·s028=0») 표본 1건을 `E05-recon.md`와 원문(`dddjango/skills/implementation-django/references/final.md`)으로 검산하라.

## 출력 형식 (최종 메시지로만 — 파일 쓰기 금지)
```
# L-D 계수 잔차 재심 결과
| # | 대상 | 판정(유지/뒤집힘/부분 수정) | 근거(원문 인용·행) | 수정 시 올바른 계수 |
## 종합
3,225라는 총계가 유지되는가, 수정되어야 하는가
```
