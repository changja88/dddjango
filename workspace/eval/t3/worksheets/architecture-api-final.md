# T3 이관 검수표 — architecture-api-final

> 원문 `dddjango/skills/architecture-api/references/final.md`(638행·마커 0) · spec `workspace/eval/t3/specs/architecture-api-final.spec.json` · 검증 전용 실행 **exit 0**(`PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py … ` — `--write` 미사용).
> 규모: REF 32절 · 블록 196 · Work 167. 절 스팬 해시·연속/무손실·헤딩+블록 byte 등가는 도구가 전 절 단언(위 실행에서 통과).
> 적대 리뷰(2026-08-22) 반영본 — 처분 내역은 `workspace/eval/t3/reviews/architecture-api-final-findings.md` §처분.

## 1. census 대사

| section_key | 헤딩 | 발주서 규범 수 | spec 규범 수 | 일치 | 배분 근거 |
|---|---|---:|---:|:--:|---|
| s013-3.1 | 3.1 명명 규칙 | 5 | 5 | ○ | 명명 규칙 표 행 5 |
| s014-3.2 | 3.2 계층적 하위 리소스 | 2 | 2 | ○ | 슬래시 사용 1+3단계 이상 회피 1 |
| s018-4.2 | 4.2 API에서 자주 사용하는 상태 코드 | 16 | 16 | ○ | 상태 코드 매핑 13(표 행)+CAS 소진 status 규칙 3 |
| s019-4.3 | 4.3 PRG 패턴 | 1 | 1 | ○ | PRG 보수 포함(P0 승계) |
| s020-5 | 5. 요청/응답 계약 | 1 | 1 | ○ | §서두 «의존 항목 명시 기록» 지시(애매→포함 +1) |
| s021-5.1 | 5.1 요청 계약 | 9 | 9 | ○ | 입력 상한 의무·매직넘버 위임 포함 |
| s022-5.2 | 5.2 응답 계약 | 6 | 6 | ○ | - |
| s023-5.3 | 5.3 계약 체크리스트 | 1 | 1 | ○ | 검토 의무 1; 표 8행 미계수 |
| s024-5.4 | 5.4 에러 프로필 선택 | 11 | 11 | ○ | 우선순위 4+wire 혼합 금지 2+신규/preserve 관할 5 |
| s025 | `dddjango-code-json` (h4) | 15 | 15 | ○ | code-json 불릿 15(P0 승계) |
| s026 | framework 기본 응답과 공개 헤더의 경계 (h4) | 3 | 3 | ○ | framework 헤더 경계 3; 전역 합성 금지 정본 |
| s027-6 | 6. RFC 9457 에러 응답 형식 | 3 | 3 | ○ | 적용 범위 자기 선언 3 |
| s029-6.2 | 6.2 예시 | 1 | 1 | ○ | 확장 필드 무시 의무 1 |
| s030-6.3 | 6.3 핵심 규칙 | 3 | 3 | ○ | 핵심 규칙 3 |
| s033-7.2 | 7.2 콘텐츠 협상 | 7 | 7 | ○ | 406/415 매핑 2+혼동 금지 1+인용 블록 4 |
| s036-8.1 | 8.1 인증 vs 인가 | 3 | 3 | ○ | challenge 의무·확립 보존+G1·합성 금지 |
| s037-8.2 | 8.2 인증 메커니즘 선택 기준 | 3 | 3 | ○ | 선택 기준 표 행 3 |
| s038-8.3 | 8.3 API 요청의 보안 원칙 | 3 | 3 | ○ | 쿼리 파라미터 비밀 금지 등 3 |
| s039-8.4 | 8.4 토큰 수명과 스코프 | 12 | 12 | ○ | Bearer 표 행 2 포함·challenge 재진술 1 포함 |
| s042-9.2 | 9.2 선택 기준 | 3 | 3 | ○ | 선택 기준 표 행 3 |
| s043-9.3 | 9.3 실전 원칙 | 4 | 4 | ○ | 실전 원칙 4 |
| s047-10.3 | 10.3 실전 원칙 | 2 | 2 | ○ | «일반 패턴» 불릿 서술 제외 |
| s049-11.1 | 11.1 Breaking vs Non-Breaking | 9 | 9 | ○ | Breaking 판정 표 행 9 |
| s050-11.2 | 11.2 Deprecation 프로세스 | 5 | 5 | ○ | Deprecation 5단계 |
| s051-11.3 | 11.3 실전 원칙 | 3 | 3 | ○ | «추가는 자유, 제거는 금지» 포함 |
| s055-12.3 | 12.3 알고리즘 선택 기준 | 4 | 4 | ○ | 알고리즘 매핑 표 행 4 |
| s056-12.4 | 12.4 실전 원칙 | 4 | 4 | ○ | Retry-After 보존·전역 합성 금지·controller 소유 |
| s059-13.2 | 13.2 Idempotency-Key 패턴 | 6 | 6 | ○ | 동작 방식 6(status 소유 내장) |
| s060-13.3 | 13.3 계약 결정 사항 | 12 | 12 | ○ | 계약 결정 1+표 내장 3+replay 5+fingerprint 3 |
| s061-13.4 | 13.4 실전 원칙 | 6 | 6 | ○ | fingerprint 재진술·채택 G0/G1 포함 |
| s065-14.3 | 14.3 반영해야 할 계약 표면 | 1 | 1 | ○ | 반영 의무 1(+표면 목록 9 열거) |
| s066-14.4 | 14.4 실전 원칙 | 3 | 3 | ○ | 실전 원칙 3 |
| **합계** | — | **167** | **167** | **○** | 발주서 스코프(REF 32절·167문장)와 전 절 일치 |

**불일치 절: 없음(32/32).** 다만 발주서 비고의 *내부 배분*과 내 문장 단위 배분이 갈린 절이 셋이라 판정을 남긴다 — 셋 다 절 합계는 불변이므로 «과소/과대 산정»이 아니라 배분 문제다.

- **s024-5.4(11)** — 발주서가 이미 «P0 비고 내부 합 28 vs 절 합 29»를 관할 문단 5로 배분해 해소한 상태다. 내 배분도 4(우선순위 서두 1+①②③ 3)+2(혼합 금지 문단)+5(관할 문단: 관할 배제·이전 근거 불인정·표준 레시피 구현·G1 표면화·주어 해석) = 11로 같다. **발주서 배분이 옳다**(문단 내 문장 수가 5로 실측된다).
- **s056-12.4(4)** — 발주서 비고는 세 항목(Retry-After 보존·전역 합성 금지·controller 소유)만 열거하지만 절 합은 4다. 실측 문장은 521(1)+522(2: «보존» / «전역 합성 금지+controller 한정 소유» 한 문장)+523(1)=4 — **절 합 4가 옳고**, 비고의 3항목은 522 두 규범의 내용 열거다.
- **s018-4.2 재진술 열(발주서 `N`)** — 발주서·census 는 이 절의 재진술을 `N`으로 뒀으나, 168행 «`Retry-After`를 공개하는 경우 **§5.4의 경계에 따라** controller가 그 헤더를 소유한다»는 §5.4 를 문면으로 지목하는 s026 b1 W3 의 같은-문서 부분 재진술이다(병렬 사례 s056-12.4 b2 와 동형). **census 열이 과소**이고 spec `restates`(b20→s026/b1)가 옳다 — 규범 수 16 은 불변이라 계수 대사에는 영향이 없다.
- **s060-13.3(12)** — 「표 내장 3」의 지목이 비어 있어 직접 판정했다. 의무 동사를 가진 행 셋(Replay «재현하고 매핑» · Conflict «충돌로 응답» · Storage «DB 설계로 연결»)만 계수하고, 나머지 넷(적용 여부·Key scope·Retention·Concurrency)은 «…인지»로 끝나는 *결정 항목*이라 미계수 — **3이 옳다**(합 1+3+5+3=12 성립).

## 2. 배선 근거 표 (전 규범 167)

`E` = enforcedBy(검사기) · `D` = delegatedTo(에이전트). 기본값 표: architecture-api → `agent-design-review-api`.

### s013-3.1 — 3.1 명명 규칙 (5)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b2 | 95–95 | 1 | 리소스 경로의 명사 사용(동사 금지) | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ② check-naming.py docstring 은 저장소 파이썬 경로·심볼 이름 축(#28·#30·#33·#41)이라 REST URL 명명 비커버 ③④ 지목 없음 — 위임 기본값(architecture-api→design-review-api) |
| b3 | 96–96 | 1 | 컬렉션 리소스의 복수 명사 | Obligation | D: agent-design-review-api | 동상 |
| b4 | 97–97 | 1 | 케밥 케이스·소문자 경로 | Obligation | D: agent-design-review-api | 동상 |
| b5 | 98–98 | 1 | 후행 슬래시 금지 | Prohibition | D: agent-design-review-api | 동상 — 금지 형식 문면 |
| b6 | 99–100 | 1 | DB 구조의 URL 반영 금지 | Prohibition | D: agent-design-review-api | 동상 — 금지 형식 문면 |

