# OHS 계약 보조 타입 허용 — 검사기 정합화 계획 v2 (적대 리뷰 반영 확정본)

- 상태: **v2 구현 완료** (2026-08-24. v1 → 3인 반증 패널 25건 → 처분 반영 → §3 사슬 전체 집행. 검증: 합성 9/9 · checker_lint 0 · findings 매트릭스 서명 불변(해시 갱신) · construct byte 골든 재발행(--emit-expected) · R-1699 리비전 2 사슬 green(게이트 90/90·render_sync red 0) · `make verify` green)
- 발단: kkebi billing 런 — `VerifyPaymentOwnershipEvidenceResponse`의 `tuple[OwnerMergeEvidence, ...]` 필드. 보조 공개 dataclass의 합법적 자리가 0(현재 private+alias 우회 — 명목 타입 private라 런 스스로 부적격 분류).

## 1. 확정 사실 (v1 + 패널 교정 2)

- 검사기 문면: #160(:451-453 공개 ClassDef ≥2)·#484(:454-456 접미 강제)·#162(:464-467 domain import) — v1 그대로. **교정 ①(R3-8)**: #483(:444-447)은 stem이 `_response`로 끝날 때만 발화 — 별도 파일 `owner_merge_evidence.py`는 #483 통과·**#484 하나로만** 차단된다(§1 «네 갈래 합쳐 자리 0» 기술 정정 — 결론 불변: 자리 0은 참).
- **교정 ②(R1-3) — #160은 순수 유령이 아니다**: 성문 산문·rulepack 채번은 부재(v1 실측 유지)지만, T3 이관 판단 기록(`workspace/eval/t3/worksheets/agent-design-architect.md:174`)이 실재 규범 **R-1698**(«OHS 내부 구조는 명세 1급 결정 — 명세에 안 박으면 coder가 즉흥 산출») join 근거에 «#156/#157/#159/#160 계약 1타입=1파일»을 명시 — #160 갈래는 R-1698의 기계 백스톱 표면이다. → 이 개정은 R-1698과 **정합 방향**(명세가 결정한 보조 타입에 자리를 주는 것)이나, architect 문면에 «보조 계약 타입» 결정 항목이 없어 그대로면 미성문 규범이 된다(§3-G).
- 배선 규범 76건 전수 대조(R1): 충돌 후보는 **R-0531**(«…Request/…Response는 OHS contract 전용 — 어휘 혼용 금지») 1건 — §2 ⓑ로 해소. R-0490 published language는 수용 방향·frozen 강제 산문 부재·타 검사기 신규 발화 없음(#169 exception 한정·#451 service 한정·#472 stdlib 무충돌).

## 2. 확정 설계 (v2)

**갈래 중립**(R2-2 — request/response 동형: 같은 함수가 suffix 매개변수로 처리하고 #633이 단일 Request 객체를 강제해 보조 타입 수요가 구조적으로 동일. response 한정은 인공 게이트 «추가»라 오히려 비용):

- **면제 수집**: 주 계약(접미 일치 공개 클래스)의 필드 어노테이션에서 기존 **`_ann_idents`(:115-126) 재사용**(R3-2 — `ast.Constant` 문자열 forward-ref까지 처리·`X | None`·Subscript 자동 포섭) → **seen-집합 고정점**으로 전이 폐포(R3-7 — 자기·상호 참조 순환 안전). Attribute `attr` 과수집은 면제 미세 확대 방향의 희귀 트레이드오프로 문서화 수용(R3-10).
- **면제 자격 3조건**: ⓐ 주 계약에서 직·간접 참조(파일-국소) ⓑ 이름이 **`Response`/`Request`/`Result`/`Command`/`Query`로 끝나지 않음**(R1-1·R3-5 — R-0531 어휘 혼용 금지·#484 자신의 «Result 금지» 문면 보존) ⓒ **import 바인딩 검증된 `@dataclass`**(R3-3 — 이름 매칭이 아니라 `from dataclasses import dataclass`[asname 인지]·`dataclasses.dataclass` receiver 실검증, `_enum_local_names`(:698) 판례) — enum·일반 클래스·미참조 공개 타입은 계속 금지.
- **#160/#157 재정식화 — 강화 밀수 금지**(R3-1·R2-3·R1-5): 발화 = `len(pubs) >= 2` **그리고** (주 계약 ≥2 **또는** 면제 미달 비주계약 존재). 공개 0·1개 파일은 현행 그대로 무발화(0-주계약 파일 신규 red 없음·접미 틀린 1개는 #484 단독 — 이중 발화 금지 결정(:829) 정합).
- **#455는 주 계약 한정으로 좁힘**(R3-4·R1-7): `suffix=="Response" and cls.name.endswith(suffix)` — 면제 보조 타입의 `reason` 류 필드에 «사유는 코드로»가 오적용되지 않게(에스컬레이션 번호 갈아타기 재발 방지). 현행 픽스처 발화(주 계약 소산)는 불변.
- **공유 보조 타입의 정합 경로 성문화**(R2-1·R1-6): 보조 타입은 **그것을 반환하는 연산 중 하나의 계약 파일에 정의**하고, 다른 연산의 계약은 **같은 BC 계약 간 import**(#472가 이미 허용 — :219-221)로 참조한다. 정의 파일의 주 계약이 참조를 끊으면 red — 참조하는 파일로 **이동**이 규범(죽은 공개 타입 금지 불변식 유지). 파일별 중복 정의는 같은 BC 안 «같은 지식 한 출처» 위반이라 비규범.
- **#484 메시지 문면 동기**(R1-9): «이 창구가 돌려주는(받는) 타입**과 그 구성 dataclass**만 온다» + 검사기 헤더(:17-18) 열거 동기.

**기각 기록**(재심의 방지 — R2-6): `<Operation>ResponseItem` 접미 확장(덜 좁고 죽은 타입 방치·의미 오류) · `contract/shared/` 칸 신설(graph-owned 트리 140행+standard_tree 개정 요구 — **공유 수요 실증 시 승격 별건**) · 중첩 클래스 공식화(소비 인체공학·#162/#455 중첩 순회 비용) · frozen 강제(주 계약에도 없음 — 비대칭 과잉·가변 위험은 기존과 동일) · 폐포 수치 상한(«계약은 얇게» 성문 부재 — 상한이야말로 유령 규범).

**잔여 위험(리뷰어 소관 명시 — R3-9)**: 더미 필드로 참조 조건 충족·메서드 잔뜩 dataclass — 의미 판단이라 결정적 검사 부적합(#462·모션 축 판례). #472 stdlib 감금이 서비스화 실익을 구조적으로 깎는 해자. discipline-reviewer 감사 단서로 남긴다.

## 3. 실행 사슬

A. 검사기 `_check_contract_kind` 개정(위 설계 — 최소 diff: 모듈 수준 면제 헬퍼 1개 + 루프 내 3분할, R3 축5 판형) → B. codex byte 미러 → C. checker_lint → D. `findings_count_matrix.py` — 현행 행 :117은 서명 불변 예상(R3-6: #484×1은 request 소산·#483 stem 불변·#455 주계약 소산), 단 #484 메시지 개정으로 **stdout 해시만 갱신** → E. 합성 검증 8방향: billing 판형 green(**인용 forward-ref + `status: str`** — R1-8: 실물이 enum이면 ⓒ로 여전히 red임을 회신에 명기) / 미참조 aux red / Result·Command 접미 참조 red / 비-dataclass(Enum) 참조 red / Response×2 red / 공개 0개 alias 파일 green 불변 / request 갈래 aux green / aux+freeform 필드 #455 무발화 → F. **성문 1줄**(R1-4·#72): architect 문면 «명세가 결정하는 것»에 보조 계약 타입 항목 — 해당 절의 소유(graph-owned/산문)를 확인해 graph-owned면 R-1698 리비전(판례 1호 사슬), 산문이면 직접 편집+LEDGER 재기준선 → G. 봉인 재발행(해당 시) → H. `make verify` → 조감도·메모리·커밋.

## 4. 비변경

#483·#162·#472 불변 · request 갈래 «완화 없는 부분»(#633 단일 객체 등) 불변 · 트리 140행 무수정 · w2 세션 파일 무접촉 · #160 류 성문 채번은 별건(유령 대사 합류 — 단 R-1698 백스톱 관계는 T3 판단표가 이미 기록).

## 5. 처분 대장 (25건 → 채택 20 · 기각 2 · 반증 실패 확인 3군)

- 채택: 강화 밀수 차단(R3-1·R2-3·R1-5) · `_ann_idents`+고정점(R3-2·7, R2-4) · 접미 제외 5종(R3-5·R1-1) · import 바인딩 dataclass 판정(R3-3) · #455 주계약 한정(R3-4·R1-7) · 공유 경로 성문화(R2-1·R1-6) · 갈래 중립(R2-2) · R-1698 관계 명기+성문 1줄(R1-3·4) · #484 메시지·헤더 동기(R1-9) · #483 사실 교정(R3-8) · 픽스처 계획 교정(R3-6) · billing status 타입 고정(R1-8) · §4 R-번호 목록 교정(R1-2) · 잔여 위험 명시(R3-9) · 기각 기록 5종(R2-6) · frozen 현상 유지+ⓒ 근거 인용(R2-5).
- 기각: 면제 스코프 디렉터리 확장(R2-1 대안 — 교차 파일 분석 복잡도 대비 import 경로가 결정적·단순) · Attribute 수집 제외(R3-10 — `_ann_idents` 재사용 이득이 큼·문서화 수용).
- 반증 실패 확인: future-import·`X | None` AST(R3) · 폐포 상한·중첩 공식화(R2) · 배선 76건 중 R-0531 외 무충돌·산문 부재 재확인·타 검사기 무발화(R1).
