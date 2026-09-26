# 검토 I — 로드맵 3 구현 적대 검토 (2026-09-27)

- 대상: 작업 트리 미커밋분. `design_pregate.py`(+Codex byte 미러) · 러너 · 새 픽스처 3 · graph-owned 규범(Coordinator · architect · houserules §3 R-3500/R-3501) · Codex 의미 미러 · #236 문면 · REQUEST_GUIDE · DEVELOPMENT §6.
- 대조 기준: 설계 v2 · 검토 H(§3 major H-M1~M5 · minor) · 규범 매핑표 · 결정 7.
- 실행: `pregate_fixture_run.py` **PASS**(1분 38초) · `pregate_field_report_smoke.py` **38 OK** · `gen_pregate_symbol_kinds.py --check` in-sync.
- 탐침은 scratch `review-I/` 에서만 돌렸다: `probe_cr.py`(check-report 세탁 경로) · `probe_s2.py`(#574 예보 가장자리) · `probe_inflow.py`(유입 적용 I/O).
- 저장소 쓰기는 이 문서 하나뿐이다. `make verify` 는 돌리지 않았다. 현장 저장소 접근 0 · Serena·Graphify 미사용.

## 판정

**조건부 통과. blocker 0 · major 1 · minor 9.**

- 설계 v2 와 H 의 major 5건은 모두 구현·규범에 들어갔다.
- 남은 major 는 하나다. H-M2 가 제안한 대로 «기준선 대조 누락»을 «마지막 절이 명시 재예보일 때»에만 걸었는데, 이 범위로는 가장 쉬운 치환 형태(`--base` 를 빼고 재발화)를 기계로 잡지 못한다.
- 이상 없이 확인한 것:
  - Codex byte 미러 4종이 같다(`design_pregate.py` · `check-port-adapter-pairing.py` · REQUEST_GUIDE · houserules final).
  - Codex 의미 미러가 Coordinator 와 삽입 43/43 일치하고, architect 도 전건 일치한다.
  - 경계 행 접두는 규범 문면과 `RUN_BOUNDARY_PREFIX` 가 바이트까지 같다.
  - 규범 md·ttl 에 옛 `--base <G1 기준선 SHA>`·WIP stash 판형 재진술이 없다(스크립트 주석의 «규약 준수 실행과 같다»는 동치 설명이다).
  - #573·#574 인용이 검사기 실물과 맞는다: #573 은 `_check_capability_folder` 안에서만 돈다(`check-port-adapter-pairing.py:242`). #574 는 application_layer 의 `_in` 생성 호출만 본다(`:1343-1358`).
  - wiring 은 R-3500 enforcedBy 두 검사기 · R-3501 delegatedTo reviewer 다.

## major

| # | 발견 | 근거 | 실패 시나리오 | 수정 |
|---|---|---|---|---|
| I-M1 | **HEAD 판형 재발화가 `--expect-base` 의무를 지운다**(기준선 치환 세탁 경로가 남는다) | `design_pregate.py:3167` — `explicit_refire` 가 마지막 절 하나만 본다 · `:3176` 의무 조건. 규범 `dddjango.md:102` 의 기본 실행 판형에는 `--base` 가 없다. 설계 v2 §3.2 는 «리포트에 명시 절이 **하나라도** 있으면 의무»였다 | Phase 2 반송 뒤 Coordinator 가 102행 판형(무 `--base`)으로 재실행한다. 그러면 절이 «초기 예보»가 되고, 기준선은 레인 구현·머지를 포함한 HEAD 가 된다(F4-21 치환과 같은 효과 — update 대상이 전부 «실존»이 된다). G2 check-report 에서 `--expect-base` 를 빠뜨리면 **exit 0** 이다. 앞에 명시 재예보 절이 있었어도 exit 0 이다(탐침 A: `[초기 G1, 명시 G1, 초기 HEAD]` · 기대 없음 → exit 0). `--expect-base` 를 주면 «기준선 치환»으로 잡힌다(탐침 A′). 즉 기계 집행이 정확히 «빠뜨림» 경로에서 빠진다 | ① 의무 트리거를 넓힌다. «마지막 실행 경계 뒤(경계가 없으면 리포트 전체) 절 가운데 명시 재예보가 하나라도 있으면»으로 바꾼다. 그러면 뒤이은 HEAD 판형 절이 기준선 대조로 치환에 걸린다. ② 남는 사각(Phase 2 첫 재발화부터 HEAD 판형)도 닫으려면 Coordinator 가 Phase 2 첫 파견 때 실행 줄과 함께 `pregate-report.md` 에 `- pre-gate 기준선 — <sha>` 행을 append 한다. check-report 가 이 행 뒤의 절에 대해 git 0회로 기준선을 대조하게 한다(R-3434 무저촉 · 경계 행과 같은 꼴). 러너에 «명시 → HEAD 판형» 사례를 더한다 |

## minor

| # | 발견 | 근거 | 실패 시나리오 | 수정 |
|---|---|---|---|---|
| I-m1 | **실행 경계 행 하나가 모든 대조를 끈다**. 명시로 준 `--expect-base` 도 조용히 무시된다 | `:3166` 은 절 뒤 어디든 접두 일치만 본다. `:3168`·`:3174` 에서 해시가 같으면 digest·명시 의무·기대 기준선을 모두 건너뛴다. 경계 행은 위임 가능한 «기계 기록»이다(`dddjango.md:217`) | 치환 기준선의 명시 재예보 절 뒤에 `- 실행 경계 —` 1행만 있으면 `--expect-base <G1>` 을 줘도 exit 0 이다(탐침 B·B′). 요약에는 «앞 실행 예보(명세 불변) · green»만 남는다. G2 배너만 읽는 사람은 기준선이 대조된 것으로 안다. 고의 기입이 필요해 major 는 아니다 | 경계 행에 G0 값을 의무로 싣는다. check-report 에 `--run-start <실행 줄 G0 값>` 을 받아 값이 맞는 경계만 인정한다. 앞 실행 정합일 때 `--expect-base` 가 주어졌으면 요약에 `기준선 대조 생략(앞 실행) · 리포트 <x> · 기대 <y>` 를 싣는다 |
| I-m2 | **#574 예보 거짓 음성**: typing 컨테이너 인자는 후보조차 안 뜬다 | `:1779-1790` — 해소기가 미해소 컨테이너 머리에서 slice 로 내려가지 않는다. 그래서 `…In` 이름이 `referenced_names` 에 들어가지 않고(`:2061`) 후보 목록도 비게 된다 | typing import 행이 없는 add 포트(현장 명세의 기본형)에서 `Optional[EntryIn]` · `Sequence[…]` · `Iterable[…]` · `Mapping[str, …]` · `Annotated[…]` 인자는 결과 `[]` 다. `list[…]`·`dict[…]`·`X \| None` 은 확정으로 잡힌다(탐침). 같은 이름 클래스가 다른 능력 폴더에서 반환되면 확정이 후보로 떨어진다(`:2101` — `maybe` 가 해소된 반환의 이름도 담는다) | 인자 주석도 `ast.walk` 로 `…In` 이름을 모아 신원 미해소분을 후보로 둔다. S-2 해소기(`_PortTypes`)에서 미해소 typing 머리(`Optional`·`Sequence`·`Iterable`·`Mapping`·`Annotated`·`Collection`)를 투명 컨테이너로 다룬다 |
| I-m3 | **update legacy 서명 비교가 문면 차이에 민감하다** · 서명을 바꾼 legacy 에는 처분 출구가 없다 | `:2052` 는 `ast.dump(args)` 를 그대로 비교한다 | 실물 `put(self, item: 'EntryIn')` 을 명세가 `item: EntryIn` 으로 다시 적으면, 손대지 않은 legacy 가 확정 #574 가 된다(탐침). `*, force: bool = False` 를 더한 legacy 도 확정이다. filtered 는 금지이고, ignored 는 legacy-debt 행이 있어야 하는데 registry 는 포트 인자를 보지 않아 빚 행이 없다. 그래서 legacy 타입 개명(어댑터·호출부 연쇄)이 강제된다 | 비교 전에 문자열 주석을 파싱해 정규화한다. 서명만 바뀐 legacy 의 기존 `_in` 인자는 후보로 두거나, 규범에 처분(슬라이스 0 정리 · STOP)을 한 줄 적는다 |
| I-m4 | **선언 확정 #574 의 filtered 금지가 산문뿐이다** | `_disposed`(`:3118-3125`)는 어떤 ID 든 `**filtered**` 를 인정한다. 선언 확정 소절 행은 `[#574]` 를 싣는다(`_declaration_lines`) | 규범(`dddjango.md:102`)이 막은 «S2 인용 filtered»가 check-report 를 그대로 통과한다. 이번 수리의 F M-4 처분이 기계로는 집행되지 않는다 | `선언 확정` 소절에서 `[#574]` 행의 ID 는 `**filtered**` 를 불인정하고 «#574 filtered 불가» 불비를 낸다(경로 등급 규칙에도 같은 틀을 쓸 수 있다) |
| I-m5 | **유입 적용 I/O 가 fail-closed 가 아니다**(트레이스백) | `apply_inflow` `:1276-1310` 은 OSError 를 감싸지 않고, `main` 은 RunError 만 잡는다(`:3513`). `_dirty_count`(`:3340`)와 파싱 단계 stub 의 `_executor_stamp`(`:3357`·`:3365`·`:3374`)는 `try` 밖이다 | 디렉터리를 같은 이름 파일로 바꾼 승인 머지(`pkg/x/a.py` 삭제 + `pkg/x` 추가)에서 `IsADirectoryError` 가 잡히지 않고 샌다(탐침 `probe_inflow.py` — 삭제 후 빈 디렉터리가 남는다). 레인 커밋이 기준선 symlink 를 디렉터리로 바꾸고 유입이 그 아래 파일을 더하면, `write_bytes` 가 symlink 를 따라 사본 밖에 쓴다 | `apply_inflow` 전체에서 OSError 를 RunError 로 바꾼다. 삭제 뒤 빈 부모 디렉터리를 `rmdir` 한다. 쓰기 전에 `target.parent.resolve()` 가 사본 루트 안인지 확인한다. 위 두 호출을 `try` 안으로 옮긴다 |
| I-m6 | **충돌 해소 제외 경로의 안내가 틀렸다**(H-m6 ① 잔여) | `annotate_post_baseline_defects` `:2821`·`:2831` 은 `inflow.changes` 만 제외한다 | 플래그를 이미 준 재발화에서, 충돌 해소분이라 I 에서 빠진 경로의 결손에 «발주자 등재 머지 유입이면 `--approved-merge-file`» 이 또 뜬다. 라우팅이 되풀이된다 | `inflow.conflict_resolved` 경로면 «플래그 동반 중 · 충돌 해소분 = 레인의 변경 — G2 귀속 판정 · 계획에 없으면 STOP» 갈래를 낸다 |
| I-m7 | **역방향·합성 머지 의심 진단을 싣지 않는다** | 로더는 `parent2_only_head` 를 계산하고 registry 는 표면화한다(`registry_gate.py:485`). pre-gate `header_line`(`:1213`)은 싣지 않는다 | 레인 내부 가지 머지가 목록에 오르면 레인 구현이 «유입»으로 기준선 사본에 실린다. pre-gate 헤더에는 흔적이 없다 | 헤더 «승인 유입» 행에 `역방향/합성 의심 <sha12>` 를 병기한다(exit 무변 · registry 와 같은 재료) |
| I-m8 | **새 실행 경계 뒤 캐시 skip 이 옛 기준선 예보를 G1 근거로 쓴다** | 규범 ① skip 조건은 해시·digest 뿐이다(`dddjango.md:104`). check-report 는 경계 뒤 해시 일치를 정합으로 본다(`:3168`) | 새 실행 G1 에서 명세 블록이 불변이면, 앞 실행 기준선(수 주 전)의 예보가 skip 으로 이어진다. M-3 한정(G1′ 생략)보다 넓게 열린다 | skip 조건에 «마지막 예보 절이 마지막 실행 경계 뒤»를 더한다. G1′ 생략 경로는 pre-gate 를 부르지 않으므로 영향이 없다 |
| I-m9 | **문면·기록** | houserules `final.md:270` · 설계 v2 §5-4 · `design_pregate.py:65` · DEVELOPMENT §6 | ⓐ R-3501 «메서드의 반환은 `<data>_in` 이다»가 `-> bool`·`-> None`·도메인 값까지 덮어 읽힌다(#485 예시 `has_shipped()`). reviewer 오탐 재료다. ⓑ «옛 `_out` 반환을 새 메서드에 옮겨 쓰지 않는다»와 «102곳은 기능 요청에서 건드리지 않는다»가 겹친다. 같은 자료를 새 메서드가 돌려줄 때 중복 `_in` 신설을 강요하는데 처분 기준이 없다. ⓒ BC 포트 반환 우주에서 framework 를 뺀 것은 설계 v2(«같은 BC + framework»)와 다르다. 규범 R-3500 과는 맞으니 결정으로만 기록한다. ⓓ 모듈 docstring `:65` «격리 사본(기준선 + dirty overlay + 명시 전사)»가 옛 문면이다. ⓔ DEVELOPMENT §6 릴리즈 창에 «진행 레인이 있으면 기다린다»가 없다. ⓕ «설계 리뷰·감수가 본다»인데 wiring 은 reviewer 하나뿐이다 | ⓐ «이름 붙인 포트 자료를 돌려주면 `_in`»으로 한정한다. ⓑ 재사용 시 처분(빚 기록 또는 슬라이스 0) 한 줄을 둔다. ⓒ 처분표에 이탈을 기록한다. ⓓ 사본 문면을 고친다. ⓔ «있으면 착륙까지 릴리즈 보류» 한 구를 더한다. ⓕ 문면과 wiring 중 하나에 맞춘다 |

## 참고 — 확인만 한 것

- S-3 오버레이 생략 · 골격 가드 기준선화(유입 적용 뒤 `baseline_bcs` · H-m6 ②)는 설계대로다. E5·E6 도 통과했다.
- S-1 유입 계산(참여 머지 · 경로별 마지막 머지 · verbatim · 삭제 · gitlink)은 설계대로다. 빈 사슬(기준선 = HEAD)은 공집합으로 안전하다.
- digest 는 두 런타임이 같다(스크립트 폴더 `*.py`·`*.json` 전량 byte 동일). 런타임에 스크립트 폴더로 쓰는 파일도 없다.
- scratch 의 `verify-step3.log`(01:21) RED 두 건은 지금 작업 트리에서 이미 재소성·갱신됐다: `pregate_symbol_kinds.json` 은 `--check` in-sync이고, `findings_count_matrix.py` 는 #236 문면 변경 골든이 수정돼 있다. 진행 중인 `make verify` 결과로 최종 확인한다.