### s014-3.2 — 3.2 계층적 하위 리소스 (2)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 102–104 | 1 | 부모-자식 관계의 슬래시 표현 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ② check-naming.py docstring 은 저장소 파이썬 경로·심볼 이름 축(#28·#30·#33·#41)이라 REST URL 명명 비커버 ③④ 지목 없음 — 위임 기본값(architecture-api→design-review-api) |
| b1 | 102–104 | 2 | 3단계 이상 깊이 회피 | Prohibition | D: agent-design-review-api | 동상 — «피한다» 회피 문면(강조 표기) |

### s018-4.2 — 4.2 API에서 자주 사용하는 상태 코드 (16)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b3 | 144–144 | 1 | 200 OK 매핑(GET·PUT·PATCH 성공) | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ② status 의미론을 보는 검사기 없음(check-transient-overmapping.py 는 transient 인프라 예외의 무분기 retryable 과잉매핑 차단이라 역방향) ③④ 지목 없음 — 위임 기본값 |
| b4 | 145–145 | 1 | 201 Created 매핑(POST 생성·Location 헤더) | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ② status 의미론을 보는 검사기 없음(check-transient-overmapping.py 는 transient 인프라 예외의 무분기 retryable 과잉매핑 차단이라 역방향) ③④ 지목 없음 — 위임 기본값 |
| b5 | 146–146 | 1 | 202 Accepted 매핑(비동기 접수) | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ② status 의미론을 보는 검사기 없음(check-transient-overmapping.py 는 transient 인프라 예외의 무분기 retryable 과잉매핑 차단이라 역방향) ③④ 지목 없음 — 위임 기본값 |
| b6 | 147–148 | 1 | 204 No Content 매핑(DELETE 성공·무본문) | Obligation | D: agent-design-review-api | 동상 |
| b9 | 153–153 | 1 | 400 Bad Request 매핑(형식 오류·유효성 실패) | Obligation | D: agent-design-review-api | 동상 |
| b10 | 154–154 | 1 | 401 Unauthorized 매핑(인증 필요) | Obligation | D: agent-design-review-api | 동상 |
| b11 | 155–155 | 1 | 403 Forbidden 매핑(인가 부족) | Obligation | D: agent-design-review-api | 동상 |
| b12 | 156–156 | 1 | 404 Not Found 매핑(자원 없음·존재 은닉) | Obligation | D: agent-design-review-api | 동상 |
| b13 | 157–157 | 1 | 409 Conflict 매핑(자원 충돌) | Obligation | D: agent-design-review-api | 동상 |
| b14 | 158–158 | 1 | 422 Unprocessable Entity 매핑(의미적 처리 불가) | Obligation | D: agent-design-review-api | 동상 |
| b15 | 159–160 | 1 | 429 Too Many Requests 매핑(Rate Limit 초과) | Obligation | D: agent-design-review-api | 동상 |
| b18 | 165–165 | 1 | 500 Internal Server Error 매핑(애매하면 500) | Obligation | D: agent-design-review-api | 동상 |
| b19 | 166–167 | 1 | 503 Service Unavailable 매핑(과부하·정비·Retry-After 가능) | Obligation | D: agent-design-review-api | 동상 |
| b20 | 168–169 | 1 | CAS 재시도 소진의 retryable status 배정(표 누락 금지) | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ② status 의미론을 보는 검사기 없음(check-transient-overmapping.py 는 transient 인프라 예외의 무분기 retryable 과잉매핑 차단이라 역방향) ③④ 지목 없음 — 위임 기본값 |
| b20 | 168–169 | 2 | Retry-After 공개 시 controller 소유 | Obligation | E: check-api-error-controller-contract.py | ② docstring «Enforce direct controller-owned code-profile error mapping» + §16 매핑 표 «controller checker» ④ T1 파일럿 ninja §6.1 «retryable BC 503의 Retry-After 컨트롤러 설정»과 동일 축 |
| b20 | 168–169 | 3 | 503/409 선택의 설계자 임의 확정 금지 | Prohibition | D: command-dddjango·agent-design-review-api | ① 문면이 «§5/G1»(게이트 절차)을 선택 소유로 지목 — 기본값 이탈 근거(파일럿 «503/409 선택의 명세 §5/G1 소유» 선례) · 표 누락 판정은 API 설계 리뷰 병기 |

### s019-4.3 — 4.3 PRG 패턴 (1)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 171–173 | 1 | PRG로 새로고침 중복 제출 방지 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) [P0 승계 — 보수 포함] |

### s020-5 — 5. 요청/응답 계약 (1)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 179–181 | 1 | 클라이언트 의존 항목의 명시 기록 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) [애매→포함 규약 적용] |

### s021-5.1 — 5.1 요청 계약 (9)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 183–184 | 1 | 필수 필드·선택 필드 구분 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b2 | 185–185 | 1 | 필드 타입·형식·단위·허용 범위·기본값 명시 | Obligation | D: agent-design-review-api | 동상 |
| b3 | 186–186 | 1 | 수치·외부 식별자 입력의 도메인/스토리지 상한 포함 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ② 입력 상한 부재로 인한 5xx 오분류를 보는 검사기 없음 — 위임 기본값 |
| b3 | 186–186 | 2 | 계약 계층의 구체 경계값(매직넘버) 고정 금지 | Prohibition | D: agent-design-review-api | ① 문면이 «implementation에 위임»을 지목 — 값 결정은 구현 계층이나 계약 계층의 금지 판정 자체는 API 설계 리뷰 |
| b4 | 187–187 | 1 | query parameter의 조회 표현 조정 용도 한정 | Obligation | D: agent-design-review-api | 동상 — 위임 기본값 |
| b5 | 188–188 | 1 | 비밀 값·인증 정보의 query parameter 금지 | Prohibition | D: agent-design-review-api | ① 문면 역할명 없음 ② URL 로그 노출을 보는 검사기 없음 — 위임 기본값(§8.3 b1 부분 재진술의 정본) |
| b6 | 189–189 | 1 | POST 본문 정의와 duplicate-sensitive 요청의 Idempotency-Key 정책 확정 | Obligation | D: agent-design-review-api | ② check-idempotency-scope-creep.py 는 «미요청 채택 금지»(G0) 축이라 «정책을 정한다» 의무 비커버 — 위임 기본값 |
| b7 | 190–190 | 1 | PUT 전체 교체의 누락 필드 처리 명시 | Obligation | D: agent-design-review-api | 동상 — 위임 기본값 |
| b8 | 191–192 | 1 | PATCH 문서 형식·멱등 여부 개별 판단 | Obligation | D: agent-design-review-api | 동상 — 위임 기본값 |

### s022-5.2 — 5.2 응답 계약 (6)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 194–195 | 1 | 상태 코드별 본문 존재 여부·schema 분리 정의 | Obligation | E: check-response-schema-bypass.py<br>D: agent-design-review-api | ② docstring «Block direct raw 200-203 returns that bypass a declared Ninja schema» — 선언 schema 경유의 **부분 백스톱**(선언된 schema 우회만 차단하고 «정의» 존재는 검사하지 않는다 — 정의 의무 자체의 소유는 위임)(파일럿 §6.3 b35 «선언 JSON 성공의 Ninja validation 경유» 선례) ④ 계약 «정의» 판정은 API 설계 리뷰 병기 |
| b2 | 196–196 | 1 | 201 Created의 Location 헤더 제공 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b3 | 197–197 | 1 | 202 Accepted의 접수 응답·결과 확인 방법 제공 | Obligation | D: agent-design-review-api | 동상 |
| b4 | 198–198 | 1 | 204 No Content의 무본문 계약화 | Obligation | D: agent-design-review-api | 동상 |
| b5 | 199–199 | 1 | 오류 응답의 media type·필드·status별 schema 문서화 | Obligation | E: check-openapi-error-declaration.py<br>D: agent-design-review-api | ② docstring «openapi_extra.responses 전수 검사 · response={status: <Bc>ErrorSchema} 선언 일치 검증» — 오류 응답 선언 축 집행(파일럿 b34 선례) ④ 프로필·media type 판정은 API 설계 리뷰 병기 |
| b6 | 200–201 | 1 | 클라이언트 동작 변경 헤더의 응답 계약 포함 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |

### s023-5.3 — 5.3 계약 체크리스트 (1)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 203–205 | 1 | 엔드포인트 설계·변경 시 계약 체크리스트 병행 검토 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |

