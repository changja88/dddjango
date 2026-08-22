# T3 발주 — architecture-db-final

- 원문: `dddjango/skills/architecture-db/references/final.md` (현재 736행 — 센서스와 일치)
- 스코프: REF 28절 · 규범 106문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/architecture-db-final.spec.json` + `workspace/eval/t3/worksheets/architecture-db-final.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s005-1.2 | 1.2 업무 파악 원칙 | 37–45 | 1 | none | N | 청유형 «말을 믿지 말자» 보수 포함(P0 승계) |
| s008-2.2 | 2.2 ERD 작성 원칙 | 58–64 | 2 | none | N | ERD 작성 원칙 2 |
| s009-2.3 | 2.3 식별자 (Primary Key) | 65–75 | 1 | table | N | 인조키 지시 1; 키 종류 표는 정의 |
| s016-3.4 | 3.4 정규화 핵심 원칙 | 133–140 | 1 | none | Y:architecture-db-final/s019-4.2 | 정규화-먼저 규칙 사본(4중 출현의 하나) |
| s019-4.2 | 4.2 핵심 원칙 | 151–154 | 2 | none | N | 정규화-먼저 규칙 정본으로 지정 |
| s021-5 | 5. 성능 최적화 순서 | 169–185 | 2 | code | N | 순서 의무 2; 순서 목록 자체는 코드 펜스 내(예제 계수 제외) |
| s028-7.1 | 7.1 복합 인덱스 컬럼 순서 | 225–241 | 2 | code | N | 순서 결정 규칙 2; 최좌선 접두사 규칙은 사실 서술 |
| s031-7.4 | 7.4 인덱스 설계 일반 원칙 | 263–275 | 4 | table | N | 원칙 표 행 4(표 행 계수) |
| s032-8 | 8. 제약조건과 중복 방지 | 276–279 | 1 | none | N | §서두 보호 원칙 1 |
| s033-8.1 | 8.1 제약조건 선택 기준 | 280–289 | 5 | table | N | 주의 셀 5(표 행 계수) |
| s034-8.2 | 8.2 FK 삭제 정책 | 290–302 | 3 | table | N | cascade 금지 1+BC 경계 FK 금지 2; 삭제 정책 표 행은 매핑 미계수 |
| s035-8.3 | 8.3 중복 방지와 멱등성 저장소 | 303–322 | 5 | table | N | 매핑 표 행 4+«최소한 다음을 정한다» 1; 하위 불릿 6은 지시 1건의 열거 |
| s036-8.4 | 8.4 제약조건 rollout 원칙 | 323–333 | 5 | none | N | rollout 설계 의무 1+단계 4(번호 목록 — 체크리스트 아님) |
| s041-9.4 | 9.4 실전 선택 가이드 | 363–372 | 1 | table | N | 핵심 지시 1; 매핑 표 행 3 미계수(P0 §9.4=1 승계 — 표 행 계수 비일관 지점, 애매) |
| s042-9.5 | 9.5 락과 동시성 제어 | 373–392 | 18 | table | N | 최중량: 엔진 의존성·연결 설정 경계·낙관적 동시성 단락(P0 18 승계); api s018-4.2 CAS status와 규칙 쌍 |
| s043-9.6 | 9.6 Risky Write Consistency Block | 393–415 | 12 | table | N | Risky Write 블록·Test criteria 심사; api s060-13.3과 규칙 쌍(상호 참조 — 사본 아님) |
| s044-9.7 | 9.7 Commit 후 메시지 전달과 Outbox | 416–434 | 12 | table | N | Outbox 표 포함; #529·#626 인라인 결정 |
| s046-10.1 | 10.1 EXPLAIN ANALYZE 읽기 | 437–459 | 1 | code,table | N | ANALYZE 조건 지시 1 |
| s050-10.5 | 10.5 쿼리 최적화 일반 원칙 | 495–507 | 3 | table | N | 원칙 표 4행 중 3 계수(서브쿼리 행은 서술 — P0 승계) |
| s051-11 | 11. 운영 rollout, backfill, migration safety | 508–511 | 2 | none | N | 관할 선언 2(구현은 implementation-django로 위임) |
| s052-11.1 | 11.1 Expand / Backfill / Contract | 512–523 | 2 | table | N | 호환 시간 고려 의무 1+add/copy/switch/drop 분해 지시 1; 단계 표는 설명 |
| s053-11.2 | 11.2 Backfill 위험 | 524–533 | 5 | none | N | 위험 대응 불릿 5 |
| s054-11.3 | 11.3 Index와 constraint lock risk | 534–545 | 5 | table | N | 설계 기준 셀 5(표 행 계수) |
| s055-11.4 | 11.4 실패 대응 | 546–557 | 1 | table | N | forward-fix 검토 의무 1; 대응 기준 표 행 미계수(P0 승계) |
| s056-11.5 | 11.5 Rollout 산출물 | 558–573 | 1 | none | N | 산출물 의무 1(불릿 7은 열거) |
| s061-12.4 | 12.4 선택 가이드 | 630–642 | 4 | table | N | 선택 가이드 표 행 4 |
| s066-13.4 | 13.4 다형적 연관 (Polymorphic Associations) | 694–708 | 1 | code | N | 앱 레벨 무결성 보장 의무 1 |
| s067-13.5 | 13.5 선택 가이드 | 709–721 | 4 | table | N | 선택 가이드 표 행 4 |
