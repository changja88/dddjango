<!--
AI-OPTIMIZED DEVLOG. 이 문서는 dddjango 작업의 자기완결 정본이다.
읽는 규칙(AI):
  1) §0 Current State를 먼저 읽어라(지금 상태·베스트 구성·금지사항).
  2) 결정은 §2 Decision Records에서 상태태그(✅adopted/❌rejected/⏸blocked/✔verified)로 찾아라.
  3) 모든 수치·주장엔 증거 앵커(세션ID·커밋SHA·파일:라인)가 붙는다 — 추천 전 실재 확인하라.
  4) 개인 메모리(~/.claude)는 초기화될 수 있어 신뢰 못 함. 이 문서가 정본이다.
마지막 갱신: 2026-06-09
-->

# dddjango DEVLOG

`/dddjango` Claude Code 플러그인 파이프라인의 설계·구현·최적화 전체 여정 기록. AI가 읽는 자기완결 정본.

---

## §0 Current State (READ FIRST)

- **무엇**: 기존 Django 프로젝트에 한 기능을 DDD로 추가하는 Claude 전용 플러그인. 단일 진입 `/dddjango`. 코디네이터(메인 세션) + 서브에이전트 7 + 스킬 11, 게이트 G0/G1/G2.
- **코드 상태**: 브랜치 `eval/codex-determinism-n2`, plugin **1.9.0**, 결정적 백스톱(게이트) **16종**(⑭transient-overmapping·⑮synthetic-infra·⑯catch-all 추가·⑰duplicate-app은 롤백). ⚠️ **eval 브랜치 전체 로컬·미push**(origin엔 P2 `58660a0`까지) — 릴리스(eval→main 머지/PR+push)는 **사용자 명시 push 승인 대기**(가드레일이 push 차단).
- **현재 베스트 구성(검증됨)** = **커밋된 표준 + extended thinking OFF**. smoke8(2026-05-28) 최종 확인: 코디 **1.58M(전 런 최저)**·기계 **41분**·테스트 **20/20**·§0/§4/ACL 충족·코더 토끼굴 0·architect 재디스패치 0 — 역대 최청결·회귀 0.
  - ⚠️ **thinking OFF는 코드가 아니라 사용자 세션 설정**(`Option+T` / `alwaysThinkingEnabled:false`). 플러그인에 못 박는다. 안 끄면 비용 ≈ 2.6M.
- **속도/비용 현실(닫힌 결론)**: 기계시간 ~41~60분은 "강한 모델 + 다단계 게이트 + TDD + 독립 리뷰" 품질우선 설계에 **내재**. 품질 손실 없이 큰 wall 단축하는 공짜 레버 없음. 통제 가능한 비용 레버는 이미 적용. 큰 비용 레버(컨텍스트 편집/compaction)는 업스트림 차단(§2 DR-11).
- **최적화 사이클: ✅ 종료** (2026-05-28, smoke8 합격). 다음 작업은 코드를 *실제로 바꿀 때*만 재개.
- **배포 상태**: Claude판 **v1.0.0 main 병합·릴리스** 완료(마켓플레이스 `changja88`). 그 후 **Codex 이식 착수** → **PoC 성공(§2 DR-12)**: `codex-dddjango/`(스킬 19, Claude `dddjango/` 무변경). 이어 **코드품질 1:1 평가(§2 DR-13)** → **결정성 2차 검증으로 결론 수정(§2 DR-14)**: N=2 결과 **1차 "claude>codex 13:2:5"는 상당 부분 N=1 분산**이었음. 핵심 신호(B1 도메인소유·stock≥0)가 양 런타임 모두 **비결정**. 2차 프레임워크 무관 코드 대등(codex가 일부 우위). **재현되는 진짜 차이 = 코드 우열이 아니라 게이트 노출 철학·스택 취향**. 표준준수 점수 추정 codex~70·claude~84(신뢰낮음, claude 분산>평균차). (상세=§2 DR-13/14·[[dddjango-codex-port]]; 평가 산출물은 §2 DR-25서 정리·git 히스토리.)
- **B1-fix 표준 검증(§2 DR-15, 2026-05-29)**: DR-14가 남긴 B1 비결정 과제에 **일반화 표준 편집(architecture-ddd §3.2 단일출처 + design-review-ddd/discipline-reviewer 2층 탐지, 12파일 미커밋)**으로 대응 → 새 스모크(sample→clone)로 codex-4·claude-3 동시검증 = **양쪽 설계·코드 끝까지 B1 CLEAN(각 N=1)**. DR-13 빈혈·DR-14 죽은코드 부재. **표준 12파일 커밋(`98ebfd3`).** (claude-3 ninja 통제이탈은 수락; 프레임워크축 비교 무효.)
- **표준 빈칸 ③·④ 메움(§2 DR-16, 2026-05-29)**: DR-15 통제 비교가 드러낸 표준 두 빈칸(코드 버그 아님)을 메움 — ③ 기존 평면 코드에 도메인 판정 얹을 때 이주 기준을 **"판정·불변식 소유냐"**(레거시 아님)로 명문화(소유→`domain_layer` 이주/데이터 소스→평면 OK/컨텍스트 간 ACL·published만), ④ **API 스택을 design-architect 명세 1급 결정으로 승격**(기본 ninja·기존 존중)+ninja 버전핀 설치 규칙. **14파일 편집·미러 byte-identical·`plugin validate` PASS·서브에이전트 3렌즈 리뷰(정확성 2픽스 반영).** 정적까지 — 동적 검증 ⑥ 이연.
- **동적 검증 Tier 2·3 + ④ 보강(§2 DR-17, 2026-05-29)**: Claude(Tier 2) ③ **STRONG PASS**·④ inconclusive(ninja 편향). Codex 전체 스모크 ×3(Tier 3): ③ 완전이주 가능·Claude 수렴이나 **비결정**(t3 평면 유지). ④ 결과 = pre-boost plain(headless 무설치 보수성) → **`design-architect` 보강 후 Ninja+requirements 핀 수렴(t3c, 결정적)**. ④(e) 스택 설계승격 전파 **확정**. (산출물 `eval/runs/{codex-5,6,7}`은 §2 DR-25서 정리·git 히스토리.) 각 N=1(sanity).
- **스모크 방식 통일(§4)**: 마스터 `~/Desktop/dddjango-smoke-sample` + `git clone`으로 런타임별 타깃(`dddjango-{claude,codex}-index`). 구 reset.sh·E2E-SMOKE-METHOD.md 폐기.
- **하드닝 이력(상세는 §2 각 DR)**: 빌드·릴리스 후 DR-16~50으로 표준 강화 — BC 판정-소유·API 스택 승격·P1a 오류중앙화·C3 멱등성·C4 빈혈SQL·NJ-2 §6.3 협상·BC FK금지·네이밍/R-C-Q·pytest·ACL 예외전수성·NJ-7 catch-all·ninja 클래스 컨트롤러·데이터소스 골격. 결정적 백스톱 16종.
- **🔬 근본원인 분석→처방(2026-06-06)**: "왜 수정이 회귀하나" 진단(DIAGNOSIS v2·근본5[스코프갭·비결정·런타임prior·릴리스미완결·빌드배선무결성]) → **R5(소스-미러 동기·`corpus_mirror_sync.py`) 완료**, 나머지 처방(R2 측정·R1 프론티어·R3 수용)은 **일단락으로 접음**. 분석 상세=git 히스토리.
- **🔎 진행 상태(2026-06-09)**: DR-44~50으로 ACL 예외전수성·NJ-7 catch-all·ninja 클래스 컨트롤러·데이터소스 골격 강화(대부분 **미푸시**·라이브 일부 검증). plugin 전면감사(ultracode)로 rank2(소스미러 재동기)·rank3(수정모드 백스톱 앵커) 완료·rank1(⑰) 보류. **현재 = DEVLOG 정리(시대별 압축)·완료 산출물 파일 정리.**
- **열린 잔무**: **미푸시**(DR-44~50 + 정리 커밋 — 릴리스는 eval→main 머지/PR+push·사용자 승인 게이트). 평가·라이브 검증·ACL-EX2·근본원인 처방·plugin 감사 트랙은 dddjango 일단락으로 **접음**(상세·산출물 git 히스토리 보존, 재개 시 발굴).
- **런타임 비교 경계**: 모든 dual 채점 **N=1·우열 결론 금지** — 치명 FAIL 레인이 런마다 갈림(P4③ run-variance), Claude/Codex 둘 다 비결정 관측.

---

## §1 What dddjango Is (architecture)

- **파이프라인**: 코디네이터가 작업을 역할로 분해 → 서브에이전트에 위임. 코디는 오케스트레이션·게이트·통합·검증보고만, 설계명세/인수테스트/구현코드는 직접 안 씀.
- **서브에이전트 7**: `design-architect`(통합 명세 작성·producer) · `design-review-{ddd,api,db}`(렌즈별 독립 리뷰·**병렬**·read-only) · `acceptance-tester`(블랙박스 인수테스트 Red) · `coder`(이중루프 TDD 구현) · `discipline-reviewer`(클린코드·TDD 규율 감사·read-only).
- **게이트**: G0 요구·스코프 → G1 설계 → G2 구현. 각 게이트는 사용자 승인(AskUserQuestion).
- **스킬 11**(서브에이전트 `skills:` frontmatter로 preload, `user-invocable:false`로 커맨드 전용): architecture-{ddd,api,db} · implementation-{django,django-ninja,django-web,python,test} · discipline-{cleancode,tdd,houserules}.
  - **코퍼스 altitude 위계**: ddd(프로젝트 전략) → db/api(측면 계약) → implementation-*(코드) → discipline-*(횡단 규율). test=메커니즘(구현측)·tdd=실천(규율측)이라 갈림.