### s024-5.4 — 5.4 에러 프로필 선택 (11)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 222–224 | 1 | 에러 wire contract의 우선순위 단일 선택 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ④ 파일럿 ninja §6.2 b1 «오류 프로필 선택의 architecture-api §5.4 위임»의 정본 — 프로필 선택은 API 계약 설계 판정 |
| b2 | 225–225 | 1 | ① 배포된 에러 계약·공개 헤더 보존 | Obligation | D: agent-design-review-api | 동상 · ② check-error-centralization.py docstring «preserve-established 는 schema semantics 미적용» — 보존 판정은 검사기 밖(파일럿 L-F 정정과 같은 근거) |
| b3 | 226–226 | 1 | ② 신규 dddjango Ninja 범위의 기본 dddjango-code-json 선택 | Obligation | D: agent-design-review-api | 동상 |
| b4 | 227–228 | 1 | ③ RFC 9457의 조건부 선택 한정 | Exception | D: agent-design-review-api | 동상 [L-E 유형: «…있을 때만» 조건 한정] |
| b5 | 229–230 | 1 | 한 API 범위의 RFC·code wire 필드 혼합 금지 | Prohibition | E: check-error-centralization.py | ① 문면 역할명 없음(«wire 필드»는 대상 어휘일 뿐 역할명 아님) ② §16 매핑 표 «schema checker»=check-error-centralization.py · docstring 의 canonical schema shape 검증 축 ④ 파일럿 b14 «타 profile 필드 혼합 금지» 선례 |
| b5 | 229–230 | 2 | code 프로필의 type·about:blank·URI 요구·problem+json 삽입 금지 | Prohibition | E: check-error-centralization.py | 동상 — 같은 검사 축 |
| b6 | 231–232 | 1 | wire 계약 한정 — preserve-established 범위의 관할 배제 | Exception | D: agent-design-review-api | ① 문면이 주어를 «신규 범위»로 한정 ② docstring 의 profile-gate(preserve 는 schema semantics 미적용)와 정합 — 관할 판정은 API 설계 리뷰 |
| b6 | 231–232 | 2 | 확립 native 구현·배선의 표준 레시피 이전 근거 불인정 | Prohibition | D: agent-design-review-api | 동상 |
| b6 | 231–232 | 3 | 신규 RFC wire 범위의 표준 controller 레시피 구현 | Obligation | E: check-api-error-controller-contract.py | ① 문면 «표준 controller 레시피(controller 소유·좁은 try·bc_error_schema.py·직접 Status 반환)» ② controller checker docstring 집행 축 |
| b6 | 231–232 | 4 | G2·12-slot 미열거 조합의 G1 표면화(STOP) | Obligation | D: command-dddjango | ① 문면이 G1·G2·12-slot·STOP 절차를 지목 — 절차 소유 Coordinator(기본값 이탈 근거·파일럿 선례) |
| b6 | 231–232 | 5 | 혼합 금지의 주어는 wire 필드 — 구현 레시피의 프로필 편입 금지 | Prohibition | D: agent-design-review-api | ① 문면 해석 규칙 — 판정은 API 설계 리뷰 |

### s025 — `dddjango-code-json` (h4) (15)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 234–235 | 1 | code 프로필 media type = application/json | Obligation | D: agent-design-review-api | ② check-error-centralization.py docstring 은 schema 모듈·wire-code 축이라 media type 비커버 — 위임 기본값 |
| b2 | 236–236 | 1 | 플러그인 지정 body property 목록 부재(기본 목록 가정 금지) | Prohibition | D: agent-design-review-api | ④ 파일럿 §6.2 b2 «플러그인 공통 body property 부재» 선례 — 검사기는 자기 입력(inventory)을 전제하므로 순환 배선 해소, 판정은 위임 |
| b2 | 236–236 | 2 | 기존 범위 관찰 shape 보존·신규 범위 표면의 분리 명시 승인 | Obligation | D: agent-design-review-api·command-dddjango | ② docstring «preserve-established … do not apply schema semantics» — 보존 판정은 API 설계 리뷰 ① 문면 «일반 G1 승인과 분리해 명시 승인» — 승인 절차는 Coordinator 병기 |
| b3 | 237–237 | 1 | 기준선 shape 변경의 별도 public contract 변경 취급 | Obligation | D: command-dddjango | ④ 파일럿 §6.2 b2 «기준선 property 변경은 별도 contract 변경»→Coordinator 선례 · 승인 등급 판정은 절차 소유 |
| b3 | 237–237 | 2 | 호환성 영향·전환 범위 제시 후 명시적 사용자 승인 | Obligation | D: command-dddjango | 동상 — 승인 절차 소유 |
| b4 | 238–238 | 1 | 공통 필드의 BC ErrorCode(StrEnum) 좁힘과 안정적 공개 식별자 | Obligation | E: check-error-centralization.py | ② docstring «wire-code uniqueness, and narrow direct raw-string discriminator forms» ④ 파일럿 b9 «<Bc>ErrorCode(StrEnum) 정확히 하나» 선례 |
| b4 | 238–238 | 2 | 식별자 필드명 미고정 | Permission | D: agent-design-review-api | ① 문면이 필드명 고정을 명시 거부 — 형태 판정은 API 설계 리뷰(검사기는 이름을 세지 않음) |
| b4 | 238–238 | 3 | 공개 구별 가능 실패 한정 값 부여·내부 예외 합류 허용 | Obligation | D: agent-design-review-api | ② 공개 구별 가능성은 정적 검사 밖(파일럿의 표명 판정 처리와 동형) — 위임 기본값 |
| b5 | 239–239 | 1 | HTTP status 계약의 body property 존재 요구·가정 금지 | Prohibition | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b5 | 239–239 | 2 | status field 존재 시 실제 status 일치·부재 시 controller literal/status 소유 | Obligation | E: check-api-error-controller-contract.py | ① 문면 «controller의 literal/status 상수가 계약을 소유» ② controller checker docstring(파일럿 b17 «status 표현의 허용 형태(literal·상수)» 선례) |
| b5 | 239–239 | 3 | 공개 문자열의 str(exc) 자동 사용·민감 내부 정보 누설 금지 | Prohibition | D: agent-design-review-api | ② 민감 정보 판정은 정적 검사 밖(파일럿의 표명·의미 판정 처리와 동형) — 위임 기본값 |
| b6 | 240–240 | 1 | 배포된 public 식별자 변경의 breaking change 취급 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) · §11.1 판정 표와 같은 축 |
| b6 | 240–240 | 2 | 클라이언트 Enum 하나 = 계약 하나 소비 | Obligation | D: agent-design-review-api | 동상 |
| b6 | 240–240 | 3 | 12-slot rollout의 동시 전환·version split 기록 | Obligation | D: command-dddjango | ① 문면이 12-slot(오류 계약 기록표) 절차를 지목 — 절차 소유 Coordinator(파일럿 b25 «12-slot이 결정» 선례) |
| b7 | 241–242 | 1 | framework 기본 응답의 code 계약 body 배제·공개 계약 주장 금지 | Prohibition | E: check-api-error-controller-contract.py<br>D: agent-design-review-api | ② controller checker docstring 의 framework-owned 경계(파일럿 b30 «framework 오류 framework 소유»·«framework body의 wire contract 주장 금지» 두 축) — 주장 표명 판정은 API 설계 리뷰 병기 |

### s026 — framework 기본 응답과 공개 헤더의 경계 (h4) (3)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 244–246 | 1 | framework 기본 응답의 전역 handler·helper 변환과 헤더 합성 금지 | Prohibition | E: check-api-error-controller-contract.py | ② docstring «Enforce direct controller-owned code-profile error mapping» — 중앙 handler 소유 차단이 검사기 계약 그 자체 [파일럿 L-F: exception_handler·catch-all 금지는 controller-contract 실재 · ninja-boundary 는 settings.MIDDLEWARE 한정이라 비대상] |
| b1 | 244–246 | 2 | 확립 계약의 WWW-Authenticate·Retry-After 헤더 보존과 별도 설계 | Obligation | D: agent-design-review-api | ② preserve-established 는 schema semantics 미적용(docstring) — 보존 판정은 API 설계 리뷰 |
| b1 | 244–246 | 3 | controller 직접 공개 retryable BC 오류의 Retry-After controller 소유 | Obligation | E: check-api-error-controller-contract.py | ② controller checker docstring ④ 파일럿 §6.1 b15 «retryable BC 503의 Retry-After 컨트롤러 설정»과 동일 축 |

### s027-6 — 6. RFC 9457 에러 응답 형식 (3)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 248–250 | 1 | RFC 9457 절의 적용 범위 자기 한정(§5.4 선택 범위) | Exception | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) [L-E 유형: «…범위에만» 한정] |
| b1 | 248–250 | 2 | dddjango-code-json 범위 미적용 | Prohibition | D: agent-design-review-api | 동상 |
| b1 | 248–250 | 3 | 신규 RFC 범위 구현 형태의 §5.4 단서 준수 | Obligation | E: check-api-error-controller-contract.py<br>D: agent-design-review-api | ① 문면이 §5.4 마지막 문단(표준 controller 레시피)을 지목 ② controller checker docstring — s024-5.4 b6 n3 과 같은 축 |

