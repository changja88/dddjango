# L-B P0 대사 반증 결과

## 발견

| # | 그룹 | 유형(누락/이중 귀속/규약 모순/산식 불일치) | 내용 | 근거(파일·절) |
|---:|---|---|---|---|
| 1 | E10 | 이중 귀속 | 단일 기계 절 `command-dddjango/s007`이 P0의 Phase 2 step 1–7, 총 7개 절에 귀속됐다. 접기 규약에 공개된 다대일 대응이므로 숨겨진 잔차는 아니지만, “한 기계 절이 두 P0 절에 귀속되지 않는다”는 검증 조건에는 명백히 실패한다. 중복 귀속은 6건이다. | [P0 정본의 step 1–7](/Users/hyun/Desktop/dddjango/workspace/design/2026-08-18-p0-census/E10-command-agents.md:34), [E10-recon §2의 7개 반복 행](/Users/hyun/Desktop/dddjango/workspace/design/2026-08-19-ontology-t1-census/E10-recon.md:30), [sections.tsv의 단일 s007 행](/Users/hyun/Desktop/dddjango/workspace/design/2026-08-19-ontology-t1-census/sections.tsv:880) |
| 2 | E10 | 산식 불일치 | §2 말미는 `1:1 44건`이라고 주장하지만 표의 실제 분류는 일반 1:1 41건, 전문 합성 8건, step 행 7건, h3 분리 행 2건이다. 올바른 P0 분해는 `41+8+7+2=58`, 기계 절 분해는 `41+8+1+4=54`다. 기재된 44를 독립 항목으로 적용하면 P0 61건·기계 57건이 되어 양쪽 모두 3건씩 초과한다. | [E10-recon §2 요약 산식](/Users/hyun/Desktop/dddjango/workspace/design/2026-08-19-ontology-t1-census/E10-recon.md:83) |

P0 전건 대조에서는 누락이 없었다: E03 37/37, E08 39/39, E10 58/58이다. 존재하지 않는 기계 절 키와 §1 접기 규약에 반하는 개별 대응도 발견되지 않았다. E03·E08에는 이중 귀속이 없다.

## 검산 결과

| 그룹 | P0 절 수 | 기계−P0 차이의 독립 분해 | 재계산 기계 절 수 | sections.tsv | 판정 |
|---|---:|---|---:|---:|---|
| E03 | 37 | SKILL 헤더가 기계에서 `(전문)+h1`로 분리 `+1` · 번호 절 h3 접기 `+105` · 출처 하위 h3 5개 접기 `+5` → 총 `+111` | `37+1+105+5=148` | 148 | 일치 |
| E08 | 39 | P0 미계수 h1 네 절 `+4` · db-final h3 `+52` · api-final h3 `+48` · api-final h4 `+2` → 총 `+106` | `39+4+52+48+2=145` | 145 | 일치 |
| E10 | 58 | 전문 합성 `0` · command step 7→1 `−6` · architect h3 분리 `+1` · review-api h3 분리 `+1` → 총 `−4` | `58−6+1+1=54` | 54 | 총계는 일치하지만 7→1 이중 귀속이며, recon의 `1:1 44건` 세부 산식은 오류 |

Serena: skipped — `.serena/project.yml`이 없어 기본 읽기 도구로 검증.