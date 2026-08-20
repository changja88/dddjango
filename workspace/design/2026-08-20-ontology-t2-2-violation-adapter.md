# T2-2 위반 그래프 어댑터 — 설계 노트 v1 (2026-08-20 · 구조 쟁점 1건 상정)

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
- **`#N` 보유 발견**: alias 대장 커버리지가 파일럿 한정이라 T2-1 귀속 #N 36 원자 술어와 교집합 0
  (`2026-08-20-ontology-t2-2-alias-ledger.md` §5) — 사실상 전건 미조인.
- **가드 센티널 발견**(sentinel «대상0»·«합성»·«바인딩»): rule 도 contract_ref 도 없다.

즉 **현행 셰이프대로면 T2 범위에서 적재 가능한 Violation 은 0건**이고, 어댑터는 «변환 결과 0» 도구가 된다.

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

## 2. 변환 사양 (처분 A 전제 — 확정 시 구현)

- 입력: `workspace/eval/violations/raw/<원천>/<파일>.jsonl`(수집기 산출) · 출력: `workspace/eval/violations/<원천>.ttl`
- 노드 IRI: `djr:v/<run_id 8자>-<record 서수>` (PN_LOCAL 안전 — 재실행 결정성 유지)
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
  | `contract_ref` | `djr:contractRef`(신설 필요 — 어휘 부재 실측) | D12 이월분 |
  | `sentinel` | 조인·contract_ref 둘 다 없음 → **미적재**(대장에 계수만 기록) | 관측 부산물 |
- **violation_id = (Work × 대상 파일 × 심볼)**, 심볼 부재 시 (Work × 파일)로 강등 명시(L-M #12) — 동일
  violation_id 의 재발은 노드 재사용이 아니라 `runId` 로 구분되는 별개 인스턴스다(계수 규약 정합).
- 구조 검사 ⑦ 후보: 적재된 Violation 의 `violatesWork`→`currentExpression`↔`violatesExpression` 왕복
  (현행 ⑤ 의 `qv` 질의가 골든에서 이미 성립을 재고 있으므로 실물 적재분으로 확장).

## 3. 자인 약점

1. 처분 A 는 셰이프를 **느슨하게** 만든다 — «Work 도 contract_ref 도 없는 쓰레기 노드»를 `sh:or` 로
   막는다고 했으나 그 조합 폭발(가드 센티널·미조인 #N)을 전수 열거하지 못했다.
2. `djr:contractRef` 프로퍼티가 어휘에 없다 — 처분 A 는 **어휘 추가**도 동반한다(봉인 개정 폭이 커짐).
3. 노드 IRI 결정성: `run_id` 는 pid·시각 포함이라 같은 위반이 매 실행 새 IRI 를 얻는다. 계수 규약의
   «동일 violation_id»는 노드 동일성이 아니라 조회 시 집계로 실현되는데, 이 설계가 A/B 계수 산식과
   정말 정합인지 실측 대조를 못 했다.