### s029-6.2 — 6.2 예시 (1)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b2 | 280–281 | 1 | 미인식 확장 필드의 클라이언트 무시 의무 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |

### s030-6.3 — 6.3 핵심 규칙 (3)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 283–284 | 1 | type의 안정적 문서화 URI | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b2 | 285–285 | 1 | title=유형 재사용·detail=특정 발생 분리 | Obligation | D: agent-design-review-api | 동상 |
| b3 | 286–287 | 1 | RFC 프로필 범위 공개 에러 응답의 일관 적용 | Obligation | D: agent-design-review-api | 동상 |

### s033-7.2 — 7.2 콘텐츠 협상 (7)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b11 | 325–325 | 1 | 406 Not Acceptable 매핑(응답 표현 협상 실패) | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ② status 의미론을 보는 검사기 없음(check-transient-overmapping.py 는 transient 인프라 예외의 무분기 retryable 과잉매핑 차단이라 역방향) ③④ 지목 없음 — 위임 기본값 |
| b12 | 326–327 | 1 | 415 Unsupported Media Type 매핑(요청 페이로드 거절) | Obligation | D: agent-design-review-api | 동상 |
| b13 | 328–329 | 1 | 406/415 혼동 금지(응답 협상 vs 요청 페이로드) | Prohibition | D: agent-design-review-api | 동상 — 금지 문면 |
| b14 | 330–331 | 1 | 406/415 계약의 별도 승인 범위 한정 | Exception | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) [L-E 유형: «별도 승인된 범위에서만» 한정] |
| b14 | 330–331 | 2 | 검증된 Ninja-owned pre-body 경계의 framework HttpError 흐름 사용 | Obligation | E: check-ninja-boundary-middleware.py | ② docstring 대표 회귀 = «406/415 콘텐츠 협상을 request.path 하드코딩한 전역 미들웨어로 자작» · «django-ninja 는 협상/임의 status 를 경계 안에서 네이티브로 낸다(§6.3)» ④ 파일럿 §6.1 b16 «406/415의 ninja 경계 내 처리» 선례 |
| b14 | 330–331 | 3 | parser 예외 정규화 차이의 실제 415 응답 확인 | Obligation | D: agent-design-review-api | ② 실제 응답 status 확인은 정적 검사 밖(mounted client 계약 검증은 implementation-test 소관) — 위임 기본값 |
| b14 | 330–331 | 4 | 전역 middleware·helper·handler의 status·body 합성 금지 | Prohibition | E: check-ninja-boundary-middleware.py·check-api-error-controller-contract.py | ① 문면이 middleware 와 handler 두 경로를 병기 ② MIDDLEWARE 자가등록은 ninja-boundary docstring, 전역 handler/helper 는 controller-contract docstring ④ 파일럿 b17 «두 경로 병기» 선례 — s026 b1 정본의 부분 재진술 |

### s036-8.1 — 8.1 인증 vs 인가 (3)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b8 | 359–359 | 1 | 401 생성 시 적용 가능한 WWW-Authenticate challenge 필수(RFC 9110) | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ② HTTP challenge 발행을 보는 검사기 없음 — 위임 기본값 |
| b9 | 360–361 | 1 | 확립·공개 요구 계약의 challenge 보존과 G1 별도 설계 복귀 | Obligation | D: agent-design-review-api·command-dddjango | ① 문면이 G1(설계 승인 게이트)을 지목 — 절차 소유 Coordinator 병기 · 보존 판정은 API 설계 리뷰 |
| b9 | 360–361 | 2 | code-profile body 강제용 전역 handler·helper challenge 합성 금지 | Prohibition | E: check-api-error-controller-contract.py | ② controller checker docstring(중앙 handler 소유 차단) — s026 b1 정본의 부분 재진술 |

### s037-8.2 — 8.2 인증 메커니즘 선택 기준 (3)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b2 | 366–366 | 1 | API Key의 서버 간·내부 API 적합 | Permission | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) [선택지 매핑 표 = 조건부 허용(L-E «선택 적용=허용» 유형)] |
| b3 | 367–367 | 1 | OAuth 2.0의 서드파티 권한 위임 적합 | Permission | D: agent-design-review-api | 동상 |
| b4 | 368–369 | 1 | JWT(Bearer Token)의 무상태·마이크로서비스 적합 | Permission | D: agent-design-review-api | 동상 |

### s038-8.3 — 8.3 API 요청의 보안 원칙 (3)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 371–372 | 1 | 비밀 정보의 쿼리 파라미터 금지 | Prohibition | D: agent-design-review-api | ① 문면 역할명 없음 ② 검사기 없음 — 위임 기본값 · s021-5.1 b5 정본의 부분 재진술 |
| b2 | 373–373 | 1 | 인증 정보의 Authorization 헤더 전달 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b3 | 374–375 | 1 | 전 API 통신의 HTTPS 사용 | Obligation | D: agent-design-review-api | 동상 |

### s039-8.4 — 8.4 토큰 수명과 스코프 (12)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 379–381 | 1 | Bearer 토큰 만료·권한 범위의 계약 명시 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b1 | 379–381 | 2 | 401 생성 Bearer 서버의 §8.1 challenge 규칙 준수 | Obligation | D: agent-design-review-api | 동상 — §8.1 규칙의 적용 선언 |
| b3 | 384–384 | 1 | invalid_token의 401 + Bearer error challenge 매핑 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ② status 의미론을 보는 검사기 없음(check-transient-overmapping.py 는 transient 인프라 예외의 무분기 retryable 과잉매핑 차단이라 역방향) ③④ 지목 없음 — 위임 기본값 |
| b4 | 385–386 | 1 | insufficient_scope의 403 + scope 안내 매핑 | Obligation | D: agent-design-review-api | 동상 |
| b5 | 387–387 | 1 | 토큰 만료의 401 인증 실패 귀속 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b5 | 387–387 | 2 | 401 생성 시 challenge의 인증 방법·오류 원인 안내 | Obligation | D: agent-design-review-api | 동상 — §8.1 challenge 의무의 Bearer 재진술 |
| b5 | 387–387 | 3 | 확립 Bearer challenge 보존과 기본 401 차이의 G1 별도 설계 | Obligation | D: agent-design-review-api·command-dddjango | ① 문면이 G1 을 지목 — 절차 소유 Coordinator 병기 · 보존 판정은 API 설계 리뷰 |
| b5 | 387–387 | 4 | 프레임워크 기본 401의 전역 handler·helper 헤더 합성 금지 | Prohibition | E: check-api-error-controller-contract.py | ② controller checker docstring(중앙 handler 소유 차단) — s036-8.1 b9·s026 b1 과 같은 축 |
| b6 | 388–388 | 1 | scope의 허용 작업 범위 정의 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b6 | 388–388 | 2 | scope 부족 시 403+insufficient_scope 응답과 필요 scope 안내 | Obligation | D: agent-design-review-api | 동상 |
| b7 | 389–390 | 1 | 토큰 수명·refresh 흐름·scope 집합의 API 계약 고정 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b7 | 389–390 | 2 | 토큰 검증·발급 구현의 인증 라이브러리·프레임워크 귀속 | Obligation | D: agent-design-review-api | 동상 — 소유 경계 선언 |

### s042-9.2 — 9.2 선택 기준 (3)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b2 | 411–411 | 1 | 소규모·관리자 대시보드의 Offset 권장 | Permission | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) [«권장» 열 = 선택지 매핑 → 조건부 허용] |
| b3 | 412–412 | 1 | 실시간 피드·무한 스크롤·대용량의 Cursor 권장 | Permission | D: agent-design-review-api | 동상 |
| b4 | 413–414 | 1 | 고성능 읽기 중심 API의 Keyset 권장 | Permission | D: agent-design-review-api | 동상 |

### s043-9.3 — 9.3 실전 원칙 (4)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 416–417 | 1 | 커서는 인덱싱·불변·유니크 필드 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b2 | 418–418 | 1 | 커서의 불투명 인코딩(base64) | Obligation | D: agent-design-review-api | 동상 |
| b3 | 419–419 | 1 | 페이지당 100–200개 결과 권장 | Obligation | D: agent-design-review-api | 동상 [단일 권장값 = 준수 대상 기본값] |
| b4 | 420–421 | 1 | 응답의 has_more·next_cursor 포함 | Obligation | D: agent-design-review-api | 동상 |

### s047-10.3 — 10.3 실전 원칙 (2)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 444–445 | 1 | 단일 버전 전략의 일관 적용 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b3 | 447–448 | 1 | 버전 관리 방식 문서화와 마이그레이션 경로 제공 | Obligation | D: agent-design-review-api | 동상 |

