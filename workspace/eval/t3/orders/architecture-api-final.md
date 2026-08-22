# T3 발주 — architecture-api-final

- 원문: `dddjango/skills/architecture-api/references/final.md` (현재 638행 — 센서스와 일치)
- 스코프: REF 32절 · 규범 167문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/architecture-api-final.spec.json` + `workspace/eval/t3/worksheets/architecture-api-final.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s013-3.1 | 3.1 명명 규칙 | 91–100 | 5 | table | N | 명명 규칙 표 행 5 |
| s014-3.2 | 3.2 계층적 하위 리소스 | 101–110 | 2 | code | N | 슬래시 사용 1+3단계 이상 회피 1 |
| s018-4.2 | 4.2 API에서 자주 사용하는 상태 코드 | 138–169 | 16 | table | N | 상태 코드 매핑 13(표 행)+CAS 소진 status 규칙 3(db s042-9.5와 규칙 쌍) |
| s019-4.3 | 4.3 PRG (POST/Redirect/GET) 패턴 | 170–177 | 1 | none | N | PRG 보수 포함(P0 승계) |
| s020-5 | 5. 요청/응답 계약 | 178–181 | 1 | none | N | §서두 «의존 항목 명시 기록» 지시 — P0 §5 구성(9+6+1+29=45)에 미포함 추정, 애매→포함 규약 적용(+1) |
| s021-5.1 | 5.1 요청 계약 | 182–192 | 9 | none | N | 입력 상한 의무·매직넘버 위임 포함 |
| s022-5.2 | 5.2 응답 계약 | 193–201 | 6 | none | N | - |
| s023-5.3 | 5.3 계약 체크리스트 | 202–220 | 1 | table | N | 검토 의무 1; 체크리스트 «표» 8행은 확인 항목 미계수(P0 승계); «- [ ]» 운반체 아님 |
| s024-5.4 | 5.4 에러 프로필 선택 | 221–232 | 11 | none | N | 우선순위 4+wire 혼합 금지 2+신규/preserve 관할 5(P0 비고 내부 합 28 vs 절 합 29 — 관할 5로 배분해 29 유지) |
| s025 | `dddjango-code-json` (새 dddjango Ninja 범위의 기본) | 233–242 | 15 | none | N | h4: code-json 불릿 15(P0 승계) |
| s026 | framework 기본 응답과 공개 헤더의 경계 | 243–246 | 3 | none | N | h4: framework 헤더 경계 3; 전역 합성 금지 정본으로 지정 |
| s027-6 | 6. RFC 9457 에러 응답 형식 | 247–250 | 3 | none | N | 적용 범위 자기 선언 3 |
| s029-6.2 | 6.2 예시 | 263–281 | 1 | code | N | 확장 필드 무시 의무 1 |
| s030-6.3 | 6.3 핵심 규칙 | 282–291 | 3 | none | N | 핵심 규칙 3 |
| s033-7.2 | 7.2 콘텐츠 협상 (Content Negotiation) | 303–331 | 7 | table,code | Y:architecture-api-final/s026 | 406/415 매핑 2+혼동 금지 1+인용 블록 4; 전역 합성 금지 1문장 s026과 중복(부분) |
| s036-8.1 | 8.1 인증 vs 인가 | 348–361 | 3 | table | Y:architecture-api-final/s026 | challenge 의무·확립 보존+G1·합성 금지; 합성 금지 1문장 s026 중복(부분) |
| s037-8.2 | 8.2 인증 메커니즘 선택 기준 | 362–369 | 3 | table | N | 선택 기준 표 행 3 |
| s038-8.3 | 8.3 API 요청의 보안 원칙 | 370–377 | 3 | none | Y:architecture-api-final/s021-5.1 | 쿼리 파라미터 비밀 금지 1문장 s021-5.1과 중복(부분) |
| s039-8.4 | 8.4 토큰 수명과 스코프 | 378–394 | 12 | table | Y:architecture-api-final/s036-8.1 | Bearer 표 행 2 포함; challenge 규칙 재진술 1 포함(부분) |
| s042-9.2 | 9.2 선택 기준 | 407–414 | 3 | table | N | 선택 기준 표 행 3 |
| s043-9.3 | 9.3 실전 원칙 | 415–425 | 4 | none | N | 실전 원칙 4 |
| s047-10.3 | 10.3 실전 원칙 | 443–452 | 2 | none | N | «일반 패턴» 불릿은 서술 제외(P0 승계) |
| s049-11.1 | 11.1 Breaking vs Non-Breaking Change | 455–468 | 9 | table | N | Breaking 판정 표 행 9(파이프라인이 쓰는 판정 기준) |
| s050-11.2 | 11.2 Deprecation 프로세스 | 469–480 | 5 | code | N | Deprecation 프로세스 5단계 |
| s051-11.3 | 11.3 실전 원칙 | 481–488 | 3 | none | N | «추가는 자유, 제거는 금지» 포함 |
| s055-12.3 | 12.3 알고리즘 선택 기준 | 510–518 | 4 | table | N | 알고리즘 매핑 표 행 4 |
| s056-12.4 | 12.4 실전 원칙 | 519–528 | 4 | none | Y:architecture-api-final/s026 | Retry-After 보존·전역 합성 금지·controller 소유 — s026 경계와 중복(부분) |
| s059-13.2 | 13.2 Idempotency-Key 패턴 | 535–551 | 6 | code | N | 동작 방식 6(status presentation 소유 내장) |
| s060-13.3 | 13.3 계약 결정 사항 | 552–569 | 12 | table | N | 계약 결정 의무 1+표 내장 3+replay 소유권 5+fingerprint 3; db s043-9.6과 규칙 쌍(상호 참조) |
| s061-13.4 | 13.4 실전 원칙 | 570–581 | 6 | none | Y:architecture-api-final/s060-13.3 | fingerprint 충돌 처리 재진술 포함(부분); 채택=G0/G1 사용자 결정 포함 |
| s065-14.3 | 14.3 반영해야 할 계약 표면 | 596–609 | 1 | none | N | 반영 의무 1(+표면 목록 9는 열거) |
| s066-14.4 | 14.4 실전 원칙 | 610–619 | 3 | none | N | 실전 원칙 3 |
