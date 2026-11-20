# 설계 v1.3 — dddjango 2.43.0 후보: 리팩토링 막힘(F4-35 · 133 · 188 · 190 ~ 198)

작성 2026-11-20 · 운영자. v1(16:00) → v1.1(16시대 끝): 독립 검토 P(글 · 차단 2 · 중요 9 · 사소 8) · T(도구 · 차단 0 · 중요 6 · 사소 6) 처분 반영(`op-rev/DISPOSITION.md` — 모두 받음) → v1.2(17시대): 좁은 재확인 1 — P(차단 0 · 중요 5: P-I9 번호 · N-I1 R-2001 의 429 · N-I2 design-review-api slot 10 · N-I3 기능 요청 길 · N-I4 옮김 + update) · T(차단 0 · 중요 2: T-I1 두 호출 자리 · T-I4 픽스처 단위 옮김) 모두 받음 → v1.3(17시대): 좁은 확인 2 · 3 — P N-I3(기능 요청은 이미 있는 403 을 바꾸지 않음 · 리뷰어 nit `G1 전 닫기: 아니오`) · T T-I4(덮어쓰기 픽스처 — §7.2 꼴 확인 7 · 검토 T 의 싼 안) · 남은 차단 0. 기준 배포판 2.42.0(`2cdfa49c` · 사본 `rel-2.42.0/`). 근거: `repro-{a,b,c}/REPORT.md` · `rev-{p,t}/REPORT.md`. 경로:줄은 rel-2.42.0.

## 0. 결정