### s049-11.1 — 11.1 Breaking vs Non-Breaking (9)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b2 | 459–459 | 1 | 응답 필드 추가의 non-breaking 판정 | Permission | D: agent-design-review-api | ① 문면 역할명 없음 ② breaking 판정을 계산하는 검사기 없음 ④ §11.3 «추가는 자유»와 같은 축 — 위임 기본값 |
| b3 | 460–460 | 1 | 선택 요청 파라미터 추가의 non-breaking 판정 | Permission | D: agent-design-review-api | 동상 |
| b4 | 461–461 | 1 | 필드 제거의 breaking 판정 | Obligation | D: agent-design-review-api | 동상 — breaking 판정 의무 |
| b5 | 462–462 | 1 | 필드 이름 변경의 breaking 판정 | Obligation | D: agent-design-review-api | 동상 — breaking 판정 의무 |
| b6 | 463–463 | 1 | 필드 타입 변경의 breaking 판정 | Obligation | D: agent-design-review-api | 동상 — breaking 판정 의무 |
| b7 | 464–464 | 1 | 필수 파라미터 추가의 breaking 판정 | Obligation | D: agent-design-review-api | 동상 — breaking 판정 의무 |
| b8 | 465–465 | 1 | URL 경로 변경의 breaking 판정 | Obligation | D: agent-design-review-api | 동상 — breaking 판정 의무 |
| b9 | 466–466 | 1 | 상태 코드 변경의 breaking 판정 | Obligation | D: agent-design-review-api | 동상 — breaking 판정 의무 |
| b10 | 467–468 | 1 | 에러 형식 변경의 breaking 판정 | Obligation | D: agent-design-review-api | 동상 |

### s050-11.2 — 11.2 Deprecation 프로세스 (5)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 470–471 | 1 | ① Deprecation 공지의 문서·변경 이력 기록 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b2 | 472–472 | 1 | ② Sunset 헤더의 만료 날짜 응답 포함 | Obligation | D: agent-design-review-api | 동상 |
| b4 | 477–477 | 1 | ③ 최소 6개월~1년 마이그레이션 기간 유지 | Obligation | D: agent-design-review-api | 동상 |
| b5 | 478–478 | 1 | ④ 대체 API·마이그레이션 가이드 제공 | Obligation | D: agent-design-review-api | 동상 |
| b6 | 479–480 | 1 | ⑤ 마이그레이션 기간 종료 후 제거 | Obligation | D: agent-design-review-api | 동상 |

### s051-11.3 — 11.3 실전 원칙 (3)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 482–483 | 1 | 추가는 자유·제거 금지(Additive changes only) | Prohibition | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b2 | 484–484 | 1 | breaking change 필요 시 새 버전 생성 | Obligation | D: agent-design-review-api | 동상 |
| b3 | 485–486 | 1 | 미인식 필드 무시 설계(Robustness Principle) | Obligation | D: agent-design-review-api | 동상 |

### s055-12.3 — 12.3 알고리즘 선택 기준 (4)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b2 | 514–514 | 1 | Token Bucket의 퍼블릭 API 기본 적합 | Permission | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) [«적합» 열 = 선택지 매핑 → 조건부 허용] |
| b3 | 515–515 | 1 | Sliding Window의 정확한 제어 적합 | Permission | D: agent-design-review-api | 동상 |
| b4 | 516–516 | 1 | Fixed Window의 간단한 내부 API 적합 | Permission | D: agent-design-review-api | 동상 |
| b5 | 517–518 | 1 | Leaky Bucket의 트래픽 셰이핑 적합 | Permission | D: agent-design-review-api | 동상 |

### s056-12.4 — 12.4 실전 원칙 (4)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 520–521 | 1 | 비용 큰 작업 전 rate limit 검사 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b2 | 522–522 | 1 | 확립 429 계약의 Retry-After 헤더 보존 | Obligation | D: agent-design-review-api | ② preserve-established 는 schema semantics 미적용(docstring) — 보존 판정은 API 설계 리뷰 |
| b2 | 522–522 | 2 | 기본 429의 전역 헤더 합성 금지와 controller 직접 공개 오류 한정 소유 | Prohibition | E: check-api-error-controller-contract.py | ② controller checker docstring(중앙 handler 소유 차단·controller 소유 헤더) ④ 파일럿 §6.1 b15 동일 축 — s026 b1 정본의 부분 재진술 |
| b3 | 523–524 | 1 | rate limit 정책의 API 문서 기재 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |

### s059-13.2 — 13.2 Idempotency-Key 패턴 (6)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b3 | 546–546 | 1 | ① 클라이언트의 고유 키 생성(V4 UUID 권장) | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b4 | 547–547 | 1 | ② 첫 요청 도메인 outcome의 응용 계층 트랜잭션 저장 | Obligation | D: agent-design-review-api | ② check-transaction-boundary.py 는 «한 트랜잭션 = 애그리거트 하나»·UoW 축이라 멱등 outcome 저장 비커버 — 위임 기본값(db §9.6 과 상호 참조) |
| b4 | 547–547 | 2 | ② HTTP status·응답 표현의 presentation 소유(application·domain의 status 생성 금지) | Obligation | E: check-api-error-controller-contract.py | ① 문면 «presentation이 소유» ② controller checker docstring — §13.3 b10 과 같은 축 |
| b5 | 548–548 | 1 | ③ 동일 키 후속 요청의 저장 결과 반환 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b6 | 549–549 | 1 | ④ 키의 24시간 만료(일반 정책) | Obligation | D: agent-design-review-api | 동상 |
| b7 | 550–551 | 1 | ⑤ POST 한정 적용(GET·PUT·DELETE 제외) | Exception | D: agent-design-review-api | 동상 [L-E 유형: 적용 범위 한정] |

### s060-13.3 — 13.3 계약 결정 사항 (12)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 553–555 | 1 | Idempotency-Key 수용 엔드포인트의 계약 결정 의무 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b5 | 560–560 | 1 | Replay — 최초 operation outcome 재현과 프로필 대응 HTTP 응답 매핑 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b6 | 561–561 | 1 | Conflict — 다른 request content의 충돌 응답(신규 작업 처리 금지) | Obligation | D: agent-design-review-api | 동상 |
| b9 | 564–565 | 1 | Storage — 내구성 저장소·transaction/lock 정책의 DB 설계 연결 | Obligation | D: agent-design-review-db·agent-design-review-api | ① 문면이 «DB 설계로 연결»을 명시 지목 — 문서군 기본값(design-review-api) 이탈의 문면 근거 · architecture-db s043-9.6(Idempotency storage)와 규칙 쌍 |
| b10 | 566–567 | 1 | Replay의 최초 처리 outcome 재현(현재 상태 재조회 금지) | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b10 | 566–567 | 2 | 가변 자원의 최초 응답 snapshot·동등 안정 결과 보관 | Obligation | D: agent-design-review-api | 동상 |
| b10 | 566–567 | 3 | outcome의 트랜잭션 기록과 owning presentation controller의 status·표현 매핑 | Obligation | E: check-api-error-controller-contract.py<br>D: agent-design-review-api | ① 문면 «owning presentation controller» ② controller checker docstring(controller-owned mapping) |
| b10 | 566–567 | 4 | 중앙 error handler 소유 금지·application·domain의 status catch·생성·저장 금지 | Prohibition | E: check-api-error-controller-contract.py | ② controller checker docstring — 중앙 handler 차단이 검사기 계약 그 자체(파일럿 b30 선례) |
| b10 | 566–567 | 5 | byte 동일 replay 보관 시에도 status 결정의 presentation 소유 유지 | Obligation | E: check-api-error-controller-contract.py | 동상 — controller 소유 축(조건부 보관 허용의 단서) |
| b11 | 568–569 | 1 | 요청 fingerprint 저장과 후속 요청 비교로 충돌 판정 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) · db §9.6 저장 축과 상호 참조 |
| b11 | 568–569 | 2 | fingerprint 일치=replay·불일치=충돌 판정 | Obligation | D: agent-design-review-api | 동상 |
| b11 | 568–569 | 3 | 선택 프로필의 public code·Problem Details 계약 명시 | Obligation | D: agent-design-review-api | 동상 |

### s061-13.4 — 13.4 실전 원칙 (6)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 571–572 | 1 | 중복이 치명적인 POST의 Idempotency-Key 필수 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b1 | 571–572 | 2 | dddjango 파이프라인 채택의 G0/G1 사용자 결정·미요청 기본 미적용 | Override | E: check-idempotency-scope-creep.py<br>D: command-dddjango | ② docstring «멱등성 스코프크립(C3) 결정적 백스톱 (G0=확장금지) … 태스크가 요청하지 않은 멱등성을 … silent 의무화 차단 · G1 채택 승인 없이 accepted scope 밖 추가 금지» 정면 커버 ① 문면이 G0/G1 사용자 결정을 지목 — 절차 소유 Coordinator 병기 |
| b2 | 573–573 | 1 | 멱등성 키의 내구성 저장소 보관 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) [저장 메커니즘은 db 축과 상호 참조] |
| b3 | 574–574 | 1 | 동일 키 동시 요청의 레이스 컨디션 처리 | Obligation | D: agent-design-review-api | 동상 |
| b4 | 575–575 | 1 | fingerprint 불일치의 충돌 처리와 status·프로필 계약 선택 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) · s060-13.3 b11 정본의 부분 재진술 |
| b5 | 576–577 | 1 | PRG 대 Idempotency-Key의 문제 유형별 선택 | Permission | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) [두 선택지 모두 정당한 조건부 안내 → 허용] |

