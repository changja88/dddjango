# T2-4 자체 적대 패스 (저자 — 레인 AP·AQ 산출 **전**)

> 규율: 저자가 자기 판단표를 공격한 기록. 레인 산출과 **독립**으로 남긴다(중복 발견의 귀속을 가리지 않기 위해 시각·선후를 명시). 작성 = 2026-08-20, 레인 기동 직후·산출 전.

## SF-1 (blocker) — 팩이 실런 런타임에 **도달하지 못한다**

- 실측: 설치 cache = `~/.claude/plugins/cache/changja88-dddjango/dddjango/**2.11.0**`(source `2.12.0`). `scripts/` 34파일 중 **`findings.py` 부재 · `regen_core.py` 부재**. 즉 T2-3 산출물조차 아직 런타임에 없다.
- 귀결: `rulepack.json`·`rulepack.py`를 저장소에 넣는 것만으로는 C암이 아무것도 못 본다. 판단표 R7이 fail-closed이므로 **C암 6런 전멸**(런 무효 → triplet 재실행 → 무한 반복).
- 판단표의 공백: §9 manifest fragment는 팩 **해시**만 봉인하고 「cache에 팩이 실재하고 source와 동등하다」를 **선행조건으로 등재하지 않았다**. T2-0b의 기존 신선도 선행조건 3항(ⓐ 갱신 ⓑ 해시 동등 ⓒ cache 경로 loop probe)은 T2-3 artifact를 겨눈 것이지 팩을 명시하지 않는다.
- 조치: ⓐ T2-0b 선행조건에 **ⓓ 「cache에 `rulepack.json`·`rulepack.py` 실재 + source 해시 동등 + 팩 스키마 파싱 성공」** 추가 ⓑ `workspace/tools/plugin_loop_probe.py`에 **팩 probe**(P5) 추가 — 두 런타임 트리에서 팩을 읽어 동일 selector 결과가 나오는지 ⓒ 판단표 §8 구현 순서에 「설치본 릴리스 버전에 팩 포함」을 명시.

## SF-2 (blocker) — `assemble_prompt` 최상위 형상 전환이 **B암 byte를 깬다**

- 실측: `regen_core.payload()`는 **list**를 돌려주고 `assemble_prompt`가 그것을 `json.dumps` 한다 — 즉 `<violations>` 블록의 JSON은 **배열**이다.
- 판단표 R3은 「C payload = `{violations:[...], norms:[...]}`」로 썼다. 이 형상은 최상위를 **객체**로 바꾸므로, 같은 조립기를 쓰는 한 **B의 JSON도 배열→객체로 바뀐다**. R4의 「B암 프롬프트 byte 불변」과 정면 충돌하고, V3 골든이 즉시 red가 된다(= 설계가 자기 검증 자산에 걸린다).
- 판단표는 「B는 `norms` 키가 없다」고만 썼을 뿐 **최상위 형상 보존을 명시하지 않았다** — 이 공백이 결함의 정확한 소재다.
- 조치(설계 정정): 최상위를 바꾸지 말고 **블록을 하나 더 붙인다**.
  - B: `<violations>[...]</violations>` — **현재와 완전 동일**.
  - C: `<violations>[...]</violations>` + `<norms>[...]</norms>` — 두 블록 모두 배열, 같은 escape 규칙.
  - 헤더는 불변, 푸터 앞에 `norms`가 있을 때만 한 문장 삽입.
- 이 정정이 부수 이득 하나를 준다: `norms`가 **별도 경계 블록**이라 「위반 목록」과 「규범 원문」이 프롬프트에서 섞이지 않는다(W3의 정밀도 손실을 모델이 최소한 **식별**은 할 수 있다).

## SF-3 (major) — 강등 사슬 ①의 계단이 급하다

- R2 ①은 「문면 → `label`만 남기고 `text` 생략」인데 이것이 **전량 삭제**다. 41번째 규범 하나 때문에 40개의 문면이 모두 사라진다.
- 조치: 정렬 **역순으로 아래에서 잘라** 상한에 맞춘다(문서·절·서수 정렬의 뒤쪽부터 `text` 제거). 계단이 1건 단위가 되고, 상위(=문서 앞쪽·절 앞쪽) 규범이 보존된다. 어느 항목이 잘렸는지 용량 로그에 기록.

## SF-4 (major) — 팩 조회와 `select_records`의 **순서가 미정**

- 판단표는 selector 규칙(R1)만 정하고 파이프라인상 위치를 안 정했다. 순서가 뒤집히면 「귀속(N∖L) 밖 위반이 규범을 끌어온다」가 성립한다.
- 조치: 순서를 **고정 명시** — ① 게이트 sidecar(N∖L) → ② `select_records`(severity·scope) → ③ 팩 조회(alias→checker) → ④ 상한·강등 → ⑤ `build_payload`. 팩 조회는 **선별된 위반만**을 입력으로 받는다(전체 findings 아님).