| 번호 | 결정 | 출처 |
|---|---|---|
| U1 | 이번 판 = 작업 리스트 «리팩토링 막힘» 8줄(F4-35 · 133 · 188 · 190 ~ 198) | 사용자 «우선 compact 준비해줘. 이후에 다음판 시작하자.»(15:00 앞) · «이제 늘 하던 차례로 진행해줘.»(15:05 앞) |
| U2 | F4-190 · 192: 401 은 Ninja 가 낸다 · WWW-Authenticate 안 붙임(한계 인정 · 감사가 위반으로 안 잡음) · 인증 틀 뒤 인증 실패는 컨트롤러가 Ninja `AuthenticationError` 를 던짐(R-0055 예외) · 로그인 필요 403 은 위반 | 사용자 «그럼 이건 그렇게 수정 방향을 잡자.»(13:10 앞) |
| U3 | F4-191: OpenAPI 3.2 표준대로 스트리밍 응답 설명서 규칙 · R-3467 은 JSON 에만 | 사용자 «좋아 그 방향으로하자.»(13:58 앞) |
| U4 | F4-193: 유스케이스 독립성 유지 · R-1511 은 유스케이스 사이 흐름에 안 걺 · 공유 칸 없음 | 사용자 «그렇게하자.»(14:10 앞) |
| U5 | F4-194: behavior_guard 그대로 · G1 승인 «케이스 옮김» 행 · 행 없는 자동 판별 없음 | 사용자 «가. 로하자.»(14:19 앞) |
| U6 | F4-197 (+ 35 · 133 · 188): 포트 자료는 도메인 값 객체 · enum · 식별자 허용 · 번역 · 검증은 어댑터(모르는 값 = 포트 실패) · #228 domain import 금지를 뺌 · 유스케이스 DTO 금지 유지 | 사용자 «가»(14:55 앞) |
| U7 | F4-196: 0C 이름 따라 바꾸기 허용 · «같은 파일 · 새 이름이 옛 이름을 품는 쌍 하나뿐» 이면 짝 · 아니면 red · G1 행 없음 | 사용자 «가.»(14:58 앞) |
| D1 | F4-195: U5 옮김 행이 단언 든 도움 함수도 받음 | 운영자 처리(14:55 · 질문 생략 · 설계 처리 · 이의 시 뒤집음) |
| D2 | **F4-198 (재현 뒤 바꿈)**: 검사기가 응답 보충을 status 칸마다 판정(오류 칸 값 = 글자 Dict · 같은 모듈 맨 위 상수 — 그 밖 #63 · `headers` 값 못 읽음은 그 status 만 ⓓ · 성공 칸은 머리 판정 밖이라 꼴 안 묻고 못 읽어도 다른 칸 판정 그대로). 14:55 의 «같은 컨트롤러 파일 맨 위 상수» 요구는 걷음 | 운영자 처리 — 2.42.0 은 같은 모듈 상수도 못 읽어 그 요구로 안 풀림 · 가림(빠진 `Retry-After`)도 닫음 · 레인 지금 꼴 그대로 표준 · 계획 요약에 한 줄 |
| D3 | F4-197 허용 = 자기 BC `domain_layer.<agg>.value_object.<모듈…>` · `domain_layer.shared_value_object.<모듈…>` 만 · 애그리거트 · 엔티티 · 이벤트 · 저장소 · 예외 · 도메인 서비스 · 꾸러미 재수출은 #228 그대로 | 운영자 처리 — U6 글 «값 객체 · enum · 식별자» · 표준 트리 칸 · 트리 명세 #267(«값 집합 Enum 계열도 값 객체») · 현장 6건 모두 value_object |
| D4 | F4-197 글: R-0589 clarification(허용 · 금지 목록) + §5.3 새 의무 «번역 · 검증은 어댑터 · 모르는 값 = 포트 실패» | 운영자 처리 — P-I5 |
| D5 | F4-193 글: cleancode §13.1 새 블록 · 새 Exception(§1.2 · §13 전체 · #189 뜻 · R-3449 유스케이스 몫 번역 · 판정 · 전이 · 바깥 값 번역은 밖) | 운영자 처리 — P-I4 |
| D6 | F4-190 글: R-2017 Obligation → Exception(«Ninja 401 은 challenge 없음 · 요구 안 함 · 감사 위반 아님») · 확립 계약 challenge 보존 문장(R-2018 · R-2032 · R-2001 의 401 몫)은 «보존이 필요하면 G1 에서 멈춤(STOP_FOR_USER_APPROVAL)» 으로 · R-2001 의 429 `Retry-After` 몫은 보존 · 별도 설계 그대로 · 합성 금지는 R-2019 · R-2000 · R-2033 몫 | 운영자 처리 — P-I2(사용자 «헤더만 붙이는 처리기는 지금 하지 않음») |
| D7 | 로그인 필요 403: 새 규범 대신 ninja §4.1 b5 **R-0757** clarification «… 403 으로 답하지 않는다 — 403 은 인증 실패를 뜻하지 않는다(권한 부족 · CSRF · 출처 같은 요청 거절) · 확립 계약의 로그인 필요 403 은 §5.4 ① 보존 대상이 아님 — 바뀌는 것 목록» · architecture-api §8.1 restates 블록 | 운영자 처리 — P-B2 · P-I1 |
| D8 | F4-192: ninja §6.2 b17 뒤 새 블록 · 새 **Exception** «인증 틀 뒤 인증 실패»(catch 본문 `raise AuthenticationError()` 한 문장 · 두 인자 Status · HttpError forwarding 금지의 예외 · `response=` 에 401 안 적음 · operations 행 없음) · 의무 여섯 자리에 참조 한 구 · 검사기는 slot 10 이 승인한 인증 실패 예외 하나를 잡은 catch 만 비켜 줌(`--auth-failure`) | 운영자 처리 — P-B1 · T-I2 |
| D9 | F4-191: 검사기 무변 · 글만 | 운영자 처리 |
| D10 | F4-194 · 195 옮김 행 = 0T 창에서만 · 단위 = 최상위 함수 · 클래스 통째 · 같은 폴더 · 원문 바이트 같음 + 묶임 맥락 같음(§7.2) · fixture 단위가 `conftest.py` 로 드나드는 옮김은 red · 0F 허용 파일 안 만듦 · 옮김은 개명과 따로 실림 | 운영자 처리 — T-I4 · T-I5 · T-I6 · P-I7 |
| D11 | 뒤 창 행(0T update/remove · 변경 창 V `시험:` · 0F retain)은 옛 경로 · 새 경로 어느 쪽으로 적어도 됨 — 장치가 «지금 키 → G1 키» 정규화 지도(끝난 개명 · 옮김 · 앞 창 통째 이동)로 읽음 · 실행 흔적은 G1 키로 | 운영자 처리 — T-I3(변경 창 개명 · 통째 이동 별칭은 지금 판에도 빠짐 — 같은 결함 함께) |
| D12 | F4-196 셈 = closed(①~⑥ §8) | 운영자 처리 — F 꼴 막고 현장 18/18 |
| D13 | 판 2.43.0(minor) · dddjango-web 무변 | 운영자 처리 |
| D14 | 이번 판 밖(작업 리스트 «현장 보고 밖 후보»): ⓐ «401 은 Ninja 몫» 기계 집행 빈자리(BC 401 직접 반환 · 루트 처리기 · wiring enforcedBy 가 실제보다 넓음 — 감사 범위는 안 줄임) ⓑ #228 남는 DTO 갈래 옛 구멍(`from …place_order import place_order_command`) ⓒ 0C «제품만 개명 · 시험 그대로» green(G2 suite 가 잡음) ⓓ 성공 칸 `{**import}` 조용히 통과(해 없음) ⓔ «인증 틀 있는 operation 에서만» 기계 판정 | 운영자 처리 |

## 1. 재현 표(배포판 2.42.0)

| 보고 | 재현 | 조건 | 생기면 | 누가 | 운영자가 본 정도 |
|---|---|---|---|---|---|
| F4-190 | 재현됨(헤더 없음) · 검사기 red 는 재현 안 됨 | 인증 틀 None → Ninja 401 머리 없음 · 실을 자리는 전역 처리기뿐(R-0076 이 막음) | 감사가 R-2017 «반드시 challenge» 로 M8 → G0 «정리» → G1 «불가» | 발주자 | 일꾼 C Ninja 사본 · 검사기 4꼴 exit 0 · 글 대조 |
| F4-192 | 재현됨 | catch 안 `raise AuthenticationError()` | code-json #125 + 계약 줄 · BC 401 은 기계가 못 막음 | 발주자 | 일꾼 C 변형 · 운영자 `:4360-4373` |
| F4-191 | 재현됨(감사 몫) | 성공 본문이 스트림 프레임 여럿 | 감사가 R-3467 을 스트림에 댐 · 고칠 길은 루트 문서 재정의(#63) | 발주자 | 일꾼 C 기록 · 변형 |
| F4-198 | 재현됨 | status 칸 하나가 글자 Dict 아님 | 그 경로 오류 머리 전부 ⓓ · 빠진 `Retry-After` 가림 · 같은 모듈 상수도 못 읽음 | 발주자 | 운영자 `:3660-3661` · 일꾼 C 변형 9 |
| F4-193 | 재현됨 | 두 유스케이스의 같은 응용 흐름 | R-1511 위반 → #189 반대 → G0 사용자 판단 → «불가» · #189 «중복해 둔다» 런타임 글에 없음 | 발주자 | 일꾼 B AST · 레인 기록 |
| F4-194 | 재현됨 | 0T 케이스를 같은 폴더 새 파일로 | 0T red 5 · 0C · 0F red 1 · G2 G0 유지 red 2 | 발주자 | 일꾼 A 장난감 7 |
| F4-195 | 재현됨 | 단언 든 도움 함수를 conftest 로 | 0T red 4(현장과 같음) | 발주자 | 일꾼 A 장난감 6 |
| F4-196 | 재현됨 | 본문 같은 정의 여럿 동시 개명 | 18 중 1 짝 · 시험 쪽 red 11 | 발주자 | 일꾼 A 현장 재연 · 실험판 18/18 · 검토 T closed 실측 |
| F4-197 | 재현됨 | 포트 `<data>` 가 `domain_layer` import | #228 6(현장 M1) | 발주자 | 일꾼 B 장난감 9 · 현장 27 검사기 · 운영자 `:461-471` |
| F4-35 · 133 · 188 | 재현됨(코드 + 기록) | 포트 자료 update 칸 · 필드 타입만 | pre-gate 예보 못 함 → G1′ | 발주자(레인 셋) | 일꾼 B — D3 뒤 값 객체는 위반 아님 |
| (덧) 변경 창 별칭 | 재현됨 | 0T 개명 · 통째 이동 뒤 V 가 G1 옛 키 | 변경 창 close red «승인 케이스 밖» | 검토 T | `rev-t/toys/d11/` · 실제 작업에서 본 것은 아님 |

## 2. F4-190 · 192 — 인증 401

### 2.1 글

- **architecture-api §8.1 b8 R-2017**(Obligation → **Exception** · redefinition): «RFC 9110 은 401 에 `WWW-Authenticate` challenge 를 요구하지만 Django Ninja 가 내는 401(인증 틀이 막은 요청 · 컨트롤러가 던진 `AuthenticationError`)은 challenge 를 싣지 못한다. 이 표준은 그 401 을 그대로 쓴다 — challenge 를 요구하지 않는다. 감사 · 리뷰는 challenge 없는 Ninja 401 을 위반으로 올리지 않는다(확립된 계약이 challenge 를 요구하는 경우는 아래 줄).»
- §8.1 b5 표 «실패 시» 칸 → «Ninja 401(challenge 없음 — 위 한계) · 확립 계약의 challenge 는 아래 줄».
- §8.1 b9 R-2018 → «이미 배포되었거나 공개적으로 요구된 계약이 challenge 를 요구하면 G1 에서 멈춘다(`STOP_FOR_USER_APPROVAL` — 이 표준에는 Ninja 401 에 challenge 를 붙이는 꼴이 없다)» · R-2019(합성 금지) 문면 «제공하지 않는다» 만.
- s026/b1 R-2001 → 둘로 가름: «확립된 계약이 401 의 `WWW-Authenticate` 를 요구하면 G1 에서 멈춘다(§8.1 — 이 표준에는 붙이는 꼴이 없다). 429 의 `Retry-After` 는 보존하고 별도 설계한다(ninja_extra `Throttled` 가 붙인다).» · §8.4 b5 R-2032 — R-2018 과 같은 뜻(멈춤).
- §8.4 b1 R-2026 · R-2027 → «Bearer 서버의 401 은 Ninja 가 낸다(§8.1 — challenge 없음). 아래 표의 `WWW-Authenticate` 칸은 확립된 계약이 challenge 를 요구할 때의 Bearer 표면이다(그 경우 §8.1 대로 G1 에서 멈춤).»
- §8.4 b2 · b3 표 머리 · R-2028 행 → «WWW-Authenticate(확립 계약 때)».
- §8.4 b5 R-2030 · R-2033 문면 · **R-2031 redefinition** «Ninja 401 은 challenge 없음 — 인증 방법은 API 문서 `security` 로 안내한다».
- §8.1 **restates 블록**(D7) → ninja R-0757.
- §5.2 `:208` 분류 · ninja §2.2 `:144` R-3735 에 한 구 «(인증 틀 뒤 인증 실패 — Ninja 기본 401 행이 적는다)»(P-S7).
- **ninja §4.1 b5 R-0757** clarification: «인증 실패 또는 인증 필요(인증 정보 없음 · 무효 · 인증 틀 뒤에 알게 된 인증 실패)는 `401` 로 응답한다 — 403 으로 답하지 않는다. 403 은 인증 실패를 뜻하지 않는다(인증된 주체의 권한 부족 · CSRF · 출처 같은 요청 거절에 쓴다). 확립된 계약이 로그인 필요를 403 으로 답해 왔어도 `architecture-api` §5.4 ① 의 보존 대상이 아니다 — 401 로 바꾸는 것은 밖 동작 변경(받는 쪽 맞춤 동반)이다: 리팩토링은 바뀌는 것 목록(영향 칸에 받는 쪽)으로 올린다. 기능 요청은 이미 있는 로그인 필요 403 을 바꾸지 않는다 — 리뷰어는 그것을 발견이 아니라 nit(`G1 전 닫기: 아니오` — 그 BC 리팩토링 몫)로 적는다(G1 배너 «미반영 minor·nit» 와 G2 감수 리포트로 간다) · 기능 요청이 새로 짓는 operation 은 401 이다.»(v1.2 뒤 · P N-I3 둘째 · 셋째 — G0 빚은 검사기 위반만 받고 슬라이스 0 은 동작 불변이라 그 길은 안 섬 · 묻는 일을 늘리지 않으려 STOP 대신 기존 nit 흐름(`commands/dddjango.md:136` · `:140` · `:229`) · 사용자 «그 BC 리팩토링 때»)
- **ninja §6.2 b17 뒤 새 블록 · 새 Exception «인증 틀 뒤 인증 실패»**: «인증 틀이 있는 operation 에서 유스케이스가 하위 서버 답 · 세션 확인으로 로그인이 필요함을 알린 구체 예외(slot 10 이 «인증 실패(Ninja 401)» 로 승인한 예외 하나)를 잡으면 그 catch(`except <그 예외>:` — 튜플 · `as` 없음) 본문은 `raise AuthenticationError()`(`ninja.errors` · 인자 없음 — 이름만 · `from None` 도 됨) 한 문장이다 — 두 인자 `Status` 직접 반환 · `HttpError` forwarding 금지의 예외다. 인자를 주면 몸통이 경로 앞 응답의 Ninja 기본 401 행과 달라진다. 이 401 은 Ninja 기본 경로 앞 응답 행이 이미 문서에 적으므로 `response=` 에 401 을 적지 않고 프로젝트 표 `operations` 행도 두지 않는다. BC 401(`Status(401, …)`) · 403 으로 바꾸지 않는다.» · §4.1 · §2.2 에 restates 블록 · wiring delegatedTo discipline-reviewer · design-review-api · enforcedBy check-api-error-controller-contract.
- **R-0076**(§6.2 b30) 한 구: «컨트롤러의 `raise AuthenticationError()`(«인증 틀 뒤 인증 실패»)는 framework 401 을 그대로 내는 길이라 BC 전환도 가로채기도 아니다».
- 참조 한 구 «(인증 틀 뒤 인증 실패는 `implementation-django-ninja` §6.2 «인증 틀 뒤 인증 실패»)»: agent-discipline-reviewer R-1000(s007/b17 · `:98`) · R-1006(s007/b18 · `:99`) · agent-coder `:55` · agent-design-review-api slot 11(`:77`) · ninja §2.2 b11 R-0684(`:139-143`) · ninja SKILL ttl(SKILL.md:30).
- **agent-design-architect slot 10 · 11**(`:59-60`): slot 10 exception path 표에 «인증 실패(Ninja 401)» 값 — 그 예외의 catch 는 `raise AuthenticationError()` 한 문장 · `response=` 401 없음.
- **agent-design-review-api slot 10**(`:76` — «concrete 예외 → ErrorSchema → Status chain 완전성»): 한 구 «(«인증 실패(Ninja 401)» 행은 ErrorSchema · Status 없이 그 예외 이름만 — `implementation-django-ninja` §6.2 «인증 틀 뒤 인증 실패»)» · Codex `dddjango-design-review-api` 뜻 미러.
- **command-dddjango** G2 렌더(`:181` «네 API-error checker command»): registry #15 에만 slot 10 «인증 실패(Ninja 401)» 행마다 `--auth-failure <예외 모듈>.<클래스>` 한 번씩(칸이 비면 발명 안 함 — `--event-value` 와 같은 꼴).
- 에이전트에 «challenge 없는 401 = 위반 아님» 문장은 더하지 않음(P-S2 — 에이전트 본문에 WWW-Authenticate 문장 0 · R-2017 로 충분).

### 2.2 검사기 `check-api-error-controller-contract.py`

- 새 인자 `--auth-failure`(반복 · `<예외 모듈>.<클래스>` · `:316` `--event-value` 곁) · docstring `:1-66`.
- `:4360-4373`(#125) · `:4407-4429`(계약 줄): catch 가 `except <클래스 하나>:`(튜플 · `as` 없음)이고 그 클래스의 바인딩 origin 이 `--auth-failure` 값 하나와 같으며, 본문이 정확히 한 문장 `Raise` 이고 `exc` 가 `AuthenticationError` 이름(origin `ninja.errors.AuthenticationError` — `:5123-5141` 선례 풀이) 또는 그 무인자 호출 · `cause` 없음 또는 `None` 이면 둘 다 비켜 줌.
- 그대로 red: `--auth-failure` 없음 · 다른 예외 · 튜플 · `as` · 인자 · `HttpError(401)` · `NotAuthenticated` · 섞임 · `from exc`.
- Codex byte · matrix `api_error_backstop_matrix.py:7677` 곁 사례(통과: 호출 · 이름 · `from None` · ninja_extra 컨트롤러 / red: 인자 없는 `--auth-failure` · 다른 예외(`except TurnNotFound:` — T-I2) · 튜플 · `as` · 인자 · HttpError(401) · 섞임 · `from exc`) → 골든 · EXPECTED · `pregate_symbol_kinds.json` 다시 짓기 · 봉인(DEVELOPMENT §3 체크리스트 8).

## 3. F4-191 — 스트리밍 응답 설명서(글만)

- **architecture-api §5.2 b7 R-3467**(revision): 주어를 «한 상태 코드의 JSON(`application/json` · `…+json`) 성공 본문» 으로 · 끝에 «스트리밍(`text/event-stream`) 성공 본문은 아래 «스트리밍 응답 설명서 꼴» 을 따른다» · prefLabel 도.
- **architecture-api §5.2 새 블록 · 새 Obligation «스트리밍 응답 설명서 꼴»**: «`text/event-stream` 으로 프레임을 잇달아 보내는 성공 응답은 그 status 의 `content."text/event-stream"` 에 프레임 설명서를 적는다 — 프레임 종류가 둘 이상이면 종류마다 `oneOf` 한 갈래(`title` = 프레임 이름 · `properties.data` = 그 프레임 data 모양 · `required`), `event:` 이름을 쓰면 `properties.event` = 그 이름 고정값 `const`. 판별 키(discriminator)는 요구하지 않는다(OpenAPI 3.2 의 SSE 예와 같음 — 갈래는 event 고정값으로 갈린다). 스트림 머리(`Cache-Control` 등)는 그 성공 칸 `headers` 에 적는다. 문서가 OpenAPI 3.2 를 내면 프레임 설명서는 `itemSchema` 에 두고 `data` 는 문자열(`contentMediaType: application/json` · `contentSchema` = 그 프레임 data 모양)로 적는다.» · wiring design-review-api.
- **ninja §2.2 b1 R-3465** revision «JSON 성공 본문» 한정 · R-3464(`:446`)는 이미 «판별 키로 갈리는 union 이면» 이라 무변(P-S4).
- **ninja §6.2 b34 뒤 새 블록 · 새 Permission**: «Ninja 가 OpenAPI 3.1.0 을 내는 동안 스트리밍 성공(`response=` 에 그 성공 status 를 `None` 으로 선언)의 프레임 설명서는 `openapi_extra` 그 성공 status 칸의 `content."text/event-stream".schema` 에 적는다 — 메타데이터 보충에 든다(`architecture-api` §5.2 «스트리밍 응답 설명서 꼴»). Ninja 1.7 의 내장 `SSE[T]` 는 오류 status 와 함께 선언되지 않고 `event:` 줄을 내지 않아 이 꼴을 대신하지 못한다.» · §2.2 b10 쪽 restates · wiring design-review-api.
- agent-design-review-api `:81` «stream carveout» → 스트림 설명서 꼴 대조 · R-3467 은 JSON 에만.
- 한계: 3.1 `schema` 의 «본문 하나» 읽힘(프레임 하나는 description 으로) · 판별 키 없는 oneOf 겹침(event const 가 가름).

## 4. F4-198 — 응답 보충 status 칸마다(D2)

- 검사기 `check-openapi-error-declaration.py`(+ Codex byte):
  - `_supplement_problems :3593-3642` 오류 칸(400–599) 검사 앞에 `value = _resolved_extra(value, tree)` — 같은 모듈 맨 위 한 번 묶은 글자 Dict 상수면 판정 · 그 밖은 지금처럼 #63(T-I1 ⓐ) · 이 함수에 `tree` 인자를 더하고 **부르는 두 자리 모두**(tree 레인 `_extra_problems :3549-3556` · code 레인 `_openapi_extra_findings :2775-2784`)가 넘긴다(한 자리만이면 auto 녹색 · cj red — 검토 T 실측 `rev-t/out/v11d2.a.*`).
  - `_header_supplement :3645-3673` → status 별 결과: 오류 칸 값을 `_resolved_extra` 로 풂 · 성공 칸(100–399) 값은 읽지 않음(머리 판정 밖) · `headers` 값을 못 읽으면 그 status 만 «못 읽음».
  - `_header_findings :5610-5660`: «못 읽음» 인 오류 status 만 ⓓ#63 · 다른 status 는 지금 판정 그대로.
  - 바깥 `openapi_extra` 값 · `responses` 값 · 키 규칙(정수 리터럴 · 문자열 · 변수 · `**` 위반)은 그대로.
- 글 ninja §6.2 b41 **R-3751** revision: «응답 보충의 오류 status 칸 값은 글자 Dict 이거나 같은 모듈 맨 위에서 한 번 묶은 글자 Dict 상수다(그 밖은 위반) — 그 `headers` 값을 검사기가 읽지 못하면 그 status 의 머리만 사람이 볼 ⓓ 후보가 된다. 성공 status 칸의 값(스트림 설명서 등)은 머리 판정 밖이라 꼴을 묻지 않는다(키 규칙은 그대로) — 두 경로가 같은 설명서를 쓰면 상수 하나를 함께 쓴다.»
- matrix `:7224` 곁(auto · cj 두 프로필 모두): 성공 칸 import + 오류 칸 글자 = ⓓ 0 / 성공 칸 import + `Retry-After` 빠짐 = #63(가림 닫힘) / 오류 칸 같은 모듈 상수 = 판정됨(빠짐이면 #63) / 오류 칸 import = #63 / 오류 칸 `headers` import = 그 status 만 ⓓ / 성공 칸 같은 모듈 상수 = ⓓ 0 → 골든 · EXPECTED · `pregate_symbol_kinds.json` · 봉인.
- 기대: 현장 사본 ⓓ 7 → 0(검토 T 실측).

## 5. F4-193 — 유스케이스 사이 흐름 중복(글만)

- `discipline-cleancode-final.ttl` §13.1 **새 블록 + 새 Exception**(ISSUED · wiring delegatedTo discipline-reviewer):
  «**유스케이스 사이 흐름 중복은 DRY · 중복 제거(§1.2 · §13)의 대상이 아니다.** 유스케이스는 서로 코드를 공유하지 않는다(houserules #189 — 유스케이스 간 돌려쓰기 금지). 두 유스케이스가 같은 응용 흐름(포트를 부르는 차례 · 자원을 잡고 놓는 순서 · 포트 예외를 도메인 예외로 바꾸는 번역 — `architecture-ddd` R-3449 의 유스케이스 몫)을 쓰면 각 유스케이스 안에 따로 둔다(진입점의 `_` 사설 함수 · 메서드 — 승격 폴더면 그 부품 · #192) — 이 중복은 위반으로 올리지 않는다. 업무 판정 · 상태 전이 · 바깥 값(하위 서버 · 바깥 답의 값)을 도메인 값으로 바꾸는 번역은 이 예외 밖이다 — 판정 · 전이는 도메인 한 곳, 그 번역은 어댑터(`architecture-ddd` §5.3) 한 곳에 둔다.»
- 감사 · G0 · 조정자 · 검사기 무변(ALLOW_KINDS = Permission · Exception). refactor_audit 픽스처 하나: 새 Exception 인용 «제외» 가 `check-verdict` 를 지남.
- `docs/master/mkrev2.py:315` `<use_case>/` 행 한 구 · 소스 미러 `workspace/reference/discipline-cleancode/…:1730` · corpus_mirror_sync.

## 6. F4-197 (+ 35 · 133 · 188) — 포트 자료 값 객체(D3 · D4)

- 검사기 `check-port-adapter-pairing.py:461-471`(+ Codex byte): `domain_layer` import 의 모듈 경로(상대 import 는 패키지 기준으로 풀어서 · `ast.Import` · `from X import <하위 모듈>` 은 모듈 + 이름을 이어서)가 `…domain_layer.<agg>.value_object.<모듈…>` 또는 `…domain_layer.shared_value_object.<모듈…>`(`value_object` 가 마지막 마디 아님 · 그 자리)이면 통과 · 그 밖 `domain_layer` 는 #228 «<data> 파일이 domain_layer 의 값 객체 칸 밖(애그리거트 · 엔티티 · 이벤트 · 저장소 · 예외 · 도메인 서비스)을 import 한다 — `domain_layer` 에서는 `value_object/` · `shared_value_object/` 의 것만 싣는다(R-0589)» · DTO 갈래 그대로 · docstring `:9-10`.
- 픽스처: `bad_rules/…/notes_out.py:6`(애그리거트) red 그대로 · `good/` 자기 BC value_object enum · 값 객체 · shared 값 객체 · `bad_rules/` 엔티티 · `ast.Import` 애그리거트 · 꾸러미 재수출 → findings_count · checker_baseline 골든 · `pregate_symbol_kinds.json`.
- 글: architecture-ddd §5.3 b5 **R-0589** clarification «… 입출력은 원시값 · 포트 자료(`<data>_in` · `<data>_out`) · 자기 BC 도메인 값 객체 · enum · 식별자(`value_object/` · `shared_value_object/` 칸의 것)다 — 유스케이스 입출력(command · query · result) · 애그리거트 · 엔티티는 싣지 않는다.» + 같은 블록 **새 Obligation**: «`port/<capability>/` 의 포트 자료가 도메인 값을 실으면 바깥 값 → 그 값 번역 · 검증은 어댑터가 한다 — 모르는 바깥 값은 포트 실패(포트 `exception.py`)로 알리고 유스케이스에 `ValueError` 로 새게 하지 않는다(도메인 우회 조회 자료는 그대로 도메인을 싣지 않는다 — #356).» · wiring delegatedTo discipline-reviewer · design-review-ddd · R-0589 enforcedBy 그대로.
- `discipline-reviewer.md:137` «… «펴서» 넘길 수 있나» → «원시값 인자로 넘길 수 있나»(P-S6).
- 문서: 트리 개정 명세 `2026-08-08-tree-revision-spec.md:548-549` #227 · #228 함께(허용 = 표준 타입 · 포트 어휘 타입 · 자기 BC value_object · shared_value_object 의 값 객체 · enum · 식별자 / 금지 = 유스케이스 DTO · 그 밖의 domain_layer) · `docs/master/mkrev2.py:324` 칸 통째 다시 · `:325` 그대로 · 실행 뒤 decision-record 되돌림.

## 7. F4-194 · 195 — 0T 옮김 행(U5 · D1 · D10 · D11)

### 7.1 꼴 · 글

- 조정자 `commands/dddjango.md:318` 곁 **새 규범 «옮김 행»**(command-dddjango): 꼴 `재조직 — 옮김 <옛 경로>::<최상위 이름> → <새 경로>` · 한 행 하나 · owner/path = 옛 경로 · 단위 = 시험 쪽 파일의 최상위 함수(케이스 · 도움 함수 · 픽스처) 또는 최상위 클래스 통째 · 옛 · 새 경로는 같은 폴더(새 파일 · 기존 파일 · `conftest.py`) · 원문 그대로(이름 · 데코레이터 · 몸) · **0T 창에서만**(0C · 0F · 변경 창의 옮김은 red) · 0F 허용 파일을 만들지 않음 · 옮기는 단위를 같은 창에서 개명하지 않음 · 옮기는 단위의 기대를 같은 창에서 바꾸지 않음(한 단위에 옮김과 0T `update` 가 함께면 0T 창을 둘로 나누고 옮김을 먼저 — 뒤 창 행은 정규화 지도가 읽음 · 0T 창 여럿이 되는지는 구현 때 조정자 글 `:163` «종류마다 하나 이상» 으로 확인) · 픽스처를 `conftest.py` 로 넣거나 빼는 옮김은 받지 않음 · 픽스처 단위는 autouse 가 아니고 그 이름을 요청하는 단위가 옛 파일에 남지 않고 새 파일에 원래 없을 때만(쓰는 쪽과 함께 옮김) · 옮긴 단위가 쓰는 묶임(모듈 수준 이름 · 파일 안 fixture · autouse · xunit 모듈 함수)이 새 자리에서 같아야 함 · 뒤 창 행은 옛 경로 · 새 경로 어느 쪽으로 적어도 됨 · 감사 키 «옮김».
- 나머지 자리는 이 규범을 가리키는 한 구: R-3506 · R-3684(coder `:80` — 0T «새 case · 개명 금지» 에 «옮김 행 몫 옮김은 됨») · R-3683(architect `:29`) · R-3245(acceptance-tester `:24`) · R-3685 · R-3686(discipline-reviewer `:65` — 옮김 키 판정 «기대 의미 그대로» · 감사 요청의 «이름 → 옛 묶임 / 새 묶임» 표를 봄) · R-3011 · R-3019 · R-1763(implementation-test) · R-3503(`:163` · 블록 s007/b3) · R-3680 · R-3681(`:312` · 같은 블록) · R-3682(`:318`).

### 7.2 0T 판정(`behavior_guard.py`)

- 몫: 옛 기준 판에 있음 ∧ 옛 새 판에 없음 ∧ 새 경로 새 판에 정확히 하나 · 옮김 행의 옛 파일은 통째 옮김 짝 맞추기(`maps.pairs`)에서 뺌(옮김 행 먼저 · 옛 파일이 비어 지워져도).
- 꼴 확인(어긋나면 `옮김 행 꼴 밖` red):
  1. 단위는 `audit_split`(`:1457`)으로 자름 — 같은 이름 최상위 정의가 둘이면 red · 그 이름의 최상위 묶음(정의 · 대입 · import)이 옛 · 새 파일에 각각 하나뿐.
  2. 새 경로 기준 판에 같은 이름 없음 · 이름 같음 · **단위 원문 바이트 같음**.
  3. 픽스처 단위(`pytest.fixture` · `pytest_asyncio.fixture` 데코레이터)는 옛 · 새 어느 쪽도 `conftest.py` 가 아님 ∧ autouse 아님 ∧ 그 이름을 요청하는 단위(매개변수 · `usefixtures` · fixture 매개변수)가 옛 파일에 남지 않고 새 파일 기준 판에 없음(쓰는 쪽과 함께 옮김 — 파일 안 override 로 남은 시험의 풀이가 바뀌는 꼴을 막음).
  4. 케이스 단위: 두 파일 모두 수집(`_collected :2032`) · `pytestmark` · `pytest_plugins` 같음 · autouse fixture 묶음 · xunit 모듈 함수(`setup_module` 등) · 매개변수와 `usefixtures` 이름이 가리키는 파일 안 fixture 정의(그 fixture 가 다시 요청하는 fixture 까지 전이)가 옛 · 새 파일에서 바이트 같거나 둘 다 없음.
  5. 단위가 읽는 모듈 수준 이름마다: 옛 · 새 파일의 묶임이 전체 경로로 같은 것에 풀림(같은 전체 경로 import · 바이트 같은 파일 안 정의 · 같은 창의 다른 옮김 행이 옮긴 것 — import 와 정의가 서로 바뀌어도 같은 것에 풀리면 됨 · builtins · 단위 안 지역 이름은 밖).
  6. 같은 폴더.
  7. **덮어쓰기 픽스처**(v1.3 · T-I4 셋째 — 검토 T 의 싼 안): 그 폴더에서 보이는 conftest 사슬(같은 폴더 → 위 폴더 · rootdir 까지)에 같은 이름 fixture 가 있는 파일 안 fixture(덮어쓰기)를 옮기는 단위로 삼으면 red · 옛 · 새 파일 어느 쪽에든 덮어쓰기 fixture 가 있으면 케이스 단위 옮김은 그 덮어쓰기 정의들이 두 파일에서 이름 · 바이트 모두 같을 때만(conftest fixture 가 요청하는 이름을 파일 안 정의가 덮어써 바뀌지 않은 시험의 값이 조용히 바뀌는 꼴 — 실측 `rev-t/pytoy/` `quota` 2 → 20) · 덮어쓰지 않는 fixture 를 빼면 남은 시험이 시끄럽게 깨지므로(suite red) 따로 대조하지 않음 · 플러그인 fixture 덮어쓰기는 대조 밖(한계).
- D 처분 `zero_t_fixed :1822-1845` 면제: 옛 «삭제»(클래스면 `클래스.메서드` 전부) · 새 «추가»(새 경로 기준 판에 없을 때) · 여러 옛 파일 → 한 곳은 행마다.
- 감사 키 `옮김 <옛>::<이름> → <새>` 를 **새 파일 처분**에(전 = 옛 단위 digest · 후 = 새 단위 digest · 요구 판정 `기대 의미 그대로` · 감사 요청 글에 두 단위 원문 + «이름 → 옛 묶임 / 새 묶임» 표) · 옮긴 단위의 보통 키(옛 «전 X · 후 없음» · 새 «전 없음 · 후 X»)는 옮김 키로 갈음.
- 케이스 다중집합 `_side_rules :3079`: `옛 경로::이름` → `새 경로::…`.
- 0C · 0F · 변경 창에 옮김 몫이 생기면 red «옮김 행은 0T 창 몫».
- 기록: 스냅숏 `retain_rows[].moves`(refactor_audit) · 허용 표 `moves`(`allow_table :2829-2855` — `retain_files` 에 넣지 않음) · close `moves` · `g0_keep_exceptions.case_moved` [(옛 경로, 클래스, 함수, 새 경로)] · verify «옮김 행인데 옮김 없음» · 머리 글 `:8-9` · `:29-48` · `:51-58`(사각 «conftest 이동으로 autouse 범위» 줄에 «옮김 행은 픽스처의 conftest 드나듦을 받지 않음»).
- 개명 기계(`renames` · `_rename_window` · `alias_renamed` · `_renamed_cases` · `_moved_rename_reds` · `g0_keep_exceptions.renamed` · `rename_label` · `_rename_row_clashes`)는 무변(T-I5).

### 7.3 정규화 지도(D11)

- `_close_refactor` 가 앞 창 기록(끝난 개명 `renames` · 옮김 `moves` · 통째 이동 `map_items.pairs`)으로 «지금 키 → G1 키» 지도를 짓고: 0T update/remove 표 · 변경 창 `approved_cases` 는 두 키로 읽음 · `approved_hits` (실행 흔적)는 G1 키로 기록 · `_side_rules` 변경 갈래 `room_rm` · `room_add`(`:3118-3121`) · `_approved_unseen`(`:1848`) · 감사 요청 `approved_cases`(`:3296`) · `_verify_refactor`(`:3866-3870`)가 같은 지도.
- 0F retain 별칭: 명시 retain 행(옮김 · 개명 행 아님)이 옛 파일을 가리킬 때만 통째 이동의 새 파일로 · `conftest.py` 로는 안 이음.

### 7.4 파서 · G2

- `refactor_audit.py`: 정규식 `:2324-2337` 옆 · `_reorg :2693` 에 «옮김» 갈래(새 함수 · 두 경로 시험 경로 `_is_test_path :2786` · 같은 폴더) · 중복(같은 옮김 두 번 · 한 단위 행 둘 · 같은 단위 옮김 + 개명 행) red · `retain_rows[].moves`(행 없으면 digest 무변 — `SpecChanges :2863-2892`) · 요약 `:3916` · 뒤 창 행이 옮긴 단위의 옛 · 새 키 어느 쪽이어도 받음.
- `behavior_support.py`: `_fold_key :1043-1057` 에 `case_moved` 케이스 단위 경로 접기 · `_g0_keep_exceptions :1276-1299` 판형 · «옮긴 케이스가 G2 에서 선택되지 않았다» 대조(`renamed_selection :1101-1125` 꼴).
- Codex byte(behavior_guard · behavior_support · refactor_audit).

## 8. F4-196 — 이름 단서 짝(D12)

- `behavior_guard.py:846-852` 뒤 한 단계(closed — 검토 T 가 `_match_defs` 안에 짠 판 실측 · `pending` 에 옛 경로): 본문 같은 후보 여럿이 남은 옛 정의마다 ① 같은 파일 ② 이름 뺀 본문 dump 같음 ③ 새 이름이 옛 이름을 부분 글자로 품음 ④ 새 이름은 기준 판 그 파일에 없던 이름 · 아직 대응 없음 ⑤ 옛 → 후보 하나 **그리고** 후보 ← 옛 하나(한 번에 셈 · 차례 소거 없음) ⑥ 그 파일 · 그 본문 무리의 남은 새 정의가 모두 ⑤ 짝으로 설명될 때만(묶음 단위 전부 아니면 없음).
- docstring · 주석 `:14-16` · `:887` · `:758` · 사각 `:51-58` «같은 파일 · 같은 본문 정의 사이 이름 증거 짝 — 짝이 틀린 개명은 리팩토링 모드는 묶음 감사 키 · 기능 모드 0C 는 자동 초록» · Codex byte · 기능 모드 0C 도 같은 `_match_defs`(함께 넓어짐).
- 글 · 그래프 무변.
- 픽스처: 기능 `cases()` — 본문 같은 예외 여럿 개명 green · 접두 겹침 red · 바꿔치기 red · 기준 판 이름 red · F 꼴 red · `rcases()` 0C 묶음 감사 하나.

## 9. 받아들일 한계

1. Ninja 401 은 RFC 9110 challenge MUST 를 어김(사용자 인정) · 확립 계약이 challenge 를 요구하면 G1 에서 멈춤.
2. «인증 틀 있는 operation 에서만» · 잡는 예외의 뜻(slot 10 승인)은 글 · 리뷰어 몫 — 검사기는 `--auth-failure` 클래스 일치만.
3. 3.1 `schema` 의 «본문 하나» 읽힘 · 판별 키 없는 oneOf 겹침.
4. 포트 자료에 애그리거트 · 엔티티를 실은 설계의 pre-gate 예보 사각(장부 사례 0) · #228 의 옛 DTO 구멍(D14 ⓑ).
5. 옮김 행: 0T · 같은 폴더 · 원문 바이트 + 묶임 같음만 — 단언 든 도움 함수를 두 파일에 복사(옛 것도 남김)는 받지 않음(공용 자리로 옮김) · 한 단위의 옮김 + 기대 바꿈은 0T 창 둘(옮김 먼저) · 픽스처는 쓰는 쪽과 함께만 · 덮어쓰기 픽스처가 있는 파일 사이 옮김은 그 정의가 같을 때만 · 플러그인 fixture 덮어쓰기는 대조 밖 · 0F 의 «제품 나누기 뒤 시험 거울 나누기» 밖 · G1′ 재실행에서 앞 창 디렉터리 이동 뒤 새 경로는 따라가지 않음(red · 창 나눔).
6. F4-196: 같은 창 개명 + 파일 옮김(본문 유일 아님) · 같은 파일 접두 겹침 · 같은 창 · 파일에 본문 같은 새 정의를 따로 더함 → red(창 나눔).
7. D14 의 다섯.

## 10. 행동 시험(옛 판 2cdfa49c · 새 판 나란히)

- F4-194 · 195 · 196: `repro-a/toys/` 같은 사례 · `repro-a/field-m34/`(red 11 → 0) · 적대(T-S6): 픽스처 conftest 드나듦 red · autouse 옮김 red · 묶임 다른 케이스 red · 데코레이터 바꿈 red · 같은 이름 둘 red · 옮김 + 같은 창 개명 red · `rev-t/pytoy/` 두 꼴(덮어쓰기 fixture 옮김 · 덮어쓰기 있는 파일에서 케이스 옮김) red.
- 정규화 지도: `rev-t/toys/d11` · `d11v` 꼴 — 0T 개명 · 옮김 · 통째 이동 뒤 V 옛 키 · 새 키 둘 다 close · verify 녹색.
- F4-197: `repro-b/toy228/` · `rev-t/toy228/`(T-S1 구멍 넷 red) · 현장 `field-m1`(6 → 0).
- F4-192 · 198: `repro-c/variants/` · `rev-t/variants/`(`--auth-failure` 있음 · 없음 · `except TurnNotFound:` red · 오류 칸 같은 모듈 상수 판정 · 가림 #63 · field ⓓ 7 → 0).
- F4-190 · 191 · 193: 렌더 결과 grep · 감사 렌즈 절(`refactor_audit.py:121-125`)에 새 문장 · refactor_audit 픽스처(새 Exception «제외» 통과).

## 11. 검사 · 문서

- `make verify` 전체 + `make verify-mutation`(rulepack · behavior_guard) · 봉인 두 번 · `claude plugin validate`.
- README `:321` 리팩토링 «구현» 줄 «시험 파일 나누기 · 모으기는 승인된 «옮김» 행으로 시험 정리 창에서» · `docs/master/work_flow.spec.json:623` 기준 판 2.43.0 · 기능 줄(선례 `:653`) → work_flow.html · `master.html:140` 기준 판 · mkrev2(§5 · §6) → file_tree.html · REQUEST_GUIDE 바뀔 것 없음(grep — 401 · 스트림 · 포트 · 시험 나누기 언급 0 · `:131` 정지 회원 예와 안 부딪음).
- 장부 다시 읽기(계획 확정 · 배포 직전).

## 12. 그래프 변경 표

| 파일 · 절 | 규범 | 새/리비전 | 종류 | wiring · enforcedBy | 비고 |
|---|---|---|---|---|---|
| architecture-api s036-8.1 b8 | R-2017 | 리비전(redefinition) | Obligation → Exception | 그대로 | prefLabel «Ninja 401 은 challenge 없음 — 요구 안 함» · 선례 `2fbc111b` |
| s036-8.1 b5 · b9 | (표) · R-2018 · R-2019 | 블록 글 · 리비전 | 그대로 | 그대로 | R-2018 prefLabel «보존 필요면 G1 멈춤» |
| s036-8.1 새 블록 | — | restates R-0757 | — | — | |
| s026 b1 | R-2001 | 리비전 | 그대로 | 그대로 | 401 challenge 요구 = 멈춤 · 429 Retry-After = 보존 · prefLabel 가름에 맞춤 |
| s039-8.4 b1 · b2 · b3 · b5 | R-2026 · R-2027 · R-2028 · R-2030 · R-2031 · R-2032 · R-2033 | 리비전(R-2031 redefinition) | 그대로 | 그대로 | prefLabel 바꿈 |
| s022-5.2 b7 | R-3467 | 리비전 | 그대로 | 그대로 | prefLabel «JSON 성공 본문 …» |
| s022-5.2 새 블록 | 새 | 새 | Obligation | design-review-api | 스트리밍 응답 설명서 꼴 |
| s022-5.2 `:208` 블록 | 해당 규범 | 리비전(한 구) | 그대로 | 그대로 | P-S7 |
| ninja s016-4.1 b5 | R-0757 | 리비전(clarification) | 그대로 | + discipline-reviewer · design-review-api | 403 |
| ninja s023-6.2 b17 뒤 새 블록 | 새 | 새 | Exception | discipline-reviewer · design-review-api · enforcedBy controller | 인증 틀 뒤 인증 실패 |
| ninja s016-4.1 · s009-2.2 새 블록 | — | restates 위 둘 | — | — | |
| ninja s023-6.2 b30 | R-0076 | 리비전(한 구) | 그대로 | 그대로 | |
| ninja s009-2.2 b1 | R-3465 | 리비전 | 그대로 | 그대로 | JSON 한정 |
| ninja s023-6.2 b34 뒤 새 블록 | 새 | 새 | Permission | design-review-api | 스트림 설명서 openapi_extra |
| ninja s023-6.2 b41 | R-3751 | 리비전 | 그대로 | 그대로 | status 칸 값 |
| ninja s009-2.2 b11 · `:144` 블록 | R-0684 · R-3735 | 리비전(한 구) | 그대로 | 그대로 | 참조 |
| ninja SKILL ttl | SKILL.md:30 규범 | 리비전(한 구) | 그대로 | 그대로 | 참조 |
| architecture-ddd s038-5.3 b5 | R-0589 · 새 | 리비전(clarification) · 새 | 그대로 · Obligation | 새 = discipline-reviewer · design-review-ddd | 번역은 어댑터 |
| discipline-cleancode s101-13.1 새 블록 | 새 | 새 | Exception | discipline-reviewer | 유스케이스 사이 흐름 |
| agent-discipline-reviewer s007/b17 · b18 · `:65` · `:100` · `:137` | R-1000 · R-1006 · R-3685 · R-3686 · (해당) | 리비전(한 구) | 그대로 | 그대로 | |
| agent-design-review-api `:76` · `:77` · `:80-81` | slot 10 · slot 11 · (해당) | 리비전 | 그대로 | 그대로 | slot 10 «인증 실패(Ninja 401)» 행 꼴 |
| agent-design-architect `:29` · `:59-60` | R-3683 · slot 10 · 11 | 리비전 | 그대로 | 그대로 | «인증 실패(Ninja 401)» 값 |
| agent-coder `:55` · `:80` | (해당) · R-3684 · R-3506 | 리비전 | 그대로 | 그대로 | |
| agent-acceptance-tester `:24` | R-3245 | 리비전 | 그대로 | 그대로 | |
| command-dddjango `:163` · `:181` · `:312` · `:318` 곁 | R-3503 · (G2 렌더 규범) · R-3680 · R-3681 · R-3682 · 새 | 리비전 · 새 | 그대로 · Obligation | 새 = coordinator 몫 | 옮김 행 · `--auth-failure` |
| implementation-test | R-3011 · R-3019 · R-1763 | 리비전(한 구) | 그대로 | 그대로 | |

- 절차(DEVELOPMENT §3 체크리스트 1~8): canon_turtle 왕복 → ttl(새 Expression · 새 Norm · 새 Block statesNorm · restates · ISSUED 끝 뒤 채번 · wiring) → ontology_gate → `ontology_render.py --apply` → LEDGER 재기준선(architecture-api s022-5.2 · s026 · s036-8.1 · s039-8.4 / ninja s009-2.2 · s016-4.1 · s023-6.2 · SKILL / ddd s038-5.3 / cleancode s101-13.1 / agent 절 · command 절 · implementation-test 절) → target-counts(지금 BlockShape 3022 · ExpressionShape 4447 · Norm/WorkShape 3793 — 새 · 리비전 수만큼) → q4 golden → `make rulepack`.
- 미러: corpus_mirror_sync(references final.md) · 소스 미러 손(`workspace/reference/` — architecture-api · ninja · cleancode · ddd · implementation-test) · Codex 뜻 미러(`codex-dddjango/skills/` — dddjango(조정자) · dddjango-coder · dddjango-design-architect · dddjango-design-review-api · dddjango-discipline-reviewer · dddjango-acceptance-tester · dddjango-implementation-test · dddjango-implementation-django-ninja SKILL).