### s065-14.3 — 14.3 반영해야 할 계약 표면 (1)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 597–599 | 1 | API 계약 변경 시 OpenAPI 표면 병행 반영 | Obligation | E: check-openapi-error-declaration.py<br>D: agent-design-review-api | ② docstring «positional/auto/preserve 실행은 openapi_extra.responses 저장소 전수 검사 … response={status: <Bc>ErrorSchema} 선언 일치 검증» — 표면 중 error response 축을 집행 ④ 나머지 표면(path·parameter·pagination·versioning) 판정은 API 설계 리뷰 병기 |

### s066-14.4 — 14.4 실전 원칙 (3)

| 블록 | 행 | # | Work label | class | E / D | 4원 근거 |
|---|---|---:|---|---|---|---|
| b1 | 611–612 | 1 | 설계 시 OpenAPI 명세 병행 유지 | Obligation | D: agent-design-review-api | ① 문면 역할명 없음 ②③④ 검사기 docstring·P0 커버·registry 지목 없음 — 위임 기본값 표(architecture-api→design-review-api) |
| b2 | 613–613 | 1 | 명세 작성 도구 활용 | Obligation | D: agent-design-review-api | 동상 [지시형 불릿 — 괄호는 «상황→선택지 매핑»이 아니라 도구 예시. 허용되는 것은 도구 선택뿐이라 §4.2 «단일 지시값=준수 대상» 규약 적용] |
| b3 | 614–615 | 1 | OpenAPI 최신 상태 유지(테스트·SDK·문서·호환성 리뷰 동일 계약) | Obligation | D: agent-design-review-api | 동상 |

### 배선 요약

| 소유자 | 규범 수 | 비고 |
|---|---:|---|
| 에이전트 `agent-design-review-api` | 146 | |
| 검사기 `check-api-error-controller-contract.py` | 15 | |
| 에이전트 `command-dddjango` | 9 | |
| 검사기 `check-error-centralization.py` | 3 | |
| 검사기 `check-ninja-boundary-middleware.py` | 2 | |
| 검사기 `check-openapi-error-declaration.py` | 2 | |
| 에이전트 `agent-design-review-db` | 1 | |
| 검사기 `check-idempotency-scope-creep.py` | 1 | |
| 검사기 `check-response-schema-bypass.py` | 1 | |

무소유 규범 0(도구 단언). 검사기 배선 총 규범 = 아래 §4 «기본값 이탈» 판정과 짝.

## 3. 재진술 유예 (다른 문서 상대 — spec 미기재·소급 패스 대상)

census restate 열은 이 문서 6쌍을 **전부 같은 문서 안**으로 기록했고, 여기에 census 미표시 3쌍을 직접 확인으로 추가해 **9쌍**을 spec `restates`로 연결했다(§4.4 판정 규약 참조). 아래는 census 비고의 «규칙 쌍»·파일럿 기이관 절 문면을 직접 읽어 확인한 **문서 횡단** 쌍이다. 브리프 규약대로 spec에 넣지 않고 여기 유예한다.

| # | 사본(또는 짝) 블록 좌표 | 상대 문서/절 | 관계 | 확인 근거 |
|---|---|---|---|---|
| 1 | s018-4.2/b20 W1·W3 (CAS 소진 status) | architecture-db-final / s042-9.5 «락과 동시성 제어»(373–392) | 규칙 쌍(상호 참조) — api=status 배정 소유, db=경합 메커니즘 소유 | 발주서·census 비고 «db s042-9.5와 규칙 쌍» + 원문 «메커니즘 §5/G1» 문면 |
| 2 | s018-4.2/b20 W2 (Retry-After controller 소유) | implementation-django-ninja-final / s022-6.1 b15 W1 «retryable BC 503의 Retry-After 컨트롤러 설정» | 부분 재진술(구현 문서가 계약을 되받음) | 파일럿 spec 실독 — 같은 문장 축·같은 검사기 배선. **같은-문서 정본은 s026/b1 로 이미 실연결**(아래 9쌍) — 여기는 교차 문서 상대만 유예 |
| 3 | s026/b1 W1 (전역 handler·helper 합성 금지) | implementation-django-ninja-final / s023-6.2 b30 W2 «framework 오류의 BC 전환·전역 handler 가로채기 금지» | 부분 재진술 | 파일럿 spec 실독(같은 검사기·같은 금지 축) |
| 4 | s025/b7 (framework 기본 응답의 code 계약 body 배제·주장 금지) | implementation-django-ninja-final / s023-6.2 b30 W1·W3 | 부분 재진술 | 동상 |
| 5 | s024-5.4/b1·b2·b3 (프로필 선택 우선순위) | implementation-django-ninja-final / s023-6.2 b1 W1·W2 «오류 프로필 선택의 architecture-api §5.4 위임» | 명시 위임 참조(ninja→api) — 정본은 이 문서 | 파일럿 spec basis 문면 |
| 6 | s033-7.2/b14 W2·W4 (406/415 ninja 경계·전역 합성 금지) | implementation-django-ninja-final / s022-6.1 b16 «406/415의 ninja 경계 내 처리·전역 미들웨어 가로채기 금지» + 같은 문서 §6.3 | 부분 재진술 + 문면이 §6.3을 직접 지목 | 원문 330행 인용 블록 문면 + 파일럿 spec |
| 7 | s018-4.2 상태 코드 표(b3~b19) | implementation-django-ninja-final / s022-6.1 b1 W1 «상태 코드 의미의 architecture-api 위임» | 역방향 위임 참조 — 정본은 이 문서 | 파일럿 spec basis 문면 |
| 8 | s060-13.3/b9(Storage)·b11(fingerprint) | architecture-db-final / s043-9.6 «Risky Write Consistency Block»(393–415) | 규칙 쌍(상호 참조) | census 비고 «db s043-9.6과 규칙 쌍» + 원문 «DB 설계로 연결» 문면 |
| 9 | s061-13.4/b1 W2 (채택 G0/G1) | architecture-db-final / s043-9.6 (Idempotency storage) | 규칙 쌍 — `check-idempotency-scope-creep.py` docstring이 «architecture-db §9.6 집행»으로 두 문서를 잇는다 | 검사기 docstring 실독 |

**같은 문서 9쌍(spec `restates`로 실연결 — 사본 블록 9개·에지 10개)**

| # | 사본 블록 | → 정본 블록 | 출처 | 판정 근거 |
|---|---|---|---|---|
| 1 | s033-7.2/b14 (W2·W4) | s026/b1 | census | 전역 합성 금지의 문맥 변형 |
| 2 | s036-8.1/b9 (W2) | s026/b1 | census | 동상 |
| 3 | s038-8.3/b1 | s021-5.1/b5 | census | «비밀 값 query parameter 금지» 축자 근접 |
| 4 | s039-8.4/b5 (W2·W4) | s036-8.1/b8 · s036-8.1/b9 | census | §8.1 challenge 규칙의 Bearer 재진술 |
| 5 | s056-12.4/b2 (W2) | s026/b1 | census | 전역 합성 금지·controller 소유 |
| 6 | s061-13.4/b4 | s060-13.3/b11 | census | fingerprint 충돌 처리 |
| 7 | **s036-8.1/b5** (Work 0) | s036-8.1/b8 | 적대 리뷰 M-1 | 355행 «실패 시» 행 인증 열 = 359행 challenge 의무의 거의 축자 사본이고 **Work 미승격** — §15의 «정본 1곳만 승격 + 사본 블록 restates» 정면 케이스 |
| 8 | **s018-4.2/b20** (W2) | s026/b1 | 적대 리뷰 M-2 | 168행이 **§5.4 를 명시 지목** + 소유 절 축자 근접. 병렬 사례 5와 동형 처리(비일관 해소) |
| 9 | **s059-13.2/b4** (W2) | s060-13.3/b10 | 적대 리뷰 M-3 | 547행이 **§13.3 을 명시 지목** + «application·domain은 status를 만들지 않는다» ↔ b10 W4 «application·domain은 status를 catch·생성·저장하지 않는다» 축자 근접 |

## 4. 경계 판단 메모

### 4.1 블록 경계·공백 소유

