# T3 적대 리뷰 — architecture-db-final (spec + worksheet)

- 대상: `workspace/eval/t3/specs/architecture-db-final.spec.json` · `workspace/eval/t3/worksheets/architecture-db-final.md`
- 대조: 발주서 · T3-authoring-brief · authoring §13~§16 · 원문 `dddjango/skills/architecture-db/references/final.md`(736행 현물 — 발주서와 일치) · `dddjango/scripts/check-*.py` 27종 docstring 전수 실독 · `workspace/plan/2026-08-11-rule-owner-map.md` · `dddjango/commands/dddjango.md` checker registry(113~) · `dddjango/scripts/checker_registry.py` · `dddjango/skills/architecture-db/SKILL.md`
- 기계 검증 재현(2026-08-22 재실행): `ontology_migrate.py`(--write 없이) **exit 0 재확인** — 28절 · 블록 179 · Work 105. 블록 연속/비중첩/절 커버·무소유 0·basis 공란 0을 spec JSON 독립 파싱으로 재확인. 행 커버리지·byte 등가는 도구가 보장하므로 아래는 전부 판단 축 지적이다.
- census 재계수: 발주서 28절 합 106 ↔ spec 105, 차 −1은 s016-3.4 한 건 — worksheet 판정(§15 정본 1곳·발주서 과대 산정)이 발주서 restate 열·s019-4.2 «정본 지정» 비고·파일럿 판례와 정합함을 확인.
- 판정 요약: **high 1 · medium 6 · low 13**. (2026-08-22 재검 패스 — 전 판(high 1·medium 6·low 8)의 M-3 «registry #10 허위»는 반증이 나와 low로 강등·교정, 배선/재진술 신규 low 4건·medium 1건 추가.)

## HIGH

### H-1 [배선] s043-9.6/b13 (#63) — enforcedBy=check-mechanism-ownership 은 이 규범의 중심 사건을 못 문다
- 규범: «add 된 동시성 테스트는 결정적 CAS-충돌 주입이 기본 — 그 목적의 커스텀 DB 백엔드 교체 금지» (원문 410행: 스레드 기반 race 재현을 위해 연결 메커니즘을 커스텀 백엔드로 바꾸지 않는다 — implementation-test §20.4/§20.5 테스트 mechanics 문맥).
- 반박: check-mechanism-ownership ⑴ AND 게이트의 1조건은 docstring 문면 그대로 **«프로덕션(비테스트) settings 의 DATABASES ENGINE 이 stock 이 아님»**이다. 이 규범의 주어는 «테스트 목적» 백엔드 교체이고 그 실물은 통상 테스트 settings·테스트 패치에 산다 — 게이트가 명시적으로 배제하는 영역이라 중심 사건에서 발화하지 않는다(프로덕션 settings 로 우회한 변종만 잡힌다). 같은 spec 의 다른 basis 들은 부분 커버 한계를 병기했는데(«ACL 경유 축만» 등) 이 건만 한계 없이 기계 커버를 주장하고, basis 인용이 ⑴의 «프로덕션(비테스트)» 한정구를 누락했다.
- 수정안: enforcedBy 제거(위임 discipline-reviewer 단독 유지)가 1안. 유지하려면 basis 에 «⑴은 비테스트 settings 한정 — 테스트 스코프 교체는 비커버(프로덕션 settings 우회형만 차단)»를 명기하고 worksheet #63 행 동일 수정.

## MEDIUM

### M-1 [배선] s042-9.5/b12 norm2 (#51) — 기본값 이탈(delegatedTo=discipline-reviewer 단독)에 문면 근거 없음
- 반박: architecture-db 문서군 기본값은 design-review-db 다(§16 표). #51의 basis 는 ②#599·④#599·②#195 뿐인데, rule-owner-map **#599 = ast → check-transaction-boundary 단독(ⓓ 없음)**·**#195 = ast 단독**이라 discipline-reviewer 치환의 ④ 근거가 없고, 원문 391행 해당 문장의 참조는 §9.6·§11(같은 문서)뿐이라 ① 근거도 없다(implementation-* 직접 지목 부재 — worksheet §2.1 스스로 «직접 지목한 규범에 한정»이라 선언한 정책과 모순). §16 «기본값 이탈은 문면 근거 필요» 위반. 같은 블록 안 norm1 [discipline, db] 병기·norm3 [db] 단독과 상호 비일관까지 겹친다.
- 수정안: delegatedTo 에 design-review-db 복원(병기 또는 단독). 이탈을 유지하려면 실존 문면·registry 근거를 basis 에 제시.

### M-2 [배선] s042-9.5/b12 norm3 (#52) — 인용한 registry ⓓ(#257=+discipline-reviewer)를 배선에 미반영
- 반박: basis 가 스스로 «④rule-owner-map #257 = ast+ → check-domain-model.py + discipline-reviewer»를 인용하면서 delegatedTo 는 design-review-db 단독이다. ast+ 후보 채널의 마무리 주체(ⓓ=discipline-reviewer)가 빠졌다. 같은 ④ ⓓ 근거로 치환/병기한 #70(#532)·#71(#181)·같은 블록 norm1(#50, 같은 #257) 처리와 정면 비일관.
- 수정안: discipline-reviewer 병기. 병기하지 않을 거면 basis 의 ④ 인용에서 ⓓ 부분을 빼고 «후보 채널 마무리는 이 규범 축이 아님» 사유를 명기.

### M-3 [배선] s042-9.5/b10 norm3 (#44) — 명세-측 의무에 대한 enforcedBy 과잉 + basis 부정확
- 규범: «SQLite 직렬화가 필요하면 begin 모드·busy_timeout 등 연결 설정을 명세가 명시».
- 반박: check-mechanism-ownership 은 명세의 연결 설정 «명시» 여부를 검사하지 않는다 — OPTIONS 를 아예 관측하지 않고, 비스톡 ENGINE + 레포-로컬 DatabaseWrapper 서브클래스 형태만 차단한다. 이 Obligation 의 기계 커버는 0이고, 커버되는 것은 인접 규범(b11의 교체 금지·승인 예외)이다. basis 의 «stock OPTIONS 축만 기계 커버» 문구 자체가 부정확하다(검사기는 OPTIONS 축을 검사하지 않는다). 저작자 자신이 #49(PRAGMA)에서 적용한 «docstring 부재 → 기본값 유지(커버 부재)» 논리를 이 규범에는 적용하지 않았다.
- 수정안: enforcedBy 제거(위임 단독), 또는 basis 를 «검사기는 이 의무의 우회형(엔진 교체)만 차단 — 명시 의무 자체는 비커버»로 교정.

### M-4 [재진술] s036-8.4/b4 (#32) ↔ s052-11.1/b1 (#83) — 같은 문서 내 준-축자 쌍의 이중 승격, restates·판정 기록 모두 없음
- 반박: §8.4 3항 «새 코드와 구 코드가 동시에 동작하는 compatibility window 를 고려한다»(329행) ↔ §11.1 서두 «운영 DB 변경은 기존 코드와 새 코드가 동시에 동작하는 시간을 고려한다»(514행). 같은 지식·거의 같은 문면이 Work 2개로 각자 승격됐고 spec restates 에도, worksheet 경계 메모·§3.1(재진술 아님 판정 목록)에도 없다. 저작자는 s016-3.4 에서 census −1 을 감수하며 §15(정본 1곳)를 적용한 선례를 만들었으므로 «발주서 계수 승계»는 면책이 안 된다.
- 수정안: 정본 1곳 지정(권장: s052-11.1 — 절 주제가 compatibility window) + 사본 블록 restates + census 대사 사유 1줄. 재진술 아님으로 판정한다면 그 근거를 worksheet §3.1에 기록.

### M-5 [규범식별] s043-9.6/b6 (#56, Rule ownership 행) — 형제 행과 다른 승격 축(내용 재승격) · class 비일관
- 반박: §9.6 표의 형제 행 7개는 전부 «…을 명시한다» Obligation 으로 잡았는데(Transaction owner·Locking strategy·Idempotency storage·Side-effect timing·Isolation/retry…), Rule ownership 행만 s042-9.5/b12 norm1의 실질 내용(판정 SQL 복제 금지)을 그대로 다시 승격한 **Prohibition** 이다. 행 자체의 문면 규범은 «Rule ownership(판정 소유·결과 저장 여부)을 Risky Write 블록에 명시하라»는 명시 의무이고, 실질 금지의 정본은 §9.5(b12)다. 현행은 같은 실질 규범의 이중 계상이며 restates 처리도 없다.
- 수정안: 형제 행과 같은 «명시» Obligation 으로 재분류(enforcedBy·병기 근거는 명시 항목의 실질 판정 근거로 유지 가능), 실질 규범은 s042-9.5/b12 정본에 위임. 현행 유지를 고집하면 재진술 판정을 worksheet 에 기록.

### M-6 [배선] s034-8.2/b8 norm2 (#23) — 문면이 architecture-ddd §3.3 을 직접 지목하는데 design-review-ddd 미병기 (병기 정책 자가 비일관)
- 반박: 원문 301행이 «(`architecture-ddd` §3.3 규칙3 영속성 확장)»을 직접 지목하고, basis 도 그 지목을 ① 근거로 쓴다. 그런데 같은 spec 에서 §3.7 지목(#76)은 design-review-ddd 병기, §3.2 지목(#43·#50)은 discipline-reviewer 병기로 처리하면서 §3.3 지목(#23)만 병기 없이 design-review-db 단독이다. worksheet §2.1의 «문면 직접 지목 → 병기» 정책이 이 건에서만 적용되지 않았고, §3.3 규칙3은 설계 시점 규범이라 §16 기본값 표 기준 design-review-ddd 병기 대상이다.
- 수정안: delegatedTo 에 agent-design-review-ddd 병기, 또는 비병기 사유(예: 영속성 확장 축은 db 설계 판정으로 충분)를 basis·worksheet 에 기록.

## LOW

### L-1 [재진술] s043-9.6/b14 (#64) 셋째 문장 ↔ s044-9.7/b1 (#65·#66) — «유실 불허 시 Outbox(듣는 쪽 별도 배포 단위 한정 — #529 · in-repo 는 cron_job 폴링 #626)» 규칙이 괄호 주석까지 동일하게(412행 ↔ 418행) 두 자리에 승격. #64는 다문장 압축 Work 라 «부분 사본» 반론 여지가 있어 low — 그러나 restates·worksheet 판정 어느 쪽에도 기록이 없다.
### L-2 [재진술] s041-9.4/b5(Serializable 행 «반드시 재시도 로직 구현» — 미계수 행) ↔ s042-9.5/b8 «Serializable + retry 필수»(#40) — 같은 문서 사본 후보. worksheet 메모 1은 «표 행 계수» 축만 다루고 재진술 축 판정이 없다. 소급 패스 후보 목록에 재진술 검토를 병기할 것.
### L-3 [재진술] s033-8.1/b3 «자연키 불안정 시 surrogate key»(#16) ↔ s009-2.3/b7 «자연 기본키 부재 시 인조키»(#4) — 유사 규범 이중 승격. 조건이 다르다(부재 vs 불안정)는 판정도 가능하나 그 판정 자체가 어디에도 없다.
### L-4 [재진술] s035-8.3/b8 «멱등성 저장소 최소 6항 결정»(#28) ↔ s043-9.6/b7 «멱등성 저장 5항 명시»(#57) — 항목 집합 5/6 중첩의 내부 쌍인데 §3.1은 api 교차 쌍만 판정하고 내부 쌍 판정(사본 아님 — retention·response snapshot 축 상이 등)을 기록하지 않았다.
### L-5 [배선] s034-8.2/b8 norm2 (#23) — check-context-isolation #12·#13은 import·호출 경로 검사라 «ID 값 참조» 축 비커버(스스로 인정). check-domain-model **#548**(«다른 애그리거트는 식별자 값 객체로만» — 남의 루트 클래스 타입 힌트 차단)이 ID-참조 축의 더 근접 후보인데 27종 전수 실독을 주장하면서 대조 기록이 없다(#548은 BC 내 애그리거트 간 규칙이라 축 상이 판정도 가능 — 그래서 low).
### L-6 [배선] s044-9.7/b1 norm2 (#66) — registry 가 #626 = human·ⓓ 단독(검사기 없음)으로 명시한 규칙에 #629 후보 채널을 이유로 enforcedBy(check-missable-entrance)를 병기 — #629는 인접 규범이고 ⓓ 후보는 exit 불산입이라 «집행» 주장이 과대. basis 가 사정을 정직히 적어 low.
### L-7 [배선] s044-9.7 #67·#69·#72·#74 basis 의 ② 인용문(«⑴ outbox 가 없다 — 커밋과 발행을 한 트랜잭션에 묶는 선언이 필요하다»·«⑷ 재시도·데드레터 선언이 없다»·«⑸ 순서 보장 «여부»의 명시가 없다») — docstring 이 아니라 검사기 위반 메시지 문자열(check-broker-contract.py 402·404·406행)이다. 내용은 docstring ⑴⑷⑸ 요약과 부합하나 ② «docstring § 인용» 축 표기가 부정확.
### L-8 [배선] s043-9.6/b7 (#57) basis «④registry #10» — 좌표 계열 미명기로 오독 유발. commands/dddjango.md checker registry(순서 고정) 124행에서 서수 10 = check-idempotency-scope-creep.py 이고 command-dddjango spec 도 같은 관례(«registry #10 — 승인 범위 밖 idempotency 산출물»)를 쓰므로 **허위는 아니다**(전 판 리뷰 M-3 정정). 다만 같은 worksheet 의 ④ 관례가 «rule-owner-map #N»이라(rule-owner-map #10 = check-layer-skeleton) 계열 표기 없이는 충돌 오독된다. 수정안: «④commands checker registry 서수 10» 으로 계열 명기.
### L-9 [배선] s042-9.5/b11 norm1 (#46) — label 의 «안전 PRAGMA 화이트리스트 한정» 절반은 저작자 자신의 #49 판정(«PRAGMA 축은 docstring 부재»)대로 비커버인데 mechanism-ownership 배선을 한계 병기 없이 유지 — basis 커버 축 과대 표기(ENGINE 절반은 #47이 이미 진다).
### L-10 [배선] s042-9.5/b9 (#41 락 범위 — 트랜잭션 안 외부 호출 금지) — check-context-isolation **#14**(«with unit_of_work: 안에서 크로스-BC 포트 호출 금지»)가 «트랜잭션 안 외부 작업» 인접 축을 무는데 기본값 위임이고 대조 기록이 없다. #14는 크로스-BC 한정이라 축 상이 판정이 유력해 low — 판정 자체는 기록할 것.
### L-11 [규범식별] s043-9.6/b12 (#62) — 원문 408행의 규범 3문장(coder «add 할 수 있다»=Permission · reuse 시 산출물 미생성 · 기존 유효 테스트 보존)을 Obligation 1건으로 압축 — Permission class 1건 소실(문서 Permission 0 분포의 원인). b13(410행: 기본 의무+백엔드 교체 금지 2문장)·b14(412행: 3문장)도 같은 압축인데, §13 «블록 내 문장→Work 대응은 검수표에 기록» 의무가 §9.5(메모 6)에만 이행되고 §9.6 산문 3블록에는 미이행. 동결 census(12) 준수 목적임은 이해되나 소급 패스 문장 해상도 재정렬 후보로 기록할 것.
### L-12 [경계kind] s042-9.5/b12 note «절 내 재진술은 같은 절이라 restates 불요» — §15에 같은-절 면제 조문이 없다(자작 규칙). 391행 CHECK 백스톱 문장, s044-9.7 b5(#69)↔b2(#67)의 «동일 트랜잭션 기록» 중복에도 같은 논리를 무근거 적용했다. 규약 인용을 달거나 §15 개정 제안으로 올릴 것.
### L-13 [경계kind] s042-9.5/b10 note «4문장 규범(사실 서술 2문장은 미계수)» — 산술 부정확. 387행 단락은 5문장이고 규범 4건은 3문장에 분포한다(넷째 문장이 방어선·연결 설정 2건을 담음). 기록 정확성 문제만(계수 18 자체는 무결).

## 검증됐고 지적하지 않는 것 (반박 시도 후 기각)

- s016-3.4 census −1: 발주서 restate 열·s019-4.2 «정본 지정» 비고·§15 문면·파일럿 판례(ddd s017-3.2)가 모두 spec 쪽을 지지 — 정당.
- 표 행 계수 비일관(§9.4·§11.4 vs §8.1·§11.3): 발주서 스스로 «애매» 동결 — worksheet 메모 1의 승계+소급 후보 지목이 계약상 옳다.
- 블록 경계·공백 소유: 절 선두 빈 줄=첫 블록, 구분자=선행 블록 후행, code 펜스 후행 빈 줄 귀속 — 28절 일관, §13 부합, 도구 byte 등가 통과. 머리행·구분행 table-row, 번호 목록 = norm(checklist 아님), blockquote·`---` = prose 처리 전부 §13 문면과 일치.
- 배선 실물 대조 일치분: #22=check-db-table #631(docstring 축자·registry ast ⓒ 단독), #37·#43=#599, #50·#56 의 #257/#195/#287 인용, #59=#200, #63 아닌 #64 3원 배선(#200·#541·#529), #65=#529(ⓓ discipline-reviewer 정당), #70=#532, #71=#181(broker-contract 의 «멱등 물음의 소유자는 #181» 명시 위임 문면 확인), #74=#603⑸, #82 의 mechanism-ownership ⑵ 비배선 논증(#336~#338·#593 은 migrations 규율이지 관할 선언 집행이 아님), #28·#49 의 «커버 부재 — 도피 아님» 논증: docstring·registry 실물 대조 전건 일치.
- 위임 분포·수치: Obligation 93·Prohibition 9·Exception 3·Permission 0·Override 0, delegatedTo 94/14/1/1/1, enforcedBy 규범 24건 — 독립 재계산과 전건 일치. agent-design-review-db 는 `dddjango/agents/design-review-db.md` 실재 doc_key.
- SKILL.md 유예 7건: 19~25행 실물 확인 일치. 불릿 2의 «선택도 높은 컬럼 앞» 상충을 restates 아닌 «개정 후보»로 올린 판정은 정확(원문 §7.1이 그 통념을 명시적으로 깬다).
- api-final 교차: api 발주서 s018-4.2(«db s042-9.5와 규칙 쌍»)·s060-13.3(«상호 참조 — 사본 아님») 비고와 worksheet §3.1 «계약 조인» 판정 정합 — 유예 대상의 spec 혼입 0.

## 처분 (수리 에이전트 · 2026-08-22)

- 수리 대상: `workspace/eval/t3/specs/architecture-db-final.spec.json` + `workspace/eval/t3/worksheets/architecture-db-final.md`. 원문·`ontology/`·타 에이전트 산출물 무수정.
- 재검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/architecture-db-final.spec.json` → **exit 0**(`--write` 미사용). 28절 · 블록 179 · **Work 105 → 104**(M-4 재진술 강등 1건).
- 번호 이동 주의: Work 강등이 s036-8.4/b4(전 #32)에서 일어나 검수표 배선 표의 # 가 재부여됐다 — 이 리뷰의 #33 이후 번호는 전부 **−1**. 아래 처분은 리뷰 표기(전 번호)를 그대로 쓴다.
- 결과: **fixed 20 · rejected 0**(단 H-1 은 지적의 논거 일부를 기각하고 수정안 2안을 채택 — 아래 참조).

| 지적 | 처분 | 근거 (원문·검사기 실물 대조) |
|---|---|---|
| **H-1** s043-9.6/b13(#63) mechanism-ownership 허위성 | **fixed**(수정안 2안 채택 · 논거 일부 기각) | 실물 확인: `_find_settings_files()` 는 **파일 이름**에 `test` 가 든 settings 모듈만 제외한다(115~117행). 따라서 «테스트 목적» 교체라도 공용 `settings.py` 의 DATABASES ENGINE 에 떨어지면 ⑴ 게이트는 정상 발화한다 — 단일 settings 레이아웃이 Django 통상형이라 «중심 사건에서 **구조적으로** 발화 불가»는 과장이라 **기각**한다. 성립하는 부분은 ⓐ basis 가 «프로덕션(비테스트)» 한정구를 누락했다는 것과 ⓑ 규범 문면의 «출처-불문»(테스트 전용 settings·런타임 패치 포함)보다 커버가 좁다는 것이다. enforcedBy 는 유지하고(§16 «담당 검사기 근거가 있는데 기본값 도피 = 오배선») basis 에 한정구+비커버 경로를 병기했다. 검수표 §2.1 «인접 검사기 대조» 표에도 같은 판정을 남겼다 |
| **M-1** s042-9.5/b12 norm2(#51) 기본값 이탈 무근거 | **fixed** | rule-owner-map 실물: **#599 = ast**(ⓒ check-transaction-boundary 단독)·**#195 = ast**(ⓒ 단독) — ⓓ 없음. 원문 391행 그 문장의 참조는 «§9.6 Isolation/retry»·«§11 rollout backfill»로 **같은 문서**뿐이라 implementation-* 직접 지목이 없다. §16 «기본값 이탈은 문면 근거 필요» 위반이 맞다 → delegatedTo 를 `agent-design-review-db` 로 복원(단독). 근거를 basis 에 명기 |
| **M-2** s042-9.5/b12 norm3(#52) ④ ⓓ 미반영 | **fixed** | rule-owner-map **#257 = ast+ → check-domain-model.py + agents/discipline-reviewer.md**. basis 가 인용한 ⓓ 를 배선에 반영해 `agent-discipline-reviewer` 병기(#50·#70·#71 과 같은 처리). M-1 과 합쳐 «ast → 기본값 유지 · ast+ → ⓓ 병기»라는 일관 규칙이 이 문서 전역에 성립한다 |
| **M-3** s042-9.5/b10 norm3(#44) enforcedBy 과배선 | **fixed**(1안 채택 — enforcedBy 제거) | 실물 확인: 검사기는 `ENGINE_RE` 로 DATABASES **ENGINE 만** 읽고 `OPTIONS`·PRAGMA 를 전혀 파싱하지 않는다. «연결 설정을 명세가 명시한다»의 기계 커버는 0이 맞다. 저작자 자신의 PRAGMA 판정(«docstring 부재 → 커버 부재»)과 일관되게 enforcedBy 제거·위임 단독으로 내리고, «기계가 무는 것은 우회형(엔진 교체)이고 그 축은 b11 이 진다»를 basis 에 적었다. b11 규범이 그 축을 이미 지므로 커버 손실 0 |
| **M-4** s036-8.4 3항 ↔ §11.1 서두 이중 승격 | **fixed**(정본 s052-11.1 지정 · 사본 restates) | 원문 대조: 329행 «새 코드와 구 코드가 동시에 동작하는 compatibility window를 고려한다» ↔ 514행 «운영 DB 변경은 기존 코드와 새 코드가 동시에 동작하는 시간을 고려한다» — 술어·목적어가 같은 준-축자 쌍이고 §8.4 쪽이 그 일반 원칙을 제약조건 rollout 절차에서 되풀이한 형태다. 발주서 재진술 열의 «N» 은 P0 계수 승계일 뿐 판정이 아니며 §15 가 상위 규약이라는 지적이 옳다(s016-3.4 자기 선례). s036-8.4/b4 를 Work 미승격 + `restates`→`s052-11.1/b1` 로 내리고 census −1 사유를 §1 표·판정 요지에 기록. **Work 105 → 104** |
| **M-5** s043-9.6/b6(#56) class 비일관·이중 계상 | **fixed** | 표 지배 문장(395행)이 «다음 항목을 **명시한다**»이고 401행 결정 내용도 «…소유하는지 — …죽이지 않는지»라는 명시 대상 물음이라 형제 7행과 같은 «명시» Obligation 이 맞다. class 를 Obligation 으로 바꾸고 label 을 «Rule ownership — 판정·불변식의 도메인 소유와 판정 복제 여부를 명시»로 재정렬. 실질 금지의 정본은 s042-9.5/b12 첫 규범(행 문면 자신이 «메커니즘 위 §9.5»로 지목)임을 basis·검수표에 명기. 블록 레벨 `restates` 는 달지 않았다 — 이 블록은 사본이 아니라 자기 «명시» 규범을 지는 행이라 §15 의 사본 표기 대상이 아니다 |
| **M-6** s034-8.2/b8 norm2(#23) design-review-ddd 미병기 | **fixed** | 원문 301행이 «`architecture-ddd` §3.3 규칙3 영속성 확장»을 직접 지목하고, 그 §3.3 규칙3 은 «다른 애그리거트는 ID로만 참조하라» — 설계 시점 규범이라 §16 기본값 표의 `agent-design-review-ddd` 행이다. 같은 spec 의 §3.7 지목(#76)·§3.2 지목(#43·#50) 처리와 정책이 어긋났다는 지적이 맞다 → `agent-design-review-ddd` 병기 |
| **L-1** s043-9.6/b14 ↔ s044-9.7/b1 재진술 | **fixed**(기록) | 412행 셋째 문장과 418행 말문이 괄호 주석(#529·#626)까지 동일함을 확인. b14 는 3문장 압축 Work 라 블록 레벨 `restates` 를 달면 나머지 두 문장까지 사본으로 표시된다 → 정본 s044-9.7/b1 지정 + 문장 해상도 재정렬과 함께 소급 패스 후보로 spec b14 note·검수표 §3.1 내부 쌍 표·메모 10 에 기록 |
| **L-2** s041-9.4 Serializable 행 ↔ #40 | **fixed**(기록) | 369행 «반드시 재시도 로직 구현» ↔ 383행 «serialization failure retry 가 필수» 동일 규범 확인. §9.4 쪽이 표 행 계수 비일관(메모 1)으로 미계수라 현재 이중 계상은 없다. 소급 패스 후보 목록(메모 1)에 «계수 증가 vs §9.5 정본 restates» 판정을 병기 |
| **L-3** s033-8.1 #16 ↔ s009-2.3 #4 | **fixed**(판정 기록 — **사본 아님**) | 74행 «자연스럽게 기본키가 될 수 있는 컬럼이 **없으면**» ↔ 284행 «자연키가 **불안정하면**» — 처방(surrogate key)은 같지만 발동 조건이 부재 vs 불안정으로 다르다. 독립 규범으로 판정하고 §3.1 내부 쌍 표에 근거 기록 |
| **L-4** s035-8.3/b8 #28 ↔ s043-9.6/b7 #57 | **fixed**(판정 기록 — **사본 아님**) | §8.3 은 DB 설계 최소 6항(`retention/cleanup`·`storage owner/location` 포함), §9.6 행은 Risky Write 블록 명시 5항(`table`·`stored result` — HTTP 표현은 presentation 소유). 항목 집합과 소유 문맥이 함께 달라 계약 조인. §3.1 내부 쌍 표에 기록 |
| **L-5** #23 ↔ check-domain-model #548 대조 부재 | **fixed**(대조·기각 기록) | #548 실물 확인: «다른 애그리거트는 «식별자 값 객체»로만 — 타입 힌트의 남의 루트 클래스 위반», 구현 위치가 «도메인 전역» 슬라이스(543·601행)로 **같은 BC 안** 애그리거트 간 규칙이다. BC 경계 참조 축과 상이 → 기각. 검수표 §2.1 «인접 검사기 대조 후 기각» 표에 기록 |
| **L-6** s044-9.7/b1 norm2(#66) enforcedBy 과대 | **fixed**(1안 채택 — enforcedBy 제거) | rule-owner-map **#626 = human → agents/design-architect.md**(ⓒ 없음). 인용된 #629 는 check-missable-entrance 의 **인접** 규칙이고 그 검사기 이관 계약이 «ⓓ 후보는 exit 불산입»이라 집행이 아니다. enforcedBy 를 내리고 delegatedTo(`agent-design-architect`) 단독으로 두되, #629 표면화 채널은 basis 에 «집행 아님»으로 명기. #626 을 무는 검사기가 애초에 없으므로 «도피»가 아니다 |
| **L-7** #67·#69·#72·#74 인용 출처 표기 | **fixed** | 실물 확인: 인용문 3종은 `check-broker-contract.py` **402·404·406행의 위반 메시지 문자열**이 맞다(docstring 아님). 각 basis 를 «docstring #603 요약 + 위반 메시지 실물(NNN행 구현 문자열)» 2단으로 정정하고 ④ 를 `rule-owner-map #603 = ast` 로 풀어 적었다 |
| **L-8** #57 «④registry #10» 계열 미명기 | **fixed** | `dddjango/commands/dddjango.md` 124행에서 서수 10 = `check-idempotency-scope-creep.py` 실재 확인(허위 아님 — 리뷰의 자기 정정이 옳다). 다만 같은 검수표의 다른 ④ 는 rule-owner-map 계열이고 그 #10 은 `check-layer-skeleton` 이라 오독 소지가 있다 → «④commands/dddjango.md checker registry 서수 10(124행)»으로 계열·행을 명기하고 충돌 사실도 basis 에 적었다 |
| **L-9** #46 PRAGMA 절반 비커버 한계 미병기 | **fixed** | basis 에 «경계의 ENGINE 쪽 절반만 기계 커버(예외·금지 축은 같은 블록 둘째·셋째 규범) · label 후반 «안전 PRAGMA 화이트리스트» 축은 같은 블록 넷째 규범 판정대로 비커버» 병기 |
| **L-10** #41 ↔ check-context-isolation #14 대조 부재 | **fixed**(대조·기각 기록) | #14 실물: «`with unit_of_work:` 안에서 크로스-BC 포트 호출 금지» — 주어가 크로스-BC 포트이고 사유가 경계 격리다. 이 규범의 주어는 외부 API·사용자 입력 대기·긴 배치를 포함하는 락 보유 시간이라 축 상이 → 기본값 위임 유지 + §2.1 대조 표에 기록 |
| **L-11** s043-9.6/b12(#62) 문장 압축·§13 미이행 | **fixed**(기록) | 408행이 4문장(정의 1 + 규범 3, 그 중 «coder 가 `add` 할 수 있다» = Permission 성격)임을 확인. 동결 census(§9.6 = 12) 승계가 이번 웨이브 계약이라 계수는 유지하고, §13 의 «문장→Work 대응 검수표 기록» 의무를 **메모 10** 신설로 이행했다(b12·b13·b14 3블록 전부). 소급 패스 «문장 해상도 재정렬» 후보로 지목하고 b12 ②의 Permission 복원을 함께 적었다 — 이 문서 Permission 0 분포의 원인 기록 |
| **L-12** b12 note «같은 절이라 restates 불요» 자작 규칙 | **fixed** | §15 를 재확인해 같은-절 면제 조문이 없음을 확인 → 자작 규칙 표현을 삭제. 실제 근거는 «`djr:restates` 가 **블록 단위** 속성인데 b12 는 자기 Work 3건을 지는 블록이라 사본 표시 대상이 아니다»라는 구조적 사유이므로 note 를 그렇게 고쳐 썼고, s044-9.7 b5↔b2 건은 별도로 «사본 아님(표 행이 산문 규범을 구체화하는 계약 분해)»으로 판정해 §3.1 내부 쌍 표에 기록했다. **§15 개정 제안 후보**(문장 일부만 사본일 때의 표기 — restates 의 Work 단위 확장 가부)를 메모 11 로 상정 |
| **L-13** b10 note 산술 부정확 | **fixed** | 387행을 재계수: **5문장**이고 규범 4건은 **3문장**에 분포(첫 1 · 넷째 2 · 다섯째 1), 둘째·셋째는 사실 서술. note 를 «5문장 중 규범 문장 3(넷째 문장이 2건)=Work 4»로 교정하고 메모 6 에도 같은 교정을 남겼다. 계수 18 은 무결 |

**수리 후 분포**: Work 104 · class Obligation 93 / Prohibition 8 / Exception 3 / Permission 0 / Override 0 · delegatedTo design-review-db 94 / discipline-reviewer 14 / design-review-ddd 2 / design-review-api 1 / design-architect 1 · enforcedBy 배선 22(수리 전 24 — M-3·L-6 강등) · 무소유 0.
