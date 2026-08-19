너는 적대 검증자다. T1 파일럿 이관의 **블록 분해 경계(kind 판정)와 계수 잔차 재판정을 반증**하라.

## 재료 (저장소 루트 기준)
- 블록 실물: `ontology/rules/implementation-django-ninja-final.ttl` · `ontology/rules/architecture-ddd-final.ttl` — 각 블록의 djr:kind(kind-norm/prose/code/table-row)와 djr:text 리터럴(원문 verbatim).
- 이관 명세: `workspace/design/2026-08-19-ontology-t1-migrate/spec-*.json`.
- 게이트 1 동결 센서스 계수(측정 연속성 기준): ninja s023-6.2 규범 85 · ddd s017-3.2 규범 23(`workspace/design/2026-08-19-ontology-t1-census/E07-classify.tsv`·`E01-classify.tsv`).
- 검수 패키지의 잔차 주장(반증 대상): `workspace/design/2026-08-19-ontology-t1-review.md` «계수 잔차 기록» — §6.2 Work 83 vs 85(잔차 2: b19 «§2.2 예시 지시문»·b24 «assert_never 해설»을 서사 재판정) · §3.2 Work 18 vs 23(잔차 5: blockquote 재진술 1+정의·인용 4 재판정).
- 판정 기준: 규범 문장 = «행동을 구속하는 지시·금지·조건 문장(설명·예제·이유 제외, 애매하면 포함+비고)». 코드 펜스 안 텍스트는 규범 계수 밖(단 강제하는 산문이 밖에 있으면 그 산문이 규범).

## 과업 (반증 지향)
1. **prose 판정 블록에서 규범 발굴**: kind-prose 블록 전건(양 문서)의 리터럴을 정독 — 행동 구속 문장이 숨었는지. 특히 ninja s023-6.2의 b19(«§2.2가 sync concrete-catch 예시다…»)·b24(«application-owned closed…drennan…드러난다») — prose 재판정이 타당한가, census가 이들을 규범으로 센 것이 옳았나.
2. **kind-norm인데 Work 0인 블록**(ninja §6.1 매핑 불릿 13항·§6.2 리스트 항 3개): «명사구라 문장 계수 밖» 판정의 타당성 — 구속 항목으로서 Work 채번이 필요했던 건 없나.
3. **§3.2 잔차 5건**: blockquote(b1 — restates로 처리)·정의 2문(b2)·인용 2문(b3)의 비규범 재판정이 타당한가.
4. **code/table-row 판정**: 펜스·표 아닌 것이 code/table-row로, 또는 그 역이 있는가.

## 출력 형식 (최종 메시지로만 — 파일 쓰기 금지)
```
# L-G 분해 경계 반증 결과
## 발견
| # | 블록 좌표 | 유형(prose 내 규범/Work 필요/잔차 재판정 뒤집힘/kind 오판) | 문장 인용 | 주장 |
(발견 0이면 «발견 0» 명시)
## 잔차 판정
§6.2 잔차 2건·§3.2 잔차 5건 각각 유지/뒤집힘 + 사유 한 줄
```