- **구분자 귀속**: §13 원칙(선행 블록 후행 귀속)을 파일럿 실측으로 검증하고 그대로 따랐다 — 파일럿 ddd `s017-3.2`의 code 블록 `[548,581]`이 닫는 펜스(580) 다음 빈 줄(581)을 품고, `s051-8`의 마지막 블록이 절 끝 빈 줄까지 덮는다. 그래서 이 문서의 모든 블록은 «내용 + 뒤따르는 빈 줄»로 끝난다.
- **선행 블록이 없는 code 블록 2건**(`s029-6.2/b1` = 264–279, `s059-13.2/b1` = 536–544): 절 선두 빈 줄을 흡수할 선행 블록이 없다. §13의 «절 선두 구분자는 첫 블록의 선두 스팬에 귀속(선행 블록이 없는 유일 예외)»를 «code 리터럴 = 펜스 전체» 문면보다 우선 적용해 빈 줄을 code 블록 안에 넣었다 — 대안(빈 줄 하나짜리 prose 블록 신설)은 kind 의미가 빈 블록이 되어 더 나쁘다. byte 등가는 어느 쪽이든 성립(도구 단언 통과).
- **표**: 머리행+구분행을 한 블록으로(표 보유 14절 공통), 데이터 행은 §13 «행 단위»대로 1행=1블록. 계수는 데이터 행만(머리·구분행 Work 0).
  - **파일럿 판형 이탈을 명시한다**(적대 리뷰 L-1): 파일럿 ddd `s051-8`은 구분행을 단독 블록(`[2061,2061]`)으로 뒀다. 이 문서는 «머리행+구분행 = 표의 도입부 한 덩어리»로 보고 §13 자연 단위 열거의 **«표 행 묶음»**을 근거로 병합했다. 근거: ⓐ byte 등가·데이터 행 계수 어느 쪽도 영향 없음, ⓑ 파일럿도 «1행=1블록»이 아니다(빈 줄+머리행을 `[2059,2060]`으로 병합), ⓒ T3 형제 spec 실측이 병합 39·분리 24 로 코퍼스 관례가 미확정, ⓓ 이 문서는 14절 전부 병합이라 문서 내 일관은 성립. **전 절 재분할은 후속 블록 서수를 밀어 `restates` 에지 10개의 좌표를 흔들므로**(정정 이득 0·회귀 위험 有) 채택하지 않았다 — 코퍼스 규약이 «구분행 단독»으로 확정되면 소급 패스에서 일괄 재분할한다.
- **규범 없는 연속 불릿 열거**(`s065-14.3` 600–609, 표면 목록 9)는 **불릿별로 분리**했다(적대 리뷰 L-2 반영 — 종전 한 prose 블록 `[600,609]` 병합에서 변경). 근거: §13 자연 단위 열거가 «불릿»을 단위로 들고, 같은 문서 `s036-8.1` 357·358행의 무규범 연속 불릿을 이미 b6·b7로 분리해 **한 형태에 두 규약이 공존**했다. 실측상 이 블록이 이 문서에서 유일한 다불릿 병합이었으므로 분리 쪽이 문서 관례(1불릿=1블록)와 일치한다. 절 마지막 블록이라 다른 절의 서수·`restates` 좌표에 영향이 없다(블록 총계 188→196).
- **굵은 라벨 소단락**(`**성공 (2xx):**` 등 s018-4.2 b1·b7·b16, s033-7.2 b6·b9, s059-13.2 b2)은 표·코드와 분리해 prose 블록으로 뒀다 — 라벨 자체는 규범이 아니다.
- **kind 판정 애매점 2**: ⓐ `s036-8.1` 357·358행 불릿은 «인증이 있어야 인가가 있다»·«401은 이름이 Unauthorized지만…» — 사실 서술이라 prose(census 3 계수와 정합). ⓑ `s033-7.2` 319행 «구체적인 것이 우선한다»는 q값 해석 서술이라 prose(P0 미계수 승계). 둘 다 norm 블록으로 올리면 절 계수가 발주서와 어긋난다. ⓑ 는 적대 리뷰 L-3 이 «우선 서술»로 재검토를 제기했으나 **현 판정을 유지**한다 — 문면의 주어가 설계자가 아니라 HTTP 협상 알고리즘이고(«Accept-Language: ko-KR,ko;q=0.9…» 예시 바로 뒤의 매칭 규칙 서술), 지시 대상·수범자가 없다. 아래 §4.5 소급 검토 후보에 기재.
- **checklist-item 0건**: 이 문서에 `- [ ]` 형태가 없다(발주서 «- [ ] 운반체 아님» 승계). 5.3의 «체크리스트»는 표다.

### 4.2 규범 유형(class) 판정 규약

문장 형태만으로 갈리지 않는 자리가 많아 규약을 먼저 세우고 전 절에 일관 적용했다(파일럿 L-E 정정 유형을 준용).

| 형태 | class | 적용 절 |
|---|---|---|
| 상황→선택지 매핑 표(둘 이상이 다 정당) | Permission | s037-8.2 3 · s042-9.2 3 · s055-12.3 4 · s049-11.1 X행 2 · s061-13.4 b5 |
| 산문 «권장»·지시형 단일 값(대안 없음 — 괄호 예시는 선택지 아님) | Obligation | s043-9.3 b3(페이지당 100–200) · s066-14.4 b2(명세 작성 도구 활용) |
| 적용 범위·조건 한정 | Exception | s024-5.4 ③ · s024-5.4 b6 W1 · s027-6 W1 · s033-7.2 b14 W1 · s059-13.2 ⑤ |
| 상위 일반 규범을 파이프라인 규칙이 눌러 씀 | Override | s061-13.4 b1 W2(채택은 G0/G1 사용자 결정 — 앞 문장의 «필수»를 제한) |
| «…하지 않는다/금지/없음» | Prohibition | s013-3.1 2 · s014-3.2 W2 · s021-5.1 등 **총 24건** |
| 그 밖 지시·의무 | Obligation | 나머지 |

**class 실측 분포(spec 재계산)**: Obligation 122 · Prohibition 24 · Permission 15 · Exception 5 · Override 1 = **167**. 종전 표의 «총 30건»은 24+Exception 5+Override 1 을 합산한 표기 오류였다(적대 리뷰 L-9 — 셈 기준은 Prohibition 단독 24건).

- `s049-11.1`은 판정 표라 Permission/Obligation이 섞인다 — «X(비breaking)» 2행은 §11.3 «추가는 자유»와 같은 축이라 Permission, «O» 7행은 breaking 판정 의무라 Obligation.
- `s066-14.4 b2`(«명세 작성 도구(Swagger Editor, Stoplight 등) 활용»)는 적대 리뷰 L-5 를 받아 **Permission→Obligation 으로 교정**했다. 종전 판정은 이 문장을 «상황→선택지 매핑 표» 행에 끼워 넣었는데 형태가 표가 아니라 지시형 불릿이고, 괄호는 «도구를 쓰지 않을 자유»가 아니라 도구 *예시*다 — 같은 절 b1·b3 과 형태가 평행하고, 단일 지시값 규약(s043-9.3 b3)과도 이 쪽이 일관된다.
- `s043-9.3 b3`(«페이지당 100-200개 결과 권장» Obligation) vs `s042-9.2`(«권장» 열 Permission)의 층위 차는 적대 리뷰 L-6 이 이견으로 제기했으나 **현 판정 유지** — 전자는 대안 없는 단일 값이고 후자는 상황별로 셋이 다 정당한 매핑 표다(위 규약 표 1·2행). 코퍼스 횡단 class 규약 확정 시 재검토 대상으로 §4.5 에 태그.
- `s025/b2 W1`(«플러그인이 정한 body property 목록은 없다»)은 파일럿 ninja §6.2 b2 «플러그인 공통 body property 부재»가 Prohibition으로 채번된 선례를 따랐다 — 자유 부여가 아니라 «기본 목록 가정 금지»다.

### 4.3 wiring — 기본값 이탈과 «기본값 도피» 방지

`check-*.py` 27종 docstring 선두를 전수 실독한 뒤 배선했다(§16 L-F 의무). 이 문서는 계약 설계 문서라 대부분이 위임이지만, 검사기 문면이 정면으로 닿는 자리에서 기본값으로 도피하지 않았다 — 실제 배선된 검사기는 6종이다.

