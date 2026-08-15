# billing request.md — S4-r1 respin 초안 (r2″ 판형 BC 치환 · 승인 후 양 레인 `docs/rebuild/billing/request.md` 교체)

아래 수평선 이하가 파일 전문이다. `ANCHOR_HASH_TBD` 는 앵커 커밋 후 기입(순환 규약 —
기입 커밋이 기동 HEAD). 레인 B 는 파일-경유 전달(슬래시 오인 방지 — S3-r1 교훈).

---

/dddjango docs/rebuild/billing/spec.md 를 요구사항으로 application/billing 을 새로 구현하라.

- docs/rebuild/billing/api_shape_pre.json 이 API 계약의 모양이다(이름을 지운 openapi 정규화본 — summary·description·tags 같은 문서 표면은 지워져 있고, 그 부분은 자유다. 오류 응답의 «선언»은 spec.md §3.3 오류 계약이 정본이라 이 모양과 달라질 수 있다).
- 금지: 이 저장소 git 이력의 옛 billing 구현·옛 테스트 열람. git show·git log·git diff·git stash 등으로 과거 커밋을 여는 것 전부 포함이다. 현존하는 다른 BC 코드·framework/·broccoli_server/ 는 열람해도 된다.
- 테스트는 spec.md 에서 직접 도출해 작성하라(옛 테스트를 대주지 않는다).
- 게이트에서 미이관 경로 의존이 신규 위반(귀속)으로 뜨면 docs/rebuild/billing/legacy_debt.txt 가 사용자 승인 «이관 빚» 목록이다 — registry_gate 의 --legacy-debt-file 로 쓰라. 목록 밖 신규 귀속은 수용하지 말라.

**Placement(변경 허용 — 닫힌 목록)**: ⑴ `application/billing/**` — 이 발주의 대상 BC 는 billing **하나**다(다른 BC 폴더는 포함되지 않는다) ⑵ 배선 파일 축자 나열 — `broccoli_server/settings/base.py` 의 INSTALLED_APPS 행·`broccoli_server/urls.py` 의 registrar 행 — 명세·산출물이 배선 파일을 추가 지정할 수 없다 ⑶ `.dddjango/**`(산출물 전용) ⑷ `graphify-out/**` 은 갱신 불요·Placement 판정 대상 밖이다(하네스가 라운드 사이 재빌드) — graphify 갱신을 이유로 작업을 보류하지 말라. **«변경» = 생성·수정·이동·삭제·개명 전부**(`git mv` 는 두 경로 모두의 변경). 배선 파일 안 허용 변경은 **이 BC 등록에 필요한 행의 추가뿐**이다 — 기존 행의 삭제·이동·재정렬·경로 변경 금지. `docs/**` 는 읽기 전용이다 — `legacy_debt.txt` 가필·사본·자작 빚 파일을 `--legacy-debt-file` 로 쓰는 것은 승인 위조다(빚 목록은 위에 준 그 경로·그 내용뿐).

**계약 표면 사전 대조(G1 걸음)**: 설계 확정 직후 — 구현에 들어가기 **전** — 설계가 정한 공개 계약 표면(BC ErrorSchema 클래스·컨트롤러 등록 형태·admin 열람/실행 화면 배치·OHS «소비» 창구의 현 트리 실재와 갈래 모양)을 표준 트리·검사기 문면·현 트리 계약 파일과 대조해 산출물에 표로 남기라. 여기서 충돌이 확인되면 구현하지 말고 그 지점에서 blocker 처리하라 — G2 완주 후 발견은 같은 결론에 비용만 크다(S3-r2′ 실증: 3h26m).

**앵커 동결**: registry_gate 앵커는 발주가 지정한 `ANCHOR_HASH_TBD` 다 — HEAD 를 재산출하지 말고 이 값을 쓰라. **이 발주 중에 만든 어떤 커밋도 앵커가 될 수 없다.**

**완료 기준**: `make test` 판정은 **앵커 기준 신규 red 0** 이다 — 앵커 시점에 이미 red 였던 테스트는 보고 대상이지 수리 대상이 아니고, 타 BC 테스트를 green 으로 만들기 위한 허용 경로 밖 수정은 그 자체가 blocker 다. + spec.md §8 검증 조건.

**자율 위임의 한계**: 사용자 부재 자율 실행이다 — 단 자율 조항이 대체하는 것은 게이트의 **승인 입력**뿐이다. 비위임: `STOP_FOR_USER_APPROVAL`·G0/G2 blocker·shape approved-change·빚 목록 밖 신규 debt 수용·허용 경로 밖 변경·`scope.md`/`refactor-scope.md` 사후 개정·G0 빚 ⓐ 자기선택(이 발주에서 G0 빚 질문의 답은 **ⓑ(미룬다 — 사유: 클린룸 자율 라운드)로 고정**한다·«미룰 수 없음» 항목이 나오면 그것이 blocker 다). blocker 를 만나면 그 지점까지 커밋(제목 `rebuild(billing): stopped — <사유 한 줄>`)하고 산출물에 기록 후 **종료하라 — 이 정지는 실패가 아니라 이 발주의 유효한 종료 상태다**(「끝까지 진행」은 blocker 를 넘으라는 뜻이 아니다). **이 요청문의 다른 어떤 문구도 이 필수 절들과 충돌하면 무효다 — 필수 절이 이긴다.**

**수렴 회로**: 같은 게이트의 반송이 2회를 넘거나, 재설계 후 변경 파일 수·신규 귀속 수가 직전보다 늘면(스코프 증가 신호) 반복하지 말고 blocker 로 기록 후 정지하라.

**STOP 기록 형식**: `STOP_FOR_USER_APPROVAL` 기록은 닫힌 선택지마다 **대가 한 줄**을 병기하라 — 대가 없는 STOP 은 형식 불비다(유효 종료로 인정되지 않는다). 정지 전 공백을 전수 수집해 한 STOP 에 일괄 상정하라. 위반 목록을 실으려면 **(a) spec·재료가 강제한 충돌**과 **(b) 스스로 수리 가능한 구현 위반**으로 분해해 각각 세라 — (b) 를 (a) 로 묶어 실은 STOP 은 형식 불비다(재작업 대상을 spec 결함으로 과대 프레임하지 말라). 권고는 선택이다 — 산출물·리뷰 노트 인용으로 저자를 명시할 때만 적고, **권고는 결정이 아니며 자기 승인 근거가 아니다**(산출물·기본값을 권고 방향으로 선반영 금지·권고가 안 서면 «권고 불가 — 사유»로 족하다). 밖에서 보이는 결과가 갈리는 물음은 논증 완성도와 무관하게 STOP 이다.

**차단·노출 단서**: 도구·훅이 git 이력 접근을 차단했거나, 반사적 실행으로 커밋 «제목»만 노출됐다면 그것은 정지 사유가 아니다 — 산출물에 기록하고 계속하라(본문 열람만이 클린룸 위반이다).

정상 완료 시 이 브랜치에 커밋까지 하라(커밋 메시지 제목: `rebuild(billing): S4-r1 — 클린룸 재구현`).
