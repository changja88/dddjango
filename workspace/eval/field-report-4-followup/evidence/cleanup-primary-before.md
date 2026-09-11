# field-report-4 — spring_dream_server 대공사 플러그인 미처리 목록

- 보고 출처: spring_dream_server 발주자 세션 · 2026-09-10~11 현장 보고.
- 정리 기준: 2026-09-11 · dddjango 2.18.2 · 미처리 12건(F4-1 잔여 범위 + F4-9~F4-19).
- 관리 원칙: 이 문서에는 미처리건만 남긴다. 수정·검증 완료 또는 비결함 종결이 확인되면 요약표와 본문에서 함께 제거한다. 일부만 해결됐으면 해당 번호에는 남은 범위만 적는다.
- 레인의 임시 우회·waiver·설계 정정은 플러그인 문제의 처리 완료로 보지 않는다. 개선 후보는 채택·기각이 결정될 때까지 남긴다.
- 항목 번호는 재사용하거나 다시 매기지 않는다. 다음 신규 항목은 F4-20부터 추가하며 요약표도 함께 갱신한다.
- 완료 근거는 기존 [수정·검증 기록](../../plan/2026-09-10-field-report-4-fixes.md)과 해당 커밋·릴리즈에서 확인한다.

| # | 남은 문제 | 영향 | 상태 |
|---|---|---|---|
| F4-1 | 기존 use case 시그니처·기존 테스트 마커 update의 pre-gate 미전사(#197·#387) | G1 누락 후 구현 단계에서 차단 | 미처리 · S5 지원 범위 검토 |
| F4-9 | framework 소유 열린 context dict의 #647 처분 기준 부재 | 설계·감수 반송 반복 | 미처리 · 규범 보완 |
| F4-10 | OHS builder + execute를 호출 2회로 계수(ⓓ#153) | 불필요한 후보 검토 | 미처리 · 계수 현상 재현 |
| F4-11 | 닫힌 StrEnum 값 객체에도 검증 후보 발행(ⓓ#268) | 불필요한 후보 검토 | 미처리 · 자동 판정 개선 후보 |
| F4-12 | pre-gate UoW 스텁에 on_commit이 없어 #376 발행 | G1 차단·수동 처분 반복 | 미처리 · 스텁과 본문 검사 적용 범위 검토 |
| F4-13 | raw infrastructure 기본 경계와 #555 예외 번역 규범의 관계 불명확 | 승인 설계와 구현 검사 사이 반송 | 미처리 · 규범 보완 |
| F4-14 | 분리된 UoW 쓰기를 함수 전체에서 합산(#546) | 정상 트랜잭션 구조 차단 | 미처리 · 오탐 재현 |
| F4-15 | 도메인 속성 code 비교를 벤더 오류 판정으로 분류(#557) | 정상 도메인 코드 차단 | 미처리 · 오탐 재현 |
| F4-16 | 기존 소형 파일의 행 수 변화가 신규 출생 위반으로 귀속(#642) | 앵커 차분 오분류·G2 차단 | 미처리 · 판정 키 문제 재현 |
| F4-17 | 삭제된 폴더의 __pycache__ 잔재를 인스턴스로 판정(#488·#218·#225) | 고정 파일 부재 오탐·G2 차단 | 미처리 · 잔재 판정 재현 |
| F4-18 | result의 aggregate 필드와 미기재 domain import를 설계 예보에서 놓침(#202·#95·#96) | G1 누락 후 구현 단계에서 차단 | 미처리 · 검출 범위 보완 검토 |
| F4-19 | 기본 pre-gate에서 미추적 실존 파일의 add/update가 모두 충돌 | Phase 1 형식 오류·반송 | 미처리 · 기본 판형 및 오류 안내 검토 |

## F4-1 — 기존 use case 시그니처·기존 테스트 마커 update의 pre-gate 미전사(S5 잔여 범위)

- 실측(A1① S3 STOP · 2026-09-10 21:4x): `update` 대상인 `list_fortune_types_use_case.py`(read UoW + select_for_update 설계)와 `test/unit/test_catalog_inquiry_contract.py`(DB 마커 추가)가 pre-gate에 보이지 않아 #197·#387이 설계 단계를 통과하고 S3 registry_gate에서야 red가 됐다. 설계 자체는 검사기가 맞고(읽기 use case는 UoW 0) 발주자가 설계를 고쳤다.
- 남은 범위: 기존 함수의 시그니처·본문 변경과 기존 테스트의 마커 변경은 현재 S5 미시뮬레이션이다. 기존 OHS 서비스에 명시된 새 모듈 함수를 추가하는 지원 범위와 구별한다.
- 검토할 사항: 명세에 적힌 UoW 인자 추가·테스트 마커 변경을 기존 코드의 의미와 바인딩을 보존하며 예보할 수 있는지 판단한다. 레인의 설계 정정과 별개로 플러그인의 해당 지원 범위는 미처리다.

## F4-9 — framework 소유 «열린 context dict」의 #647 처분 문면 부재(B0 STOP-10 · 22:02 KST · 낮음 · 규범 빈칸)

- 실측(B0 최종 감수 `review-final.md` F01 important · registry 귀속 0 · ⓓ#647 3건): `fortune_character/…/admin/character/panel.py:158 changeform_view(extra_context: dict[str, object] | None)` · `:189 _render_failed_submission(extra_context …)` · `:220 context: dict[str, object] = {**self.admin_site.each_context(request), "title": …, 14키}` → `.update(extra_context)` → `render_change_form`. 검사기 물음 «이 object 는 입구인가 — 받는 즉시 좁히는가」.
- 왜 STOP 이 됐나: houserules `SKILL.md:71`(framework override 는 Any 대신 object) 과 `:73`(리터럴 고정 키 레코드 = TypedDict)이 있지만, **framework 가 소유하고 우리가 값을 읽지 않는 열린 dict 를 그대로 전달하는 자리**를 어느 쪽으로 닫는지 문면이 없다. architect(안 A = private TypedDict 14키 + 한정 예외 · 안 B = 계약 축소)와 reviewer 가 모두 «현행 규범과 native 계약을 동시에 만족하는 승인 경로 없음」으로 발주자에 반송. 같은 형태의 `media_library/…/admin/media_asset/panel.py:61`(`extra_context: dict[str, object] | None`)은 앞선 레인에서 조용히 통과했다(판정 일관성 없음).
- 발주자 판정: ③ 유지 — 값을 읽지 않는 전달 컨테이너는 «입구」가 아니고 좁힐 자리가 없다 · :73 은 우리가 소유·소비하는 레코드 규정 · TypedDict 뒤 병합에서 소거되는 타입은 소비자 없는 구조. 코드 변경 0.
- 제안: houserules #647 문면에 한 줄 — «framework 가 소유한 열린 context/kwargs dict(admin extra_context · render context · signal kwargs 등)를 값을 읽지 않고 전달만 하는 자리는 `dict[str, object]` 로 두고 ⓓ 는 ③ 유지로 닫는다(우리가 읽는 키만 즉시 좁힌다)」. 없으면 admin override 가 있는 발주마다 architect·reviewer 가 같은 반송을 반복한다.

## F4-10 — `check-context-isolation.py` ⓓ#153 이 표준 OHS 창구(builder 1 + execute 1)를 «유스케이스 호출 2회」로 계수(A12 · B0 창구 3 · 2026-09-11 00:3x · 낮음 · ⓓ 소음)

- 실측(2.18.2 · registry_gate/직접 실행 공통): `application/fortune_record/…/record_archive_service.py` `record_fortune_failure_command`(:141 `build_record_fortune_failure_use_case()` · :143 `use_case.execute(command)`) 과 `application/fortune_library/…/book_directory_service.py` 의 창구 3(:34 · :51 · :59 · B0 G2 통과 코드)이 전부 `[ⓓ#153] … 유스케이스 호출이 2회다` 로 예보됨. 실제 execute 는 각각 1회.
- 상황: dddjango 표준 창구 형태(composition root builder 호출 → execute 1회 → 예외 번역)가 그대로 후보에 오르므로 표준을 따르는 모든 OHS 함수가 ⓓ 를 받는다. exit 불산입이라 차단은 아니지만 감수자가 매 레인 같은 후보를 닫아야 한다(A12 · A3 G0 · B0 REPORT 3건).
- 제안: 호출 계수에서 `build_*_use_case()`/composition-root builder 호출을 제외하거나, «execute 호출 수」만 세도록 문면·계수를 좁힌다. 또는 builder+execute 짝이 정확히 1쌍이면 후보에서 제외.

## F4-11 — `check-domain-model.py` ⓓ#268 이 닫힌 `StrEnum` 값 객체에 «__init__ raise 없음」 후보를 낸다(A12 `FortuneFailureTicketOutcome` · B0 `BookKind` · 낮음 · 제안)

- 실측: `application/fortune_library/domain_layer/book/value_object/book_kind.py:6 BookKind`(StrEnum · B0 G2 통과) · A12 `fortune_failure_ticket_outcome.py FortuneFailureTicketOutcome`(StrEnum) 에 `[ⓓ#268] … __init__/__post_init__ 에 raise 가 없다 — 물음: Q2 이 타입 조합만으로 잘못된 값이 «불가능」한가`.
- 상황: `StrEnum` 은 정의된 멤버 밖 값을 생성 시점에 `ValueError` 로 거절하므로 Q2 의 답은 항상 «불가능」이다. 검사기가 이미 «물음」 형태로 낸 것이라 결함이 아니라 자동 판정 여지.
- 제안: `Enum`/`StrEnum`/`IntEnum` 상속 클래스는 #268 후보에서 자동 제외(또는 «닫힌 enum · 자체 검증」으로 corrected 처리).

## F4-12 — pre-gate 스텁(`raise NotImplementedError`) × `check-port-adapter-pairing.py` #376 «after_commit 본문에 on_commit 없음」 교차 오탐 — 새 UoW 를 계획하는 모든 설계에서 재발(B0 2.18.0 · A3 2.18.2 · 2026-09-11 01:14 KST · 중)

- 실측(2.18.2): `design_pregate.py:858 _class_stub` 은 base 가 정확히 `ABC` 가 아닌 클래스의 메서드 본문을 일률 `raise NotImplementedError` 로 생성한다(882–883행 · 명세에 적힌 `transaction.on_commit(callback, using="default", robust=False)` 본문은 전사하지 않음). `check-port-adapter-pairing.py:745–753` 은 `after_commit` 함수 본문을 `ast.walk` 해 `on_commit` 호출이 없으면 #376 을 발행한다. 결과 = 격리 사본의 driven UoW 스텁이 항상 #376 귀속 red → pre-gate exit 2 → G1 차단.
- 재발 실측: B0 `application/fortune_library/driven_layer/adapter/persistence/unit_of_work/book_unit_of_work.py`(안정 ID `78ca0823d417` · 2.18.0 · `pregate-report.md:1243` filtered ⓐ S1 로 수동 처분) · A3 `…/unit_of_work/item_dictionary_unit_of_work.py`(`d1f28cb44fd5` · 2.18.2 · 레인이 STOP 으로 올림 · 발주자가 같은 filtered 처분 지시). 두 레인 모두 S1 실구현의 registry_gate 가 실제 본문(on_commit · robust)을 검사하므로 실 검증에는 공백이 없다 — 문제는 pre-gate 의 결정적 오탐과 그로 인한 STOP/수동 처분 왕복.
- 제안(택1): ⓐ pre-gate 교차 필터에 «스텁 생성 파일 × #376/#566(본문 조건 검사기)」 행을 추가(95a95ccf 의 «cross(skeleton×port-adapter/usecase-dto 2행 제거 — 결정 2)」 와 같은 기계 · 스텁 본문은 전사 대상이 아니므로 본문 조건 검사기를 pre-gate 에서 not-applicable 처리) ⓑ `_class_stub` 이 UoW `after_commit` 에 한해 명세 전사 본문(또는 `transaction.on_commit(..., robust=False)` 정형 본문)을 생성 ⓒ #376 을 «구현 트리에서만」 판정(pre-gate 격리 사본 제외). 어느 쪽이든 SKILL.md:114 의 filtered 수동 처분을 매 레인 반복하지 않게 된다.

- 재발 4회째(A5 · 2.18.2 · 2026-09-11 17:04 KST): `…/unit_of_work/search_term_mapping_unit_of_work.py` 안정 ID `a679cc23d89e` · 명세 220행에 `transaction.on_commit(callback, using='default', robust=False)` 본문이 적혀 있어도 스텁은 `raise NotImplementedError` → #376 귀속 → 레인 STOP(개정 1 문구가 filtered 를 막은 것으로 읽음) → 발주자 filtered ⓐ S1 처분(개정 2). 새 UoW 를 계획하는 레인마다 STOP/처분 왕복 1회가 고정 비용으로 남는다 — pre-gate 가 `after_commit` 스텁에 `on_commit` 호출 1행을 합성하거나(#376 판정 입력만 충족 · 본문 전사 아님) #376 을 스텁 사각 자동 filtered 로 처리하는 것이 후보.

## F4-13 — 규범 문면 빈칸: discipline-reviewer «raw infrastructure 기본 경계」 vs `check-port-adapter-pairing.py` #555 «어댑터 bare raise 금지」의 관계(A3 STOP-02 · 2026-09-11 01:44 KST · 낮음 · 문면)

- 실측: A3 architect 가 discipline SKILL 의 «raw DB/SDK/network 오류는 framework 500 경로가 기본 · G1 승인된 안정 의미만 concrete 오류로 정규화」를 읽고 리포지토리 `except IntegrityError` 블록에서 알려진 UNIQUE 만 번역하고 나머지는 bare `raise` 로 raw 전파하도록 설계 → S1 `registry_gate` 가 #555 귀속 2(`information_item_repository.py:101` · `relation_kind_label_repository.py:64`). 레인은 «승인 계약 vs 검사기」 충돌로 STOP. pre-gate 는 본문을 보지 않아 G1 에서 못 잡음.
- 발주자 판정(저장소 선례 = 남은 IntegrityError 를 BC 백스톱 예외로 번역 · house `VisitIntegrityViolation` 등 · bare raise 0): 두 문면은 충돌이 아니라 층이 다름 — «어댑터가 **잡은** 벤더 예외는 계약 예외(백스톱 포함)로 바꾼다(#555)」 / «어댑터가 **잡지 않은** 인프라 예외는 raw 로 500 경로(discipline 기본 경계)」. 그러나 두 SKILL 어디에도 «잡았으면 bare raise 금지 · 백스톱 계약 예외 1 이 표준」이 한 문장으로 없어 architect 가 raw 전파를 설계로 적었다.
- 제안: architecture-ddd/db 또는 discipline SKILL 의 raw infrastructure 절에 한 문장 추가 — «어댑터가 잡은 벤더 예외(IntegrityError 등)는 계약이 선언한 실패(알려진 제약 → 구체 예외 · 그 밖 → BC 백스톱 무결성 예외 1)로 바꾸고 bare raise 하지 않는다(#555) · 잡지 않은 인프라 예외만 raw 로 흘린다」 + pre-gate 가 `except <VendorError>` 블록의 bare raise 를 설계 단계에서 예보할 수 있으면 더 좋음(본문 미전사라 어려우면 architect 체크리스트 항목으로).

## F4-14 — `check-domain-model.py` #546 «한 트랜잭션 = 애그리거트 하나」가 **함수 단위**로 쓰기 타입을 합산 — root 별 UoW 가 분리된 두 반복문도 위반(A3 STOP-05 · 2026-09-11 04:22 KST · 중 · 대리 지표)

- 실측: A3 S3 `seed_items_use_case.py` 의 `execute` 가 승인 명세대로 «관계 root 마다 `with uow: relation_repo.save_new(r)`」 뒤 «항목 root 마다 `with uow: item_repo.save_new(i)`」 를 실행(두 반복문 바깥 공통 UoW 없음 · 매 with 에 save_new 하나). 고정 앵커 registry 가 #546 귀속 1(`:45`). 검사기 `:779-816` 은 `written=set()` 뒤 `ast.walk(fn)` 으로 **함수 전체**의 save/remove 리포지토리 타입을 모아 2 이상이면 위반 — `with` UoW 경계·`__exit__` 로 갈린 트랜잭션을 구분하지 않는다.
- 발주자 판정: 계약 위반 아님(트랜잭션 하나에 애그리거트 하나 유지). waiver 대신 코드 구조 정합 — execute 는 검증 뒤 애그리거트별 private 쓰기 메서드 2개를 순서대로 호출(한 메서드 = 한 애그리거트). 동작 동일 · 생성자/공개 계약 무변(발주서 개정 5).
- 제안: `written` 을 `with` 블록(UoW context) 단위로 계수하거나, 같은 함수 안에서 서로 다른 `with` 문에 각각 격리된 쓰기는 합산하지 않는다. 최소한 문면에 «함수 단위 계수」 임을 적어 architect 가 설계 단계에서 쓰기 메서드를 애그리거트별로 나누도록 예보(pre-gate 후보).

## F4-15 — `check-port-adapter-pairing.py` #557 «벤더 오류 코드 위층 판정」이 Compare 왼쪽 속성 **이름**(code · errno · status_code)만 보고 판정 — 도메인 자연 코드 `relation.code` 비교를 확정 위반으로 분류(A3 STOP-05 · 2026-09-11 04:22 KST · 중 · 오탐)

- 실측: `seed_items_use_case.py:66` `if relation.code not in existing_codes`(관계 종류 자연 코드 · `_SeedRelationKind.code: str` · `existing_codes` 는 `exists_by_code` bool 결과 집합). 검사기 `:1165-1171` 은 `isinstance(node, ast.Compare) and isinstance(node.left, ast.Attribute) and node.left.attr in ("code","errno","status_code")` 만 검사 — 값의 타입·선언·출처(예외/응답 객체)를 보지 않아 «code」 라는 흔한 도메인 속성 이름이 전부 걸린다.
- 발주자 판정: 계약 위반 아님. waiver 대신 존재 판정을 관계당 1회 수행해 (관계 · 존재 여부) 쌍으로 분할하는 형태로 정합(조건식에 `.code` 비교 없음 · 중복 조회 0 · 동작 동일 · 발주서 개정 5).
- 제안: 판정 대상을 «except 핸들러에 바인딩된 이름 · 어댑터/SDK 응답 객체에서 온 이름」 의 속성으로 한정하거나, 같은 BC 의 command/domain dataclass 필드 `code` 는 제외. 최소한 ⓓ 후보로 내려 감수자가 «출처 = 벤더 오류인가」 를 판정하게 한다.

## F4-16 — `registry_gate.py` 앵커 차분이 `check-layer-skeleton.py` #642 «출생 하한 50행」 레코드를 행 수 문면까지 포함해 대조 → 앵커에 있던 소형 파일을 **편집(축소)** 하면 «신규 출생」으로 재귀속(A2① STOP 5 · 2026-09-11 09:48 KST · 중 · 앵커 대조 한계)

- 실측: A2① S2 가 `application/fortune_catalog/application_layer/catalog_inquiry/{list_fortune_types,select_visible_fortune_candidates,resolve_fortune_support}/*_use_case/*_source_unavailable.py`(앵커 3121071d 에 존재 · 각 20여 행)에서 삭제된 관계표 classmethod `from_relation_table_load_failure` 를 지우자 `registry_gate.py . --anchor 3121071d…` 가 `[#642] … 부품 21행 — 출생 하한 50행 미만(신규 여부는 게이트 앵커 차분이 가른다 · 기존분은 잔존 보고)` 3건을 **귀속(N∖L)** 으로 냈다. 파일은 신규가 아니고 편집은 축소만인데, 앵커 레코드의 문면(«부품 NN행」)이 바뀌어 같은 레코드로 매칭되지 않는 것으로 보인다.
- 기대: #642 의 «신규 여부는 앵커 차분이 가른다」 문면대로 **파일 출생**(앵커에 경로 부재)만 귀속으로 세고, 앵커에 있던 파일의 행 수 변화는 잔존(L∩N)으로 분류. 제안 = 레코드 identity 를 (검사기 · 규칙 · 경로)로 두고 문면의 가변 수치(행 수)는 identity 에서 제외 · 또는 #642 는 경로 출생 여부를 직접 `git diff --name-status --diff-filter=A <anchor>` 로 판정.
- 우회 금지 확인: 50행 padding·파일 분리·`ignored` 처분은 규범 위반이라 발주자가 **waiver 분리**(exact 3 레코드 · 조건 = 앵커 존재 + 삭제 편집만 · REPORT 별개 보고)로 처리.

## F4-17 — `check-layer-skeleton.py` #488 / `check-port-adapter-pairing.py` #218·#225 가 git 에서 삭제된 포트·어댑터 폴더의 **`__pycache__` 잔재**를 «폴더 존재」로 읽어 고정 파일 부재 10건을 귀속(A2① STOP 5 · 2026-09-11 09:48 KST · 중 · 재발 3회째)

- 실측: A2① S2 가 `application/fortune_catalog/application_layer/port/relation_table/**` 와 `driven_layer/adapter/relation_table/**` 를 `git rm` 했으나 작업 트리에 `__pycache__/*.pyc` 가 남아 폴더가 존재 → `[#488] …/port/relation_table/exception.py: 고정 파일 부재 — 비면 빈 파일로 만든다` 등 8건 + `[#218] 계약 파일 이름이 폴더와 다르다([])` · `[#225] exception.py 가 없다` 2건. 같은 현상은 B0(2026-09-10) · A11 발주자 G2 에서도 각 8건(발주자 메모 registry-gate-stale-pycache-dirs).
- 기대: 스켈레톤·포트 검사기가 폴더 존재 판정에서 `__pycache__` 만 있는(또는 `git ls-files` 0 인) 디렉터리를 «없음」으로 다룸 · 또는 registry_gate 가 실행 전 `git ls-files` 기준으로 폴더 목록을 만든다.
- 임시 처분(레인): `git ls-files <경로>` 0 확인 → `git clean -fdX <경로>` → 빈 폴더 rmdir → 재실행(0 기대). 플러그인 편집 0.

## F4-18 — `design_pregate.py` 가 machine symbols 의 **애그리거트/엔티티 필드를 가진 application result DTO**(#202)와 그것을 투영하는 OHS 의 domain import(#95/#96)를 예보하지 못함 → G1 exit 0 뒤 S3 실물 registry 에서 귀속 6(A4 STOP · 2026-09-11 10:22 KST · 중 · pre-gate 사각)

- 실측: A4 G1 정본 `.dddjango/20260911-0651-fortune-library-answer-assembly/design-spec.md` machine symbols 가 `_ActiveAnswerOutlineData {outline: AnswerOutline, visual_block_kinds: tuple[VisualBlockKind, ...]}` · `GetActiveAnswerOutlinesResult {outlines: tuple[_ActiveAnswerOutlineData, ...]}` · `GetActiveVisualBlockKindsResult {visual_block_kinds: tuple[VisualBlockKind, ...]}` 를 고정했고 pre-gate `--check-report` 는 exit 0(귀속 예보 1 = #376 filtered) 이었다. S3 구현 뒤 `registry_gate.py . --anchor 3121071d…` 가 `check-usecase-dto-placement.py #202` 3(result 가 애그리거트 보유) + `check-context-isolation.py #95` 2 + `check-event-publish.py #96` 1(OHS 잎이 `OutlineRow`·`VisualBlockKind` import)을 귀속 → red.
- 원인 추정: pre-gate 가 (a) symbols 의 result 필드 타입이 같은 명세의 aggregate/entity 이름인지 대조하지 않고 (b) OHS 절 imports 가 contract/composition 만 열거되면 «result 내부를 투영하려면 domain 타입을 알아야 한다」는 파생 import 를 시뮬레이션하지 않는다(설계 STOP 문면 «G1 pre-gate 는 aggregate field 와 누락된 result-domain imports 를 결합하지 못해 예보하지 않았다」).
- 기대: pre-gate 가 machine symbols 에서 `*Result`/`*Out` DTO 필드 타입 ∈ {aggregate, entity} 이면 #202 를 예보하고, driving 잎(OHS) 이 그런 result 를 소비하면 #95/#96 후보로 예보. 발주자 처분 = 설계 정정(투영 DTO · OHS domain import 0 · A3 `DictionaryItem` 선례) · waiver 0.

## F4-19 — `design_pregate.py` Phase 1 기본 판형에서 **미추적(오버레이) 실존 add 의 탈출구 0** — `baseline_form_errors` 문면 «오버레이 실존은 판정에 넣지 않는다」와 `materialize` 의 «add 충돌(실존)」 판정이 어긋남 · `update` 로 적으면 «update 대상 부재」(A5 STOP · 2026-09-11 16:52 KST · 중 · 판형 불일치)

- 실측(2.18.2 · 실행 트리 digest `4a435c2f6d600de6`): A5 레인 coordinator 가 G0 에서 발주서 필수 REPORT(`docs/superpowers/orders/lane/REPORT-fortune-library-a5.md` · 적재 버전 이력 기록용)를 먼저 쓴 뒤(미추적 · HEAD a6e3692d 부재) architect 명세 file-plan 에 그 경로가 들어갔다. ① `update` 태그 → `baseline_form_errors`(design_pregate.py:1953) «update 대상 부재: … 기준선 a6e3692d3e9f 에 없는 경로는 add 다(재라벨 도피 금지)」 exit 3(07:24:57Z · 블록 해시 13d8146d56a3) ② 지시대로 `add` 로 교정 → `materialize`(:1310) «add 충돌(실존): … 계획과 실물의 모순은 그 자체가 발견이다」 exit 3(07:49:47Z · a357988fad5a). 두 실행 모두 기본 판형 `design_pregate.py <spec> . --report <report>`(`--base` 미명시 · 리포트 헤더는 «(--base HEAD)」로 표기). 원출력 `.dddjango/20260911-1549-fortune-library-search-mapping/pregate-{first,revision-1}.log`.
- 원인: `baseline_form_errors` docstring 은 «오버레이 실존은 판정에 넣지 않는다(미커밋 기실현 add 의 재라벨도 기준선 부재라 red)」로 add 판정을 기준선 기준으로 못 박지만, `materialize` 는 격리 사본(기준선 + dirty overlay) 에 대상이 «존재」하면 add 를 red 로 세우고 그 docstring 은 «사본에 실존하는 add 는 기준선 트리 실존뿐」이라 전제한다(:1302). 이 전제는 `lift_realized_adds`(:1101) 가 오버레이 실존 add 를 걷어낸 뒤에만 참인데, 그 함수는 `explicit_base`(`--base` 명시) 일 때만 동작한다(«--base 미지정이면 공집합」). 결과 = Phase 1 기본 판형에서 «기준선 부재 ∧ 오버레이 실존」 경로는 add(materialize red)·update(baseline red) 어느 태그로도 통과 불가하고, 오류 문면은 «기준선 실존」을 암시해 원인을 오귀속한다. coordinator SKILL 은 `--base HEAD` 를 «Phase 2 진입 후 재발화 판형」으로만 기술해(:116 ②) 레인이 Phase 1 에서 이를 쓸 규범 근거가 없어 STOP 으로 올렸다.
- 발주자 처분(플러그인 편집 0): REPORT 는 발주서 소유 레인 기록이고 registry 판정 대상이 아니라 file-plan 행이 아님 → architect 반송으로 그 1행 삭제(검출 집합 변화 0 · 선례 = `.dddjango/**/design-spec.md` 전부 `docs/` 행 0 · A3 REPORT 미추적 상태 G1 green). 발주서 개정 1.
- 기대(후보 2 중 하나): (a) Phase 1 기본 판형에서도 «기준선 부재 ∧ 오버레이 실존 add」를 기실현 add 로 처리(스텁 대체 예보 · already-built 기록 — 지금은 `--base` 명시 때만) 또는 (b) materialize 의 add 충돌 문면을 기준선 실존과 오버레이 실존으로 나누고 후자에 «미추적 실물이 있다 — 커밋/stash 하거나 --base HEAD 재발화」 처방을 병기. 별건 후보: file-plan 이 registry 판정 밖 경로(`docs/**` 등 비-.py) 를 받을 때의 처리 기준을 architect SKILL 에 한 줄(«코드 트리 밖 문서는 file-plan 밖」 또는 «허용·스텁 0」).

## F4-20 — `check-transaction-boundary.py` #195 가 «팩토리 호출로 태어난 이름」을 `for` 원소·컴프리헨션 원소로 전파하지 않음 → 명세가 요구한 «전량 생성 → 전량 검증 → 없는 행만 저장」 순서의 정당한 코드가 귀속(A5 STOP-03 · 2026-09-11 18:40 KST · 중 · AST 추적 한계)

- 실측(2.18.2 · registry_gate 앵커 a6e3692d · 귀속 1): `[#195] application/fortune_library/application_layer/search_term_mapping/import_search_term_candidates/import_search_term_candidates_use_case.py:N: save/remove 인자 `mapping` — 같은 함수 안에서 루트 메서드 호출을 받은 적이 없다`. 실물 = `mappings: tuple[SearchTermMapping, ...] = tuple(SearchTermMapping.create_pending(...) for candidate in command.candidates)` → `for mapping in mappings: self._reference_policy.validate(mapping, …)` → `for mapping in mappings: if self._repository.load_by_identity(mapping.identity) is None: self._repository.save_new(mapping)`.
- 원인: `_check_execute_body`(468~515행)는 `Assign/AnnAssign(target=Name, value=Call)` 에서만 `factory_born` 에 target 이름을 넣는다(여기선 `mappings`). `ast.For` target(`mapping`)·컴프리헨션 원소로의 전파 분기가 없고, 저장 인자 이름 `mapping` 은 `method_called`/`factory_born` 어디에도 없어 #195. 검사기 33~35행 «정직 기록」(«도메인 팩토리 호출로 태어났으면 통과」)과 실측이 어긋난다. 도메인 서비스 호출 `self._reference_policy.validate(mapping, …)` 은 수신자가 Attribute 라 `method_called` 에 안 들어가는데 이는 의도된 정의(루트 메서드 아님).
- 왜 회피 불가: «첫 쓰기 전 전체 검증」 계약은 집합을 두 번 순회해야 하므로 저장 인자는 필연적으로 반복 변수다. 우회 후보(원소마다 no-op 루트 메서드 호출 · 저장 직전 변수 재대입 · 저장소 집합 메서드 신설)는 전부 «AST 인식만을 위한 재작성」 또는 설계 변경이라 규율 위반.
- 발주자 처분: waiver 레코드 1(A5 발주서 개정 3 · REPORT 별개 보고 · 파일 구조 유지). 기대: `for target in <factory_born 이름>` 과 컴프리헨션 `for x in <factory_born>` 의 원소 이름을 factory_born 으로 전파(iterable 이 `tuple/list/frozenset(<genexpr of Call>)` 이면 원소도 팩토리 출생) — 또는 «집합 정렬 저장」 정형(`tuple(Factory(...) for …)` → `for m in …: repo.save(m)`)을 화이트리스트로.