- `check-api-error-controller-contract.py`(controller 소유 축): Retry-After controller 소유(s018-4.2·s026·s056-12.4) · 전역 handler/helper 합성 금지(s026·s036-8.1·s039-8.4) · status literal 소유(s025) · 표준 controller 레시피(s024-5.4·s027-6) · replay status 소유(s059-13.2·s060-13.3). 파일럿 L-F 정정이 «전역 handler 금지는 controller-contract 소관(ninja-boundary는 settings.MIDDLEWARE 한정)»으로 못 박아 그 경계를 그대로 지켰다.
- `check-ninja-boundary-middleware.py`: **문면이 middleware를 직접 말한 한 자리**(s033-7.2 b14 W2·W4)만. docstring 대표 회귀가 «406/415 협상을 전역 미들웨어로 자작»이라 정면 커버 — 여기서 기본값으로 도피하면 L-F 오배선이다.
- `check-error-centralization.py`(§16 매핑 표 «schema checker»): wire 필드 혼합 금지 2(s024-5.4 b5 — basis 의 «① 문면 wire 필드» 표기는 적대 리뷰 L-8 대로 **철회**했다. 4원 ①은 검사기를 가리키는 *역할명* 슬롯인데 «wire 필드»는 규범의 대상 어휘일 뿐이다. 배선 자체는 ②(§16 매핑 표)+④(파일럿 b14)로 그대로 성립) · ErrorCode(StrEnum) 좁힘(s025 b4 W1). 반대로 «기존 계약 보존» 계열은 docstring이 «preserve-established는 schema semantics 미적용»이라 배선하지 않고 위임했다(과배선 방지).
- `check-openapi-error-declaration.py`: 오류 응답 문서화(s022-5.2 b5) · OpenAPI 표면 반영(s065-14.3). 둘 다 **표면의 일부만** 집행하므로 설계 리뷰를 병기했다.
- `check-response-schema-bypass.py`: 상태 코드별 schema 분리 정의(s022-5.2 b1) — docstring이 «선언 schema를 우회하는 raw 200-203 차단»이라 계약의 구현 백스톱. 적대 리뷰 L-7(과배선 소지)을 받아 **E는 유지하되 basis에 한정을 명기**했다: 이 검사기는 «선언된 schema의 우회»만 막고 «정의했는가»는 보지 않는 **부분 백스톱**이며, 정의 의무 자체의 소유는 병기한 위임(D)에 있다. E 제거는 채택하지 않았다 — 검사기 문면이 같은 축(상태 코드별 선언 schema 경유)에 정면으로 닿는데 위임만 남기면 §16이 금지한 «기본값 도피»가 된다.
- `check-idempotency-scope-creep.py`: s061-13.4 b1 W2. docstring이 «G0=확장금지 · 미요청 멱등성 silent 의무화 차단 · G1 채택 승인 없이 scope 밖 추가 금지»로 이 문장을 정면 커버한다 — 이 문서에서 가장 «도피하기 쉬웠던» 자리다.

**기본값 이탈(문면 근거 있는 것만)**

| 이탈 | 자리 | 문면 근거 |
|---|---|---|
| `command-dddjango`(절차 소유) | s018-4.2 b20 W3 · s024-5.4 b6 W4 · s025 b2 W2·b3 W1·W2·b6 W3 · s036-8.1 b9 W1 · s039-8.4 b5 W3 · s061-13.4 b1 W2 | 문면이 G0/G1·G2·12-slot·STOP·«명시 승인»을 직접 지목(파일럿 «503/409 선택의 명세 §5/G1 소유» 선례) |
| `agent-design-review-db` | s060-13.3 b9 (Storage 행) | 문면 «내구성 있는 저장소와 transaction/lock 정책은 **DB 설계로 연결**» — architecture-db §9.6과 규칙 쌍 |

**«비커버» 판정을 문면으로 남긴 것**(도피가 아님을 밝히는 자리)

- REST **URL 명명**(s013-3.1·s014-3.2) ↔ `check-naming.py`: 그 docstring의 축은 저장소 파이썬 경로·심볼 이름(#28 약어·#30 접미·#33 폴더 토큰·#41 Port/Adapter)이라 URL 문자열을 보지 않는다.
- **retryable status 배정**(s018-4.2 b20 W1) ↔ `check-transient-overmapping.py`: 그 검사기는 «transient 인프라 예외를 분기 없이 retryable로 통째 매핑» *차단*이라 방향이 반대다 — 배정 의무는 커버하지 않는다.
- **멱등 outcome 저장**(s059-13.2 b4 W1) ↔ `check-transaction-boundary.py`: 축이 «한 트랜잭션 = 애그리거트 하나»·UoW라 멱등 저장 계약을 보지 않는다.
- **표명·의미 판정**(«공개 계약이라고 주장하지 않는다» s025 b7, «민감 정보 누설» s025 b5 W3, «공개 구별 가능성» s025 b4 W3): 정적 검사 밖 — 파일럿이 같은 성질의 문장을 위임 처리한 선례와 동형.

### 4.4 부분 재진술의 취급

census가 «(부분)»으로 표시한 6쌍은 축자 사본이 아니라 문맥별 변형이다(예: s026 «전역 handler나 helper» / s033-7.2 «전역 middleware·helper·handler» / s056-12.4 «프레임워크 기본 429에 전역적으로»). 그래서 §15의 «정본 1곳만 Work 승격»을 사본 블록 전체 강등으로 읽지 않고, **사본 블록에도 자기 Work를 채번하고 블록 수준 `djr:restates`만 정본 블록으로 걸었다** — 발주서 계수 167과 정합하고, 소비층이 정본-사본 관계를 잃지 않는다.

**연결 판정 기준(적대 리뷰 M-1~M-3·L-10 처분에서 명문화 — 소급 패스 제안)**

| 형태 | 처분 | 이 문서 사례 |
|---|---|---|
| ⓐ 사본 블록이 **Work 미승격**(계수 0)인데 내용이 다른 블록의 규범을 거의 축자로 담음 | `restates` **의무** — §15의 «정본 1곳만 승격 + 사본 블록 restates» 정면 케이스. 미연결이면 소비층이 «왜 이 문장이 Work가 아닌지» 추적 불가 | s036-8.1/b5 → b8 (신규 연결) |
| ⓑ 양쪽 다 승격됐지만 사본 문면이 **정본 절을 명시 지목**(«§5.4의 경계에 따라»·«…; §13.3») + 소유 절이 축자 근접 | `restates` 연결(부분 재진술) | s018-4.2/b20 → s026/b1 · s059-13.2/b4 → s060-13.3/b10 (신규) · 기존 s033-7.2·s036-8.1·s039-8.4·s056-12.4·s061-13.4 |
| ⓒ 양쪽 다 승격 + § 지목 없음 + 표 행은 *계약 항목*, 문단은 *상세·부정형 해설*로 서로 다른 내용을 더함(요약-상세) | **연결하지 않는다** — 별개 Work로 채번한 판정과 모순되고, 재진술로 단정할 축자성이 없다 | s060-13.3 b5(Replay 행) ↔ b10 W1 · s039-8.4 b4(insufficient_scope 행) ↔ b6 W2 (적대 리뷰 L-10 — 유예 유지) |

ⓐ·ⓑ와 ⓒ의 경계는 «축자 근접 + 명시 지목»이다. 블록 전체가 축자 사본인 경우(파일럿 ddd b1 유형)는 이 문서에 없다(ⓐ는 표 행 한 셀 수준).

### 4.5 소급 검토 후보 (현 판정 유지 · 코퍼스 규약 확정 시 재검토)

적대 리뷰가 «현 판정 유지 시 종결 가능»으로 남긴 항목을 소급 패스가 잃지 않게 여기 고정한다.

| # | 좌표 | 쟁점 | 현 판정과 근거 |
|---|---|---|---|
| 1 | s033-7.2 / 319행 | «구체적인 것이 우선한다»의 규범 승격 여부 | prose 유지 — 주어가 HTTP 협상 알고리즘인 프로토콜 동작 서술(P0 미계수 승계). 승격 시 절 계수 7→8 로 발주서와 어긋난다 |
| 2 | s029-6.2 / 280행 | «문제 유형 정의에서 추가 가능»의 Permission 채번 여부 | 미채번 유지 — RFC 9457 본문 서술의 인용이고 수범자가 이 파이프라인이 아니다(P0 미계수 승계). 승격 시 절 계수 1→2 |
| 3 | s043-9.3 b3 ↔ s042-9.2 | «권장» 문면의 Obligation/Permission 층위 | 현 판정 유지(단일 값=Obligation / 매핑 표=Permission) — **코퍼스 횡단 class 규약 확정 시 재검토 대상** |
| 4 | s060-13.3 b5↔b10 W1 · s039-8.4 b4↔b6 W2 | 절 내 요약-상세 쌍의 재진술 취급 | 미연결 유지 — §4.4 ⓒ 규약. same-section 규약이 «요약-상세도 재진술»로 확정되면 두 쌍을 일괄 연결 |
| 5 | 표 머리행+구분행 병합(14절) | 파일럿 판형(구분행 단독 블록)과의 판형 차 | 병합 유지 — §4.1 근거 ⓐ~ⓓ. 코퍼스 규약이 «구분행 단독»으로 확정되면 일괄 재분할(서수·`restates` 좌표 동반 갱신) |
