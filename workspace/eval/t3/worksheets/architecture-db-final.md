# T3 저작 검수표 — architecture-db-final

- 원문: `dddjango/skills/architecture-db/references/final.md` (736행 · 센서스와 일치 — 드리프트 경고 없음)
- spec: `workspace/eval/t3/specs/architecture-db-final.spec.json` (REF 28절 · 블록 179 · Work 104)
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/architecture-db-final.spec.json` → **exit 0**(적대 리뷰 수리 후 재실행 포함 · `--write` 미사용). 28절 전량이 센서스 좌표·절 스팬 sha256·블록 연속/무손실·헤딩+블록 byte 등가 단언을 통과.
- 적대 리뷰 수리(2026-08-22): `workspace/eval/t3/reviews/architecture-db-final-findings.md` 지적 20건 처분 완료 — 그 «처분» 절이 건별 판정의 정본이다. 수리로 Work 105 → 104(§8.4 3항 재진술 강등)이고 배선 표의 # 는 재부여됐다(리뷰의 #32 이후 번호는 −1 이동).
- 필독 이행: 발주서 · authoring §13~§16 · migrate docstring · 파일럿 spec 2건(ddd s051-8·s017-3.2 / ninja s022-6.1) · **`dddjango/scripts/check-*.py` 27종 docstring 선두 전수 실독**(§16 L-F 교훈) · `workspace/plan/2026-08-11-rule-owner-map.md`(④ registry #N 대조).

## 1. census 대사

| section_key | 발주서 규범 수 | spec 규범 수 | 블록 수 | 대사 |
|---|---|---|---|---|
| s005-1.2 | 1 | 1 | 4 | 일치 |
| s008-2.2 | 2 | 2 | 2 | 일치 |
| s009-2.3 | 1 | 1 | 7 | 일치 |
| s016-3.4 | 1 | 0 | 3 | **불일치(−1)** — 발주서 «과대 산정»이 옳다: 이 절의 유일 규범 문장은 §4.2 정본의 사본이라 §15 재진술 규약대로 Work 미승격 + `restates`→`s019-4.2/b1`. 규범 자체는 그래프에 1개로 존재 |
| s019-4.2 | 2 | 2 | 1 | 일치 |
| s021-5 | 2 | 2 | 5 | 일치 |
| s028-7.1 | 2 | 2 | 4 | 일치 |
| s031-7.4 | 4 | 4 | 8 | 일치 |
| s032-8 | 1 | 1 | 1 | 일치 |
| s033-8.1 | 5 | 5 | 7 | 일치 |
| s034-8.2 | 3 | 3 | 8 | 일치 |
| s035-8.3 | 5 | 5 | 9 | 일치 |
| s036-8.4 | 5 | 4 | 6 | **불일치(−1)** — 발주서 «과대 산정»이 옳다: 3항(329행 «신·구 코드 동시 동작 compatibility window 를 고려한다»)은 §11.1 서두(514행 «운영 DB 변경은 기존 코드와 새 코드가 동시에 동작하는 시간을 고려한다»)와 술어·목적어가 같은 준-축자 사본이라 §15대로 Work 미승격 + `restates`→`s052-11.1/b1`. 정본을 §11.1 로 둔 이유는 §11 이 «운영 rollout» 관할을 스스로 선언하고 §8.4 쪽이 그 일반 원칙을 제약조건 rollout 절차 안에서 되풀이한 형태이기 때문(s016-3.4→s019-4.2 와 동형) |
| s041-9.4 | 1 | 1 | 6 | 일치 |
| s042-9.5 | 18 | 18 | 12 | 일치 |
| s043-9.6 | 12 | 12 | 15 | 일치 |
| s044-9.7 | 12 | 12 | 12 | 일치 |
| s046-10.1 | 1 | 1 | 8 | 일치 |
| s050-10.5 | 3 | 3 | 8 | 일치 |
| s051-11 | 2 | 2 | 1 | 일치 |
| s052-11.1 | 2 | 2 | 7 | 일치 |
| s053-11.2 | 5 | 5 | 6 | 일치 |
| s054-11.3 | 5 | 5 | 8 | 일치 |
| s055-11.4 | 1 | 1 | 8 | 일치 |
| s056-11.5 | 1 | 1 | 4 | 일치 |
| s061-12.4 | 4 | 4 | 8 | 일치 |
| s066-13.4 | 1 | 1 | 3 | 일치 |
| s067-13.5 | 4 | 4 | 8 | 일치 |
| **합계** | **106** | **104** | **179** | 차 −2(위 2건) |

**판정 요지**: 28절 중 26절이 발주서 계수와 정확히 일치한다. 차 2건은 둘 다 §15 재진술 규약 적용분이고 규범 자체는 정본 쪽 Work 로 그래프에 남는다(소실 0). ① s036-8.4 — 적대 리뷰 M-4 지적을 대조 후 수용: 329행 ↔ 514행이 같은 규범의 준-축자 쌍이고 발주서 재진술 열이 «N»인 것은 P0 계수 승계일 뿐 판정이 아니다. §15 는 발주서 계수보다 상위 규약이라 «발주서 계수 승계»는 면책이 되지 않는다(s016-3.4 에서 이미 같은 판단을 했다). ② s016-3.4 — 발주서(P0 승계)가 §3.4 말미의 «정규화 먼저 · 필요한 경우에만 역정규화» 절편을 독립 규범으로 계수했으나, 같은 발주서의 restate 열이 이미 `Y:architecture-db-final/s019-4.2`로 사본임을 지정하고 s019-4.2 비고가 «정본으로 지정»이라 적시한다. §15 «정본 1곳만 Work 승격 + 사본 블록에 djr:restates»가 정면으로 적용되는 케이스라 **발주서 쪽 과대 산정**으로 판정하고 Work를 승격하지 않았다(파일럿 ddd s017-3.2/b1 blockquote 사본과 동형 처리). 규범 자체는 s019-4.2/b1의 Work로 그래프에 남고, s016-3.4/b1은 그 블록을 `restates`로 가리킨다.

## 2. 배선 근거 표 (전 규범 104)

| # | 절 | 블록 | Work label | enforcedBy | delegatedTo | 4원 근거 |
|---|---|---|---|---|---|---|
| 1 | s005-1.2 | b1 | 말을 믿지 말고 UI 합의안으로 업무를 확정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) · 청유형(«갖자») 규범을 보수적으로 계수(P0 승계) |
| 2 | s008-2.2 | b1 | 연관 정보 덩어리 식별 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 3 | s008-2.2 | b2 | 조회·조인에 유리하도록 엔티티 적절 분리 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 4 | s009-2.3 | b7 | 자연 기본키 부재 시 인조키(Surrogate Key) 사용 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 5 | s019-4.2 | b1 | 정규화 먼저 · 필요한 경우에만 역정규화 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 6 | s019-4.2 | b1 | 읽기가 많다는 이유의 즉시 역정규화 금지 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 7 | s021-5 | b1 | 성능 최적화는 슬로우 쿼리→인덱스→캐시→역정규화 순서 준수 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 8 | s021-5 | b3 | 슬로우 쿼리 탐색·최적화부터 착수 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 9 | s028-7.1 | b3 | 복합 인덱스 컬럼 순서는 가장 많은 쿼리를 서비스하도록 결정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 10 | s028-7.1 | b3 | 등호(=) 조건 컬럼을 범위 조건 컬럼보다 앞에 배치 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 11 | s031-7.4 | b3 | 높은 카디널리티 컬럼 우선 인덱싱 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 12 | s031-7.4 | b4 | 읽기/쓰기 비율에 따른 인덱스 증감 결정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 13 | s031-7.4 | b5 | 미사용 인덱스 정기 감사 후 삭제 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 14 | s031-7.4 | b6 | 복합 인덱스 도입 전 단일 인덱스 조합 벤치마크 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 15 | s032-8 | b1 | DB가 강제할 수 있는 불변식은 제약조건으로 보호(애플리케이션 validation 단독 금지) | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 16 | s033-8.1 | b3 | 자연키가 불안정하면 surrogate key 사용 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 17 | s033-8.1 | b4 | FK는 삭제 정책과 함께 결정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 18 | s033-8.1 | b5 | Unique는 NULL 처리·partial unique 여부 확인 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 19 | s033-8.1 | b6 | Check는 다른 행·외부 상태가 필요한 규칙에 사용 금지 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 20 | s033-8.1 | b7 | Not Null은 기존 데이터 backfill 후 적용 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 21 | s034-8.2 | b7 | 이력 보존이 중요한 데이터에 무심코 cascade 사용 금지 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 22 | s034-8.2 | b8 | FK는 같은 바운디드 컨텍스트 안에서만 — 타 BC 모델의 ForeignKey 참조 금지 | check-db-table.py | agent-design-review-db | ②check-db-table docstring «#631 타 BC 모델을 FK·O2O·M2M 으로 참조 금지(문자열 참조 포함)» 축자 대응 · ④rule-owner-map #631 = ast → check-db-table.py(ⓒ 단독) · ①문면 «BC 경계 FK 금지» |
| 23 | s034-8.2 | b8 | 타 BC는 ID 값 참조 + 앱 레벨/ACL 무결성으로 대체 | check-context-isolation.py | agent-design-review-db·agent-design-review-ddd | ②check-context-isolation docstring «#12 부를 수 있는 것은 OHS·published_event 둘 · #13 OHS 소비는 ACL 뿐» — ACL 경유 축만 기계 커버(ID 값 참조 채택 판정은 설계 몫이라 db 리뷰 병기) · ①문면이 architecture-ddd §3.3 규칙3(«다른 애그리거트는 ID로만 참조하라» — 설계 시점 규범) 영속성 확장을 직접 지목 → §16 기본값 표(architecture-ddd 설계 시점 → design-review-ddd) 병기 · check-domain-model #548(«다른 애그리거트는 식별자 값 객체로만») 대조 후 기각 — #548 은 같은 BC 도메인 안 애그리거트 간 타입 힌트 축이라 BC 경계 참조 축과 상이 |
| 24 | s035-8.3 | b4 | 자연 유일성은 unique constraint 또는 partial unique index | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 25 | s035-8.3 | b5 | soft-delete 후 활성 행 유일성은 partial unique index | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 26 | s035-8.3 | b6 | 동일 요청 retry 재생은 idempotency key table + unique constraint | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 27 | s035-8.3 | b7 | 같은 key 다른 본문은 key scope + request fingerprint/hash 저장으로 충돌 판정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 28 | s035-8.3 | b8 | 멱등성 저장소는 최소 6항(scope·owner·unique·fingerprint·result·retention)을 결정 | — | agent-design-review-db | ②check-idempotency-scope-creep 의 docstring § 지목은 «architecture-db §9.6 Idempotency storage» 한정이고 그 소유도 «미요청 멱등성 확장 차단»뿐 — §8.3 은 비지목이라 기본값 유지(기본값 «도피»가 아니라 커버 부재) |
| 29 | s036-8.4 | b1 | 제약조건 추가 전 데이터 정리와 rollout 순서 선설계 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 30 | s036-8.4 | b2 | 현재 데이터의 제약조건 만족 여부 점검 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 31 | s036-8.4 | b3 | 필요 시 batch backfill·cleanup 선행 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 32 | s036-8.4 | b5 | NOT NULL·unique·check 는 검증 실패와 rollback/forward-fix 방법을 정한 뒤 적용 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 33 | s041-9.4 | b6 | 필요 이상으로 높은 격리 수준 채택 금지 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 34 | s042-9.5 | b1 | 격리 수준으로 불변식이 안 지켜지면 제약조건·명시적 락을 함께 설계 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 35 | s042-9.5 | b4 | unique 방어는 충돌 시 예외/재시도/기존 결과 조회 정책을 함께 결정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 36 | s042-9.5 | b5 | 낙관적 락은 version 컬럼 또는 CAS 조건 필수 | check-transaction-boundary.py | agent-design-review-db | ②check-transaction-boundary docstring «#599 ㉡맨 bulk_update(경합 가드 없음)면 위반» — 경합 가드(version/CAS) 부재를 쓰기 지점에서 기계 차단 · ④rule-owner-map #599 = ast → check-transaction-boundary.py |
| 37 | s042-9.5 | b6 | 행 잠금 미지원(SQLite)·저경합은 낙관적 락 우선 — lock 순서·timeout·deadlock 대응 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 38 | s042-9.5 | b7 | advisory lock 은 lock key 설계와 해제 실패 대응을 함께 결정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 39 | s042-9.5 | b8 | Serializable 채택 시 serialization failure retry 필수 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 40 | s042-9.5 | b9 | 락 범위 최소 유지 — 트랜잭션 안 사용자 입력 대기·외부 API 호출·긴 배치 금지 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 41 | s042-9.5 | b10 | 개발과 운영 DB가 다르면 명세에서 분기 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 42 | s042-9.5 | b10 | 환경 무관 방어선은 불변식 CHECK 백스톱 + 낙관적 version/CAS 조건부 원자 UPDATE(WHERE엔 경합 가드만) | check-transaction-boundary.py | agent-design-review-db·agent-discipline-reviewer | ②check-transaction-boundary docstring «#599 ㉡맨 bulk_update(경합 가드 없음)면 위반» — 경합 가드(version/CAS) 부재를 쓰기 지점에서 기계 차단 · ④rule-owner-map #599 = ast → check-transaction-boundary.py · ①문면이 architecture-ddd §3.2 를 지목 |
| 43 | s042-9.5 | b10 | SQLite 직렬화가 필요하면 begin 모드·busy_timeout 등 연결 설정을 명세가 명시 | — | agent-design-review-db | ②check-mechanism-ownership ⑴ 은 OPTIONS 를 아예 관측하지 않는다(ENGINE_RE 로 DATABASES ENGINE 만 읽고 비스톡 점경로 + 레포-로컬 DatabaseWrapper 만 문다) — 이 «명세가 명시한다» 의무의 기계 커버는 0이라 enforcedBy 미배선(#49 PRAGMA 건과 같은 «docstring 부재 → 커버 부재» 논리 · 도피 아님). 기계가 무는 것은 이 의무의 우회형(엔진 교체)이고 그 축은 b11 #46·#47·#48 이 이미 진다 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 44 | s042-9.5 | b10 | Risky Write 의 락·동시성은 대상 엔진별 동작 차이까지 설계에서 확정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 45 | s042-9.5 | b11 | '연결 설정 명시'는 Django stock OPTIONS·안전 PRAGMA 화이트리스트 한정 | check-mechanism-ownership.py | agent-design-review-db | ②check-mechanism-ownership docstring ⑴ «프로덕션 DB 엔진의 트랜잭션·락·격리 메커니즘을 명세 승인 없이 커스텀 백엔드로 교체한 정확한 형태만 차단 — stock ENGINE 여부·DatabaseWrapper 서브클래스» · ①문면 «stock OPTIONS만, 엔진 교체는 아니다» — 한계: 경계의 ENGINE 쪽 절반만 기계 커버(그마저 금지 축은 #47·#48 이 진다)이고 label 후반의 «안전 PRAGMA 화이트리스트» 축은 #49 판정대로 비커버(검사기가 OPTIONS·PRAGMA 를 관측하지 않음) |
| 46 | s042-9.5 | b11 | 프로덕션 ENGINE 교체·커스텀 DB 백엔드는 설계가 명시 승인할 때만 허용 | check-mechanism-ownership.py | agent-design-review-db | ②check-mechanism-ownership docstring ⑴ «프로덕션 DB 엔진의 트랜잭션·락·격리 메커니즘을 명세 승인 없이 커스텀 백엔드로 교체한 정확한 형태만 차단 — stock ENGINE 여부·DatabaseWrapper 서브클래스» · ①문면 «stock OPTIONS만, 엔진 교체는 아니다» |
| 47 | s042-9.5 | b11 | 구현이 환경 한계를 이유로 커스텀 백엔드를 자기 판단으로 생성 금지(출처 불문) | check-mechanism-ownership.py | agent-discipline-reviewer | ②check-mechanism-ownership docstring ⑴ «프로덕션 DB 엔진의 트랜잭션·락·격리 메커니즘을 명세 승인 없이 커스텀 백엔드로 교체한 정확한 형태만 차단 — stock ENGINE 여부·DatabaseWrapper 서브클래스» · ①문면 «stock OPTIONS만, 엔진 교체는 아니다» · ①문면이 implementation-django §16.4 를 지목 → §16 기본값 표(implementation-* → discipline-reviewer) 병기 |
| 48 | s042-9.5 | b11 | 격리·락·동시성 의미를 바꾸는 PRAGMA도 같은 설계 승인 대상 | — | agent-design-review-db | ②mechanism-ownership 의 AND 게이트는 ENGINE 점경로·DatabaseWrapper 축만 본다 — PRAGMA 축은 docstring 부재라 기본값 유지(커버 부재) |
| 49 | s042-9.5 | b12 | 판정·불변식은 도메인 소유 — 비즈니스 판정의 SQL WHERE·ORM 이동 금지, 리포지토리는 결과만 저장하고 인프라엔 경합 가드만 | check-domain-model.py·check-transaction-boundary.py | agent-discipline-reviewer·agent-design-review-db | ②check-domain-model «#257 상태 변경은 루트를 지난다»·check-transaction-boundary «#195 애그리거트를 건너뛰지 않는다 / #287 쓰기 인자는 애그리거트» · ④rule-owner-map #257·#195·#287 · ①문면이 architecture-ddd §3.2 빈혈 차단을 지목 → §16 기본값 표의 «architecture-ddd 구현 시점 규범(§3.2 등) → discipline-reviewer» 를 문면 근거로 병기 |
| 50 | s042-9.5 | b12 | QuerySet.update() 0행이면 경합 — 재조회 후 도메인 메서드부터 재실행 | check-transaction-boundary.py | agent-design-review-db | ②check-transaction-boundary docstring «#599 ㉡맨 bulk_update(경합 가드 없음)면 위반» — 경합 가드(version/CAS) 부재를 쓰기 지점에서 기계 차단 · ④rule-owner-map #599 = ast → check-transaction-boundary.py · ②#195 «루트 메서드 호출을 받은 객체만 save 인자» · ⓓ 위임은 기본값 유지: #599·#195 는 registry 상 ast(ⓒ 단독 — ⓓ 없음)이고 이 문장(391행)의 참조는 §9.6·§11 로 같은 문서뿐이라 discipline-reviewer 치환의 문면 근거가 없다(§16 «기본값 이탈은 문면 근거 필요») |
| 51 | s042-9.5 | b12 | version 은 애그리거트 루트가 소유·증가 | check-domain-model.py | agent-design-review-db·agent-discipline-reviewer | ②check-domain-model «#257 상태 변경은 루트를 지난다» · ④rule-owner-map #257 = ast+ → check-domain-model.py(ⓒ) + agents/discipline-reviewer.md(ⓓ) — ast+ 후보 채널의 마무리 주체가 ⓓ 라 병기(#50·#70·#71 과 같은 처리) |
| 52 | s043-9.6 | b1 | 중복·race 가 치명적인 쓰기에는 Risky Write Consistency Block 8항목을 명시 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 53 | s043-9.6 | b4 | transaction boundary 를 소유하는 use case/service 명시 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 54 | s043-9.6 | b5 | 사용할 락 전략 명시 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 55 | s043-9.6 | b6 | Rule ownership — 판정·불변식의 도메인 소유와 판정 복제 여부를 명시 | check-domain-model.py·check-transaction-boundary.py | agent-discipline-reviewer·agent-design-review-db | ①이 표를 지배하는 문장(395행)이 «다음 항목을 명시한다»이고 이 행의 결정 내용도 «…소유하는지 — …죽이지 않는지»라는 명시 대상 물음이라 형제 7행과 같은 «명시» Obligation 으로 분류(전 판의 Prohibition 은 실질 금지를 이 자리에 재승격한 것 — 실질 금지의 정본은 s042-9.5/b12 #50 이고 이 행 문면 자신이 «메커니즘 위 §9.5»로 그리 지목한다) · ②check-domain-model «#257 상태 변경은 루트를 지난다»·check-transaction-boundary «#195 애그리거트를 건너뛰지 않는다 / #287 쓰기 인자는 애그리거트» — 명시 대상 사건을 코드 축에서 무는 백스톱 · ④rule-owner-map #257(ast+ → +discipline-reviewer)·#195·#287 · ①문면이 architecture-ddd §3.2 빈혈 차단을 지목 → §16 기본값 표의 «architecture-ddd 구현 시점 규범(§3.2 등) → discipline-reviewer» 병기 |
| 56 | s043-9.6 | b7 | 멱등성 저장(key scope·table·unique·fingerprint·stored result) 명시 | check-idempotency-scope-creep.py | agent-design-review-db | ②check-idempotency-scope-creep docstring 선두 «architecture-db §9.6 Idempotency storage 집행» 직접 지목 · ④commands/dddjango.md checker registry 서수 10(124행 = check-idempotency-scope-creep.py — 이 문서의 다른 ④ 표기인 rule-owner-map #N 계열과 다르므로 계열을 명기한다. rule-owner-map #10 은 check-layer-skeleton 이라 계열 미표기 시 오독) — 단 소유는 «미요청 멱등성 산출물의 승인 없는 추가 차단» 한정이라 명시 의무 잔여는 설계 판정 |
| 57 | s043-9.6 | b8 | Idempotency-Key replay/conflict 계약을 architecture-api 와 정합 | — | agent-design-review-db·agent-design-review-api | ①문면이 architecture-api 를 직접 지정 — 파일럿 판례(명시 문면이 위임 기본값에 우선, ninja s022-6.1 b1)를 준거로 design-review-api 병기 |
| 58 | s043-9.6 | b9 | 외부 결제·알림·publish 의 commit 전/후 실행 위치 명시 | check-transaction-boundary.py | agent-design-review-db | ②check-transaction-boundary «#200 커밋 뒤 부작용은 unit_of_work.after_commit — 응용이 transaction.on_commit 직접 호출이면 위반» · ④rule-owner-map #200 |
| 59 | s043-9.6 | b10 | isolation level 과 deadlock/timeout/serialization failure retry 기준 명시 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 60 | s043-9.6 | b11 | Test criteria 는 보호할 위험·failure 후보와 근거일 뿐 자체로 테스트 의무 아님 | — | agent-discipline-reviewer | ①문면이 discipline-tdd 입장 심사를 지목 → §16 기본값 표(discipline-tdd → discipline-reviewer) |
| 61 | s043-9.6 | b12 | Test criteria 심사 — 독립 production failure 면 add, 중복이면 reuse(테스트 산출물 미생성)·기존 유효 테스트 보존 | — | agent-discipline-reviewer | ①문면이 discipline-tdd 입장 심사와 coder 의 add/reuse 를 지목 → §16 기본값 표(discipline-tdd → discipline-reviewer) |
| 62 | s043-9.6 | b13 | add 된 동시성 테스트는 결정적 CAS-충돌 주입이 기본 — 그 목적의 커스텀 DB 백엔드 교체 금지 | check-mechanism-ownership.py | agent-discipline-reviewer | ②check-mechanism-ownership docstring ⑴ «프로덕션 DB 엔진의 트랜잭션·락·격리 메커니즘을 명세 승인 없이 커스텀 백엔드로 교체한 정확한 형태만 차단 — stock ENGINE 여부·DatabaseWrapper 서브클래스» · ①문면 «stock OPTIONS만, 엔진 교체는 아니다» · ①문면이 implementation-test §20.5·implementation-django §16.4 를 지목 → 기본값 표(implementation-* → discipline-reviewer) — 한계: ⑴ AND 조건 1은 «프로덕션(비테스트) settings» 한정이고 _find_settings_files 가 이름에 test 가 든 settings 모듈을 제외하므로, 테스트 전용 settings·런타임 패치로 교체한 형태는 비커버다. 공용 settings.py 의 DATABASES ENGINE 을 테스트 목적으로 갈아끼운 형태만 차단된다(규범 문면의 «출처-불문»보다 좁음 — 잔여는 위임) |
| 63 | s043-9.6 | b14 | 외부 부수효과는 트랜잭션 밖 — commit 이후 handoff, 유실 불허 시 Outbox(듣는 쪽이 별도 배포 단위일 때만) | check-transaction-boundary.py·check-usecase-dto-placement.py·check-broker-contract.py | agent-discipline-reviewer | ②check-transaction-boundary «#200 after_commit» · check-usecase-dto-placement «#541 커밋 «전» 발행 금지» · check-broker-contract «#529 external 을 가르는 물음 「듣는 쪽이 다른 배포 단위에 있나」» · ④문면 인라인 «#529» ↔ rule-owner-map #529 = ast+ → check-broker-contract.py + discipline-reviewer |
| 64 | s044-9.7 | b1 | 이중 쓰기 유실이 치명적이면 Outbox 로 해결 — 듣는 쪽이 별도 배포 단위일 때만 | check-broker-contract.py | agent-discipline-reviewer | ④문면 인라인 «#529» ↔ rule-owner-map #529 = ast+ → check-broker-contract.py(ⓒ)+discipline-reviewer(ⓓ) · ②broker-contract docstring «#529 external 을 가르는 물음 「듣는 쪽이 다른 배포 단위에 있나」 — 구독이 이 저장소 안이면 후보» |
| 65 | s044-9.7 | b1 | in-repo 소비자의 유실 불허는 받는 쪽 cron_job/ → 주인 OHS 폴링으로 해결 | — | agent-design-architect | ④문면 인라인 «#626» ↔ rule-owner-map #626 = human → agents/design-architect.md(ⓓ 단독 — 검사기 ⓒ 없음)라 enforcedBy 미배선 · ②check-missable-entrance 의 #629(«빠진 것은 cron_job 이 시각에 깨어나 주인에게 «물어» 메운다(#626)»)는 인접 규칙의 후보 채널이고 그 검사기 이관 계약이 «ⓓ 후보는 exit 불산입»이라 집행이 아니다 — 같은 사건을 좁히는 표면화 채널로만 기록한다(도피 아님: #626 자체를 무는 검사기가 존재하지 않음) |
| 66 | s044-9.7 | b2 | 발행 메시지를 비즈니스 데이터와 같은 트랜잭션으로 outbox 테이블에 기록 | check-broker-contract.py | agent-design-review-db | ②check-broker-contract docstring «#603 external 에 내용이 오면 딸림이 함께 선다 — ⑴outbox … («선언 유무»만 잰다)» + 그 ⑴ 슬라이스의 위반 메시지 실물 «⑴ outbox 가 없다 — 커밋과 발행을 한 트랜잭션에 묶는 선언이 필요하다»(check-broker-contract.py 402행 — docstring 이 아니라 구현 문자열) · ④rule-owner-map #603 = ast → check-broker-contract.py |
| 67 | s044-9.7 | b2 | 별도 디스패처가 미발행 행을 읽어 발행하고 발행 표시 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 68 | s044-9.7 | b5 | outbox 테이블은 필수 컬럼을 갖고 비즈니스 write 와 동일 트랜잭션에 기록 | check-broker-contract.py | agent-design-review-db | ②check-broker-contract docstring «#603 … ⑴outbox …(«선언 유무»만 잰다)» + 위반 메시지 실물 «⑴ outbox 가 없다 — … 한 트랜잭션에 묶는 선언»(402행 구현 문자열) · ④rule-owner-map #603 = ast → check-broker-contract.py |
| 69 | s044-9.7 | b6 | 전달 보장은 at-least-once — exactly-once 미보장을 명시 | check-broker-contract.py | agent-discipline-reviewer | ②check-broker-contract «#532 external 계약은 at-least-once 를 «요구로» 적는다 — 명시가 없으면 후보» · ④rule-owner-map #532 = ast+ → broker-contract + discipline-reviewer |
| 70 | s044-9.7 | b7 | 소비자는 event id 등으로 중복 수신을 무시할 수 있어야 한다 | check-missable-entrance.py | agent-discipline-reviewer | ②check-missable-entrance «#181 멱등성은 유스케이스가 갖는다» — broker-contract docstring 이 «멱등 물음의 소유자는 #181» 로 명시 위임 · ④rule-owner-map #181 = ast+ → check-missable-entrance.py + discipline-reviewer |
| 71 | s044-9.7 | b8 | 발행 실패는 retry_count 증가 후 재시도하고 한계 초과는 dead-letter 격리 | check-broker-contract.py | agent-design-review-db | ②check-broker-contract docstring «#603 … ⑷데드레터 …(«선언 유무»만 잰다)» + 위반 메시지 실물 «⑷ 재시도·데드레터 선언이 없다»(404행 구현 문자열) · ④rule-owner-map #603 = ast → check-broker-contract.py |
| 72 | s044-9.7 | b9 | 디스패처 동시성은 행 잠금(FOR UPDATE SKIP LOCKED) 또는 단일 워커 직렬화 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 73 | s044-9.7 | b10 | 전역 순서가 필요하면 aggregate 단위 직렬화·정렬 키, 불필요하면 명시적 포기 | check-broker-contract.py | agent-design-review-db | ②check-broker-contract docstring «#603 … ⑸순서 보장 명시 …(«선언 유무»만 잰다)» + 위반 메시지 실물 «⑸ 순서 보장 «여부»의 명시가 없다»(406행 구현 문자열) · ④rule-owner-map #603 = ast → check-broker-contract.py |
| 74 | s044-9.7 | b11 | 외부 부수효과 없음·on_commit 충분·유실 수용 가능이면 Outbox 회피 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 75 | s044-9.7 | b11 | Outbox 채택의 도메인 측면은 architecture-ddd §3.7, Django 구현은 implementation-django §16.5 를 따른다 | — | agent-design-review-ddd·agent-discipline-reviewer | ①문면이 architecture-ddd 와 implementation-django 를 직접 지목 → §16 기본값 표(architecture-ddd 설계 시점 → design-review-ddd · implementation-* → discipline-reviewer) |
| 76 | s046-10.1 | b8 | 예상 행과 실제 행이 크게 다르면 ANALYZE 로 테이블 통계 갱신 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 77 | s050-10.5 | b3 | SELECT * 회피 — 필요한 컬럼만 지정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 78 | s050-10.5 | b4 | 가능한 한 DB 단에서 필터링(애플리케이션 필터링 회피) | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 79 | s050-10.5 | b5 | 결과 집합 크기를 LIMIT 으로 제한 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 80 | s051-11 | b1 | architecture-db 의 관할은 운영 중 구조 변경의 안전 순서와 DB 위험 결정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 81 | s051-11 | b1 | migration file 구현(RunPython·apps.get_model·sqlmigrate·migration class)은 implementation-django 관할 | — | agent-design-review-db·agent-discipline-reviewer | ①문면이 implementation-django 위임을 명시 → §16 기본값 표(implementation-* → discipline-reviewer) 병기 · ②check-mechanism-ownership ⑵ 는 migrations 파일 «규율»(#336·#337·#338·#593)이지 관할 선언 집행이 아니므로 enforcedBy 미배선(도피 아님 — 커버 축 상이) |
| 82 | s052-11.1 | b1 | 운영 DB 변경은 신·구 코드 동시 동작 시간을 고려 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 83 | s052-11.1 | b7 | rename·type 변경은 한 번에 바꾸지 않고 add/copy/switch/drop 으로 분해 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 84 | s053-11.2 | b2 | batch 크기와 pause 정책 결정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 85 | s053-11.2 | b3 | row lock·replication lag·long transaction·vacuum 영향 확인 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 86 | s053-11.2 | b4 | 실패한 batch 재실행이 안전하도록 idempotent 하게 작성 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 87 | s053-11.2 | b5 | 진행률·오류율·lag·query latency 모니터링 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 88 | s053-11.2 | b6 | 부분 완료 상태의 rollback/forward-fix 를 사전 결정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 89 | s054-11.3 | b4 | 새 index 는 online/concurrent 생성 필요 여부 확인 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 90 | s054-11.3 | b5 | unique constraint 는 사전 중복 탐지와 cleanup 선행 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 91 | s054-11.3 | b6 | NOT NULL 은 nullable 추가 → backfill → NOT NULL 순서 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 92 | s054-11.3 | b7 | check constraint 는 사전 검증과 점진적 validation 고려 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 93 | s054-11.3 | b8 | FK 추가는 orphan cleanup 과 cascade/delete 정책 결정 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 94 | s055-11.4 | b1 | 운영 변경 계획은 rollback 만이 아니라 forward-fix 도 함께 검토 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 95 | s056-11.5 | b1 | 운영 변경을 다룬 DB architecture 답변은 rollout 산출물 7항을 남긴다 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 96 | s061-12.4 | b3 | 작은·단순 트리에 빈번한 갱신이면 Adjacency List | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 97 | s061-12.4 | b4 | 깊은 계층·복잡한 조상/자손 쿼리면 Closure Table | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 98 | s061-12.4 | b5 | 읽기 중심·안정적 트리면 Nested Set | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 99 | s061-12.4 | b6 | 단순 트리·보통 수준 갱신이면 Materialized Path | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 100 | s066-13.4 | b3 | 다형적 연관의 참조 무결성은 애플리케이션 레벨에서 보장 | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 101 | s067-13.5 | b3 | 타입 간 속성이 대부분 공유되면 STI | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 102 | s067-13.5 | b4 | 타입별 속성이 크게 다르고 무결성이 중요하면 CTI | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 103 | s067-13.5 | b5 | 타입이 완전 독립이고 접근 패턴이 다르면 TPC | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |
| 104 | s067-13.5 | b6 | 여러 부모 타입에 댓글/태그를 연결하면 Polymorphic Association | — | agent-design-review-db | ①문면 역할명·②검사기 docstring·④registry #N 어느 축도 이 규범을 지목하지 않음 — §16 위임 기본값 표(architecture-db → agent-design-review-db) |

### 2.1 배선 요약

- **enforcedBy 배선 22건 / 104**(수리 전 24 — #44·#66 강등) — 검사기가 실제로 그 사건을 무는 규범에만 달았다. 사용된 검사기 8종: `check-db-table.py`(#631 타 BC FK) · `check-context-isolation.py`(#12·#13 ACL) · `check-transaction-boundary.py`(#195·#200·#287·#599) · `check-domain-model.py`(#257) · `check-mechanism-ownership.py`(⑴ ENGINE·DatabaseWrapper 축 — b11 경계 3건 + §9.6 b13 1건) · `check-idempotency-scope-creep.py`(§9.6 직접 지목) · `check-broker-contract.py`(#529·#532·#603) · `check-missable-entrance.py`(#181) · `check-usecase-dto-placement.py`(#541 커밋 전 발행 금지).
- **enforcedBy 강등 2건(적대 리뷰 수리)**: s042-9.5/b10 «연결 설정 명시»(검사기가 OPTIONS 를 아예 관측하지 않아 이 명시 의무의 기계 커버 0 — 무는 것은 우회형 엔진 교체이고 그 축은 b11 이 진다) · s044-9.7/b1 «#626 cron_job 폴링»(rule-owner-map #626 = human ⓓ 단독 · 인접 #629 는 ⓓ 후보라 exit 불산입 = 집행 아님). 둘 다 «도피»가 아니라 커버 부재/집행 부재의 정직 기록이다.
- **위임 기본값 이탈 근거**(§16 «이탈도 도피도 문면 근거 필요»):
  - `agent-discipline-reviewer` 병기/치환 14건 — 문면이 `architecture-ddd` §3.2(빈혈 차단·구현 시점 규범) · `implementation-django` §16.4 · `implementation-test` §20.4/§20.5 · `discipline-tdd` 입장 심사를 **직접 지목**한 규범에 한정. §16 기본값 표의 «architecture-ddd 구현 시점 → discipline-reviewer», «implementation-*·discipline-tdd → discipline-reviewer» 행이 근거.
  - `agent-design-review-api` 병기 1건(s043-9.6/b8 API handoff) — 문면이 `architecture-api`를 직접 지정. 파일럿 판례(ninja s022-6.1 b1, «명시 문면이 기본값에 우선») 준거.
  - `agent-design-review-ddd` 병기 2건 — s044-9.7/b11(`architecture-ddd` §3.7 지목) · s034-8.2/b8 norm2(§3.3 규칙3 «다른 애그리거트는 ID로만 참조하라» 직접 지목 — 설계 시점 규범이라 §16 기본값 표의 design-review-ddd 행. 적대 리뷰 M-6 수리: 같은 spec 의 «직접 지목→병기» 정책이 이 건만 미적용이었다).
  - `agent-design-architect` 단독 1건(s044-9.7/b1 «#626») — rule-owner-map #626 = `human` → `agents/design-architect.md`. 검사기 ⓒ가 없는 human 규칙이라 registry가 판정 주체를 직접 지정한다.
  - **기본값 유지로 되돌린 1건**(적대 리뷰 M-1 수리) — s042-9.5/b12 norm2(#50 «QuerySet.update() 0행이면 재조회 후 도메인 메서드부터»)는 discipline-reviewer 단독이었으나, 인용된 #599·#195 가 registry 상 `ast`(ⓒ 단독)이고 391행 그 문장의 참조가 §9.6·§11(같은 문서)뿐이라 이탈의 문면 근거가 없다 → design-review-db 로 복원.
  - **ast+ ⓓ 반영 1건**(적대 리뷰 M-2 수리) — s042-9.5/b12 norm3(#51 «version 은 애그리거트 루트가 소유·증가»)의 basis 가 인용한 #257 = `ast+`(ⓒ check-domain-model + ⓓ discipline-reviewer)의 ⓓ 를 배선에 반영해 병기.
- **기본값 «도피» 아님을 명시한 4건**(담당 검사기가 있어 보이나 커버 축이 다른 곳):
  - s035-8.3/b8 — `check-idempotency-scope-creep.py`의 docstring § 지목은 «architecture-db §9.6 Idempotency storage» 한정이고 소유도 «미요청 멱등성 확장 차단»뿐이라 §8.3 결정 의무는 비커버.
  - s042-9.5/b10 셋째 규범(«연결 설정을 명세가 명시») — `check-mechanism-ownership.py`는 `ENGINE_RE` 로 DATABASES ENGINE 만 읽고 `OPTIONS`·PRAGMA 를 관측하지 않는다. 명시 의무의 기계 커버 0.
  - s042-9.5/b11 넷째 규범(PRAGMA) — 같은 AND 게이트가 `ENGINE` 점경로·`DatabaseWrapper` 서브클래스 축만 본다. PRAGMA 축은 docstring에 없다.
  - s051-11/b1 둘째 규범 — `check-mechanism-ownership.py` ⑵는 migrations 파일 «규율»(#336·#337·#338·#593)이지 «관할 선언» 집행이 아니다.
- **인접 검사기 대조 후 기각 기록**(§16 «로스터 전수 실독»의 판정 잔여):
  - s034-8.2/b8 norm2(타 BC ID 값 참조) ↔ `check-domain-model.py` **#548**(«다른 애그리거트는 «식별자 값 객체»로만 — 타입 힌트의 남의 루트 클래스») — 기각. #548 은 «도메인 전역» 슬라이스의 **같은 BC 안** 애그리거트 간 타입 힌트 규칙이라 BC 경계 참조 축과 상이하다. BC 경계 축의 금지 절반은 `check-db-table.py` #631, 대체 수단(ACL) 절반은 `check-context-isolation.py` #12·#13 이 진다.
  - s042-9.5/b9(#40 락 범위 — 트랜잭션 안 외부 호출 금지) ↔ `check-context-isolation.py` **#14**(«`with unit_of_work:` 안에서 크로스-BC 포트 호출 금지») — 기각. #14 의 주어는 «크로스-BC 포트»이고 금지 사유는 경계 격리다. 이 규범의 주어는 외부 API·사용자 입력 대기·긴 배치를 포함하는 «락 보유 시간»이라 축이 다르다(교집합은 있으나 #14 로 커버되는 부분집합이 규범의 중심 사건이 아니다) → 기본값 위임 유지.
  - s042-9.5/b11 셋째 규범(#47 커스텀 백엔드 자기 판단 생성 금지)·s043-9.6/b13(#62 테스트 목적 백엔드 교체 금지) ↔ `check-mechanism-ownership.py` ⑴ — **부분 커버로 유지**. `_find_settings_files()` 가 이름에 `test` 가 든 settings 모듈을 제외하므로 테스트 전용 settings·런타임 패치 경로는 비커버이고, 공용 `settings.py` 의 ENGINE 교체만 차단된다. 규범 문면의 «출처-불문»보다 좁은 커버라 한계를 basis 에 병기했다(적대 리뷰 H-1 수리 — 다만 «구조적으로 발화 불가»라는 리뷰의 강한 주장은 기각한다. 단일 `settings.py` 레이아웃에서 테스트 목적 교체는 그 파일에 떨어지고 게이트가 발화한다).

## 3. 재진술 유예 (교차 문서 — 전 웨이브 후 소급 패스 연결)

같은 문서 쌍 2건(s016-3.4/b1 → s019-4.2/b1 · s036-8.4/b4 → s052-11.1/b1)은 spec `restates`에 직접 넣었다. 아래는 **다른 문서** 상대라 spec에 넣지 않고 유예한다. 전량 «상대가 사본, 내 절이 정본» 방향이므로 소급 패스는 상대 문서 spec 쪽에 `restates` 엣지를 달게 된다.

| # | 정본(내 절/블록) | 사본 상대 | 사본 문면 | 확인 |
|---|---|---|---|---|
| 1 | s021-5/b1 · s019-4.2/b1 | `architecture-db-skill` §핵심 운영 원칙 불릿 1 | «성능 최적화 순서를 지킨다: 슬로우 쿼리 최적화 → 인덱스 적용 → 캐시 → 역정규화. … 정규화 먼저 한 뒤 필요한 경우에만 적용한다 (§4, §5)» | SKILL.md 19행 직접 확인 |
| 2 | s028-7.1/b3 | `architecture-db-skill` §핵심 운영 원칙 불릿 2 | «복합 인덱스는 선택도 높은 컬럼을 앞에 … 실제 액세스 패턴 기반으로 결정한다 (§7)» | SKILL.md 20행 — **부분 상충 주의**: 사본이 «선택도 높은 컬럼을 앞에»라 적어 정본 §7.1의 «"가장 선택적인 컬럼을 먼저" 신화 깨기»와 어긋난다. 소급 패스에서 restates가 아니라 **개정 후보**로 올려야 한다 |
| 3 | s032-8/b1 · s036-8.4/b1 | `architecture-db-skill` §핵심 운영 원칙 불릿 3 | «비즈니스 불변식이 DB 경계에서 지켜져야 하면 unique constraint·FK·check constraint를 사용하고, 제약조건 rollout은 lock risk를 고려한 단계적 순서를 따른다 (§8)» | SKILL.md 21행 |
| 4 | s041-9.4/b6 | `architecture-db-skill` §핵심 운영 원칙 불릿 4 | «격리 수준은 필요 이상으로 높이지 않는다 … (§9.4)» | SKILL.md 22행 |
| 5 | s043-9.6/b1 · b11 · b12 | `architecture-db-skill` §핵심 운영 원칙 불릿 5 | «Risky Write … 명시한다. Test criteria 자체는 테스트 의무가 아니며 … `add`일 때만 coder가 새 테스트를 작성한다 (§9.6)» | SKILL.md 23행 |
| 6 | s043-9.6/b14 · s044-9.7/b1·b6·b7 | `architecture-db-skill` §핵심 운영 원칙 불릿 6 | «외부 결제·알림·메시지 발행은 DB 트랜잭션 내부에서 실행하지 않는다. … Outbox로 at-least-once 전달을 보장하고, consumer는 중복 수신을 무시할 수 있어야 한다 (§9.7)» | SKILL.md 24행 |
| 7 | s052-11.1/b1 · s053-11.2 | `architecture-db-skill` §핵심 운영 원칙 불릿 7 | «운영 컬럼·인덱스·constraint 변경은 Expand / Backfill / Contract 단계를 따르고, 대용량 backfill은 … 배치 처리를 계획한다 (§11)» | SKILL.md 25행 |

**유예 기록 7건.** 상대 문서 `architecture-db-skill`은 T3 웨이브 3 소속(미이관)이라 §15 «상대 블록이 미이관 절이면 restates 생략 + 유예 기록» 그대로다.

### 3.1 재진술 판정 기록 — 교차 참조(사본 아님) + 문서 «안» 쌍 (소급 패스 지침)

- s042-9.5 ↔ `architecture-api-final` s018-4.2 — 발주서 비고의 «CAS status와 규칙 쌍». db는 CAS **메커니즘**(경합 가드·재실행)을, api는 재시도 소진의 **status 배정**을 정한다. 축이 달라 사본 아님.
- s043-9.6/b7·b8 ↔ `architecture-api-final` s060-13.3 — 발주서 비고가 스스로 «상호 참조 — 사본 아님»이라 명시. api §13.3 표는 7항(적용 여부·Replay·Conflict·Concurrency 등), db §8.3/§9.6은 저장소 6항으로 항목 집합이 다르다. 문면 자체가 «HTTP status·응답 표현은 presentation이 소유»로 소유 분할을 선언하므로 재진술이 아니라 계약 조인이다.
- s034-8.2/b8 → `architecture-ddd` §3.3 규칙3 · s042-9.5/b12 → `architecture-ddd` §3.2 · s044-9.7/b11 → `architecture-ddd` §3.7·`implementation-django` §16.5 — 전부 «따른다/지목» 형태의 위임 참조. 사본 아님(배선의 ① 근거로만 사용).

**문서 «안» 쌍의 판정 기록**(적대 리뷰 M-4·M-5·L-1~L-4 수리 — 지금까지 §3.1 이 교차 문서 쌍만 다뤄 내부 쌍 판정이 비어 있었다):

| 쌍 | 판정 | 근거 |
|---|---|---|
| s036-8.4/b4(329행) ↔ s052-11.1/b1(514행) | **사본** — spec `restates` 적용(census −1) | 술어(«고려한다»)·목적어(신·구 코드 동시 동작 기간)가 같은 준-축자 쌍. §11 이 «운영 rollout» 관할을 스스로 선언하므로 §11.1 이 정본이고 §8.4 3항은 제약조건 rollout 절차 안의 되풀이다 |
| s043-9.6/b6(401행 Rule ownership) ↔ s042-9.5/b12 norm1(391행) | **재승격이었음 — 실질 규범은 §9.5 정본에 위임** | 401행의 실질 내용(판정 SQL·ORM 복제 금지)은 §9.5 가 정본이고 401행 자신이 «메커니즘 위 §9.5»로 그리 지목한다. 다만 401행의 고유 규범은 «이 항목을 명시하라»(표 지배 문장 395행)라 Work 는 유지하되 class 를 형제 7행과 같은 «명시» Obligation 으로 재분류했다(블록 레벨 restates 는 부적합 — 블록이 사본이 아니라 자기 규범을 진다) |
| s043-9.6/b14 셋째 문장(412행) ↔ s044-9.7/b1(418행) | **부분 사본 — 소급 패스 후보** | «유실 불허 시 Outbox(별도 배포 단위 한정 #529 · in-repo 는 cron_job 폴링 #626)»가 괄호 주석까지 동일. 다만 b14 는 3문장 압축 Work 라 블록 레벨 restates 를 달 수 없다 → 정본 s044-9.7/b1 로 두고 문장 해상도 재정렬과 함께 소급 패스 후보로 지목(spec b14 note 에 기록) |
| s044-9.7/b5(424행 Outbox 테이블 행) ↔ b2(420행) | **사본 아님** | 겹치는 것은 «동일 트랜잭션 기록» 술어뿐이고 b5 는 필수 컬럼 집합(`id`·`event_type`·`payload`·`published_at`·`retry_count`)을 추가로 규정한다. 표 행이 산문 규범의 결정 항목을 구체화하는 관계라 계약 분해이지 재진술이 아니다 |
| s041-9.4 Serializable 행(369행 «반드시 재시도 로직 구현» — 미계수) ↔ s042-9.5/b8(#39 «Serializable + retry 필수») | **사본 후보 — 소급 패스 병기** | 같은 문서·같은 규범인데 §9.4 쪽은 표 행 계수 규약 비일관(메모 1)으로 미계수라 현재 이중 계상이 없다. 메모 1의 «표 행 계수 규약 1회 정렬» 후보에 §9.4 b4·b5 를 올릴 때, 계수를 늘리는 대신 §9.5/b8 을 정본으로 한 `restates` 로 처리할지를 함께 판정해야 한다 |
| s033-8.1/b3(#16 «자연키가 불안정하면 surrogate key») ↔ s009-2.3/b7(#4 «자연 기본키 부재 시 인조키») | **사본 아님** | 조건절이 다르다 — #4 는 자연 PK 후보의 **부재**(선택지 없음), #16 은 존재하는 자연키의 **불안정**(선택지가 있으나 부적격). 같은 처방(surrogate key)을 부르는 서로 다른 판정 기준이라 각각 독립 규범 |
| s035-8.3/b8(#28 멱등성 저장소 6항) ↔ s043-9.6/b7(#56 Idempotency storage 5항) | **사본 아님** | 항목 집합이 다르다 — §8.3 은 DB 설계의 최소 결정 6항으로 `retention/cleanup`·`storage owner/location` 을 포함하고, §9.6 행은 Risky Write 블록에 명시할 5항으로 `table` 과 `stored result`(= 도메인/응용 outcome, HTTP 표현은 presentation 소유)를 규정한다. 소유 문맥(DB 설계 vs Risky Write 심사)과 항목이 함께 달라 중첩 5/6 은 계약 조인이다 |

- **class 분포**: Obligation 93 · Prohibition 8 · Exception 3 · Permission 0 · Override 0. **delegatedTo 분포**: design-review-db 94 · discipline-reviewer 14 · design-review-ddd 2 · design-review-api 1 · design-architect 1. **무소유 0건**(도구 단언 통과). Permission 0 의 원인은 s043-9.6/b12 압축(메모 10)이며 소급 패스 후보로 기록했다.

## 4. 경계 판단 메모

1. **표 행 계수의 문서 내 비일관 — 발주서 계수를 그대로 승계했다.** §8.1은 «주의» 셀 5행을 전부 규범으로 계수하는데, §9.4는 같은 꼴의 «주의» 셀 3행 중 «직렬화 실패 시 재시도 필요»·«반드시 재시도 로직 구현»을 계수하지 않고 §11.4도 «대응 기준» 5행을 계수하지 않는다(반면 §11.3의 «설계 기준» 5행은 계수). 발주서 스스로 §9.4 비고에 «표 행 계수 비일관 지점, 애매»라 적었다. **판정**: 여기서 계수를 늘리면 이 문서 한 건만 웨이브 분모에서 이탈하고, 줄이면 §8.1·§11.3의 기존 계수와 충돌한다. 동결 센서스가 T3 전체의 분모라 **계수는 승계하고 사실만 기록**한다 — 소급 패스(웨이브 4)의 «표 행 계수 규약 1회 정렬» 후보로 §9.4 b4·b5(재시도 셀)와 §11.4 b2~b8(대응 기준 셀)을 지목해 둔다. 블록 자체는 kind=table-row로 전부 존재하므로 나중에 norms만 얹으면 되고 블록 경계 재작업은 없다. **소급 판정 병기**(적대 리뷰 L-3 수리): §9.4 Serializable 행의 «반드시 재시도 로직 구현»은 s042-9.5/b8(«Serializable + retry 필수»)과 같은 문서·같은 규범이다. 정렬 시 계수를 늘리는 선택지와 §9.5 를 정본으로 한 `restates` 선택지를 함께 판정해야 한다(§3.1 내부 쌍 표에 기록).
2. **`---` thematic break와 «> 출처» blockquote의 소유.** 두 요소 모두 절 스팬 안이라 kind=prose 블록으로 분리했다(§13 «리스트·blockquote는 마커 포함 verbatim»). 절 말미 빈 줄은 선행 블록의 후행 스팬에 귀속시켰고, 절 선두 빈 줄만 첫 블록 선두에 붙였다 — 28절 전부 이 규칙 하나로 통일했고 도구의 byte 등가 단언이 통과했다.
3. **code 펜스 블록의 후행 구분자.** s021-5/b2(173–179)·s028-7.1/b4(233–241)·s046-10.1/b1(438–450)·s066-13.4/b2(698–706)는 닫는 펜스 다음 빈 줄까지 code 블록에 넣었다. §13의 «펜스 전체 라인 verbatim»과 «블록 간 구분자는 선행 블록 후행 귀속»이 겹치는 자리인데, 후자를 우선했다(전자는 «최소 포함 범위» 규정이지 «최대» 규정이 아니다). s028-7.1/b4·s061-12.4/b8처럼 펜스가 절 끝인 경우도 같은 규칙이라 예외가 없다.
4. **번호 목록 vs checklist-item.** §8.4의 1.~4. 단계는 `- [ ]` 형태가 아니므로 kind=checklist-item이 아니라 kind=norm이다(발주서 비고 «번호 목록 — 체크리스트 아님»과 일치). 코퍼스 체크박스 0 실증(§12)이 여기서도 재확인된다. 3항 블록은 kind=norm 을 유지하되 Work 대신 `restates`를 진다(§1 census 대사 ①) — 절차 4단계의 원문 텍스트는 블록으로 온전히 남고 규범만 §11.1 정본을 가리킨다.
5. **«열거는 규범이 아니다» 판정 3곳.** §8.3의 6불릿(316–322) · §11.5의 7불릿(562–568) · §2.2의 하위 불릿 2행(62–63)은 상위 지시 1건의 열거라 독립 Work를 주지 않았다. 앞 둘은 kind=prose 블록으로 분리했고(상위 지시 문단과 다른 자연 단위), §2.2만 상위 번호 항과 한 블록으로 묶었다(들여쓴 하위 불릿이라 상위 항의 일부).
6. **§9.5(18) 분해가 이 문서 최난.** 굵은 라벨 3단락(387·389·391행)이 각각 한 «행»에 다문장 규범을 담는다. 문장 등장 순 = 채번 순 규약대로 387행=4 · 389행=4 · 391행=3으로 잘랐고, 판정 근거는 ⓐ 사실 서술 문장(«SQLite는 select_for_update를 no-op으로 무시한다» 등)은 미계수 ⓑ 한 문장 안 괄호 부연(«WHERE엔 version 경합 가드만 담고 비즈니스 판정은 제외»)은 모문장 Work에 흡수 ⓒ 절 내 재진술(391행의 «선언적 불변식 백스톱 … 최후 안전망으로 병행»은 387행 규범의 되풀이)은 별도 Work 미승격 — 세 규칙이다. **387행 단락의 정확한 산술**(적대 리뷰 L-13 수리 — 전 판 note 의 «4문장 규범 + 사실 서술 2문장»은 부정확했다): 이 단락은 **5문장**이고 규범 4건은 **3문장**에 분포한다(첫 문장 1 · 넷째 문장 2 — «환경 무관 방어선»과 «연결 설정 명시» · 다섯째 문장 1). 둘째·셋째가 사실 서술이다. 계수 18 자체는 무결이고 기록만 교정했다. «고경합 핫 로우는 비관적 락도 고려한다»는 385행 «락 범위» 규범의 트레이드오프 단서라 흡수했다. 이 분해로 정확히 18이 되며, 다른 분해(387=5·389=3·391=4 등)도 18을 만들 수 있으므로 **경계는 판단이고 총계만 동결값에 맞춘 것**임을 정직히 기록한다.
7. **§9.6의 8행 표 = 8 Work.** 표의 각 행이 «명시한다»(395행)의 목적어 항목이라 행마다 명시 의무 1건으로 승격했다(1 + 8 + 산문 3 = 12). «Test criteria (candidate)» 행은 마지막 문장이 «자체로 테스트 의무가 아님»이라 class=Exception으로 잡았다. **Rule ownership 행의 class 교정**(적대 리뷰 M-5 수리): 이 행만 Prohibition 이었는데, 형제 7행과 같은 표·같은 지배 문장 아래 있고 결정 내용도 «…소유하는지 — …죽이지 않는지»라는 **명시 대상 물음**이라 «명시» Obligation 으로 재분류했다. 그 행이 담은 실질 금지(판정의 SQL·ORM 복제)는 s042-9.5/b12 첫 규범이 정본이고 행 문면 자신이 «메커니즘 위 §9.5»로 그리 지목하므로 이 자리의 재승격이 잘못이었다.
8. **class 배정의 보수 규칙.** «~하지 않는다/금지/회피»는 Prohibition, «~일 때만/한정»은 Exception, 나머지 지시는 Obligation으로 갔다. §12.4·§13.5의 «권장 패턴» 표 8행은 강도상 권고지만 djr 5종에 «권고» 자리가 없어 Obligation으로 두었다(Permission은 «해도 된다»라 의미가 더 어긋난다). Override는 이 문서에 해당 문면이 없어 0건이다.
9. **s034-8.2 «타 BC ID 값 참조»의 enforcedBy.** `check-context-isolation.py`는 FK가 아니라 import·호출 경로를 보는 검사기다. 그럼에도 배선한 이유는 규범의 대체 수단인 «앱 레벨/ACL 무결성»을 #12·#13이 정확히 무는 축이기 때문이고, «ID 값 참조» 채택 자체는 설계 판정이라 db 리뷰를 병기했다. 금지 축(타 BC FK)은 `check-db-table.py` #631이 문자열 참조까지 포함해 축자로 문다. 인접 후보였던 `check-domain-model.py` #548 은 §2.1 «인접 검사기 대조 후 기각» 표에 판정을 남겼다.
10. **§9.6 산문 3블록(408·410·412행)의 문장→Work 대응**(§13 «블록 내 문장→Work 대응은 검수표에 기록» 이행 — 전 판은 메모 6의 §9.5 만 이행했다. 적대 리뷰 L-11 수리):
    - **b12(408행 · 4문장 → Work 1)**: ①«Test criteria 는 후보 목록이다»(정의 서술 — 미계수) ②«…coder 가 `add` 할 수 있다»(**Permission 성격**) ③«…`reuse` 하며 test artifact 를 만들지 않는다» ④«기존 유효 테스트는 보존한다». ②~④가 규범인데 동결 census(§9.6 = 12)를 승계하려고 «Test criteria 심사» Obligation 1건으로 압축했다 — **이 문서 Permission 분포 0의 원인**이다.
    - **b13(410행 · 2문장 → Work 1)**: ①«결정적 CAS-충돌 주입(스파이)을 기본으로 한다» ②«스레드 race 재현을 위해 연결 메커니즘을 커스텀 백엔드로 바꾸지 않는다». 의무+금지 쌍을 한 Work 로 압축.
    - **b14(412행 · 3문장 → Work 1)**: ①«외부 부수효과는 DB 트랜잭션 내부에서 실행하지 않는 것을 기본» ②«묶을 이유가 없으면 commit 이후 handoff» ③«유실 불허 시 Outbox(§9.7)(별도 배포 단위 한정 #529 · in-repo 는 cron_job 폴링 #626)». ③은 s044-9.7/b1 과 괄호 주석까지 같은 부분 사본(§3.1 내부 쌍 표 참조).
    - **판정**: 동결 census 승계가 이번 웨이브의 계약이므로 계수는 바꾸지 않고 대응만 기록한다. 소급 패스(웨이브 4)의 «문장 해상도 재정렬» 후보로 이 3블록을 지목하고, 재정렬 시 b12 ②의 class 를 Permission 으로 되살릴 것을 함께 적어 둔다.
11. **«절 내 재진술» 처리의 근거 교정**(적대 리뷰 L-12 수리). 전 판 s042-9.5/b12 note 는 «같은 절이라 restates 불요»라 적었는데 §15 에 같은-절 면제 조문은 없다(자작 규칙이었다). 실제 근거는 구조다 — `djr:restates` 는 **블록 단위 속성**이고 b12 는 자기 Work 3건을 지는 블록이라 «이 블록은 저 블록의 사본»이라는 표시를 달 수 없다. 즉 «면제»가 아니라 **문장 레벨 restates 의 부재**가 원인이고, 그래서 재진술 문장은 Work 미승격 + note 기록으로 처리했다. 같은 구조가 s043-9.6/b14 셋째 문장에도 걸린다. **§15 개정 제안 후보**로 올린다 — «한 블록의 여러 문장 중 일부만 사본일 때의 표기»(§13 이 이미 `statesNorm` 다중 연결로 문장 해상도를 실현했으므로, restates 도 Work 단위 속성으로 확장할 수 있는지)를 웨이브 4에서 판정할 것.
