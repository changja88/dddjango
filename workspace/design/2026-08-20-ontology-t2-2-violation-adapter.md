# T2-2 위반 그래프 어댑터 — 설계 노트 **v2** (2026-08-20 · 최소 경로 구현·실증 완료)

> **v2 갱신(리뷰 AL-7·AL-10 반영)**: v1 의 «변환 결과 0» 전제는 **소멸**했다 — 판단표 v2 가
> `rule#488 → R-0120` 을 확정 등재했고 `check-layer-skeleton.py` 가 `#488` 을 실발화하므로 조인이 성립한다.
> `workspace/tools/violation_adapter.py` 를 구현해 **end-to-end 실증 완료**(§4). §1 의 구조 쟁점은
> **미조인분(선행 계약·미이관 #N·센티널)에 한정**된 문제로 축소됐다.

> 대상: t2-plan v1.1 §T2-2 «위반 그래프 어댑터: findings/0 → `djr:Violation`(byChecker·targetFile·
> severity·violatesWork/violatesExpression — `expression` 실값)». 생산 측(설치본 sink·수집기)은 이미
> 착지했고(`findings.py` 디렉터리 sink·`collect_violations.py`), 남은 것은 **raw jsonl → ttl 변환**이다.

## 1. 구조 쟁점(blocker 후보) — `ViolationShape` 필수 프로퍼티 vs D12·커버리지 격차

`ontology/shapes/djr-shapes.ttl:251–260` 실측:

```
djr:ViolationShape-violatesWork       sh:class djr:Work ;       sh:minCount 1 ; sh:maxCount 1 ; sh:nodeKind sh:IRI
djr:ViolationShape-violatesExpression sh:class djr:Expression ; sh:minCount 1 ; sh:maxCount 1 ; sh:nodeKind sh:IRI
```

→ **Work 조인이 없는 발견은 `djr:Violation` 노드로 저작할 수 없다**(SHACL red). 그런데 실물은:

- **선행 계약 발견**(rule=null + contract_ref — 계약 레인 7종·T2-1 확정): 애초에 Work 가 없다.
  t2-plan §T2-2 는 «선행 계약 발견은 Work 조인 없이 `contract_ref` 적재(D12)»라고 **명시**한다 —
  현행 셰이프와 정면 충돌.
- **미이관 `#N` 보유 발견**: alias 대장 커버리지가 파일럿 한정이라 대다수 `#N` 은 Work 가 없다
  (판단표 v2 §5 — 확정 조인률 3/446). **단 조인분은 실재**한다(`#488`→R-0120 — §4 실증).
- **가드 센티널 발견**(sentinel «대상0»·«합성»·«바인딩»): rule 도 contract_ref 도 없다.

즉 현행 셰이프대로면 **조인분은 정상 적재되고 미조인 3군만 적재 불가**다(v1 의 «적재 가능 0» 판단은
`#488` 조인 누락에서 온 오판이었다 — 리뷰 AL-7). 어댑터는 미조인분을 **계수로만 보고**한다(침묵 탈락 금지).

### 처분 후보 3안 (택일 — 리뷰 상정)

| 안 | 내용 | 비용 | 위험 |
|---|---|---|---|
| **A. 셰이프 개정** | `violatesWork`/`violatesExpression` 을 `minCount 0` 으로 낮추고, «Work 조인 ∨ contract_ref» 택일을 `sh:or` 로 강제 | 어휘 v1 봉인 밖 **셰이프 개정** — authoring §7 절차(리네임 맵 불요·추가만)·골든 재작성·계수 기대표 갱신 | 동결 문면(§8) 대비 **문면 정합형 개정**(D12 가 이미 승인 문면) — R2 절차 대상 |
| **B. 미조인 전용 클래스** | `djr:Violation` 은 조인분 전용으로 두고, 미조인분은 신설 클래스(예 `djr:UnjoinedFinding`)로 적재 | **어휘 신설** — v1 봉인 개정(§7)·셰이프 신설·구조 검사 확장 | 클래스 이원화로 질의가 둘로 갈림(C암 규칙 팩이 양쪽을 봐야) |
| **C. 적재 유예** | T2 에서는 raw jsonl 수집까지만 하고 ttl 변환은 T3(대량 이관으로 조인 성립) 이후 | 0 — 도구 미작성 | §8 T2 완료 기준의 «위반 그래프» 항목 미달 — 마일스톤 보고에 미달성 명시 필요 |

**저자 권고 = A**. 근거: ⓐ D12 는 이미 승인된 t2-plan v1.1 문면이고 «contract_ref 적재»를 명령한다 —
셰이프가 그 명령을 불가능하게 만드는 것은 **문면 간 모순**이지 설계 의도가 아니다(개정 2 이월 명시가
그 증거). ⓑ B 는 어휘 봉인을 더 크게 깨고 질의를 이원화한다. ⓒ C 는 «관측 부산물»을 T3 까지 그래프
밖에 두어 A/B 의 C암 재료를 비운다. **단 A 도 셰이프 개정이므로 R2(문면 정합형) 절차 — codex 반증
통과 시 잠정 발효·마일스톤 추인 목록 등재**로 처리한다.

## 2. 변환 사양 (조인분 = 구현 완료 · 미조인분 = 처분 대기)

- 입력: 수집기 산출 raw jsonl(또는 설치본 sink 디렉터리 직접) · 출력: ttl(`--out`)
- 노드 IRI: **`djr:v-<sha16>`** — sha16 = `(Work × targetFile × symbol)` 해시라 **같은 사건 = 같은 노드**
  (재실행 결정성). 재발 구분은 `runId` 가 진다(구안 `v/<run_id>-<서수>`는 매 실행 새 IRI 를 만들어 폐기)
- 필드 대응:
  | findings/0 | 그래프 | 비고 |
  |---|---|---|
  | `checker` | `djr:byChecker` → `djr:c/<파일명>` | registry.ttl 선언 27종과 대조(미등재면 재료 결손) |
  | `file` | `djr:targetFile` (xsd:string) | `<rel>:<lineno>` 원문 보존 |
  | `symbol` | `djr:targetSymbol` | null 이면 생략(shape 는 minCount 0) |
  | `severity` | `djr:severity` → `sh:Violation`/`sh:Warning`/`sh:Info` | `sh:in` 3값 |
  | `ts` | `djr:detectedAt` (xsd:dateTime) | UTC |
  | `run_id` | `djr:runId` | |
  | `message` | `djr:evidence` | |
  | `rule` | **alias 대장 조인** → `djr:violatesWork` + Work 의 `currentExpression` → `djr:violatesExpression` | 미해소면 조인 생략(처분 A) |
  | `contract_ref` | `djr:contractRef`(신설 필요 — 어휘 부재 실측) | **미구현** — 처분 A 확정 후 |
  | `sentinel` | 조인·contract_ref 둘 다 없음 → **미적재**(계수 보고) | 관측 부산물 |
- **violation_id = (Work × 대상 파일 × 심볼)**, 심볼 부재 시 (Work × 파일)로 강등 명시(L-M #12) — 동일
  violation_id 의 재발은 노드 재사용이 아니라 `runId` 로 구분되는 별개 인스턴스다(계수 규약 정합).

## 3. 후속

- 구조 검사 ⑦ 후보: 적재된 Violation 의 `violatesWork`→`currentExpression`↔`violatesExpression` 왕복
  (현행 ⑤ 의 `qv` 질의가 골든에서 이미 성립을 재고 있으므로 실물 적재분으로 확장).

## 4. end-to-end 실증 (AL-10 완료 기준 이행 · 2026-08-20)

검사기 발화 → 설치본 sink → 수집 → 그래프 적재 → 셰이프 통과의 전 사슬을 실물로 통과시켰다:

1. `check-layer-skeleton.py` 를 설치 표식(`.dddjango/`)이 있는 임시 프로젝트에 실행 → exit 2 ·
   레코드 10건 게시(그중 `#488` **7건**).
2. `violation_adapter.py --records <sink> --strip <root>` → **적재 7 · 미조인 #N 3**(계수 보고 —
   침묵 탈락 없음).
3. 산출 ttl 의 각 노드가 `djr:violatesWork <djr#R-0120>` · `djr:violatesExpression <djr#R-0120@2026-08-19>`
   **실값**을 갖는다(대장 조인 + `currentExpression` 경유).
4. **pySHACL 검증 `conforms: True`**(정본 rules+wiring+vocab 병합 + 전 셰이프) — `ViolationShape` 의
   필수 프로퍼티를 만족하는 실물 Violation 이 그래프에 존재한다.
5. `--self-test`: 정본 대장으로 «조인 1 · 미조인 1» 합성 대조(대장 3종 조인 가능 확인).

**violation_id 결정성**: 노드 IRI = `(Work × 파일 × 심볼)` sha16 이라 같은 사건은 재실행에도 같은 노드다
(심볼 부재 시 (Work × 파일)로 강등 — L-M #12). 재발 구분은 `runId` 가 진다.

## 5. 자인 약점

0. **미조인분 처분은 여전히 미결**(§1 3안) — 실증은 조인분만 닫았다.
1. 처분 A 는 셰이프를 **느슨하게** 만든다 — «Work 도 contract_ref 도 없는 쓰레기 노드»를 `sh:or` 로
   막는다고 했으나 그 조합 폭발(가드 센티널·미조인 #N)을 전수 열거하지 못했다.
2. `djr:contractRef` 프로퍼티가 어휘에 없다 — 처분 A 는 **어휘 추가**도 동반한다(봉인 개정 폭이 커짐).
3. `targetFile` 정규화가 `--strip` 수동 인자다 — 검사기별로 절대/상대 경로가 섞이는 기존 불일치
   (layer-skeleton 은 절대·다수는 상대)를 어댑터가 떠안았다. 근본 처분은 검사기 층의 locator 통일이며
   T2-3 이후 백로그.
4. A/B 계수 산식(동결 §6 «Work×파일×심볼»)과 노드 동일성의 정합은 sha16 키로 맞췄으나, **재발 계수를
   조회로 집계하는 질의**는 아직 없다(규칙 팩 T2-4 소유).