## SF-5 (major) — 팩은 **투영물**이므로 E1 규율이 그대로 붙는다

- E1: 「참조성 산문 문서는 단방향 렌더 투영물(직접 편집 금지, CI가 «투영물==render(그래프)» 검증)」. `rulepack.json`은 그래프의 렌더 투영물이므로 같은 규율 대상이다.
- 판단표는 V2(재현성)로 사실상 그 검사를 넣었으나 **«투영물»로 명명하지 않았다** — 명명하지 않으면 「팩을 손으로 고쳐도 되는가」가 열린 채로 남는다.
- 조치: P2에 「팩 = 투영물 · 직접 편집 금지 · 생성기만이 저자」를 명문화하고, 파일 상단에 편집 금지 표지 키(`"_generated": "ontology_rulepack.py — 직접 편집 금지"`)를 넣는다.

## SF-6 (major) — codex 미러 의무가 **봉인·검증에 없다**

- §8 구현 순서 3에 「codex 미러 복사」를 적었을 뿐, §5 검증 자산과 §9 봉인 목록에는 미러 대조가 없다. T2-3에서 미러 누락은 **실제 verify red**를 냈다(`identity()` 추가 후).
- 조치: V6에 `tree_mirror_check` 정합(팩·조회 모듈 양 런타임 동일) 편입, §9에 codex 측 파일 해시 추가.

## SF-7 (minor) — 용량 로그의 `arm` 필드

- 발주 봉인은 「arm명·밀착도·가설 비노출」을 요구한다. 로그는 프롬프트가 아니므로 실제 노출은 없으나, `arm` 값을 프로세스에 넣으려면 환경변수가 하나 더 생긴다.
- 조치: `arm` 제거. `selector`(`plain|rulepack`)만 기록하고 arm 대응은 채점 측에서 allocation 표로 조인한다.

## SF-8 (minor) — `paths.ttl` 신설의 원장 영향 미확인

- `ontology_gate`·`ontology_structural_check`는 `wiring/*.ttl`을 **자동 glob** 하므로 신설 파일은 자동 편입된다(실측: `ontology_gate.py:145`·`ontology_structural_check.py:38`). 그러나 `LEDGER.tsv`(코퍼스 해시 대장)와 `ontology_ledger_check` 영향은 확인하지 않았다.
- 조치: 저작 직후 `make verify`로 확인하고, red면 재기준선 append(T2-3 전례).

## SF-9 (확인 — 결함 아님) — `by_checker` 키 정합

- 우려: 팩 키(검사기 파일명) ↔ 위반 레코드 `checker` 값의 형식 불일치.
- 실측: `findings.py:_default_checker()` = `Path(sys.argv[0]).name` → **bare filename**. 명시 전달 2곳(`check-error-centralization.py:4716`·`check-openapi-error-declaration.py:3434`)도 `tree_findings.checker`를 넘기는데 그 값 역시 기본값 경유의 bare filename이다. 그래프 registry는 `#c/check-domain-model.py` 꼴로 **동일**.
- 결론: 정합. **가정이 아니라 실측으로 확정**했음을 기록한다(W8은 «이름 변경 시 침묵 미스» 축이므로 별개로 유효).

## SF-10 (major·미해결) — C의 이점 가설을 **T2가 반증할 수 없다**

- W1은 「가설 미검증」을 자인하지만 처분이 없다. 실제 위험은 다르다: C가 져도 그것이 ⓐ 그래프 재료가 무용해서인지 ⓑ **checker 축의 정밀도 손실**(W3) 때문인지 ⓒ 팩 커버리지 부족(폴백)인지 **구분할 수 없다**. 세 원인이 한 처치에 묶여 있다.
- 판정 산식은 이 구분을 요구하지 않으므로 go/no-go는 나온다. 그러나 **no-go일 때 T3 결정이 근거를 잃는다**.
- 조치(제안): 용량 로그에 `norms_source:{alias,checker}`와 `fallback_n`을 이미 넣었으므로, **사후 층화 보고**를 사전 등록한다 — 「alias 정밀 조인이 걸린 회전 vs checker 축만 걸린 회전」의 위반 감소를 분리 병기(탐색적·판정 산입 금지). 표본이 극소(alias 3건)라 신호는 기대하지 않으나, **구분 불가를 구분 시도 없음으로 남기지는 않는다**.

---

**요약**: blocker 2(SF-1 팩 미도달 · SF-2 B암 byte 파손) · major 5 · minor 2 · 확인 1. SF-2는 **판단표가 자기 검증 자산(V3)에 걸리는** 종류라 구현 전에 잡힌 것이 특히 중요하다.