- **파일트리 표준**(출처: 사용자 실프로젝트 HaffHaff, DDD 4계층): `application/<app>/{domain_layer,application_layer,infra_layer,presentation_layer}/`. `_layer` 접미사가 컨테이너 `application/`과 응용계층 이름충돌 해소. 단일 출처 = `discipline-houserules` final.md **§0 불변식**.
- **2부 코퍼스 동기화 규칙**: 스킬 지식은 배포본 `dddjango/skills/<s>/references/final.md` + 소스 미러 `workspace/reference/<s>/reference/final.md` 양쪽에 존재. **본문 byte-identical** 유지(소스엔 `## P1 Source Sufficiency` 헤더만 더 붙을 수 있음). **agents·commands·SKILL.md는 plugin-native라 미러 없음(단일 파일).** ⚠️ **정정(DR-46)**: houserules는 외부 출처가 없어 P1 블록만 없을 뿐 **final.md 미러는 *보유*(불변식1 대상, 11번째)** — 과거 "houserules 미러 없음" 표기는 부정확. 추가 불변식: 배포본 Claude≡Codex final.md byte-identical(불변식2). **동기 검사·해소 = `workspace/tools/corpus_mirror_sync.py`**(메인테이너/빌드타임 도구, fail-CLOSED, `--check`/`--write` — 16 런타임 게이트와 별개·배포 경계 밖).
- **BC 배치는 G0에서 사람이 결정**(§2 DR-07): ① 새 독립 영역 / ② 기존 영역 포함 / ③ architect가 정함.
- **작업 방식(사용자 선호)**: 논의 우선·작은 단위. 큰 플랜 직행 거부. **코어 텍스트(agents/*.md·final.md) 변경은 구현 전 서브에이전트 리뷰**(skill-creator·plugin-creator·근본원인 렌즈) 필수.

---

## §2 Decision Records (status-tagged, evidence-anchored)

### 시대 1·2 — 빌드·표준확정·최적화·Codex 포트·결정성 검증 (DR-01~15) ✅ git 히스토리

> 플러그인 빌드(스킬 10·에이전트 7·커맨드·`plugin validate`)·파일트리 표준(HaffHaff)·**§0 불변식·§4 명명·ACL 분리**·코더 메커니즘 가드레일·BC 경계 G0 고정·**thinking OFF(−24%)**·Codex 포트 PoC(`codex-dddjango/`)·결정성 2차 검증(재현되는 차이=대부분 N=1 분산·제품철학이지 코드 우열 아님). **현행 규칙은 §0·§1·houserules·§3 DO-NOT-RETRY에 보존**, 측정 방법론은 `eval/rubric/EVAL-METHOD.md`로 승계. 상세·커밋 앵커(`fc1d9ce`~`98ebfd3`·HEAD `15ff62d`)·평가 산출물 = **git 히스토리(2026-05-25~29)**.

### 시대 3 — 표준 빈칸 ③·④ + 최종 스모크 + P1a 오류중앙화 집행 사가 (DR-16~24) ✅ 종료·압축

> P1a(ninja problem+json 오류 중앙화)가 핵심 교훈원: **긍정 레시피·LLM 리뷰어 문구만으론 textbook 위반을 못 막고 → 결정적 백스톱이 필요**(DR-21·22 실패가 §3 DO-NOT-RETRY 근거). 라이브 테스트 방법론은 §4 정본. 서사·증거는 git 히스토리·[[dddjango-final-smoke-findings]](C 트랙 등 상세=git 히스토리).

- **DR-16** ✅ 표준 빈칸 ③·④ 메움: ③ 판정-소유 이주 기준(*"레거시냐"가 아니라 "판정·불변식 소유냐"* — 소유→`domain_layer`/순수 데이터→평면 OK/컨텍스트 간 ACL만) + ④ API 스택을 `design-architect` 1급 결정 승격(기본 ninja·기존 존중·버전핀). 14파일 미러. [[dddjango-bc-boundary-nondeterminism]]
- **DR-17** ✅ 동적검증 Tier 2·3 (`b89c59a`): ③ Codex 완전이주 가능(`db_table` 보존+마이그레이션)이나 **비결정** / ④ `design-architect` 보강("의존성 없음→plain 금지·채택=매니페스트 버전핀")으로 **Ninja+핀 수렴 달성**.
- **DR-18** ✅ 최종 수동 스모크(clean fixture)=성공(N=1)·실행 갭 4건 발견·구현: **P1a**(ninja 오류 positive 레시피·`2795824`)·**P1b**(`houserules §6.2` 의존성 핀)·**P2**(코더 메커니즘-소유권 4수·`58660a0`)·**P3**(§9.6 Risky Write 4스테이지·`246ccfc`)·**P4**(③ 이주 비결정·N≥5 보류).
- **DR-19** ✅ 라이브 재테스트(smoke2·방식=§4 스모크 절차): **P1b·P2·P3 라이브 집행 확정**(P3=Codex서 discipline-reviewer blocker 발화=최강 증거) · **P1a Codex 재발**(긍정 레시피-only라 미차단 → *집행 게이트 있는 항목만 라이브 차단됨*).
- **DR-20~22** 🔴 P1a 백스톱 진화 실패: discipline-reviewer "오류 중앙화 규율" blocker(DR-20·`990efb9`·텍스트판별 9/9)→**라이브-파이어서 재현율 약함**(DR-21·Codex 위반을 권고로 강등)→문구 강화 v2도 사전시뮬 0/3(DR-22). **교훈=텍스트판별 통과 ≠ 라이브 발화·LLM 문구 집행이 약함**.
- **DR-23** ✅ P1a v3 = 결정적 백스톱 `check-error-centralization.py`(`b1d8db6`·2미러·`application_layer` HTTP 누수 AND-탐지·0.21s) + 생산자 예방(design-architect 명세) + reviewer 보조. **LLM 불안정을 우회**(P2 이중구조 선례). 라이브 dual 준수.
- **DR-24** 🔴 C 트랙 심층 감사(5 서브에이전트)가 DR-23 "dual 완전 준수" 정정: Codex에 P1a **의미 변종** 잔존(멱등성 스코프크립→`IdempotencySnapshot status:int`가 app 흐름·중앙 핸들러 죽은코드=뿌리 C3). 인벤토리 C1~C9·L1~L4·메타 4갭(①의미변종 백스톱 미포착 ②스코프 규율 ③G1 비결정 ④§9.6 테스트 집행). **P1a 릴리스 보류 재개**(일단락). 정본=git 히스토리.

---

### 시대 4 — 평가 재구조화 + catalog 회귀 + 백스톱 정착·라이브 배선 (DR-25~34) ✅ 종료·압축

> 결정적 백스톱이 7→11종으로 늘고, "exit2→반송" 라이브 배선이 dual 확정된 시기. **채점 방법론은 §4·`eval/README.md` 정본.** 백스톱 코드는 `dddjango/scripts/check-*.py`. 서사는 git 히스토리·메모리 슬러그.

- **DR-25** ✅ 평가 시스템 폴더 재구조화 + 관리 규약: `eval/rubric/`(RUBRIC·EVAL-METHOD 기준 정본)·`eval/results/`(결과 누적)·`README.md`(규약)로 git mv·이력 보존. 시대1 결정성-조사 하니스(`runs/`·`baseline/`·`reset.sh`·`PROTOCOL.md` 등)는 git rm(히스토리 복구 가능). **관리 규약·채점 방법론은 §4·`eval/README.md` 정본**(채점=RUBRIC+EVAL-METHOD·고정입력 RETEST §1·결과 results/ 누적).
- **DR-26** ✅ catalog 컨테이너 §0-1 회귀 3-leg 수정: 근본=3-leg 부재(백스톱 위치 미검사·§632-(2) 위치 침묵·평가 오독)+architect 코인플립. 예방(`design-architect` "평면 유지" 탈출구 폐기·houserules §1.1 carve-out)+백스톱 ⑦ `check-app-container`(루트 컨테이너 차단·1.0.3·7종)+감사(RUBRIC 위치/깊이 분리). 잔존 B-1(빈혈)=reviewer-only. [[dddjango-catalog-container-regression]]
- **DR-27** ✅🔴 NJ-경계 가이드+백스톱(1.0.4): ninja §6.3 신설(415/406 협상=ninja 경계 내)·§6.2 problem 헬퍼 위치 규칙·백스톱 ⑧⑨(미들웨어 자가등록·`common/` 차단·9종). **P-α/P-β 라이브 예방 양 런타임 작동** / 단 Codex 픽스처는 직교 미해결 **C3 멱등성 스코프크립**으로 NJ-2·SD-6 치명 FAIL(DR-24 재현). [[dddjango-njlive-result]]
- **DR-28** ✅ C3 멱등성 스코프크립 집행(1.0.5): 회귀 원인=가드는 이미 있었으나(`ebe116e`) architect 라이브 번복=집행력 부재. 적대 3렌즈가 spec-대조→**코드 산출물 탐지** 재설계 → 백스톱 ⑩ `check-idempotency-scope-creep`(10종)+가드 salience. 라이브 미검증. [[dddjango-c3-enforcement]]
- **DR-29** ✅ 백스톱 10종 발화 매트릭스 검증(스크립트): 전 10종 위반입력 exit2·clean exit0(실 픽스처 5+합성 5·P-α·P-β·C3 실발화). 잔여=라이브 배선 미검증.
- **DR-30** ✅ 라이브 배선 dual 검증: 실제 `/dddjango`서 위반 주입→**exit2 게이트 차단 양 런타임 확정**(DR-21 강등 미재발). Claude=풀 자율 반송-수정 루프·Codex=차단 후 정지(둘 다 안전속성 합격·자율성 차). "주입" 프록시·자연발화 아님. [[dddjango-livewiring-verified]]
- **DR-31** ✅ G0 plain-추천 결함 예방(1.0.6): coordinator가 G0서 framework 즉흥 over-ask+plain 추천=DR-16 위반(Claude 특정·Codex 흔적 0). 처방=G0 절 항목2에 음성 경계 2미러("framework는 G0 축 아님·architect 소유"). 백스톱 부적합(대화 행동·디스크 산출물 0). [[dddjango-g0-plain-recommendation]]
- **DR-32** ✅ C4 빈혈 SQL 가드 ⑪(1.0.7): Codex 3픽스처 판정 SQL 복제(`stock__gte=qty`)에 C형(`domain_layer` 메서드 0개) 백스톱 `check-anemic-sql-guard`(11종)+reviewer 부재-직격. `domain_layer` 유무로 C형(차단)/B형(통과) 갈림·발화 9/9. B형(atomic 관용구)은 보류. [[dddjango-c4-anemic-enforcement]]
- **DR-33** ✅ C 트랙 C1·C6 정리(1.0.8): C1=과대평가 스킵(파일명 차이 무해·소진→409 Minor)·C6=진짜 §2 위반이나 N=1(p1a-v3 1개)→reviewer 한 줄만. **메타=표준 보강은 *반복 확인된 것만***(C4만 N=3 진짜 갭).
- **DR-34** ✅ 라이브 검증 dual(1.0.8): G0(DR-31)·C4⑪(DR-32)·DR-26⑦ **라이브 작동 확정**(G0 framework 미띄움·⑪ 주입 차단·⑦ catalog 자연 이주). **정식 채점(33항목): Claude=FAIL(치명 NJ-2=operation raw 파싱)·Codex=PASS(품질 상)**. 🔄 반전(DR-24 Codex→이번 Claude)·N=1·우열 아님. major-1=NJ-2 갭 후속. [[dddjango-c4live-verified]]

---

### 시대 5 — 표준 개정 라운드: NJ-2·FK·어노테이션·폴더·네이밍·pytest·R/C/Q (DR-35~43) ✅ 종료·압축

> 라이브에서 드러난 갭으로 표준을 정밀 개정한 시기(대부분 N=1·라이브 미검증·커밋됨). 각 처방 상세=메모리 슬러그·`design/` 설계문서(닫힘→git 히스토리)·적대 리뷰 리포트. plugin 1.0.8→1.4.0.

- **DR-35** ✅ NJ-2 원인규명 → §6.3 협상 레시피 교체: 근본=ninja 1.6.x `parse_body`→400 wrap 버그로 **표준 §6.3 처방 자체가 버그**(P1a/C4 "묻힌 가드"와 다름·단순 차단 백스톱은 coder를 막다른 길로 강제하는 함정). `add_decorator(mode="view")` 데코레이터 레시피로 §6.3 3미러 교체+architect/reviewer. **백스톱 신설 ❌**(operation 입력파싱은 11종 원리상 사각·N=1 비결정). [[dddjango-nj2-enforcement]]
- **DR-36** ✅ DR-35 라이브 효과검증 dual + 33항목 채점: **양 NJ-2 PASS=효과 입증**(Claude c4live FAIL→PASS). **반전: Claude 정적준수(품질 상)·Codex FC-2 경계(stock==quantity) 회귀테스트 FAIL**(`.pyc` 정리 후 재현·기능오류 아님·런간 비결정). DR-34서 또 반전·N=1·우열 금지. [[dddjango-nj2-enforcement]]
- **DR-37** ✅ BC 경계 ORM FK 금지: DR-36 부수(Claude OrderModel→catalog ORM FK)를 외부권위(Vernon·모듈러모놀리스)로 파라 — 근본=규칙3이 도메인레벨로만 쓰여 영속성/ORM 미확장. 규칙3 영속성/ORM 확장(같은 애그리거트 FK자유/같은 BC 허용/다른 BC 금지)+규칙4 직교분해 **텍스트 16미러**(DR-05 번복). 백스톱 보류(N=1·BC판별 위양성)·nj2 FK는 underdetermined. [[dddjango-bc-fk-enforcement]]
- **DR-38** ⏸️ NJ-1/협상 over-impl 심층 추적 → **협상=막을 위반 아님**(§6.3:441이 406 협상 허용/명령→백스톱 신호가 정당 코드와 동형=구조적 불가). Claude 5핸들러=django-ninja 공식 1:1(재구현 0). 현 구조(⑧+§6.3+reviewer) 충분·Q-1 경미. 채점지/RUBRIC Q-1 미세보정만(미커밋). [[dddjango-negotiation-noncatch]]
- **DR-39** ✅ 변수 타입 어노테이션(1.0.9·`6fc850f`): 사용자 "변수 전부" → 적대 4렌즈가 "전부 의무화" 기각(자기모순 ~400·집행공백·한계효용) → **공개표면(모듈/클래스 리터럴 상수)만 필수**·지역변수 권장 유지. 백스톱 ⑫ `check-public-surface-annotation`(직계 bare 리터럴만·`Router()` 등 호출식 면제·py3.9/3.12/3.14 1843파일 FP0). [[dddjango-public-surface-annotation]]
- **DR-40** ✅ 산출물 폴더 규약(1.1.0·`012cb5f`): `.dddjango/<생성일>-<slug>/`·재빌드는 Phase 0서 기존 폴더 사용자선택(slug 비결정 B1 완화)·커밋 명문화. 조사 반전(spec-kit/Kiro=커밋주류). `EVAL-METHOD §4.3` 동작관측 트랙 신설(완료 정의 비산입). [[dddjango-output-folder-convention]]
- **DR-41** ✅ 네이밍 규약 + §4 포트/어댑터 헥사고날(1.2.0·`3fd27f5`·DR-05/37 번복): 도메인 bare·역할 접미사·파일명=주클래스 snake·`_app` 폐기·이벤트 과거형·스키마 In/Out·`service/`→`adapter/`. 일반 포트 `…Port`↔`…Adapter`·확립명(Repository/Gateway)은 추상=구현. 외부권위(ACL=Port 사례 0)·적대 4렌즈. 백로그=command/dto 폴더 정렬. [[dddjango-naming-convention]]
- **DR-42** ✅ pytest 테스트 표준(1.3.0·생태계-우선): pytest 3-tier·`mocker`(carve-out=`create_autospec`만·context7 검증)·§6.1 부트스트랩 해지·Phase2 "러너 준비" 신설·eval 하니스 manage.py→pytest 이주·백스톱 ⑬ `check-test-config`(settings 바인딩 부재→exit2). 적대 6렌즈(NO-GO 2 구제). [[dddjango-pytest-test-standard]]
- **DR-43** ✅ R/C/Q 응용 계층 명명(1.4.0·`f6e6b89`·`96b895b`·DR-41 백로그 해소): command/=`…Command`·query/=`…Query`·dto/=`@dataclass …Request` 인터랙터(`execute(request)`)·**selector 함수 폐기**(Way2). 코퍼스 Command=메시지 어휘 보존+§3.6 포인터. RUBRIC SH-3 거주 명명 확장(소급 N/A·시점 ≥1.4.0). [[dddjango-rcq-application-naming]]

---

### DR-44 🔧 ACL 예외 전수성 + 경계 실패 모드 완전성 — 포트 계약 앵커·reviewer C1/C2·api/architect 실패모드 열거 (rcqlive Claude런 흠·미러 적용·미커밋·🔴라이브미검증)
2026-06-06. 발단: rcqlive Claude런 minor 흠 — catalog `StockConflictError`(CAS 재시도 소진 예외)가 order ACL 미번역→presentation 미매핑→HTTP 500(Codex는 409 매핑). 사용자 "이 문제부터 원인 적대리뷰" 지시.
- **원인(적대 4렌즈 — 내 1차 진단 3개 철회/정정)**: ① ACL 번역 비-전수성(코드 1차 뿌리·houserules:205 '번역'은 명령하나 *전수* 미명문) ② 코더 자기-규율(StockConflictError 직접 발명·raise·단위테스트하고 경계처분 누락·"코더 무죄" 철회) ③ acceptance-tester 종단 테스트 갭(CAS 소진→HTTP 인수테스트 양 BC 0건) ④ 표준 이중성(houserules:143 '(`domain_layer` 하위)' 한정구 갭 + ninja:111/341 '도메인/*애플리케이션* 예외→status 매핑' *이미 처방*→500 누수는 위반). **진짜 구조적 뿌리(렌즈B)=포트 예외 계약이 업스트림과 1:1 동기화 의무 부재.** 중대도 LOW(sqlite 자연도달~불가·design-spec:191)·status underdetermined(503>500>409 의미순·Codex 409 독립선택=중립실증).
- **forks(사용자 확정)**: B 보류 · E(포트앵커) 채택 · C2 blocker.
- **처방(6 편집·미러)**: **A**(houserules:143 한정구 `domain_layer`/`application_layer` 확장+전수 번역+bare-catch 비혼동·:205 표셀) + **E**(포트 ABC/docstring=전수 예외목록 단일앵커·업스트림 새예외 시 포트+ACL 함께 갱신=② cross-file 차단) [byte] / **C1**(중앙핸들러 완전성 important·line40 부분중앙화 blocker 우선·프로그래밍오류500 carve-out) + **C2**(ACL 전수성 blocker·포트앵커 위 catch집합-vs-포트선언집합·import-축 직교·DoesNotExist내부번역/재raise/except-Exception carve-out) [semantic reviewer] / **D1**(architecture-api status표 소진 실패모드·retryable 503|409 *둘다정당* 비강제) [byte] + **D2**(design-architect api계약 실패outcome 열거) [semantic].
- **적대 검증 3라운드**: 원인 4렌즈 → 설계 4렌즈(D1 '503권장'→대칭중립·C1/C2 carve-out·C1↔line40 우선순위·E 신설·B 보류·D2 신규성과장 제거) → 계획 3렌즈(Task4 OLD 비유일·grep regex크래시·lookahead미지원·negative-guard 5건 수정).
- **검증**: [byte] 미러 diff IDENTICAL(houserules·api)·[semantic] append 양본 동일·한정구 잔존0·변경 8파일만(negative-guard: acceptance-tester·scripts·tdd·coder·RUBRIC 무수정). **DR-22 사전시뮬 강력 통과**(2 독립 sim: Claude픽스처 C2 blocker+C1 important 발화·Codex픽스처 비발화·carve-out FP0 — P1a 0/3 실패와 달리 포트앵커 결정적판정이라 발화).
- **보류(비-목표)**: B(acceptance-tester 종단 인수테스트 의무화)=유일 신규machinery·D2 게이트·N=1 LOW → 라이브 N≥2 재현 시 재개. 결정적 백스톱=전파 도달성 정적분석 FP불가+'예외 정의-집합 vs ACL catch 차집합' 변종도 내부번역 FP → 보류·재검토 후보. status 특정코드 강제 안함(underdetermined). 층배치(domain vs app) 비처방(A가 무의미화).
- 🔴 라이브 미검증·N=1 → **커밋 `b7cf255`(1.5.0·미푸시)·DR-45서 라이브 검증=생산자측 작동·BUT 부분 미완 발견**. 정본=git 히스토리(설계 v2·적대 리포트).

### DR-45 🔴 aclex 듀얼 라이브 + 심층 적대 감사 — DR-44 fix 부분 미완(인프라 예외 500 누수)·위장 green 테스트·pytest N=2 (커밋 b7cf255·결과지 미커밋)
2026-06-06. DR-44(1.5.0) 라이브 검증: greenfield fixture `~/Desktop/dddjango-aclex-{claude,codex}`(baseline claude `6e48b68`·codex `32d1cf5`·rcqlive 동일 입력·고정 게이트)에서 dual `/dddjango`(사용자 드라이브) → 조정자 채점(코드 직접 정독 + 백스톱 13종 실행 + pytest 실행).
- **커밋**: DR-44 6편집 = `b7cf255`(1.4.0→1.5.0·**미푸시**·origin baseline=`58660a0`). 양 캐시 1.5.0 신선화 IDENTICAL.
- **1차 채점(단일-패스+백스톱)**:
  - **Codex**(결과지 git 히스토리): DR-44 축 PASS(**원래부터 준수** — rcqlive서 이미 409·DR-44는 Codex 대상 아니었음). 포트앵커 얇음·**Q-6 pytest MISS**(manage.py test+unittest=DR-42 C3 **N=2 재현**). 13 tests. `command_factory`=컴포지션루트(ninja:151 *요구*사항이지 위반 아님 — 사용자 오해 정정).
  - **Claude**(결과지 git 히스토리): **rcqlive 흠 직접 수복** — catalog `StockWriteConflict`(CAS 소진)→ACL `StockReservationConflict` 번역(`catalog_product_stock_adapter.py:50-51`)→중앙핸들러 409 retryable, 500 누수 0(조정자 probe 대조=409 problem+json). D2 status표 소진 열거 교과서적(design-spec §2.4:138·§5:190 "미매핑 500" 위험 인용)·포트앵커 3예외 전수·**Q-6 pytest STRONG**(풀스택·함수형 62·mocker 15·TestCase 0). 61 passed. **P4③ 반전: Claude Q-6 강·Codex 약.**
- **🔴 심층 적대 감사(DR-24식·5 서브에이전트 — 사용자 "A" 선택)**: 백스톱 13종+단일정독이 못 본 **major 4 적출**, 조정자 2건 **직접 재현**:
  1. **[VERIFIED] ACL 전수성 인프라-예외 누수 = DR-44 부분 미완**: ACL이 catalog *도메인* 예외 3종(`CatalogError`)만 catch. raw `OperationalError("database is locked")`·`IntegrityError`는 비-CatalogError라 통과→**HTTP 500(text/plain)**(probe B/C 재현). §5.1이 동시성 락을 *인정*하나 §6.7 동시성 테스트가 sequential이라 영구 green. **DR-44가 막으려던 500 누수를 형제 예외 패밀리로 재현.** 대조 probe: StockWriteConflict는 409(처방 작동).
  2. **[VERIFIED] 깨진 JSON 400 plain**: 올바른 CT+깨진 본문→ninja `HttpError(400)`→기본핸들러→400 `application/json`(problem+json 아님·선언 status 밖)(probe A 재현). §2.5.3 위반·**DR-35 변종**(415 데코는 CT만 봄).
  3. **[mutation] 위장 oversell 테스트**: `test_sequential_requests_do_not_oversell` 순차(스레드 0)→CAS 충돌 0회→lost-update 차단 미증명. CAS 무력화(`save_with_cas`→항상 True)해도 통과. + `assert (n-remaining)<=n` 항진(죽은 단언).
  4. **[mutation] 오귀속 check-constraint 테스트**: `IntegrityError`를 내는 건 명명 제약 아니라 `PositiveIntegerField` 암묵 CHECK. 명명 제약 `stock>=-999999` 약화해도 green→산출물 삭제해도 false green.
  - minor: product_id 거대정수→sqlite OverflowError 500(underdetermined·sqlite 아티팩트) · `InvalidOrderQuantity` 핸들러 부재(스키마 `Field(ge=1)`가 가려 latent) · §6.8 write-conflict 종단 미검증(조각 mock 3개만).
  - **CLEAN 확인(거짓양성 차단)**: 계층순수성/DIP/컨텍스트격리(Agent3 CLEAN)·빈혈SQL 0·BC FK 0·스코프크립 0(멱등성 흔적 0)·도메인예외 ACL 번역 진짜 전수·boundary `<` 정확.
- **조정자 자기-정정**: Claude 1차 채점서 "비재시도 OperationalError만 500=C1 carve-out 정당"이라 한 것은 **오판**(동시성 락은 retryable transient지 서버버그 아님). 단일-패스 합리화를 심층감사가 적출. 결과지 PASS→**결함발견 4** 정정(addendum 기록).
- **표준-수준 함의(중요·미해결)**: DR-44 "ACL 전수성"이 *포트 선언(도메인) 예외*에 앵커링→인프라 transient 범위 밖→**표준 완벽 준수 ACL도 OperationalError 누수**. fixture 결함 아니라 **DR-44 표준(`b7cf255`) 자체 빈틈**. Codex는 catalog command가 락마커를 retry 흡수해 우연 회피(구현 특수성·표준 보장 아님). → **소유권 결정 필요**: "ACL이 인프라 예외도 번역" vs "catalog가 락을 retry 흡수"(어느 계층) — 원인 적대리뷰 선행.
- **미해결 백로그(우선순위)**: ① **DR-44 인프라-예외 누수**(방금 작업의 직접 미완·원인리뷰 필요) ② #2 깨진JSON problem+json 중앙화(DR-35 후속) ③ #3·#4 위장 green 테스트(acceptance-tester 동시성 진정성) ④ **pytest 강제**(DR-42·Codex N=2·백스톱 ⑬ 맹점=pytest *무설정*은 못 봄, 깨진설정만) ⑤ DR-44 C1/C2 차단측 라이브 미검증(양런 누수 0이라 발화 안 됨).
- 🔴 **N=1·우열 결론 아님**(DR-44 축은 양 런타임 정상: Codex 기존부터·Claude 수정 후). 정본=결과지 2개(addendum 포함)·이 엔트리.

### DR-47 ✅ NJ-7 오류 변환 완전성(catch-all) — 평가지 차원 신설 + §4.3.1 RUBRIC 등재 + 표준 집행 백스톱⑯ (양판·1.8.0·미푸시·🔴라이브배선미검증)
2026-06-08. 발단: aclex2live B트랙(§4.3.1·ACL-EX2·결과지+메모리 정본) 후속. 사용자 "Claude 평가 거의 만점인데 catch-all 흠이 안 잡힌다 → 추가→채점방법→재채점→수정". (DEVLOG 갭: DR-46=rootcause 소스미러 별도 트랙·aclex 본류 maj1~maj4·min1·min2·§4.3.1·B트랙⑮는 결과지/메모리 `[[dddjango-aclex-r2]]` 정본·DEVLOG 미소급.)
- **흠(NJ-7)**: ninja 최후방 `@api.exception_handler(Exception)` 부재 또는 핸들러 `raise exc` 되던지기 → 미식별(`KeyError`·`ValueError`)·비-retryable 예외가 problem+json 단일변환점 우회→Django 기본 500(DEBUG traceback 누출). §6.2:368-371·477-479 *선재*(집행 갭·텍스트 갭 아님)인데 33항목에 측정 차원 없어 라벨 미포착("Claude 100점인데 흠").
- **① 평가지 NJ-7 신설**(동결 1회 해제·RUBRIC §5.2 정직표기): NINJA 차원 추가(catch-all 등록 grep + bare `raise exc`·비치명 '강'·SD-6[중앙화 *위치*]와 직교[NJ-7=*완전성*]). 재채점: Claude 품질 상→중·Codex 중→하(양 catch-all 부재 grep 확정). **교훈(곁길·내 실수)**: 처음 §4.3.1 EP-5(관측트랙·freeze 라벨무변)로 넣으려다 적대3렌즈 NO-GO→폐기. 정답=RUBRIC 33항목(라벨 반영). 관측 트랙(§4.3.1)↔RUBRIC 차원 구분.
- **② §4.3.1 RUBRIC 등재**(사용자 "회귀 보게 정식 등재"): maj1live엔 EP 표 有·aclex2live 누락(내 §6 재작성 누락) 발견 → RUBRIC **TIER-OBS** 포인터 스텁(status 미복제·SSOT=EVAL-METHOD §4.3.1·라벨 무영향·freeze 밖·NJ-7과 배타) + EVAL-METHOD **§6.1 #9.5** 필수 섹션화(maj1live 이후 cutoff·소급 미적용) + 채점지 2 EP 표 복원. 적대 1렌즈 MODIFY 반영(freeze 자기충돌·소급위반·SSOT 3결함 교정).
- **③ 표준 집행(수정·2.5층)**: 백스톱 **⑯ `check-catch-all-handler.py`**(NinjaAPI 인스턴스별 합산·조건1 catch-all 부재 OR 조건2 핸들러 `raise` 되던지기[Codex `:117 raise exc` 포착]·`raise X from exc`/alt-B+catch-all/분산-파일 면제·alt-B 단독은 면제 아님 §6.2:479) + reviewer "catch-all 안전망" important(blocker 금지·완전성 렌즈와 배타) + 게이트 배선 ①-⑯·1.8.0. **생략**(렌즈C): final.md salience·SKILL.md·coder.md(표준 3중 완비·DR-22 텍스트 효용0).
- **적대 검증**: 등재 1렌즈+집행 3렌즈(정밀도·충분성[백스톱 유일강제·DR-22/21]·범위[새백스톱 vs ⑨확장·N=1 규율 maj1⑭선례]) 전부 MODIFY·NO-GO 0. 백스톱 정밀도: **known-bad 4/4 exit2**(aclex2live claude·codex[조건1+2]·maj1live-codex·합성)·**known-good 5/5 exit0**(maj1live-claude·분산·alt-B+catch-all·plain·번역)·거짓양성0. 미러 byte-id·배선 정합(15→16·잔여0)·문법 OK.
- **커밋**: 평가지=`676c583`·집행=이 커밋(1.8.0·**미푸시**). 🔴 **라이브 배선 미검증**(DR-30식 dual 후속·⑮도 미검증)·N=1(양 런타임 2표본·§6.2 선재·grep 결정적·우열 금지). 정본=결과지 2·RUBRIC TIER-OBS·EVAL-METHOD §4.3.1/§6.1·`[[dddjango-nj7-catchall]]`.

### DR-48 ✅ ninja 함수형→ninja-extra 클래스 컨트롤러 강제 — 표준·에이전트·평가지·백스톱봉합 (9커밋+nit·1.9.0·미푸시·🔴라이브미검증)
2026-06-08. 발단: 사용자 "ninja view 함수형→클래스형 *무조건* 강제·추후 api는 뷰클래스 탐색→포함/생성". 브레인스토밍→spec v1~v3(적대 7리뷰)→subagent-driven 구현.
- **사실확정(브레인스토밍)**: 순수 django-ninja엔 CBV **없음**(`@router.path`=proposal·`ninja/router.py`에 `path` 부재→`AttributeError`·context7+WebFetch raw 확인). 클래스 컨트롤러=**django-ninja-extra**(`@api_controller`+`route`+`register_controllers`). 신뢰성 실사: 활발(★587·MIT)하나 **1인·0.31.x·`django-ninja>=1.6`**. 인증 호환(same API)·예외 중앙화/NJ-7 **보존**(`NinjaExtraAPI(NinjaAPI)` 상속)·415만 재설계.
- **핵심 결정**: ninja-extra **최소**(클래스 라우팅만·permission/throttling/pagination/APIException 제외)·진입점 `NinjaExtraAPI`·컨트롤러=애그리거트·**ControllerBase 미상속**(자동주입·헬퍼 미사용)·`route.*`·파일명 **`<aggregate>_controller.py`**(houserules 파일명=클래스명)·**415 C정책**(기본 내부전용 비적용·외부공개 *명시* 시 함수형 `Router` 격리[클래스엔 `add_decorator` 부재])·등록 **단일 인스턴스 BC로컬**(config 소유·`<app>_api_router.py` import)·grandfather(**touched** 술어=신규/수정만 강제).
- **집행 (a)단계적**: **0차** 백스톱 회귀봉합(`check-{response-schema-bypass,openapi-error-declaration,error-centralization}` `NINJA_IMPORT_RE`에 `ninja_extra` + `check-structure` NJ-1 토큰 — *변경이 유발한* 거짓음성 실측)·**1차** 표준+reviewer("무조건 클래스" 렌즈 **important** 별도 top-level 불릿·DR-21 강등방지·결정적 차단은 3차)·**2차** 라이브(미)·**3차** 무조건클래스 백스톱(미·"컨트롤러부재+신규함수형" *부재신호*·DR-38 동형신호 함정회피·라이브 N≥2 후).
- **적대 7리뷰**(spec): v1 4렌즈 **BLOCKER2**(415 외부공개 모순·기존 백스톱 import 거짓음성회귀)+MAJOR(architecture-api 415"계약"·NinjaExtraAPI스택 **오귀속**[건드리면 안됨·P1 프레임워크비종속]·implementation-test/INSTALLED_APPS/NJ-1/reviewer열거/coder 누락)→v2→v2 재3리뷰 MAJOR(부재신호 거짓음성[미끼컨트롤러]·거짓양성[grandfather편집] **실측**·등록 공유인스턴스·NJ-1=*판정기준*변경→DR-47식 동결해제·grandfather경계 touched·미러 SKILL.md 2벌누락)→v3.
- **9커밋+nit**(832f195·0a92659[Phase0]·f82f9d7·a1af4c8·3301242·0ed3cea·74ad682·88b6434·b1ef7d9·ce87a86[nit]). 미러 **16/16 백스톱+3/3 final.md byte-id**·plugin 1.9.0·spec §7 전수커버·415 C정책 5doc 일관. 최종통합리뷰 Ship-ready.
- **부수발견**: ① **정본↔skill 드리프트 전11스킬**(Claude↔Codex는 IDENTICAL이나 `workspace/reference`↔`skills` 어긋남·ninja만 skill +99줄). **옵션A**=우리변경만 3사본동일·기존드리프트 보존(라이브=skill사본 핵심·정본 백로그). ② **버전핀 정본 `houserules §6.2`(DR-18 신설됐다 해소)→`ninja §2.1` 이동** + bare `§6.2 핀` 댕글링 8곳 청소(RFC9457 `ninja §6.2`와 *맥락구분*). ③ **`user-invocable: false`** frontmatter Claude 11/11·Codex 0/19 선재(→SKILL.md **body** byte-id 기준).
- **백로그**: 2차 라이브 dual·3차 백스톱·정본↔skill 드리프트·`houserules §6.2` 섹션 본체·reviewer `§6.1/§6.2` test-stack·test §20. **토끼굴 2회 회피**(정본드리프트 전면정렬·버전핀 §6.2 섹션 — 둘 다 백로그).
- 🔴 **미푸시**(이전 `9c6d148`·`8f6922c`·DR-47 포함)·**라이브 미검증**(N=0·2차 전)·생성물 미관측이라 우열·효과 결론 없음. 정본=`[[dddjango-ninja-cbv]]`(spec/plan=git 히스토리).

### DR-49 ✅ 데이터소스 골격 의무화 — §632-(2) 면제 폐지·application 이하 모든 BC 골격 무조건·SH-3 치명 (양판·커밋 d2a5536·✅라이브검증=DR-50)
2026-06-08. 발단: cbvlive dual 채점 라이브 피드백(사용자: codex catalog 두 군데·`application/catalog` 골격 불완전·pytest 미도입 → "평가지에 있나·어떤 항목"). 발견1(두 군데)·발견2(골격 미비)·발견3(pytest=Q-6 기존 FAIL).
- **사용자 결정**: "application 이하에 생기는 폴더는 무조건 표준 파일트리 규칙 준수"(catalog 데이터소스도 order처럼 5개 직하+종류 폴더). 경로=(나)트리 전부 무조건→(다)ACL/port도→(A)데이터소스 `application_layer` 빈 계층.
- **§632-(2) 데이터소스 면제 폐지**: 면제는 *판정 실내용(`.py`)*에만. 데이터소스도 위치+4계층+`domain_layer/<aggregate>/` 빈 애그리거트 골격(**애그리거트명=ORM 모델명 도출** `ProductModel`→`product`)+종류 폴더+`api`/`schema`+`acl`/`port` 빈 패키지 무조건. 유스케이스 없으면 `application_layer`만 빈 계층(개념 1차는 *개념 식별 시*). `[통합 시]` port/acl carve-out 폐지(`[선택]`처럼 폴더 항상·코드는 통합 시).
- **발견1**(catalog 두 군데): **SH-9 신설 헛다리**(결정 레인 `test`/`tests` 공존만 봄·codex 루트 catalog는 죽은 startapp 잔재+0001 보존 migrations 핀). 실제는 `check-structure.py:89`가 루트 `apps.py`를 줄곧 **SH-1 FAIL-신호**로 냈는데 채점지 *산문*이 마스크 C에서 "모델 이주로 위치 충족"으로 PASS 뒤집은 것 → **기존 SH-1/SH-4 복원**(소급 아님·기준 변경 아님=§5.4 비위반). cbvlive-codex SH-1 ❌·종합 **(정적 준수→FAIL)** 재판정. migrations-only 핀(apps.py 이주)은 SH-4 🟡·Q-5 경계.
- **발견2**(catalog 골격): **SH-3 치명 격상**(동결 해제 3건째·개정 신규=**소급 금지**·신규 산출분부터·cbvlive 면제). 백스톱 `check-layer-skeleton` 로직 확장.
- **변경(전부 양 미러 byte-id·md5 동일)**: 표준(ddd §632·houserules §0-1/§0-4/§117/§151/트리/표/§123·SKILL)·에이전트(`design-architect:40` "4계층 전개 지시 안 함"→골격 무조건·`discipline-reviewer:46`·**`design-review-ddd:28`**·coordinator ⑦④)·평가지(RUBRIC·rubric-metrix·EVAL-METHOD **17곳**: SH-3 치명 정본 6곳·마스크 C §1.1.M "위치·골격 ⊥ 판정 실내용"·§2.3③ SH-3 WEAK 폐기·freeze 해제 3건째·소급 두 갈래)·백스톱(check-app-container 텍스트만·check-layer-skeleton 로직: api/schema/acl 고정명+*존재* 애그리거트 코어 완비·**ORM 이름 추론 안 함**·`[선택]` 폴더 보수적 미검사·합성5 PASS·거짓양성0)·채점지(cbvlive-codex).
- **적대 검증 7포인트**: FIX-THEN-SHIP → 유일 결함 `design-review-ddd`(lens 리뷰어 매핑 누락·"평면 OK" stale·**G1 설계 감수자**라 백스톱 사각 prose 레인 의존도 큼) 수정 → **SHIP**. 모순·미러·연쇄·평가지정합·백스톱거짓양성·freeze소급·YAGNI 전부 OK.
- 🔴 **미커밋**(이전 `9c6d148`·`8f6922c`·DR-47·DR-48 포함 미푸시)·**라이브 미검증**(post-revision 픽스처 부재·N=1·우열 금지). **후속(비차단)**: ① 발견1 잔재 *생산시점* `check-app-container` G3(`_has_migrated_counterpart`) 면제로 미차단(모델 이주 시 루트 `apps.py` 놓침·eval-time `check-structure:89`만 잡음)·향후 백스톱 보강 ② check-layer-skeleton 정상 BC 거짓양성·architect/reviewer 골격 생성 dual 관측. 정본=`[[dddjango-datasource-skeleton-mandate]]`(결과지 git 히스토리).

### DR-50 ✅ DR-49 데이터소스 골격 라이브 dual 검증 — 개정 메커니즘 작동·Codex 정적FAIL(발견1·FC-2)·Claude 정적준수 (🔴미커밋·N=1·우열금지)
2026-06-08. DR-49(`d2a5536`) 캐시 신선화(1.9.0 양판 rsync+md5·check-layer-skeleton 3자 byte-id) 후 dual `/dddjango` 라이브. fixture `dslive-{claude,codex}` = baseline `17d25a3` + ninja-extra 0.31.4 + 평면 `catalog.Product` 선재(touched 데이터소스 트리거) + eval-meta(PROMPT/README/setup.sh) 제거. 프롬프트="재고 부족 409·충분 시 차감 주문 생성". 게이트=① 새 BC·Ninja·내부전용·thinking OFF. **백스톱 16종 양 런 전부 exit0.**
- **Codex = 정적 FAIL(치명 3)**: SH-1·4(**발견1 재현**=루트 `catalog/apps.py·models.py` 잔재·`settings`는 `application.catalog...django_catalog` 등록·루트는 죽은 잔재)·FC-2(경계 `>`→`>=` mutation green=stock==qty 테스트 부재·DR-35 재현). **단 데이터소스 골격은 완벽** → **DR-49 검증 ①②③④ 직접 입증**: `application/catalog/` 4계층+`domain_layer/product/`(ORM `ProductModel`→`product` 도출) 빈 골격+종류폴더+OHS 완전 실현 · **check-layer-skeleton exit0 거짓양성0** · design-spec §6 골격 명세 · SH-3 PASS. 부수 Q-1(415/406 협상 발명=내부전용인데 design-spec "external" 자체판단)·Q-6(Django TestCase). 결과지=git 히스토리.
- **Claude = 정적 준수·품질 상**: 완전이주(루트 catalog `D`삭제·0001 `R`rename → SH-1·4 PASS)·**DR-48 클래스 컨트롤러**(`@api_controller`+`register_controllers`+`@inject`)·**Q-1 협상 미발명**(내부전용 준수)·**Q-6 pytest**(pyproject `[tool.pytest]`+`mocker`+`@pytest.mark.django_db`·36 passed)·**FC-2 경계 보유**(`test_deduct_stock_to_exactly_zero` stock5→0)·NJ-7 catch-all·EP-3 분기(transient503/영구500). **catalog를 판정소유 BC로 해석**(`Product.deduct_stock`)→데이터소스 시나리오 우회=검증① N/A. 결과지=git 히스토리.
- **DR-49 효과**: 데이터소스 골격 의무화는 **Codex 런(catalog=데이터소스 해석)이 ①②③④로 직접 입증**·백스톱 거짓양성0·SH-3 치명 작동. catalog 역할(판정소유 vs 데이터소스)은 designer-decides 게이트 하 **둘 다 방어가능 설계 분기(P4③)**.
- 🔴 **후속(비차단)**: ① **발견1 생산시점 백스톱 보강 우선순위↑** — `check-app-container` G3(`_has_migrated_counterpart`) 면제로 루트 잔재 exit0 **라이브 확정**(검증⑤ "못 잡음"·reviewer prose도 미포착·SH-1 채점은 grep FAIL이나 게이트는 통과) → 루트 앱 패키지 잔재 직격 백스톱 ② **DR-48 415 우회**(Codex 내부전용인데 external 자체판단→함수 Router로 클래스 강제 무력화) ③ **FC-2 경계**(Codex DR-35 재현) ④ **EP-1 problem+json 형식 갭**(사후 실측·대칭 확인 → **비대칭**: Claude 깨진본문→**400 problem+json**[`@api.exception_handler(HttpError)` 有·채점지 🟡→✅ 정정], Codex→**400 `application/json` `{detail}`**[HttpError 핸들러 부재·problem+json 중앙화 우회·🟡 유지·aclex2live-codex 형식갭 후속후보 재확인·NJ-7 catch-all이 HttpError 경로 못 봄]) · EVAL-METHOD §4.3.1 **probe override 보강**(미실측 시 status 추론 금지·추론은 ninja 파싱/검증 2단계 혼동). **N=1·런간 비결정(DR-24/c4live/nj2live 역방향)·우열 금지.** 정본=`[[dddjango-datasource-skeleton-mandate]]`(결과지 git 히스토리).

### DR-52 🔬 근본원인 전수 분류 (ultracode 99에이전트) — 관측 87% 비결정·잠재 7건 전부 스킬측·reference 결함 8 + 과잉정정 반전 박제 (🔴미커밋·박제=`eval/rootcause/CLASSIFICATION-20260609.md`)
2026-06-09. 발단: nj7live vs ptbootlive dual 비교(사용자: Codex 경미 개선·Claude 퇴행)→"개선이 결정적이지 않고 비결정이 남아 시도마다 품질이 다르다 — **비결정 / reference 부족 / reference 미반영 skill** 3분류로 전 reference·skill·관측 문제 근본원인 파악". ultracode 요청.
- **방법**: Workflow(Inventory→Classify[결정트리 0/1/2a/2b/3]→Latent sweep[미발화 코퍼스]→Synthesize·각 분류 적대검증)·**37분류·11스킬·99에이전트**·HEAD `a4c7434`. 휘발성 /tmp 원본(`wv5num2m0.output` 192KB)→`eval/rootcause/CLASSIFICATION-20260609.md` **영구 박제**(/tmp + 조정자 수동 ninja 보강 병합·181KB·835줄).
- **결과(보정 후)**: 총30 = 관측23(0=2·1=20·2b=1[FC-1]) + 잠재7(2a=2·2b=5). **스킬측 결함=8**(reference 8 = 2a 2 + 2b 6). 핵심=**관측 한정 87%(20/23) 비결정**(표준·Claude/Codex 미러 byte-id로 올바른데 LLM[특히 Codex coder/architect] 런간 흔들림: catalog husk·raw JsonResponse·openapi_extra-only·빈혈SQL·멱등성 스코프크립) · **잠재는 정반대**(7건 전부 스킬측)→"비결정 우세"=이미 하드닝된 관측 모집단 **선택편향**(미발화 코퍼스 결함은 별개로 존재).
- **reference 결함 8(정정 대상)**: **2b 6** = **FC-1**(치명·관측·`Status(201,Out)`×ninja-extra 다중응답→201→OrderOut 바인딩 실패→**happy path 500**·A/B 격리: 튜플 `return 201,X`는 통과·`Status` 래퍼가 범인)·ddd-factory(`architecture-ddd:847` factory가 Product에 없는 `store_id`+description 누락 TypeError)·check_password(`discipline-cleancode:458` `->bool`인데 no-user None 누수)·safe_sql(`implementation-python:2559` `->str`인데 자기-강제 mypy strict 깨짐)·test-router(`implementation-test:2507` §20.1 import flat)·ninja-api(`django-ninja:500` `NinjaAPI()`↔강제 `NinjaExtraAPI()`). **2a 2** = django-web 서버렌더 에러페이지(진짜 고아·ninja JSON-only 위임불가)·test 에러변환 계약테스트 *기법*. **잠재 2b 3건(ddd/cleancode/python)=워크플로 실행증명**(조정자 미재확인→정정 1단계=직접 재현·거짓양성이면 드롭).
- **과잉정정 반전 박제**: 조정자가 4표본 손수검토만으로 "대부분 스킬 부족·비결정 아님" 단언 → 전수 적대검증이 *관측 한정* 87% 비결정으로 **반전**(표본 추출의 함정). **ACL-EX2 앵커 2a→1 STALE 정정**(DR-44 이후 `houserules:144`·ninja §6.2가 침묵 byte-id로 메움).
- **워크플로 불완전→보강**: `ninja` latent 에이전트 API 500 크래시(사용자 실시간 포착)→5스킬만 완료. 조정자 수동 보강=ninja-api 추가·`problem(404,...)` 문서 ellipsis 오탐 기각. /tmp 7/29 → 보정 **8/30**.
- **비결정 20 라우팅**(정본 무수정): 이미 배선 백스톱 ⑤⑩⑪⑯(계측만) · backstopable=yes(catalog-husk·httperror-malformed-body·migration-0001-rewrite)=라이브 N≥2 후 별건 · no(ACL-EX2·FC-2·NJ-2·cross-bc-fk 등)=수용+EVAL 매트릭스·reviewer salience · nit(NJ-1🟡·NJ-5·ControllerBase)=RUBRIC 경미. 0(BC분해·415/406)=드롭, 재현성은 정본 아닌 eval 하니스(G0 고정).
- **다음**: 브레인스토밍으로 정정 *방법* 결정(FC-1 설계선택 3옵션: ①성공 단일 schema / ③튜플+:625 노트 정정 / ②status키 비충돌=기각)→Phase A(즉사 2b 4건 적대리뷰+venv 재검증+`corpus_mirror_sync`). 🔴 **미커밋**(DR-47·48·49·50·51[롤백] 포함 미푸시)·N=관측 한정·우열 금지. 정본=`eval/rootcause/CLASSIFICATION-20260609.md`·`[[dddjango-rootcause-classification-20260609]]`.

### DR-53 ✅ 2b 정정 구현 + FC-1 재분류(2b→비결정) — ddd-factory·check_password·safe_sql·ninja-api + FC-1 상수화 (3미러 전파·🔴미커밋)
2026-06-10. DR-52 분류의 2b 6건 중 **5건 구현**. 발단: 사용자 "2b부터 수정 계획". 절차=배포 master(`dddjango/skills/`) 편집 → `corpus_mirror_sync --write`로 정본+codex 전파(배포정본 모델).
- **결정적 4건(재현·검증 확실)**: ddd-factory(`architecture-ddd` factory를 문서 Product 정의와 정합·store_id 제거+description+price int·인메모리 TypeError 해소·적대리뷰 옵션A)·check_password(`discipline-cleancode` `-> bool` 명시 분기·no-user None누수 제거)·safe_sql(`implementation-python` `-> str`→`-> tuple[str, list[object]]`·strict `disallow_any_generics` 정합)·ninja-api(`implementation-django-ninja §6.2` `NinjaAPI()`→`NinjaExtraAPI()`·:222와 정합).
- **🔴 FC-1 재분류 2b→1(간헐 비결정)**: 코어 ninja 변경 전 실측 중 초반 A/B 발화(`Status(201,…)`→500 / 튜플→통과)했으나 **이후 전수 재현불가**(fresh venv·PYTHONHASHSEED 0-7·pydantic 2.11-2.13·pristine fixture·"첫 몇 런만 실패"). 표준 `Status`는 django-ninja **공식형·대부분 작동** → 결정적 표준결함 아님·**상류 ninja-extra 간헐 미스바인딩**. **③ 튜플 폐기**(deprecated 박제 손해·사용자 결정). 적용=**매직넘버 `201`→`status.HTTP_201_CREATED`(ninja_extra plain int·`HTTPStatus.CREATED`는 IntEnum이라 역효과 500 확인→회피) 상수화**뿐. FC-1 500 비결정 수용(→후속 동시성 검증서 *비결함* 확정·아래 불릿).
- **방법론 교훈(중요)**: 코어 변경 전 실측이 *결정적이라던 결함을 간헐로 뒤집음* → DR-52 "관측 문제 대부분 비결정"을 **FC-1 자신으로 자기-확증**. ③를 박았으면 더 나빴음(공식형→deprecated 교체). 적대 서브에이전트도 독립적으로 500 재현실패. **dual-mirror 절차 정정**: `corpus_mirror_sync`는 **배포(`dddjango/skills/`)가 master**고 `--write`가 정본·codex를 거기 맞춤(소스←배포·옛 메모리 "reference=정본" STALE).
- **✅ 동시성 검증·FC-1 비결함 확정(2026-06-10·후속)**: 사용자 "간헐도 용납 불가"로 봉인 착수→**봉인 전 재현 사냥**. 순차 240+(해시시드 0-19·`.pyc` 정리·fixture 통합12·Literal `status` 충돌 MRE 75)+**동시 1200+**(진짜 멀티스레드 WSGI[`wsgiref`+`ThreadingMixIn`]·워밍업 없는 첫요청 다발·**`Status` vs 튜플 대조 무차별**=둘 다 100% 201) **전부 음성·500=0회**. → FC-1 **1(간헐 비결정)→사실상 비결함(유령)** 격상·초반 A/B=환경 아티팩트(stale `.pyc`)·**`Status` 표준 무변경 확정**(봉인 강행=공식 비-deprecated형을 추측 교체=회귀위험; 튜플=deprecated·단일 schema=200+NJ-4 파괴라 대안 전무). 부수: 415 carve-out(C정책·DR-48) 사용자 재확인=무변경. 매직넘버 상수화만 유지. 격리 MRE=`/tmp/ninja_mre`(휘발).
- **남은 것**: test-router(§20.1 DR-48 클래스컨트롤러 얽힘·보류). (FC-1 상류추적=불요·비결함 확정) 검증: 5정정 재현·`corpus_mirror_sync` **11/11 in-sync**·전파 byte-id. 🔴 미커밋·N=1. CLASSIFICATION 사후정정 반영. 정본=`eval/rootcause/CLASSIFICATION-20260609.md`·`[[dddjango-rootcause-classification-20260609]]`.

### DR-54 ✅ 파이프라인 flow 최적화 리뷰 (트랙 A/B/C) + L1 구현·L2 보류·L3 UX판정 — flow-review.md/l2-spec.md 흡수 후 삭제 (🔴미커밋·N=관측 8런)
2026-06-10. 발단: 사용자 "플러그인 flow가 최선인가". telemetry 실측 3트랙(도구 `workspace/tools/session_telemetry.py`·최근 8 라이브 런). **`flow-review.md`·`l2-reviewer-firstline-spec.md` 정본을 본 DR로 흡수하고 삭제**(배포 직전 정리; 타임라인 다이어그램 `workspace/flow/dddjango-timeline.html`·L1 상세 `g1-tradeoff-hybrid-spec.md`는 잔존).
- **트랙 A(시간)**: WALL(75~699m)은 **게이트 휴먼 유휴**로 9배 출렁여 성능지표 불가(ptcat 699m=사람 자리비움·sub_wall 정상 50m). 비교 가능 지표=서브에이전트 compute(겹침병합) **41~71m** + 코디 턴. 시간 동인=**coder(45~55%)+architect(25~30%)=산출물 본체**(절단 대상 아님). 백스톱 16종·병렬 design-review는 직접비용≈0(코디 Bash <1초). thinking-OFF(−24%) 이미 적용.
- **트랙 B(효용)**: 백스톱은 공짜·거짓양성≈0(AND·git touched-gate)이라 **성능 목적 절단 0개**. 진짜 산출=**정확성 백로그**: ⑦⑬⑮ 표준-수준 사각(⑮ 인프라 transient 누수=DR-45 "빈틈 #1")·⑩ 저-recall·🟡 6종(①⑤⑥⑫⑭⑯) 라이브 미검증 = 성능 아닌 *품질* 트랙(별도).
- **트랙 C(반송)**: 유일 실질 레버=반송 감소. 가장 비싼 반송="설계갭이 G2 백스톱서 터지는 연쇄"(cbvlive catalog 1근인→4런). 후보 레버 L1/L2/L3.
- **L1 ✅구현(`652d826`·🔴dual 라이브 대기)**: G1 트레이드오프 잠금 재호출 제거. v1 mutator(`lock-tradeoffs.py`)=skill-creator·plugin-dev 적대 **NO-GO**(결정성 이동만·읽기전용 안전계약 위반·미러 붕괴·doctrine:44/50 위반)→**v3 2분기 하이브리드**: architect가 G1 기본값을 step4서 명세에 *현재상태 commit*+배너 override. **Y**(scope.md "범위 아님" 항목 수락)=architect 재호출 0·**Z**(override·ripple)=좁은 재호출(coordinator는 scope.md만 갱신=읽기전용 유지). 절감 천장 작음(~5~8%). **라이브 검증(다음 작업·🔴미실행)**: dual N≥2 — (a)Y 수락 시 architect 재호출 0·(b)override 시 재호출+입력 형식 작동·(c)Y override 채택 시 백스톱⑩ exit0(coordinator가 scope.md를 "G1 채택(사용자 승인)" 단독줄로 갱신→⑩ 기존 면제 발화=B1 회귀)·(d)동일 입력→동일 명세(결정성)·(e)Codex 역할계약 충돌 없음·미러 byte-id. 변경 파일=`design-architect.md:36`(멱등성 G1 표면화 제자리 수정)+입력 절 override 1급 항목·`commands/dddjango.md` Phase1 step4~5+G1 배너후 분기+G1'·Codex 미러 2(코드가 정본·스펙 전문 git `652d826`).
- **L2 🔴보류**: "백스톱 위반을 discipline-reviewer가 명세단계 1차 방어"가 목표였으나 **`design-review-ddd.md:28`이 이미 명세단계서 §0 구조(데이터소스 위치 `application/<app>/`·4계층·골격·평면 금지)를 점검**=중복(구조=명세단계 design-review-ddd + 코드단계 백스톱⑦/④의 **2중 방어**). cbvlive 갭은 **DR-49(`d2a5536`)가 이미 처방**(데이터소스 조항을 cbvlive 1차 6/8 15:55 *後인* 20:19 추가). 진단 착오 원인=timeline이 review-ddd 구조점검을 desc 없이 그려 '부재' 오독(→보강 완료). 적대 2차 3렌즈가 구현 직전 중복 적출. 갈래 A(코드단계 ③⑤⑧⑨)도 반송연쇄 약함·가시성 자해로 ROI 낮아 함께 보류.
- **L3 ❌안 함(플러그인 영역 아님)**: wall 최대 변수 게이트 휴먼 유휴는 *사용자 페이싱*이라 UX(게이트 일괄 승인·비동기 알림)로만 개선 가능·기계시간 무관·플러그인이 강제 불가. = 운영 습관 트랙.
- **경고(박제)**: "흐름이 비대하니 검사·리뷰를 쳐내 빠르게"는 트랙 A·B가 정면 반박 — 시간 거의 못 줄이고 안전만 잃음. 단계 제거는 라이브 재현 필수. 🔴 미커밋·N=관측 8런(우열 아님). 정본=본 DR·`g1-tradeoff-hybrid-spec.md`·`[[dddjango-flow-review-l1]]`.

### DR-55 ✅ finallive dual 채점 + EP-1 원인 5단 확정 + 처방 C 집행(백스톱 ⑯ HttpError 확장·1.10.0) — SH-7 Codex 원인=architect 포트 오분류 (🔴미커밋·라이브 자연발화 대기)
2026-06-10. 발단: 파이널 라이브 dual(verbatim 동일 프롬프트·캐시 신선화) 채점 → 사용자 "Claude 잔여 문제 원인 철저 분석 + 재발 방지 수정".
- **finallive dual 채점**: **Codex=종합 FAIL**(SH-7 치명 — `ProductStockPort`를 `application/order/application_layer/place_order/port/`에 배치)·**Claude=종합 정적 준수·품질 상**(WEAK 1=Q-2 깨진본문 EP-1). 정확한 교차(P4③ 재현): Codex=구조 흠+EP-1 problem+json 완비 / Claude=구조 정위치+EP-1 미달. 결과지 `results/20260610-161{5,6}-finallive-{codex,claude}.md`. N=1·우열 아님.
- **SH-7 원인(3 Explore 수렴)**: ① 직접 원인=**Codex design-architect가 design-spec:85·:344에 "use-case dependency under `application_layer/place_order/port/`"로 명시 배치**(coder는 충실 구현 — 책임 아님). "Order 애그리거트가 import 안 함→유스케이스 포트" 추론은 일반 클린아키텍처(use-case outbound port) 정통으론 방어 가능하나 dddjango 표준(houserules §2:144 협력 포트=도메인 소유 `domain_layer/<agg>/port/`)과 충돌 — **LLM 일반지식이 표준을 덮어쓴 형태**. ② 표준 텍스트는 단정적·양 미러 byte-id(약화 없음)·architect:40/reviewer:48 지침 실재 — 그런데 **4중 미포착**(architect 오분류→reviewer가 G2서 "권고 잔여"로 강등→백스톱 16종에 포트 위치 검사 없음→사용자 G2 승인) → 채점만 적출. ③ **"20+회 중 처음"의 3겹**: SH-7 루브릭 신설 2026-05-30(`c5d2437`·신설 후 5회 연속 PASS) + 협력 포트는 매 런 등장(태스크 동형 — "협력 포트 부재" 가설 기각) + 이번에 처음 architect 분류가 use-case 방향으로 굴러간 잠재 비결정 첫 발현. **처방 미정**(사용자 논의 대기).
- **EP-1(Claude 잔여 흠) 원인 5단 사슬 확정**: ① **처방 A(architect)는 작동** — design-spec:95·:319에 "깨진 본문도 중앙 problem+json이 덮는다" 형식 의무 실재(초판 결과지 "A·B 미반영"은 A에 부정확 → 결과지 사후정정 완료). ② 명세 §6.6 행위 목록에 깨진 본문 없음(목록의 결["외부 결과를 가르는 행위"]대로면 일관된 제외) → acceptance-tester 미행사 → coder가 Red를 본 적 없음. ③ **coder 전사 누락** — §6.2:527 레시피 블록에서 핸들러 7종 중 HttpError만 빠뜨림(P1a·C4 동형 묻힌-가드). ④ reviewer 불릿(처방 B) 캐시 실재·신선에도 라이브 미발화(B 0/1·3분 홀리스틱 가시성 천장 — DR-21/22 동형). ⑤ 백스톱 ⑯ 원리상 사각(`Exception` catch-all만 검사). **교훈: 프롬프트 사슬은 어디서든 한 군데만 새도 결과 미달 — 간헐성의 정체는 "의무의 마지막 50cm(핸들러 1개 등록)가 LLM 자유도에만 의존"**.
- **처방 C 집행**(사전 합의 "또 plain이면 C" 결과-기준 충족): `check-catch-all-handler.py`에 **조건 (3) HttpError problem 핸들러 부재** 확장(신설 아님 — NJ-7 한 계약 두→세 조건·게이트 16종 수 불변). **적대 2렌즈 사전 리뷰 MODIFY 반영**: 렌즈A가 ninja 1.6.2 실소스 사실 확정(깨진본문→`HttpError(400)` 재포장·디스패치는 raised 타입 MRO만[`__cause__` 안 봄 → JSONDecodeError 핸들러는 깨진본문 경로에서 죽은 코드]·기본 HttpError 핸들러 선등록→**catch-all이 못 가로챔**·alt-B는 CT만 변경 body `{"detail"}` 유지·Auth 401/403이 HttpError 서브클래스라 GET-only에도 경로 실존) + **D1 적출**: v1이 register call-form을 "저-recall"로 오분류(실제는 거짓양성 벡터) → **등록 인정**으로 수정(인정-전용·차단 표면 불변)·별칭 출처-불문 인정. 렌즈B: 확장>신설(분석 단위 재사용·DR-51 ⑰ 신설→롤백 전례=카운트 churn 실비용)·§6.6 행위 목록 추가 기각(목록 결 붕괴→P4③ 신규 비결정 생성)·coder 체크리스트 기각(동종 전사 신호·P2/DR-22 선례)·**서사 정정 필수**(반영).
- **검증**: 발화 매트릭스 10/10 — known-bad(finallive-claude `config/api.py:78`) **exit2 조건③ 단독**·known-good(finallive-codex `:134` HttpError 핸들러) **exit0**·합성 8종(catch-all만=2·HttpError만=2[기존 ①]·둘다=0·핸들러0=0·별칭=0·register call-form=0·Attribute 인자=0·둘다부재=2/2건) **FP 0**. 나머지 15종 무변경(스크립트 16종 양 미러 byte-id)·캐시 신선화(claude `1.0.0`·codex `1.10.0` 라벨 디렉터리)·plugin.json **1.9.0→1.10.0**. 배선=coordinator ⑯ 설명+pass-note 양 미러·reviewer :45 분업 문구 2곳 양 미러(해당 행 byte-id).
- **부수 관찰(비처방·근거 명시)**: tuple 반환 DeprecationWarning 2건(기능 정상·DR-53 동시성 사냥 음성·`Status` 표준 무변경 유지)·mypy 미실행(표준 §4는 *작성* 규율이지 실행 의무 아님=DR-39 결·Q-7 PASS)·1h 런타임(DR-54 트랙A — coder+architect=산출물 본체·L2 보류 천장). 검증 중 회귀 루프 1회 ⑯=exit0 관측 → **동시 라이브 세션의 픽스처 `git add` 순간 상태**(재실행 exit2·스크립트 결함 아님). 주의: 픽스처가 커밋되면 touched 면제로 백스톱 재현이 침묵(게이트 라이브 시점은 항상 미커밋이라 무관·검증 재현 시만 유의).
- 🔴 미커밋·**라이브 자연 발화 미검증**(다음 dual 라이브에서 ③ 발화/예방 확인)·N=1.

### DR-56 ✅ SH-7 협력 포트 위치 처방 4층(A architect·B reviewer·C 백스톱 ④확장·D 표준 §3 표) — 1.11.0 (🔴미커밋·라이브 자연발화 대기)
2026-06-10. 발단: 사용자 "SH-7은 Codex쪽만 발생 — 원인파악 확실히 먼저, 계획·수정·확인·진행". DR-55의 SH-7 원인 분석을 텍스트 수준까지 완결 후 처방 집행.
- **원인 최종 확정(DR-55 보강)**: ① 근본=**LLM 일반지식(Clean Architecture "use-case가 outbound port 소유")이 하우스 표준(협력 포트=도메인 소유)을 덮어쓴 재분류** — Codex architect가 design-spec:85·:344에 "use-case dependency under `application_layer/place_order/port/`"(근거="Order 애그리거트가 import 안 함") 명시·coder 충실 구현(무책). 탈출구는 표준 자신의 서술: **§3:178 "도메인이 *의존하는* 역할 포트"** — 실제 호출자는 양 런타임 모두 application command(PlaceOrderCommand)라 "도메인이 직접 의존 안 함→협력 포트 아님" 독해 가능(채점지 노트3 "해석 여지 정직 기록"과 정합). ② **reviewer 강등의 정확한 텍스트 루프홀**: red flag("협력 포트가 application_layer에 배치")는 :48에 실재했으나, "명세 부합만으로 통과 금지" 조항이 **§0 불변식에만 앵커** → 명세가 박은 §2 위반을 "설계 위반 아님·하우스룰 권고 잔여"로 강등(라이브 실증·DR-21 동형). ③ 백스톱 16종 포트 위치 비검사(port/는 `[선택]` 저-recall). ④ **N 정정: N=1이 아니라 N=2** — 적대 렌즈B가 RUBRIC:142의 SH-7 FAIL 앵커(`Codex application_layer/create_order/port/`·루브릭 신설 전 8벌 코퍼스 관측)를 적출 → 동일 형상 2회·둘 다 Codex(DR-55의 "첫 발현" 표현 정정). "반복 확인된 위반만" 규율 충족. 미러는 의미동등(규칙 양쪽 실재) — 차이는 런타임 prior·N=2라 Codex-편향 단정은 보류·처방은 런타임 불문 양 미러.
- **처방 4층(적대 2렌즈 MODIFY 반영)**: **A**(architect 양 미러) — §2 결정 문장 뒤 재분류 금지: "협력 포트의 *위치*는 무조건 `domain_layer/<aggregate>/port/` — 호출자가 application command이고 애그리거트가 직접 import하지 않아도 'use-case dependency' 재분류 금지(command가 *domain-owned* port에 의존하는 것이 DIP)". **B**(reviewer 양 미러) — ① spec-override 앵커 "§0"→"§0·**§2 협력 포트 위치**" 확장(lead-in+말미 설계반송 문장; **§4 명명 확장은 렌즈B 기각** — N=0·§4:250 자기-권장수위 침범) ② red flag에 **blocker**+명세-정당화-무효 명시+백스톱 분업(사각=개명 변종·presentation_layer·빈 골격 뒤 도메인 밖 정의). **C**(백스톱) — **신설 아닌 `check-layer-skeleton` 4번째 위반 형태 확장**(렌즈B: DR-55 확장>신설 성문 선례·게이트 16종 수 불변·DR-51 churn 교훈): `application_layer`/`infra_layer` 하위 `port/`에 비-`__init__` .py → blocker. 기존 AND 가드(표준 레이아웃·BC-단위 touched) 상속·빈 port/ 면제·test 경로 스킵·메시지 3요소(G1 탈출구·양방향 처방[ABC→domain port/·어댑터→acl/ 직속]·기술-유틸 분기 — 렌즈A 필수). **D**(표준) — §3:178 표 정의에 "(호출자가 application 유스케이스여도 소유·위치는 도메인 — 재분류 금지)" 1구·**배포-master 편집→`corpus_mirror_sync --write`**(11/11 in-sync·3미러 md5 일치). 기각: architecture-ddd:1496 포인터(위계 충분·코퍼스 오염 위험)·17번째 신설.
- **검증**: 발화 매트릭스 — **known-bad=finallive-codex exit2**(사건 파일 `application_layer/place_order/port/product_stock_port.py` 정확 적출)·**known-good=finallive-claude+잔존 8픽스처 전수 exit0**(FP 0/9)·합성 8종(application_layer port 실코드=2·infra_layer/acl/port=2·domain 정위치=0·빈 port=0·test 경로=0·비표준 레이아웃=0·완전평면 회귀=2·종류폴더 회귀=2). **16종 전체 회귀 교차**: codex=④만 발화·claude=⑯(DR-55)만 발화 — 두 픽스처가 상호 대조군. 미러: scripts 16종 byte-id·에이전트 수정 문장 양 미러 각 1회·게이트 문단 ④+pass-note 양 미러·캐시 신선화(claude/codex). plugin **1.10.0→1.11.0**.
- 🔴 미커밋·**라이브 자연 발화 미검증**(다음 dual 라이브에서 architect 예방/④ 차단 확인)·잔여 사각(개명 변종·presentation_layer)은 reviewer 의미 레인+채점 레인 동일 사각(비대칭 없음).

### DR-57 ✅ lastlive dual 채점 + **조정자 오채점 사후정정**(Claude "테스트 0"→실측 33 그린·정적 준수) + 채점 가드 3종(EVAL-METHOD §1.5) + L1 ②③ 합류 1문장 (🔴미커밋)
2026-06-10. 발단: 마지막 라이브 dual(lastlive·fixture `~/Desktop/dddjango-lastlive-{claude,codex}`·plugin 1.11.0·verbatim 동일 프롬프트). Codex 채점(`results/20260610-2130-lastlive-codex.md`)=**정적 준수·품질 상**(감수 리포트만 미완·토큰 소진·SH-7 정위치·EP-1 완비). Claude 채점(`-2202-lastlive-claude.md`) **초판=보류(미완성·"테스트 0·테스트도구 0")** → 사용자 "finallive·그전 런에 없던 문제 발생 — 최근 수정들이 Claude 플러그인 악화? 땜빵 말고 전체 재점검 방식?" 질문이 재조사 트리거.
- **반전(포렌식 3트랙+직접 검증): 문제는 플러그인이 아니라 조정자 오채점.** 픽스처 실측 — 테스트 모듈 7+factories 2(`*_test.py` 접미 관례)·`pytest --collect-only -q` **33 collected**·전수 **33 passed**·Tier-1 4종 *런이 직접 부트스트랩*(`.venv/bin/pytest` 20:56:25)·`requirements-dev.txt` 핀+`pyproject.toml` DSM 완비·**런 자신이 21:40 pytest 실행**(`.pytest_cache`)·이후 변경 0(런-정지 상태 채점·22:02). TDD 순서 정상(G1 Y채택 20:48→러너 20:56→인수 21:01→단위·동시성·경계 ~21:30). **재채점**: FC-2 ②경계 `<`→`<=` **2 red**(단위+인수 양 레벨=FC-2 (b)+(d) 효과)·①방향 **13 red**·복원 33 green → **정정 종합=✅ 정적 준수(치명 0)·품질 상**(WEAK=NJ-1 JsonResponse·NJ-5 /v1 — 기존 비결정 축 경미). EP-3도 테스트 주입 라이브 행사(CAS 소진→503+Retry-After·락 503·영구 500 과잉매핑 0·IntegrityError 409). **DR-55 EP-1 수복 + DR-56 SH-7 정위치 양 런타임 = 두 처방 라이브 우호 신호**(단 위반 부재라 백스톱 *차단* 발화는 미관측 — 예방 관측).
- **오판 기전(박제)**: 부재 단정을 뒷받침하는 측정 명령이 transcript에 없음(collect-only·pip list·find 전무) — **측정 없이 부재 단정**. 유력 혼동=직전 채점 Codex 픽스처 `test_*.py` **접두** 관례를 Claude `*_test.py` **접미** 픽스처에 가정 + `requirements.txt`(불변)만 보고 `requirements-dev.txt` 누락. "자기보고 불신" 원칙이 *채점자 자신의 부정 단정*에는 미적용이던 갭.
- **처방 3종**: ① 결과지 2202 **in-place 사후정정**(원 오판 ~~취소선~~ 보존·헤더/종합/FC-2/Q-3/Q-6/EP-3/노트 전 섹션 갱신·**Codex 결과지는 오판 파생 서술 없음 확인 → 무수정**). ② **EVAL-METHOD §1.5 채점 결정성 가드 3종 신설**(freeze 밖·소급 미적용): 수집 오라클 의무(`pytest --collect-only -q` 인용·픽스처 자체 설정 기준·pytest 부재 시 find 양 관례 병기)·부정 단정=출력 인용 의무(§1.2 "인용 없는 PASS 무효"의 대칭)·런-정지 mtime 확인(움직이는 표적 차단). ③ **L1 ②/③ 분기 합류 1문장**(적대 1렌즈 FIX-THEN-SHIP 반영): "②·③도 override 반영이 끝나면 ①과 동일하게 Phase 2로 진행한다(분기는 결정을 반영하는 절차만 가르고 후속 단계는 같다)" — coordinator+codex SKILL 양 미러·양 캐시(claude `1.0.0`·codex `1.10.0` 라벨 디렉터리) 4지점 byte-id. **이번 사고 원인 아님**(mtime이 Y-경로 정상 진입 입증·예방 대칭화)·리뷰어가 재승인-생략=L1 명세 의도 일치 확정·"배너 재출력 금지" 류 절대 문구 금지 경고(architect:54·엣지 :109 탈출구 보존).
- **"최근 수정이 악화" 가설 반증**: 핵심 근거("테스트 0")가 오채점으로 소멸 — lastlive-claude는 finallive 대비 **EP-1 수복**·치명 0·SH-7 유지. L1 유발 가설도 mtime 반증. **전면 재점검 보류 권고**(원하면 별도 트랙: 코디네이터 흐름 계약 전수·DEVLOG 미해결 표지 ~53건 원장 triage).
- **부수 발견(기록만·처방 없음)**: ① **산출물 커밋 단계 부재** — coordinator :22 "코드와 함께 커밋해" *선언*은 있으나 실행 *단계*가 없음·**4픽스처 전수 baseline-only 커밋**(finallive 2 + lastlive 2 = 회귀 아닌 일관 동작) → 처방은 별도 결정 대기. ② 재고 판정 소유 underdetermined 재관측(Codex=catalog `deduct_stock` / Claude=order `StockDeductionService`·ddd §648-(2) 허용 분기·P4③). ③ 테스트 파일명 접두/접미 관례가 런타임 간 갈림(비처방 관찰·pyproject `python_files`로 수집은 결정적).
- 🔴 미커밋·N=1·우열 금지(게이트 조건·설계 분기·완성도 축 모두 상이).

### DR-58 ✅ relive G1 31분 포렌식 — **초기 진단(effort) 적대 기각·진범=Edit 부재 증폭기** → design-architect Edit 허용 (1.12.0·🔴미커밋·라이브 미검증)
2026-06-11. 발단: relive 라이브 런(`~/Desktop/dddjango-relive-claude`·6/10 23:36 구동) G1 ~34분 체감 — 사용자 "문제 있는 듯, 전체로그 원인→적대→계획→적대→구현→완성도 확인으로 진행 + **처방이 성능·품질 저하 없는지 확인**(비저하 하드 게이트)".
- **측정(transcript 정밀 분해)**: G0응답→G1배너 기계구간 finallive **17.3m** / lastlive **18.6m** / relive **31.0m**. 둔화는 **architect 2호출에 국한**(초안 4.3→11.8m·반영 5.2→11.8m — 같은 세션 리뷰3·tester·coder는 전부 정상/더 빠름). **처리율 불변**(60 tok/s·Write 106~145 c/s — 심야 relive가 최고): 모델이 느려진 게 아니라 **출력량 2.1~2.6배**. lastlive "31분" 체감의 본체=L1 ② Y-override 호출(5.4m·설계상)+휴먼 대기 — 결함 아님.
- **반전(적대 2렌즈+claude-code-guide가 초기 진단 기각)**: 조정자 초기 가설 "effort=xhigh 교락"은 **사실관계 오류** — `/effort max`는 "this session only"(stdout 실측·공식 문서)·`effortLevel: xhigh`는 **5/5 백업부터 전역=3런 공통**·finallive(최속)가 직접 반례·architect thinking 블록 0. 기각 가설 일괄: DR-55/56 텍스트(reflect 5.2↔5.1m 동일이 반박)·측정 비대칭(±0.7m 각주)·스킬 비대 누적·심야 API 지연(동세션 통제군 정상)·CC 버전/모델(3런 동일 2.1.170·opus-4-8).
- **진범(relive +844s 분해)**: ① **~430s(51%) 전량 재작성 2회** — 자기일관성 스캔이 실결함 적발(환영 §5.6 참조·이중 `InsufficientStock` 번역 모호) → **Edit 시도 → `No such tool available`**(frontmatter `tools: Read, Grep, Glob, Write`) → 2~3줄 고치려고 26.8/34.2KB 전량 재Write. ② ~330s(39%) 코디 프롬프트 변이(relive에만 "스킬 로드" 지시·Y후보 3 vs 1)發 정독 확대. ③ ~80s(10%) 스펙 비대. 상류=런간 비결정 × **Edit 부재 증폭기**.
- **처방 C-1(채택·적대 2렌즈 양 GO)**: `design-architect.md:4`에 **Edit 추가**. 품질 렌즈 격상 발견 — 이건 시간 최적화가 아니라 **본문↔도구 모순 해소**(:23 "해당 절만 제자리 갱신·전체 재작성 금지"·:52·coordinator :20이 이미 제자리-수정 명령) + **Write-only가 발견 결함의 수정 포기 유도 실측**(14:46:27 "two cosmetic pointer fixes"로 강등) + 환영·오참조 ~10건의 *생산* 모달리티가 전량 Write임을 transcript 확정(Edit는 미접촉 절 바이트 불변). 집행 렌즈: 미러 면제(`corpus_mirror_sync.py:17` agents/*.md 스코프 밖·Codex 대응물 frontmatter tools 메커니즘 없음·body 도구명 일반화)·백스톱 16종 frontmatter 비참조·validate PASS. body 지침 추가 비권고(DR-22 문구강화 계보 — 힘은 도구 가용성). **비저하 게이트**: 검사·스캔·리뷰 절단 0·새 호출/읽기 0.
- **보류(정직)**: C-2 코디 프롬프트 변이 축소(기여 비결정 추정·L2 인접)·C-3 tester Edit(미관측 3.0~3.7m 정상·DR-35 "반복 관측만"). **기대 효과 정직**: G1 중앙값(15~20m)은 분산 그대로 — C-1은 **상한**(재작성 발화 시 31→~24m)을 깎는 처방.
- **P2(G2 구현) 시간 검증(A-5·후속)**: 사용자 "구현도 평소보다 오래?" → 6런 동일 방법론 측정 **반증 — relive G2 37.9m(기계)=6런 중 최속**(finallive 41.0·lastlive 46.2·ptboot 44.3·ptcat 48.3). 백스톱 반송(check-context-isolation 발화→coder fix ~4.5m) 포함하고도 최속·에이전트 단가 전부 정상 하단 → **G1 둔화가 G2로 안 번짐**(동일-세션 통제군 재확인). 체감 "오래"=상태줄 ⏱️가 세션 오픈부터 누적(명령 전 유휴 ~14m)+G1 31m(§기진단)+G2 게이트 인지 ~2m. 전체 벽시계 finallive 75.3m↔relive 77.3m(+2m·분포만 G1 쏠림). 부수: check-context-isolation 라이브 발화 2런째(ptcat·relive=coder ACL 우회 import 재발·차단 정상 작동·N=2 생산자측 예방 후보·DR-35 "반복 관측만" 계보).
- 검증: validate ✔·미러 11/11·백스톱 무변경·캐시 신선화(relive 종료 확인 후 byte-id·1.12.0). **측정 구간표·기각 가설 상세·방법론 노트(out_tok 스트리밍 usage 회계 함정·machine-time 정의 등)는 `g1-latency-forensics.md` 정본을 본 DR로 흡수하고 삭제**(배포 직전 정리; `workspace/flow/`는 `dddjango-timeline.html`만 잔존). 라이브 미검증(다음 런 백로그: architect Edit 실사용·명세 내부 참조 정합 grep·L60형 표적 검증 오판 관측)·N=1.

### DR-58.5 ✅ 백스톱 정밀도 라운드 — brownfield 거짓양성 3건 정밀화 + 빈혈 백스톱 제거(16→15) (Claude 1.13.0·codex 1.10.0·소급 기록·커밋됨)
2026-06-11. DR-58 직후 적대 재평가에서 "실전 잔존"으로 분류된 brownfield 거짓양성과 형태매칭 한계를 정리한 백스톱 정밀도 릴리스. DR 항목 없이 1.13.0(codex 1.10.0)으로 나갔던 것을 배포 전 소급 기록(DR-59 "버전 라인 정리 필요" 해소).
- **brownfield 거짓양성 3건(`631abfd`·버전 미범프)**: B `check-catch-all-handler` 되던지기(조건2)를 그룹 게이트→**파일별 touched-gate**로 좁힘 — 공유 api에 신규 핸들러를 추가했을 때 미변경·커밋된 형제의 legacy `raise exc`까지 차단하던 오발화 제거(조건1 catch-all·조건3 HttpError 부재는 NinjaAPI 인스턴스 단위라 그룹 게이트 유지). C `implementation-django-web` SKILL 라우팅 표에 §11(서버렌더 에러 처리—view-local 재렌더·handler500·transient 503·HTMX) 행 추가(final.md 실재·표 미수록이라 선택 로드 시 미도달 해소). D import 출처 일치(`myproject.errors`→`common/ninja/errors`·ninja+web 2경계 공유=루트 `common/ninja/`).
- **빈혈 백스톱 제거 16→15종(`562facc`·Claude 1.12.0→1.13.0·codex 1.9.0→1.10.0)**: C형 빈혈(비즈 판정이 도메인 규칙 메서드 없이 SQL에만)은 의미 판정이라 AST 형태매칭으로 "규칙 소유"를 판정하면 거짓양성(필드명≠도메인어휘인 정당 규칙 차단)·거짓음성(흔한 컬럼명 우연 매칭)이 **양립 불가**임을 독립 적대 검증으로 확인(면제 정교화가 1차 FN3→2차 13→3차 양면 12로 악화만). C형 적출은 `discipline-reviewer` 의미 점검에 전적 위임(reviewer "부재형(C형) 직격"=`domain_layer` 규칙 0개면 blocker·오케스트레이터 step5 reviewer가 step6 백스톱보다 선행 → 안전망·커버리지 손실 0). `check-anemic-sql-guard.py` 삭제(양 미러)·step6 ⑪ 항목·통과문장 제거·16→15 재번호(⑮=catch-all). (이후 DR-59가 `check-composition-root` 신설로 15→16 복귀 — anemic out·composition-root in, 순계 16 불변·구성만 교체.)
- **web 주석 조건부 정확화(`b9e242a`)**: `_is_retryable_db_error` 공유 위치 주석을 단정→"공유할 때만 루트 승격" 조건부로 약화(의미 불변).
- 3건 다 Claude·Codex 미러 byte-identical 동기. **버전 스킴**: 1.14.0(codex 1.11.0)은 **미사용** — DR-59가 1.13.0→**1.15.0**(codex 1.10.0→**1.12.0**)로 건너뜀. 번호 갭은 의도적(릴리스 경계 압축 없이 비움)·published 버전은 단조 증가라 무해.

### DR-59 ✅ 컴포지션 루트(DI 배선) spec 갭 정본화 — Tier A(스펙)+B(백스톱 ⑯ V1/V2)+v3(V3 presence·reviewer·완전성), 2라운드 설계 적대검증 수렴 (Claude 1.15.0·codex 1.12.0·커밋 3e4e1f7·✅comproot 라이브 dual 검증 GO·a656209)
2026-06-22. 발단: Codex 라이브 산출물에 정본 트리에 없는 `order/composition/` 폴더 발생(파일트리=플러그인 1급 계약·off-tree 폴더 최초) → 사용자 "완벽 원인조사". 근본원인=**컴포지션 루트(구체 infra를 use-case에 주입하는 DI 배선)가 행위로만 강제되고 (WHERE)트리 자리·(WHETHER)긍정 의무·(HOW)예제·집행이 전무** → 런타임이 제각각 즉흥(Codex=off-tree `composition/` 폴더, Claude=`composition_root.py` 우연 근접).
- **확정 결정**: 정본=BC 루트 단일 파일 `application/<app>/composition_root.py`(무접두)·소비=매요청 팩토리 `build_<usecase>_command()`/`_query()`·존재=조건부(application 로직 가진 BC만·데이터소스 BC=빈 `application_layer`는 생략). DDD 교리상 ②전용 파일·BC 루트·per-BC(Seemann 단일 루트+Grzybek 모듈러 모놀리스).
- **처방 Tier A(스펙)**: houserules §0 트리(:70)+파일표(:219)에 composition_root 노드+**긍정 의무**("application 로직 가진 BC는 반드시 둔다·만들어·매요청 호출만") · ninja worked example(매요청 팩토리·base명 `product_stock_port=`↔`DjangoProductStockAdapter` §4 정합) · SKILL.md §0 digest 조건부 1줄(양 미러·reviewer in-prompt 등식 복구) · design-architect 위치·팩토리 명시.
- **처방 Tier B+v3(집행 ⑯ — 신설 아닌 기존 `check-composition-root` 확장·게이트 16종 불변)**: **V1** off-tree `composition/` 폴더 · **V2** `composition_root.py` 오배치 · **V3(v3 신규)** application 로직(`application_layer` 비-`__init__` .py·`dto`/test 제외) 가진 BC의 정본 *부재*. 데이터소스 BC(빈 `application_layer`)는 `_needs_composition_root`=False로 면제. + reviewer 구조 렌즈 §4: 빈-정본 알리바이(점검=팩토리 실재∧new-up 부재·Q-7 스코프를 application service/published_service까지 확장)·모듈/lazy 싱글톤 계약(import/첫호출 공유 불문)·개명 변종 port 동형 열거·"in-tree only" 과한정 제거·touched-gate 사각 노트(양 미러).
- **2라운드 설계 적대검증 수렴(선설계·loop-until-dry — 사용자 "빈틈 누적 금지")**: 1R — v1(무조건 강제) → B/C/D 3렌즈가 `architecture-ddd §632` 데이터소스 골격 열거(comp-root 없음)·`django-ninja:238`·`reviewer:48`과 모순 적발 → **조건부로 기각**(layer-skeleton REQUIRED_KIND_DIRS 선례는 disanalogous — api/schema/acl은 §632에 추가됐으나 comp-root는 아님). 2R — v2(조건부 command/query 게이트) → A'렌즈가 use-case 로직을 적법 `service/`에 fold+`command/` 비워 V3 면제시키는 우회 실측(exit0) → **게이트를 `application_layer` 실 로직 전체로 확장(v3)**. (B'렌즈 GO=데이터소스 FP 실측 해소·C'렌즈 GO=정의 seam 닫힘.)
- **검증**: 발화 매트릭스 7/7 — ds(데이터소스)=exit0·uc(command 부재)=exit2·svc(service-fold 부재)=exit2·dto(dto-only)=exit0·ok(정상)=exit0·v1(off-tree)=exit2·v2(오배치)=exit2(메시지 변종 정확). 미러 byte-identical(스크립트 diff 0·reviewer composition 렌즈 동일)·`corpus_mirror_sync --check` 11/11 0 drift. Tier B 적대 재검증=후속. **버전 라인 정리 완료(→DR-58.5)**: Claude DR-58(1.12.0)→DR-58.5 백스톱 정밀도(1.13.0)→DR-59(1.15.0)·codex 1.9.0→1.10.0→1.12.0. 1.14.0(codex 1.11.0)은 미사용 스킵(의도적). 미커밋 스택은 배포 커밋들로 해소. **버전 라인 통일(2026-06-22, 사용자 요청)**: codex-dddjango를 **1.12.0→1.15.0**으로 올려 Claude·릴리스 태그(`dddjango--v1.15.0`)와 일치 — 두 플러그인은 byte-identical 미러라 같은 번호가 맞다(이후 단일 버전 라인: 양 plugin.json + 릴리스 태그 항상 동일). 내용 무변경·미러 11/11 불변. **✅comproot 라이브 dual 검증(a656209·2026-06-22)**: V3 양방향 발화 확인 — codex catalog=데이터소스적(application 로직 없음)→면제·Claude catalog=use-case(`DecreaseStockCommand`) 보유→발화. 무조건 게이트였다면 codex 거짓차단. service-fold 차단은 합성 매트릭스 svc=exit2로 확인(자연 발화는 미관측). 한계=의미 레인 N_grader=1·blind 미집행.

---

## §3 DO-NOT-RETRY (검증된 실패·헛다리 — 미래 에이전트는 반복 금지)

1. **서브에이전트 모델 다운그레이드**(특히 coder→Sonnet) — 게이트 반송 폭증으로 net 느리고 비쌈(DR-09).
2. **코더가 architect의 기술 메커니즘 대체** — 커스텀 락 백엔드 자작 등 33분 토끼굴(DR-06).
3. **"오케스트레이션 서술 줄여 비용절감"** — 헛다리. 서술은 비용 ~4%. 비용 1위는 코디 output(×5 가중)이고 cache_read는 0.1x(싸다).
4. **커밋 타임스탬프로 "그 smoke가 쓴 코드" 추론** — 워킹트리/캐시는 커밋보다 앞설 수 있음. 세션 로그·design-spec·서브에이전트 시스템프롬프트로 검증하라(DR-10).
5. **machine-time = wall − (user행으로 끝나는 큰 갭)** = 버그. 서브에이전트 반환은 `attachment` 행으로 끝나 오분류됨. **올바른 정의**: `machine = wall − Σ(서브에이전트 실행구간에 안 걸치는 >120s 갭)`(§4).
6. **BC 배치를 사람 선택 제거로 "결정론화"** — 아님. G0에서 선택지를 *표면화*하는 게 정답(DR-07).
7. **catalog 같은 기존 startapp 앱을 표준 트리로 강제 이주** — 스코프 초과·기존 소비자 위협. 결정 = 조치 없음(A), 표준 변경 없음(2026-05-27). **(DR-26 정정 2026-06-02: 이 규칙은 *런이 안 건드린 무관* 앱에만 유효하다. *이번 작업이 touched(새 마이그레이션·판정·쓰기경로)한* 데이터소스 앱은 위치를 `application/<app>/`로 이주한다 — 4계층 전개는 §632-(2) 면제, *위치*는 §0-1 비면제. "조치 없음"을 touched catalog까지 확장한 것이 위치 회귀(smoke4·smoke6)의 표준-측 뿌리였음 → DR-26 3-leg 수정.)**
8. **긍정 레시피만으로 LLM 의미적 안티패턴 차단 기대** — P1a는 §6.2를 positive 레시피로 재작성했으나 *집행 게이트 없이* N≥5까지 보류 → 라이브 재테스트(smoke2)서 Codex가 또 operation 본문 수제 응답(DR-19). 집행 게이트(reviewer blocker·결정적 백스톱) 있는 P2·P3는 라이브 차단됨. **교훈: 의미적 안티패턴은 긍정 레시피 + 집행 게이트 둘 다 있어야 라이브에서 막힌다.** (→ P1a도 2026-05-31 discipline-reviewer 집행 게이트 추가, DR-20.)
9. **편집한 표준을 캐시 신선화 없이 라이브 검증** — 플러그인 캐시(`~/.claude/plugins/cache`·`~/.codex/plugins/cache`)는 워킹트리와 **별도 사본**이라 편집이 안 실림(smoke2 직전 양 캐시 14커밋 stale). `/reload-plugins`는 캐시 재복사 안 함. **라이브 런 전 rsync(또는 재설치) + md5/diff 검증 + 새 세션 필수**(DR-19).
10. **N=9 텍스트-판별 통과를 "라이브 발화"로 간주** — P1a 백스톱은 *고립된 체크를 에이전트에 "적용하라"고 준* 조건에서 9/9 blocker(DR-20)였으나, **라이브 discipline-reviewer**(전체 에이전트 + carve-out + 홀리스틱 심각도 + 경쟁 blocker 맥락)는 같은 실위반을 **권고로 강등**(DR-21). **교훈: 의미적 게이트 문구 검증은 텍스트-판별로 끝내지 말고 *라이브 파이프라인 발화*까지 확인**한다(강등시킬 carve-out·경쟁 blocker가 있으면 특히). 다운그레이드를 막는 강한 표현 필요. **(DR-22 갱신: bullet 문구 강화 v2도 사전 시뮬 0/3 실패 — *문구 강화 자체가 부족*. silent downgrade/누락은 bullet이 아니라 주의 배분·산출 형식에서 일어남. 명시 판정 강제·생산자 예방·결정적 백스톱 등 구조적 개입 필요.)**
11. **결정적 백스톱 exit0을 "구조적 준수"로 해석** — DR-23 B 트랙서 `check-error-centralization.py` dual exit0을 "dual P1a 완전 준수"로 기록했으나, C 트랙 심층 감사(DR-24)서 Codex가 백스톱이 *원리상 못 보는* 의미적 변종(status-bearing snapshot이 application 흐름+중앙 핸들러 죽은 코드, 멱등성 크립이 뿌리)을 가진 게 드러남. **교훈: 백스톱 침묵(exit0)은 "그 백스톱의 좁은 텍스트 계약 통과"일 뿐 "구조적/의미적 준수"가 아니다.** 고정밀·저-recall 게이트의 통과를 전면 준수로 일반화 금지 — 의미적 준수는 코드 정독/심층 리뷰로 별도 확인(특히 멱등성처럼 status-bearing 객체가 계층을 흐를 수 있는 설계).
12. **operation 콘텐츠 협상(406)에 결정적 백스톱 시도** — §6.3:441-442가 operation `Accept`검사→`HttpError(406)`을 *허용/명령*하므로 백스톱 신호가 정당 코드와 **동형**(잡으면 FP·안 잡으면 operation 인라인 회피·양립불가). 멱등성 ⑩ 승격도 표면유비(scope 흔적·§9.6 8행 강제·중복-치명 무게 전무·scope-코드 모순 없음). c4live 채점이 협상을 "범위내 수락"(Q-1🟡·NJ-2/NJ-4 PASS). **협상=§6.3 허용 영역 Q-1 경미지 막을 위반 아님** — ⑧(미들웨어 차단)+§6.3(operation 형태)+reviewer(Q-1)로 충분. 라이브 *미들웨어 아닌 동일신호* N≥2 시만 재검토(DR-38).
13. **변수 어노테이션 "전부(함수 지역변수 포함) 의무화"** — 정상 모범코드 85~100%가 bare 매치라 거짓양성≈0 백스톱 구조적 불가·reviewer-only 집행은 DR-22 문구강화처럼 라이브 실패 위험. **공개 표면(모듈/클래스 변수 *리터럴 상수* 첫 대입)만** 좁혀야 백스톱 성립(좁은 고정밀=11종 안전망 성격 유지). RHS 호출식(`router=Router()`)·타입별칭·이름참조는 면제(타입 자명)·리터럴만 검출. 면제는 직계 base-name 매칭이라 2단 상속 로컬 base 못 미침(known-limitation·reviewer 보완)(DR-39).
14. **ACL "전수 번역"을 포트 *도메인* 예외 집합으로만 앵커링** — DR-44가 ACL 전수성을 포트 선언(도메인) 예외에 묶었으나, OHS 경로는 raw 인프라 예외(`OperationalError "database is locked"`·`IntegrityError`)도 던진다. 비-도메인 예외라 ACL 3-catch를 통과→**500 누수**(aclex Claude 라이브 재현·probe B/C). 동시성 락은 `architecture-db §5.1`상 retryable transient지 서버버그 아님 → 번역/흡수 대상. **교훈: 경계 누수 "전수성"은 포트 도메인 예외뿐 아니라 *그 경로가 실제 던지는 인프라 transient*까지 봐야 한다.** sequential 테스트는 이 경로를 영영 안 태워 green 위장(DR-45 #3). + 단일-패스 채점이 "OperationalError→500=carve-out 정당"으로 합리화한 것을 5-서브에이전트 심층감사가 적출 — **백스톱 13종 exit0 + 단일정독 "clean"을 전면 준수로 일반화 금지**(#11 강화·DR-45).

---

## §4 Methodology & Tools

- **telemetry 파서**: `workspace/tools/session_telemetry.py` — 세션 jsonl에서 서브에이전트 시간/토큰 + 코디 토큰을 raw vs cost로 분해. `--smoke 3 4 5`.
- **리포트 생성기**: `workspace/tools/smoke_report.py` → `smoke_timeline.html`(전 smoke 비교표 + smoke별 단계 타임라인).
- **주의사항**:
  - 서브에이전트 디스패치 도구명 = **`Agent`**(Task 아님).
  - 병렬 판정 = 같은 턴이 아니라 **실행구간 겹침**(설계 리뷰 3종은 이미 병렬 — 레버 아님).
  - cost 가중(입력1 기준): cache_read 0.1 · cache_creation 1.25 · input 1.0 · output 5.0.
  - **machine-time 정의**(사람 대기 제외): `wall − Σ(서브에이전트 실행구간에 안 걸치는 >120s 갭)`. 항상 machine ≤ wall.
  - 서브에이전트 내부 턴은 별도 파일 `<session>/subagents/agent-<id>.jsonl`(`message.model` 포함).
### 스모크 테스트 방식 (정본 — 2026-05-29 통일, 이전 방식 전부 폐기)

표준(스킬/에이전트)을 바꾼 뒤 "**실제 파이프라인이 결함 없는 동작 코드를 만드는가**"를 end-to-end 검증하거나 런타임을 1:1 비교하는 **단일 절차**. (과거 `git clone 토이` 레시피·`reset.sh 인플레이스 리셋`·`E2E-SMOKE-METHOD.md`는 이걸로 대체됨.)

**핵심: 마스터 1개 + 복제 N개.** 데스크탑에 마스터 템플릿 `~/Desktop/dddjango-smoke-sample` 하나만 두고(여기서 직접 런 안 함), `git clone` 으로 런타임별 타깃을 뜬다 → 추적 코드 **바이트 동일**(검증: 세 폴더 `git ls-files | xargs shasum` 동일 해시), venv·DB·시드는 핀(`requirements.txt`)+`setup.sh`로 **결정적 동일** ⇒ 두 런이 같은 시작점에서 출발.

- `~/Desktop/dddjango-claude-index` = Claude `/dddjango` 타깃 · `~/Desktop/dddjango-codex-index` = Codex `dddjango` 스킬 타깃. (회차 구분 필요하면 접미사만 바꿈.)

**마스터 구성**(= baseline + 고정입력 + 셋업):
```
config/ catalog/(Product만) manage.py     # baseline 시드 (구 eval/baseline/ = §2 DR-25 정리·git 히스토리)
requirements.txt   # Django==4.2.30
PROMPT.md          # 고정 기능 프롬프트 + 고정 게이트 답 + 시드 정의(아래)
setup.sh           # venv 생성 + 의존성 + migrate + 시드 + check (멱등)
.gitignore         # .venv/ db.sqlite3 __pycache__/ .dddjango/
```
**생성·복제(분실 시 재현)**:
```bash
S=~/Desktop/dddjango-smoke-sample   # 데스크탑 마스터가 정본 — 분실 시에만 아래로 재현
# baseline 시드(config/catalog/manage.py)는 DR-25 전 git 히스토리: git show <pre-DR25>:workspace/eval/baseline/<경로>
(cd "$S" && git init -q && git add -A && git commit -qm baseline && bash setup.sh)        # 마스터 = 실행가능
git clone "$S" ~/Desktop/dddjango-claude-index && bash ~/Desktop/dddjango-claude-index/setup.sh
git clone "$S" ~/Desktop/dddjango-codex-index  && bash ~/Desktop/dddjango-codex-index/setup.sh
# 리셋 = 폴더 삭제 후 재클론.
```

**고정 입력**(마스터 `PROMPT.md` — 양 런타임 동일하게 답해야 차이가 "런타임 차이"로 읽힘; DR-14 교훈: 프레임워크·러너·구조옵션 미고정 시 비교 불가):
- 프롬프트(토씨 그대로): `재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.`
- 고정 게이트: BC=**① 새 독립 영역**(완전 §0 4계층·평면 교란 제거) · lens=**ddd+db+api** · 스코프=제안대로 · **plain Django** · **Django 기본 test** · G1/G2 무수정 승인 · **thinking OFF**(DR-08).
- 시드(테스트 DB 비오염 위해 마이그레이션 아닌 런타임 데이터로 db.sqlite3에만): Widget stock=10·price=1000, Gadget stock=3·price=2000.

**⚠️ 플러그인 캐시 신선도(표준 편집 시 필수)**: 서브에이전트는 **설치된 플러그인 캐시**에서 스킬/에이전트를 로드(워킹트리 아님). `/reload-plugins`는 캐시를 **재복사하지 않음**(기존 캐시 재독). 반영 = 편집 파일을 캐시에 직접 `cp`(Claude `~/.claude/plugins/cache/changja88/dddjango/<ver>/` · Codex `~/.codex/plugins/cache/dddjango-local/dddjango/<ver>/`) 또는 uninstall→install. 풀런 전 `grep -c "<신문구>" <캐시>/…/final.md`(=1) + 프로브 서브에이전트 1개로 검증. 보조: `~/.claude/plugins/installed_plugins.json` `gitCommitSha`가 의도 HEAD인지.

**합격 기준**:
- (A) `manage.py check` clean · migrate 정합 · `test` 전부 green(201·409·404·**동시성 oversell 없음** 커버).
- (B) 역사적 결함 부재(grep+리뷰): **B1(빈혈/판정 인프라 누수)** — `grep -rn "stock__gte\|balance__gte" application --include=*.py | grep -v test | grep -v "stock__gte=0"` =0, 도메인 판정 메서드(`.deduct(` 등)가 **프로덕션 호출처** 보유, repo CAS의 `WHERE`엔 version 경합가드만(판정 SQL 없음; `stock>=0`은 CHECK 불변식 백스톱이라 OK). **§0 파일트리·§4 명명**. (권장) `discipline-reviewer` 서브에이전트 홀리스틱 감사 blocker/important 0.

**캡처·채점(현행 — §2 DR-25 규약 + 채점지 v2)**: fixture는 **데스크탑(`~/Desktop/dddjango-*`)에 두고 레포로 복사 안 함**(코드트리 대량복사 회피 = 구 `eval/runs/` 폐기 이유). 채점은 **반드시 `eval/rubric/EVAL-METHOD.md`로**(RUBRIC=항목, EVAL-METHOD=결정∥의미 레인·사전식 집계·치명 게이트·마스크 C). **채점지(결과지)** = `eval/rubric/rubric-metrix.md`(33항목 표 + 작성법 *템플릿*)를 복사해 **`eval/results/<날짜시간>-smoke{N}-{claude|codex}.md`**로 만들어 채운다 — **클로드·코덱스 개별**(한 런타임=한 파일). 표 칸 = `Result`(실제 한 것 한 줄·사실만) · `결정`(스크립트/grep) · `의미`(grader) · `종합`(둘 중 하나라도 FAIL→FAIL; `결정PASS∧의미FAIL`=의미적 변종도 FAIL; 치명 종합 FAIL 1개=픽스처 전체 FAIL). 한 줄 → §5 Ledger · telemetry `workspace/tools/session_telemetry.py --smoke N` → `smoke_report.py`.

**정직 경계**: 1회 = 통합 sanity("만들 수 있다"+"게이트 작동"). 확률적 결함(B1·BC비결정)의 *빈도 감소* 증명은 같은 입력 **N≥5 블라인드** + 루브릭(`workspace/eval/rubric/`) 필요(별도 작업). 커밋 타임스탬프로 "그 런이 쓴 코드" 추론 금지(DR-10).

> **폐기(§2 DR-25)**: 구 결정성-조사 하니스(`eval/{baseline,reset.sh,runs/,gate-questions*}`)·인플레이스 `reset.sh` 리셋·`~/Desktop/dddjango-smoke*` 타깃은 정리됨(git 히스토리). 새 런은 sample→clone, 채점은 `eval/rubric`→`eval/results`.

---

## §5 Smoke Run Ledger

machine = 사람 대기 제외 기계시간(§4 정의). cost = 코디 과금 가중단위(M). 상세·단계 타임라인은 `workspace/tools/smoke_timeline.html`.

| smoke | 세션 | machine/wall(m) | 코디 raw/cost(M) | 개선·검증한 가설 | 결과 |
|---|---|---|---|---|---|
| 1a | smoke/a4ef25ae | 47/78 | 12.1/2.71 | 최초 풀 파이프라인 + ninja(JSON·415) 어댑터 | 베이스라인 |
| 1b | smoke/655f2453 | 50/82 | 16.0/3.55 | 주문 베이스라인 | 안정 |
| 1c | smoke/7e71310d | 50/82 | 9.1/2.76 | 주문 베이스라인(G2 정정 패턴 첫 관측) | 안정 |
| 2 | smoke/d3eb9734 | 114/164 | 18.9/5.60 | coder 메커니즘 토끼굴 노출(33분) | 🔴 느린 런(DR-06 동기) |
| 3 | smoke3/a0d03aed | 85/88 | 10.7/3.35 | coder 가드레일 + 표준강화 검증 | 🟢 PASS |
| 4 | smoke4/4cc77948 | 50/50 | 8.1/2.39 | BC 비결정성 노출(catalog 내부 경량) | DR-07 동기 |
| 5 | smoke5/5494f4d0 | 60/60 | 8.1/2.62 | BC 고정 + 규칙4 가드 검증 | 🟢 PASS(`15ff62d`) |
| 6 | smoke6/17a0b9b6 | 52/79 | 8.0/**1.98** | thinking OFF A/B | 🟢 **베스트(−24%)** |
| 7 | smoke7/1a5c44a8 | 60/629 | 9.0/2.91 | 모델 다운그레이드 A/B | 🔴 역효과(+47%, 원복) |
| 8 | smoke8/25fd3ae4 | 41/41 | 7.2/**1.58** | 커밋 HEAD 최종 확인(thinking off) | 🟢 **합격·회귀0**(cost 최저) |

**smoke8 합격 결과**(2026-05-28): 테스트 **20/20 OK**(201·409·404·422·동시성 전부 커버) · 별도 BC `orders`+ACL(port/+acl/, catalog import는 ACL에만) · §0 불변식 전부(application/ 컨테이너·4계층·빈 종류폴더·`infra_layer/django_orders`·`OrderModel`) · §4 명명(`ProductStockPort`←`DjangoProductStockAcl`·`OrderRepository`) · **coder 토끼굴 0**(최장 6.5분) · **architect 정정 재디스패치 0**(2회) · 프로덕션 시그니처 타입. 역사적 결함(루트 models.py·ORM 오명명·ACL 혼입·토끼굴·BC 비결정) **전부 부재**. → 최적화 사이클 종료.

---

## §6 Pointers

- **핵심 커밋**(feat/dddjango-build): `5925ce1`(파일트리 표준) · `6d7720d`/`ad86443`/`1f1ea7e`(표준 강화) · `f9ea088`(coder 가드레일) · `fac248b`(5 레버) · `15ff62d`(BC 수정, HEAD).
- **설계·로그 문서**: `workspace/design/`은 dddjango 일단락으로 비움 — 모든 설계 산출물(빌드·codex포트·catalog·네이밍·폴더·R/C/Q·acl-exception·rootcause 등)은 git 히스토리·메모리 슬러그(§2 각 DR이 가리킴).
- **도구·리포트**: `workspace/tools/{session_telemetry.py, smoke_report.py, smoke_timeline.html}`.
- **AGENTS.md**: Claude 전용 파이프라인 구조 설명.
- **Codex 이식**(§2 DR-12): 조사=git 히스토리(`2026-05-28-codex-port-research.md`) · 빌드 `codex-dddjango/`(스킬 19) · 로컬 마켓플레이스 `.agents/plugins/marketplace.json` · 테스트 픽스처 `/Users/hyun/Desktop/dddjango-smoke`(git 아님, =codex-2 런).
- **평가 시스템 + 결정성-조사 정리**(§2 DR-25): **현행** = `eval/rubric/{RUBRIC,EVAL-METHOD,rubric-metrix}.md`(기준 정본 — RUBRIC=항목·EVAL-METHOD=방법·**rubric-metrix=채점지 템플릿**[33항목 표+작성법, 복사해 채움]) + `eval/results/`(결과·채점 기록, **현행 명명 `<날짜시간>-smoke{N}-{claude|codex}.md`**, 클로드·코덱스 개별) + `eval/README.md`(관리 규약). 채점지 칸=`Result·결정·의미·종합`(§4). DR-13/14/15 결정성-조사 산출물(`comparison*.html`·`RESULTS.md`·`RUBRIC-conformance.md`·`gate-questions*`·`*-N-analysis.md`·`runs/`·`baseline/`·`reset.sh`·`PROTOCOL.md`)은 정리됨 → **git 히스토리**(결론·커밋앵커는 §2 시대2에 압축).
- **표준 빈칸 ③·④ 메움**(§2 DR-16): 14파일 편집 — `architecture-ddd §3.2` 확장(3벌)·`design-review-ddd`/`discipline-reviewer` 2층 탐지(각 2벌)·`design-architect` ③배치+④API스택(2벌)·`implementation-django-ninja` final.md 설치규칙(3벌)+SKILL(2벌). 정적 검증·`plugin validate` 통과, 동적 ⑥ 이연.
- **동적 검증 Tier 2·3 + ④ 보강**(§2 DR-17): Tier 2 = Claude `design-architect` spec(③ migrate + §1.1/§1.2 명시·④ inconclusive). Tier 3 = Codex 전체 스모크 ×3(t3 평면·plain / t3b 이주·plain / t3c POST-boost·Ninja+핀; 산출물 구 `eval/runs/{codex-5,6,7}`은 DR-25 정리·git 히스토리). 보강 = `design-architect` 2미러(headless의 "설치 불확실→plain" 직격 → t3c Ninja 수렴). fixture `~/Desktop/dddjango-codex-{t3,t3b,t3c}`(git 아님)·인터랙티브 미실행 fixture `~/Desktop/dddjango-codex-interactive`. 각 N=1.
- **향후(범위 밖)**: OHS→Published Language DTO 전환 · Codex 품질평가·전체 smoke 루프.
- **개인 메모리 슬러그**(세션 회상용, 정본 아님): dddjango-rebuild-direction · dddjango-work-style · dddjango-audit-ledger · dddjango-standard-hardening-verification · dddjango-bc-boundary-nondeterminism · dddjango-cost-token-optimization. → **내용은 이 DEVLOG에 흡수됨**.
