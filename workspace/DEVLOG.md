<!--
AI-OPTIMIZED DEVLOG. 이 문서는 dddjango 작업의 자기완결 정본이다.
읽는 규칙(AI):
  1) §0 Current State를 먼저 읽어라(지금 상태·베스트 구성·금지사항).
  2) 결정은 §2 Decision Records에서 상태태그(✅adopted/❌rejected/⏸blocked/✔verified)로 찾아라.
  3) 모든 수치·주장엔 증거 앵커(세션ID·커밋SHA·파일:라인)가 붙는다 — 추천 전 실재 확인하라.
  4) 개인 메모리(~/.claude)는 초기화될 수 있어 신뢰 못 함. 이 문서가 정본이다.
마지막 갱신: 2026-06-04
-->

# dddjango DEVLOG

`/dddjango` Claude Code 플러그인 파이프라인의 설계·구현·최적화 전체 여정 기록. AI가 읽는 자기완결 정본.

---

## §0 Current State (READ FIRST)

- **무엇**: 기존 Django 프로젝트에 한 기능을 DDD로 추가하는 Claude 전용 플러그인. 단일 진입 `/dddjango`. 코디네이터(메인 세션) + 서브에이전트 7 + 스킬 10, 게이트 G0/G1/G2.
- **브랜치**: `eval/codex-determinism-n2` (DR-14~20 작업분, main 미병합·main 직계 후손=**ff 가능**). **HEAD = P1a 백스톱(`990efb9`) + docs**. ⚠️ **eval 브랜치 전체가 로컬·미push**(origin엔 P2 `58660a0`까지; P3 `246ccfc`·P1a 백스톱 `990efb9` 모두 로컬) — 릴리스(eval→main 머지/PR + push)는 **사용자 명시 push 승인 대기**(가드레일이 push 차단). (이전 `feat/dddjango-build` HEAD `15ff62d`=DR-13까지.)
- **현재 베스트 구성(검증됨)** = **커밋된 HEAD(`15ff62d`) + extended thinking OFF**. **smoke8(2026-05-28)이 최종 확인**: 코디 과금비용 **1.58M cost-unit(전 런 최저)**, 기계시간 **41분**, 테스트 **20/20**, §0/§4/ACL 전부 충족, 코더 토끼굴 0, architect 정정 재디스패치 0 — 역대 가장 깨끗, 회귀 없음. (smoke6도 동일 구성으로 1.98M·52분이었고, smoke8이 더 낮은 건 슬라이스 granularity 확률 변동.)
  - ⚠️ **thinking OFF는 코드가 아니라 사용자 세션 설정**(`Option+T` / `alwaysThinkingEnabled:false`). 플러그인에 못 박는다. 안 끄면 비용 ≈ 2.6M.
- **속도/비용 현실(닫힌 결론)**: 기계시간 ~41~60분은 "강한 모델 + 다단계 게이트 + TDD + 독립 리뷰" 품질우선 설계에 **내재**. 품질 손실 없이 큰 wall 단축하는 공짜 레버 없음. 통제 가능한 비용 레버는 이미 적용. 큰 비용 레버(컨텍스트 편집/compaction)는 업스트림 차단(§2 DR-11).
- **최적화 사이클: ✅ 종료** (2026-05-28, smoke8 합격). 다음 작업은 코드를 *실제로 바꿀 때*만 재개.
- **배포 상태**: Claude판 **v1.0.0 main 병합·릴리스** 완료(마켓플레이스 `changja88`). 그 후 **Codex 이식 착수** → **PoC 성공(§2 DR-12)**: `codex-dddjango/`(스킬 19, Claude `dddjango/` 무변경). 이어 **코드품질 1:1 평가(§2 DR-13)** → **결정성 2차 검증으로 결론 수정(§2 DR-14)**: N=2 결과 **1차 "claude>codex 13:2:5"는 상당 부분 N=1 분산**이었음. 핵심 신호(B1 도메인소유·stock≥0)가 양 런타임 모두 **비결정**. 2차 프레임워크 무관 코드 대등(codex가 일부 우위). **재현되는 진짜 차이 = 코드 우열이 아니라 게이트 노출 철학·스택 취향**. 표준준수 점수 추정 codex~70·claude~84(신뢰낮음, claude 분산>평균차). (상세=§2 DR-13/14·[[dddjango-codex-port]]; 평가 산출물은 §2 DR-25서 정리·git 히스토리.)
- **B1-fix 표준 검증(§2 DR-15, 2026-05-29)**: DR-14가 남긴 B1 비결정 과제에 **일반화 표준 편집(architecture-ddd §3.2 단일출처 + design-review-ddd/discipline-reviewer 2층 탐지, 12파일 미커밋)**으로 대응 → 새 스모크(sample→clone)로 codex-4·claude-3 동시검증 = **양쪽 설계·코드 끝까지 B1 CLEAN(각 N=1)**. DR-13 빈혈·DR-14 죽은코드 부재. **표준 12파일 커밋(`98ebfd3`).** (claude-3 ninja 통제이탈은 수락; 프레임워크축 비교 무효.)
- **표준 빈칸 ③·④ 메움(§2 DR-16, 2026-05-29)**: DR-15 통제 비교가 드러낸 표준 두 빈칸(코드 버그 아님)을 메움 — ③ 기존 평면 코드에 도메인 판정 얹을 때 이주 기준을 **"판정·불변식 소유냐"**(레거시 아님)로 명문화(소유→`domain_layer` 이주/데이터 소스→평면 OK/컨텍스트 간 ACL·published만), ④ **API 스택을 design-architect 명세 1급 결정으로 승격**(기본 ninja·기존 존중)+ninja 버전핀 설치 규칙. **14파일 편집·미러 byte-identical·`plugin validate` PASS·서브에이전트 3렌즈 리뷰(정확성 2픽스 반영).** 정적까지 — 동적 검증 ⑥ 이연.
- **동적 검증 Tier 2·3 + ④ 보강(§2 DR-17, 2026-05-29)**: Claude(Tier 2) ③ **STRONG PASS**·④ inconclusive(ninja 편향). Codex 전체 스모크 ×3(Tier 3): ③ 완전이주 가능·Claude 수렴이나 **비결정**(t3 평면 유지). ④ 결과 = pre-boost plain(headless 무설치 보수성) → **`design-architect` 보강 후 Ninja+requirements 핀 수렴(t3c, 결정적)**. ④(e) 스택 설계승격 전파 **확정**. (산출물 `eval/runs/{codex-5,6,7}`은 §2 DR-25서 정리·git 히스토리.) 각 N=1(sanity).
- **스모크 방식 통일(§4)**: 마스터 `~/Desktop/dddjango-smoke-sample` + `git clone`으로 런타임별 타깃(`dddjango-{claude,codex}-index`). 구 reset.sh·E2E-SMOKE-METHOD.md 폐기.
- **최종 수동 스모크 → 실행가능 갭 4건 + 라이브 재테스트(§2 DR-18·19, 2026-05-30)**: 커밋된 표준의 라이브 sanity 스모크가 **P1a~P4** 발견 → P1a(positive 레시피·`2795824`)·P1b(houserules §6.2)·P2(메커니즘-소유권 4수·`58660a0`·origin)·P3(§9.6 4스테이지·`246ccfc` 로컬) 구현. **라이브 재테스트(smoke2 fixtures, 캐시 신선화 후 실제 `/dddjango`): P1b·P2·P3 집행 라이브 확정**(P3=Codex서 discipline-reviewer "Risky Write 테스트 부족" blocker 발화→교정, 최강 증거)**·P1a Codex 재발**(또 operation 수제 응답·중앙핸들러 0 — 긍정 레시피-only로 미차단; Claude는 준수). P4 ③ 비결정=N≥5 보류. **P1a 집행 백스톱 구현·검증(§2 DR-20, 2026-05-31)**: discipline-reviewer "API 오류 응답 중앙화 규율" blocker(적대 리뷰 3렌즈 + 텍스트-판별 N=9/9) → DR-19 잔여 ① 해소. **🔴 그러나 P1a 백스톱 라이브-파이어(§2 DR-21, 2026-05-31)에서 재현율 약함 확인**(Codex 실위반→reviewer가 blocker 아닌 권고로 강등; N=9 텍스트-판별 통과 ≠ 라이브 발화) → **릴리스 보류·백스톱 문구 강화 필요.** **강화 v2 구현+사전 시뮬(§2 DR-22)도 P1a 0/3 — 문구 강화만으론 부족(렌즈3 예언 실증; Claude 리뷰어조차 강화 미적용). v3 구현·검증 완료(§2 DR-23): 결정적 백스톱 `check-error-centralization.py`(2미러)+생산자 예방, 위반본 exit2/준수본 exit0·시간 0.21s — LLM 불안정 우회로 P1a actionable 결정적 해결. ✅ 라이브 검증(B, §2 DR-23): dual 실제 `/dddjango`서 P1a 완전 준수(백스톱 exit0·app 깨끗·중앙 핸들러 Codex12/Claude7), coordinator 백스톱 호출=배선 작동·거짓양성0·(나) 예방 작동(이전 Codex 위반→dual 준수); exit2→반송은 dual 준수라 미관측(예방이 막음, 저장 위반본+P2 배선 갈음). P1a 릴리스 보류 해소(릴리스 미실행).** **🔴 그러나 C 트랙 심층 감사(§2 DR-24, 2026-05-31)가 이 'dual 완전 준수'를 정정 — 백스톱 exit0의 후한 해석이었고, Codex에 백스톱이 못 보는 P1a 의미적 변종(멱등성 크립→status-snapshot이 app 흐름+중앙핸들러 죽은코드)이 남음. → P1a 릴리스 보류 *재개*.** P1b·P2·P3는 라이브 견고(릴리스 가능). 정본=`workspace/eval/results/{REMAINING-ISSUES,LIVEFIRE-RESULTS}.md`. **평가 시스템 재구조화·관리 규약**(2026-05-31)=§2 DR-25 / `workspace/eval/README.md`. **C3 멱등성 스코프크립 집행(§2 DR-28, 2026-06-03)**: DR-24가 P1a 보류 재개의 핵심 축으로 지목한 C3에 결정적 코드-탐지 백스톱 ⑩(`check-idempotency-scope-creep`, 게이트 **10종**·`plugin.json 1.0.5`) + `design-architect` 가드 salience 추가 — njlive 2픽스처+합성 검증(codex exit2·claude exit0), 단 **라이브 발화 미검증**(위반주입 fresh 런 필요)이라 보류 완전 해소는 미정. 백스톱 *발화*는 전 10종 **스크립트-레벨 검증(§2 DR-29)**, **라이브 배선도 dual 검증(§2 DR-30)** — 양 런타임 exit2 게이트 차단 ✅(Claude 풀 반송루프·Codex 차단후정지·DR-21 강등 미재발). 잔여 = *자연발화*(주입 아닌 흐름). 부수 발견 **G0 plain-추천 결함**은 §2 DR-31서 예방 처방(API 스택=G0 결정축 아님 G0 절 명시·`1.0.6`, 라이브 관측 미검증). **C 트랙 C4 빈혈 SQL 집행(§2 DR-32)**: Codex 3픽스처 `stock__gte` 판정 SQL 복제에 C형(도메인 메서드 부재) 결정적 백스톱 ⑪ `check-anemic-sql-guard`(게이트 **11종**·`1.0.7`)+reviewer 부재-직격. 표준 텍스트 불변(B형 atomic 관용구 허용=나-3은 적대리뷰가 11곳·DR-06 근거 거짓 판정해 보류). 발화 9/9·라이브 배선 미검증. **C 트랙 C1·C6(§2 DR-33)**: C1 과대평가 스킵(파일명 차이 무해)·C6 진짜 §2위반이나 N=1→reviewer 명확화(`1.0.8`); 메타 = C 트랙 대부분 N=1 단발이라 *반복 확인된 것만* 보강(C4만 N=3). **라이브 검증 dual(§2 DR-34)**: 1.0.8 fresh 런 — **G0(DR-31)·C4⑪(DR-32) 처방 + DR-26⑦ 라이브 작동 확정**(G0 framework 미띄움·Claude before/after·⑪ 주입차단·반송·⑦ catalog 자연이주); L1·L2·C3·P1a·④·P1b 양 런타임 실현; P4③·G1에스컬레이션 갈림 재현. N=1·비결정. **NJ-2 §6.3 버그 집행(§2 DR-35, 2026-06-03)**: DR-34 major-1=NJ-2(Claude operation raw파싱) 파보니 *§6.3 415 처방이 ninja 1.6.x `parse_body`→400 wrap 버그로 작동 안 함*이 근본(P1a/C4 '묻힌 가드'와 달리 처방 자체가 버그 → 단순 차단 백스톱은 coder를 막다른 길로 강제하는 함정). 처방=§6.3 **3미러** 415 불릿→작동 view 데코레이터 레시피(코드~16줄)+406 본문파싱 한정+귀결문 열거, design-architect/discipline-reviewer **2미러** 1구씩(**백스톱 신설 ❌**·텍스트만·적대 6렌즈 통과). 검증 단위6/6·통합19/19·캐시재복사. **라이브 효과검증·정식 채점 완료(§2 DR-36, 2026-06-03)**: 사용자 구동 dual `/dddjango`(415 없는 c4live 동일 입력) → **양 NJ-2 PASS=§6.3 교체 효과 입증**(Claude c4live operation `json.loads` FAIL→nj2live 선언적 payload PASS·design-spec §4.5 §6.3 데코레이터 정확인용=180도 사고전환; Codex operation 얇음·415는 ninja `auth=preflight` 콜백 분리). **정식 33항목 채점 반전: Claude=정적 준수(품질 상·치명 0) / Codex=FC-2 치명 FAIL**(핵심 판정 경계 `<`→`<=` mutation green=stock==quantity 경계 회귀테스트 부재·`.pyc` 정리 후 재현 — *경계 테스트 부재이지 기능 오류 아님*, FC-1 6/6·G3 통과; c4live-codex는 경계 1 red=런간 비결정). 부수=Claude OrderModel→catalog ORM FK 의미흠(c4live는 FK 없음)·Codex JsonResponse idiom/변환점 config 분산/auth 오용/superpowers 간섭. 실측 백스톱 11/11·FC-1 6/6·test 43/15 OK·0001 Claude byte-identical/Codex reformatting. **DR-34(Claude FAIL·Codex 준수)서 또 반전=P4③·N=1·우열 금지**. **BC 경계 ORM FK 금지 처방(§2 DR-37, 2026-06-03)**: DR-36 부수(Claude OrderModel→catalog ORM FK)를 사용자 '정답?' 질문으로 파라 — 외부 권위(Vernon Reference-by-Identity는 ORM/DB FK까지·BC 경계 간 금지·모듈러 모놀리스 합의) no-FK 압도·c4live 양쪽 no-FK 선례 → 근본=규칙3이 도메인 레벨만(영속성 미확장)·런간 정반대 해석=P4③ 빈틈. 처방=**규칙3 영속성/ORM 확장 + 규칙4 직교분해 텍스트 16미러**(claude8+codex8 byte-identical·3계층·합법경로·`implementation-django:1668` 오염제거·design-architect/discipline-reviewer 집행). **백스톱 보류**(cross-BC FK N=1·채점 부수 → DR-35/DR-33 '반복 확인된 것만' 일관·BC판별 위양성·coder 막다른길 — 라이브 N≥2 후 AST+apps.py 재설계). 적대 3리뷰가 규칙4 내부반론·6번째 오염사이트·N=1 위반 발굴→반영. 🔴 라이브 미검증·우열 금지.

---

## §1 What dddjango Is (architecture)

- **파이프라인**: 코디네이터가 작업을 역할로 분해 → 서브에이전트에 위임. 코디는 오케스트레이션·게이트·통합·검증보고만, 설계명세/인수테스트/구현코드는 직접 안 씀.
- **서브에이전트 7**: `design-architect`(통합 명세 작성·producer) · `design-review-{ddd,api,db}`(렌즈별 독립 리뷰·**병렬**·read-only) · `acceptance-tester`(블랙박스 인수테스트 Red) · `coder`(이중루프 TDD 구현) · `discipline-reviewer`(클린코드·TDD 규율 감사·read-only).
- **게이트**: G0 요구·스코프 → G1 설계 → G2 구현. 각 게이트는 사용자 승인(AskUserQuestion).
- **스킬 10**(서브에이전트 `skills:` frontmatter로 preload, `user-invocable:false`로 커맨드 전용): architecture-{ddd,api,db} · implementation-{django,django-ninja,django-web,python,test} · discipline-{cleancode,tdd,houserules}.
  - **코퍼스 altitude 위계**: ddd(프로젝트 전략) → db/api(측면 계약) → implementation-*(코드) → discipline-*(횡단 규율). test=메커니즘(구현측)·tdd=실천(규율측)이라 갈림.
- **파일트리 표준**(출처: 사용자 실프로젝트 HaffHaff, DDD 4계층): `application/<app>/{domain_layer,application_layer,infra_layer,presentation_layer}/`. `_layer` 접미사가 컨테이너 `application/`과 응용계층 이름충돌 해소. 단일 출처 = `discipline-houserules` final.md **§0 불변식**.
- **2부 코퍼스 동기화 규칙**: 스킬 지식은 배포본 `dddjango/skills/<s>/references/final.md` + 소스 미러 `workspace/reference/<s>/reference/final.md` 양쪽에 존재. **본문 byte-identical** 유지(소스엔 `## P1 Source Sufficiency` 헤더만 더 붙을 수 있음). houserules·agents·commands는 plugin-native라 미러 없음(단일 파일).
- **BC 배치는 G0에서 사람이 결정**(§2 DR-07): ① 새 독립 영역 / ② 기존 영역 포함 / ③ architect가 정함.
- **작업 방식(사용자 선호)**: 논의 우선·작은 단위. 큰 플랜 직행 거부. **코어 텍스트(agents/*.md·final.md) 변경은 구현 전 서브에이전트 리뷰**(skill-creator·plugin-creator·근본원인 렌즈) 필수.

---

## §2 Decision Records (status-tagged, evidence-anchored)

### 시대 1 — 빌드·표준확정·최적화·Codex PoC (DR-01~12) ✅ 종료·압축

> 닫힌 시대. 각 결정은 한 줄 + 커밋 앵커로 보존, 서사 디테일은 git 히스토리(해당 커밋). 운영 교훈은 §3 DO-NOT-RETRY에 별도 박제.

- **DR-01** Claude 전용 재구축 + `/dddjango` 단일 진입. 진짜 자산 = `workspace/reference/<skill>/reference/final.md`(소스 코퍼스). Codex 호환은 P9 이월(→DR-12 재개). 2026-05-25.
- **DR-02** 소스 코퍼스 전수 감사·정화 6클러스터 A~F(원칙=**한 주제 한 소유자**, dangling 0). 커밋 `fc1d9ce`·`bb5b751`·`50559c3`·`c57e2da`(django→web 표현계층 이관)·`defc54d`·`76aa30a`.
- **DR-03** 빌드: 스킬 10 + 에이전트 7 + 커맨드, `plugin validate --strict` 통과. 커밋 `08ad561`·`910aab4`·`64ccad7`(설계 `329748e`).
- **DR-04** 파일트리 표준 확정(HaffHaff): 적응형 알고리즘→**단일 표준 트리**, houserules를 코퍼스 1급(단일 출처)으로 승격, 테스트=의미군(`test/{unit,integration,e2e}/`). 커밋 `27dfacd`→`e2cb989`→`5925ce1`.
- **DR-05** 표준 강화: §0 불변식(`application/` 컨테이너·4계층·종류2차폴더 전체·`infra_layer/django_<app>/`·`<Name>Model`/도메인 bare) · §4 명명(추상=개념+역할접미사·구현=기술접두+base일치·`Interface`/`Impl` 금지) · ACL 분리(domain `port/`+infra `acl/`) · ninja. 커밋 `6d7720d`·`ad86443`·`1f1ea7e`.

- **DR-06** 코더 메커니즘-대체 가드레일(smoke2 33분 토끼굴→smoke3 소멸): `coder.md`(명세가 정한 기술 메커니즘=architect 결정, 임의대체 금지·부족하면 반송) + `implementation-django §16.4`(sqlite no-op·커스텀 백엔드 금지·`CheckConstraint` 방어). 커밋 `f9ea088`. → §3 #2. **한계**: LLM 확률적이라 완화책이지 결정론 차단 아님.
- **DR-07** BC 경계 비결정성 수정(smoke4 관측→smoke5): 같은 프롬프트에 architect가 BC 배치를 런마다 다르게 정함 → G0에서 배치를 사람에게 묻고 고정(①새 독립/②기존 포함/③architect) + architect 규칙4 가드(ddd §3.3 애그리거트 완화 ≠ BC 합병·ACL 생략 허가). 커밋 `15ff62d`. → §3 #6·[[dddjango-bc-boundary-nondeterminism]].
- **DR-08** extended thinking OFF = 비용 **−24%**(2.62M→1.98M·smoke5 vs 6), 품질 무손실. 사용자 세션 설정(`Option+T`)이라 못 박음(안 끄면 ≈2.6M).
- **DR-09** ❌ 서브에이전트(특히 coder) 모델 다운그레이드 = 기계시간 +14%·비용 **+47%**(1.98M→2.91M·smoke6 vs 7) 역효과(약한 coder 반송 폭증). 원복·금지. → §3 #1.
- **DR-10** 5 실행시간 레버(명세 다이어트·architect 자기리뷰·db엔진 분기지식·호출 병합·오케스트레이션 경량화). 커밋 `fac248b`. 교훈: 커밋 타임스탬프로 실행시점 코드 추론 금지 → §3 #4.
- **DR-11** ⏸ 공식문서 조사 = 새 저위험 레버 없음. wall은 output 토큰 지배(입력절감 지연 1~5%만), 우리 토큰 88%(cache_read)는 비용 문제지 wall 문제 아님. compaction 세밀설정 업스트림 미노출([1M] 창이라 ~95% 트리거 미달, `#26215`), `/compact` 자동화 불가·실익 제한.
- **DR-12** Codex 이식 PoC 성공(**메커니즘만** 검증): 현행 Codex CLI 0.134.0은 `spawn_agent`·Skills·Plugins GA라 과거 폐기(`911cd22`) 원인 해소(superpowers 패턴 차용). `codex-dddjango/`(스킬 19, **Claude `dddjango/` 무변경**). 설치=`codex plugin marketplace add`+`plugin add`(⚠️캐시 함정·수정 때마다 재설치+세션 재시작). PoC=3가정 통과·end-to-end 16 OK. 상세=`workspace/design/2026-05-28-codex-port-research.md`·[[dddjango-codex-port]]. 미해소(품질단계로): 평면 catalog(§1 vs §0)·coder 가드레일 Codex 약발.

> **시대 1 닫힘**: 최적화 사이클 종료(§0). 베스트 구성 = 커밋 HEAD(`15ff62d`) + thinking OFF(smoke8 합격, §5).

### 시대 2 — Codex 포트 코드품질·결정성·B1-fix 검증 (DR-13~15) ✅ 종료·압축

> 닫힌 시대. 평가 산출물(`runs/`·`comparison*.html`·`*-analysis.md`·하니스)은 DR-25에서 정리됨 — 상세는 정리 전 git 히스토리. 현행 평가 시스템 = `eval/rubric/`+`eval/results/`.

- **DR-13** ⏳ Codex 포트 코드품질 1:1(통제: 같은 baseline·프롬프트·게이트, 같은 최소 스택). 서브에이전트 2종 합산 **claude-1 13 : codex-2 2 : 동등 5**, 격차=구조 생성력 아닌 **감사/리뷰 깊이**(codex 빈혈 도메인 `reserve()` 죽은코드·stock≥0 누락을 감사가 통과). **단 N=1**. 2026-05-28. → DR-14가 결론 수정.
- **DR-14** 🔁 결정성 2차(각 N=2) — **DR-13 결론 대폭 수정**: 1차 격차는 **상당 부분 N=1 분산**(비결정 신호가 우연히 claude 정렬; B1 도메인소유·stock≥0 둘 다 양 런타임 비결정). 프레임워크 무관 코드 **대등**(codex-3 DB감사가 오히려 날카로움). **재현되는 진짜 차이 = 코드 우열 아니라 게이트 노출 철학(claude ~3배 노출·근거 동반)·기본 스택 취향(claude→ninja/pytest, codex→plain)**. 표준준수 점수 추정 codex~70/claude~84(신뢰낮음, claude 분산>평균차). 교훈: 서브에이전트 강한 주장도 경험검증 후 채택(stock CHECK "거짓테스트" 오판). 2026-05-29.
- **DR-15** ✔ B1-fix 표준 검증(codex-4+claude-3, §4 sample→clone): DR-14의 "B1 도메인소유 비결정"에 **`architecture-ddd §3.2` 단일출처(판정·불변식 소유 원칙, db §9.5는 동시성 *메커니즘*만) + 리뷰어 2층 탐지(`design-review-ddd`·`discipline-reviewer`)** 편집으로 대응 → **양 런타임 설계·코드 끝까지 B1 CLEAN**(각 N=1, DR-13/14 빈혈·죽은코드 둘 다 부재). 표준 12파일 커밋 **`98ebfd3`**. 발화 테스트=2 clear+1 fire(B1 오탐0·판별력). 통제 이탈: claude-3 ninja(프레임워크 게이트 미노출, DR-14 재현). 2026-05-29.

> **시대 2 닫힘**: 결정성 결론 = 차이는 대부분 분산·제품철학(코드 우열 아님). B1 표준 `98ebfd3` 커밋. 측정 방법론 교훈(N≥5 블라인드·게이트 고정·형태 다른 태스크·루브릭 정의가 가치 80%)은 현행 `eval/rubric/EVAL-METHOD.md`로 승계.

### DR-16 ✅ 표준 빈칸 ③·④ 메움 (BC 판정-소유 구조 규칙 + ninja 설계 승격·설치 규칙)
2026-05-29. DR-15 통제 비교(claude-3 vs codex-4)가 드러낸 **표준의 두 빈칸**(코드 버그 아님 — 표준이 결정을 안 내려 런타임마다 갈림)을 사용자 논의 후 메움. (DR-15 표준 12파일은 `98ebfd3`로 커밋 완료, 본 항목은 그 위 ③·④ 추가.)
- **③ 구조 배치 빈칸**: 스코프가 기존 평면 코드에 도메인 판정을 얹을 때 표준 4계층 트리로 이주할지 미규정. 실측: claude-3=평면 `catalog/Product.deduct_stock`에 판정 얹음·실행, codex-4=catalog는 순수 데이터·판정은 `Order`(orders) 소유 — 둘 다 B1 CLEAN이나 **BC 분할이 갈림**(=BC경계 비결정 [[dddjango-bc-boundary-nondeterminism]]). **결정**: 이주 기준을 *"레거시냐"가 아니라 "판정·불변식 소유냐"*로 명문화 — (1)소유→`domain_layer` 애그리거트 이주(평면 모델에 판정 메서드 금지), (2)단순 상류 데이터 소스(필드·CHECK만)→이주 불필요·ACL/포트 통합·평면 OK, (3)컨텍스트 간 접근은 ACL/`published_service`만(직접 import 금지). brownfield 기존 규약 §1.1 존중·판정 얹히는 코드에 한정.
- **④ 스택 전파 빈칸**: "greenfield 신규 API=Django Ninja 기본"이 coder 구현스킬에만 묻혀(design-architect 미로드) 설계 전파 안 됨 → codex-4 plain Django 이탈(DR-14·15 재현). **결정**: design-architect가 명세에 **"API 스택"을 1급 결정**으로 기록(기본 ninja, 기존 스택 존중) → 양 런타임 결정론적 수렴 + ninja 신규도입 시 requirements **버전 핀** 설치 규칙. architecture-api(계약 전용)·coordinator 불가침.
- **편집 14파일(미러 byte-identical)**: `architecture-ddd §3.2` 확장(소스+Claude+Codex 3벌) + `design-review-ddd`·`discipline-reviewer` 2층 탐지 보강(각 Claude .md+Codex SKILL 2벌) + `design-architect` ③배치·④API스택 불릿(2벌) + `implementation-django-ninja` final.md 설치규칙(3벌)+SKILL.md(2벌).
- **서브에이전트 리뷰 3렌즈**: plugin-creator=**양호**(미러·매니페스트·런타임 대칭 PASS) / 의도충실성=④충실·③ IMPORTANT 2건 **수정**(`discipline-houserules §2`→`references/final.md §2` 한정자 + 빈혈 적발 괄호를 앱루트 bare 모델까지 확장) / skill-creator=조건부(verbosity 지적 — dddjango "명시=결정성" 가치와 충돌, **현행 유지** 결정; ④ ref위임은 architect 미로드라 거부).
- **검증(정적)**: 미러 byte-identity·`claude plugin validate` PASS·인용 정합.
- **동적 검증 Tier 1 — 리뷰어 발화(2026-05-29)**: 편집된 `discipline-reviewer`(워킹트리 — 캐시는 ③ 미반영 stale 확인)를 중립 픽스처·실측 캡처 4건에 "rubric대로 감사"만 시켜(③ 미언급, 편향 방지) 발화 여부 관찰. **③ 판별 정확**: ⓥ `placement-firetest`(판정이 ORM `ProductModel`에 — 표준트리 존재)→**blocker 발화**(§3.2 "ORM≠도메인"→`domain_layer` 이주), ⓧ `crosscontext-firetest`(ordering이 catalog `domain_layer` 직접 import)→**blocker 발화**(`references/final.md` §2), codex-4(catalog 순수 데이터)→**무발화**("§3.2 case2 정상", 오탐0·보너스로 실측 FK cross-import는 important로 잡음), claude-3(실측)→§3.2↔§1.1 긴장을 **important로 표면화·설계결정 반송**(brownfield 과발화 방지; deduct_stock 프로덕션 호출돼 빈혈/죽은코드 아님 정확 구분). → **발화·무발화·모호처리 3모드 의도대로 작동.** 픽스처 `workspace/design/{placement,crosscontext}-firetest/`(중립·메타0). 각 N=1.
- **이연**: Tier 2(캐시 재설치 + design-architect가 명세에 ③ 이주·④ ninja 박는지) · Tier 3(양 런타임 수렴) · N≥5 빈도통계. → **Tier 2·3 + ④ 보강은 DR-17에서 실행·해소.**

### DR-17 ✅ 동적 검증 Tier 2·3 + ④ 보강 (Codex 스모크 ×3 — ④ 결과 수렴 달성)
2026-05-29. DR-16 ③·④ 편집의 동적 검증(Tier 2·3)을 실행하고, Tier 3가 드러낸 **④ 결과-수렴 실패**를 표준 보강으로 해소. 산출 `workspace/eval/runs/{codex-5,codex-6,codex-7}/`.
- **Tier 2 (Claude `design-architect` spec, 캐시 재설치본)**: ③ **STRONG PASS** — 평면 catalog를 `application/catalog/` 표준트리로 이주 + §1.1 vs §1.2 구분 명시("§1.1 존중=확립 규약이지 미조직 평면 답습 아님 → §1.2 적용") + 판정 도메인 `Product` 소유. ④ **inconclusive** — ninja 쓰나 Claude가 원래 ninja 편향이라 ④ 편집 효과 분리 불가 → 결정적 ④ 테스트는 Codex(원래 plain).
- **Tier 3 (Codex 전체 `/dddjango` headless `codex exec` · framework 미강제 · reserve-stock 스코프 · 평면 catalog fixture · 각 N=1)**:

  | 런 | 조건 | ④ 스택 | ④f requirements | ③ 구조 | tests |
  |---|---|---|---|---|---|
  | codex-5(t3) | pre-boost·no-net | plain | — | 평면(판정 ORM `catalog.models.Product.reserve`) ✗ | 12 OK |
  | codex-6(t3b) | pre-boost·ninja설치 | plain | — | `application/catalog/` 이주·판정 도메인 ✓ | 24 OK |
  | **codex-7(t3c)** | **POST-boost·ninja설치** | **Ninja ✓** | **`django-ninja==1.6.2` ✓** | **완전이주(판정 bare 도메인 + ORM→`infra_layer/django_catalog/ProductModel` db_table 보존 + `catalog/models.py` shim) ✓** | 22 OK |

  - **④ 실패 진단(t3·t3b)**: Codex가 *"adding Django Ninja requires installation not guaranteed in this environment"*로 plain 다운그레이드 — **headless 무설치 보수성**. 단 **④(e) 전파는 확정**: 양 런 모두 "API Stack Decision"을 1급 기록 + *"overrides the dddjango default of Django Ninja"* 명시(codex-4 무자각 plain과 대비). ninja 사전설치해도 architect가 `requirements.txt`만 보고 venv 미확인 → 핑계 유지.
  - **③**: codex가 표준대로 **완전 이주 가능**(t3b·t3c) + Tier 2(Claude)와 수렴. 단 **비결정**(t3 평면 "승인된 설계 예외") — BC경계 런변동 [[dddjango-bc-boundary-nondeterminism]]. t3c는 `db_table="catalog_product"` 보존 + 마이그레이션 이주로 t3가 핑계삼은 *"테이블 연속성 ≠ 코드 이주 불가"*를 정면 입증.
- **④ 보강 (`design-architect` 2미러 byte-identical)**: t3·t3b 실패 추론("requirements에 없음 → 설치 불가 → plain")을 직격 — "신규라 의존성 없다는 사실만으로 plain 안 낮춤 / 채택=매니페스트 버전핀(`implementation-django-ninja` §2.1)이지 라이브 설치 아님 / 확보 불가가 *구체 근거로 확인*된 때만 명세 기록 후 예외". **서브에이전트 리뷰 3건 반영**(출처 §2.1-only 정확화[houserules §6는 "(보류)"라 인용 회피] · escape hatch "막연한 우려 아닌 구체근거+명세기록"으로 루프홀 차단 · 2문장 분리). **효과=결정적**: pre-boost 2런 plain → **post-boost(t3c) Ninja+핀+Ninja Router**, 22 tests green.
- **결론**: ③ = 표준 작동(Codex 완전이주 가능·Claude 수렴) **단 비결정**. ④(e) 전파 = **확정**. **④ 결과 수렴 = 보강으로 달성**(headless에서도 Ninja+핀; (f/g) 설치규칙 t3c 발동). 인터랙티브 ④ 런은 보강이 *더 어려운* headless를 통과해 **선택사항(미실행)**.
- **정직 경계**: 각 N=1(sanity, 빈도 아님). ③ 비결정 미해소(N≥5 별도). 보강은 `design-architect`에만(coder는 §2.1 기보유).

### DR-18 ✅ 최종 수동 스모크 → 실행가능 갭 4건(P1a~P4) 발견·구현
2026-05-30. DR-17까지로 ③·④ 닫은 뒤, **최종 수동 스모크**(Claude 태스크A 재고예약·단일 컨텍스트 + Codex 인터랙티브 태스크B 주문생성·cross-context, clean fixture)로 "커밋된 표준 전부가 라이브에서 발화하는가" sanity 확인. **판정=성공(N=1)**: 정합성 버그 0, 양 런 전 게이트 통과·test green(Claude 25/Codex 23), **축9 인터랙티브 ④ 결판**(ninja 미설치 fixture에서도 Ninja+핀 수렴 — DR-17 boost가 인터랙티브까지). 단 **실행가능 갭 4건 확정**(상세·증거 정본=`workspace/eval/results/REMAINING-ISSUES.md` + [[dddjango-final-smoke-findings]]):
- **P1a** ninja problem+json operation 품질 — Claude 준수(중앙 `@api.exception_handler`+얇은 operation)/Codex 위반(operation 본문 수제 `problem_response`+`OrdersNinjaAPI` 상속 OpenAPI 몽키패치). 근본=§6.2가 problem+json 미디어타입 필수↔schema 우회금지를 동시 요구하나 **ninja에선 에러에 양립불가**(실증 1.6.2). **해법=prohibition→positive 레시피 재작성**(중앙 핸들러+단일 헬퍼 기본A·`create_response` 오버라이드 DRY대안B·프레임워크 기본 5종·OpenAPI application/json **수용한계**·`get_openapi_schema` 사후변형만 금지[상속 허용]·1.6.x핀; 6파일 byte-identical). 실증 probe×3 + 서브에이전트 3리뷰. 커밋 `2795824`. **집행 백스톱(Stage4)은 레시피가 실패모델 뿌리를 쳐서 N≥5까지 보류.**
- **P1b** 의존성 버전 stale(④f) — Codex가 `django-ninja==1.4.5`(최신 1.6.2)를 *기억 속 옛버전*으로 핀(핀=설치 일치→무핀 resolve 안 함). **해법=`discipline-houserules §6.2` 신설**(새 런타임 의존성=무핀 resolve→실제 설치값 핀, '최신'은 기존 프레임워크 핀 호환·안정만·막힌환경 보고; ⚠️ ninja §6.2와 이름만 같음) + ninja §2.1 교차참조 + coder.md 집행. 7파일 byte-identical. 커밋됨.
- **P2** 코더 메커니즘-소유권 — Claude 코더가 커스텀 `BEGIN IMMEDIATE` 백엔드(`DatabaseWrapper` 상속)를 프로덕션 DATABASES ENGINE 배선(=**DR-06 가드레일이 *발화하나 차단 못 함***; 픽스처 오프타깃 4.2.30이 stock `transaction_mode` 부재로 발생조건). 적대검증 2번 뒤집힘: 본질=명시 금지를 코더가 무시+집행 부재(코드 보는 유일 게이트 discipline-reviewer가 Django 기술정확성 명시 제외). **해법=4수**(①픽스처 5.2.14 ②표준 **출처-불문** 정합 `architecture-db §9.5`["stock OPTIONS만, ENGINE교체 아님"]·`implementation-django §16.4`·`coder.md`[상속·몽키패치·시그널·init_command·미들웨어·테스트패치 어떤 형태든 동일위반]+안전PRAGMA 화이트리스트 ③`discipline-reviewer` 메커니즘-소유권 blocker[소유권이지 정확성 아님] ④`scripts/check-mechanism-ownership.py` AND-합성 결정적 백스톱+coordinator G2 Bash 배선[exit2→설계반송]). Ultraplan 원격 4커밋 `af306a4..58660a0`·origin·스크립트 실증 5/5.
- **P3** §9.6 Risky Write 준수 집행 — Codex 동시성 테스트 0(구조 가드만). **사용자 reframe: 본질은 "테스트 누락"이 아니라 "§9.6 Consistency Block 준수 집행" — P2·P3 = 한 집행 공백의 양면**(같은 재고 Risky Write: Claude/A §9.6·테스트 준수하나 §16.4 위반=P2 / Codex/B §16.4 준수하나 §9.6·테스트 위반=P3, 둘 다 게이트 통과). **해법=4스테이지 prevent→catch**(①`implementation-test §20.5` 결정적 CAS-충돌 스파이 레시피[stale-version 주입→재시도, 스레드·커스텀백엔드 없이]+§9.6 포인터 → §9.6↔§16.4 인과 차단 ②`design-architect` 8행 표 산출 ③`design-review-db` 블록 8행 점검 ④`discipline-reviewer` 테스트 *실현* 점검[가드만=blocker]). 적대 리뷰 4회·동적검증 저장산출물 G1 5/5·G2 codexB recall 3/3. 커밋 `246ccfc`(로컬).
- **P4** ③ 판정-소유 이주 비결정 — Claude=catalog 완전이주+Product 애그리거트 / Codex=catalog 평면+published_service 함수(트랜잭션 스크립트). 정반대지만 둘 다 DR-16 허용. **N≥5 블라인드 보류**.
- **정직 경계**: 각 런타임 N=1 + 서로 다른 태스크 → 차이가 런타임차/태스크차 분리 불가. 우열결론·③ 비결정 정량화는 N≥5 별도. 표준 보강 대상이지 "Claude>Codex 입증" 아님.

### DR-19 ✅ 라이브 재테스트(smoke2) — P1b·P2·P3 집행 라이브 확정 · P1a Codex 재발
2026-05-30. DR-18의 P1a~P3 수정을 **실제 `/dddjango` 라이브 런**으로 재검증(저장 산출물·텍스트 검증을 넘어). 방식=`workspace/eval/results/FINAL-SMOKE-PLAN.md` rev3(축13 신설=P3) + `RETEST-HANDOFF.md`.
- **프리컨디션(make-or-break)**: 양 캐시(`~/.claude/plugins/cache/changja88/...`·`~/.codex/plugins/cache/dddjango-local/...`)가 **14커밋 stale**였음(별도 사본·심링크 아님) → 레포 HEAD `246ccfc`와 **byte-identical rsync 신선화**(P2 백스톱 `scripts/check-mechanism-ownership.py` 포함, diff 0 검증). ⚠️ DEVLOG 교훈: `/reload-plugins`는 캐시 재복사 안 함 → 직접 rsync 또는 재설치 필요. **라이브 런은 새 세션에서**(기존 세션은 구 텍스트 메모리 로드).
- **fixture 2개**: `~/Desktop/dddjango-smoke2-{claudeA,codexB}` — smoke-sample 클론, **Django 5.2.14·Python 3.12**(P2 발생조건=stock `transaction_mode` 경로 부여)·**ninja 미설치**(축3 거짓PASS 차단)·**PROMPT.md 제거**(옛 plain-Django 게이트답 누설 차단)·baseline 커밋. 태스크A=Claude·태스크B=Codex 인터랙티브, 게이트 미강제(설계자 결정)·무수정 승인. 13축 직접 채점 + 테스트 독립 재실행 green(Claude 18·Codex 25).

  | P | Claude/A(재고예약) | Codex/B(주문생성) | 판정 |
  |---|---|---|---|
  | **P1b** | `django-ninja==1.6.2` 신선 핀 | `1.6.2`(원래 stale 1.4.5 교정) | ✅ 양쪽 해결 |
  | **P2** | 순수 version CAS·커스텀백엔드 0·백스톱 exit0 | 동일·exit0 | ✅(준수 확인; 위반 미주입=*차단* 미stress) |
  | **P3** | §9.6 8행 + CAS-스파이 4테스트 green | §9.6 8행 + catalog CAS-mock 2테스트; **1차 감사서 "Risky Write 테스트 부족" blocker→coder 교정** | ✅(**Codex서 catch 라이브 발화=최강 증거**) |
  | **P1a** | operation `raise`·중앙 `@api.exception_handler` 5개·수제 0 | ❌ `create_order(request)→JsonResponse` 직접·예외 operation try/except 수제 변환·**`exception_handler` 0** | 🟡 갈림 |

- **P1a 재발 상세**(`smoke2-codexB/.../api_orders.py:108,150-201`): Codex가 raw `HttpRequest`를 받아 `json.loads`·수동검증·`JsonResponse` 직접 반환, 도메인 예외를 operation try/except로 수제 `_problem()→JsonResponse` 변환, 중앙 핸들러 0개. **OpenAPI 몽키패치만 사라짐**(정식 `openapi_extra` 사용)=**(b) 하류 해킹 교정·(a) 핵심 안티패턴 잔존**. Claude/A는 `inventory_api_router.py`에 `@api.exception_handler` 5개로 준수.
- **핵심 교훈**: 긍정 레시피 + *집행 게이트*(P2 결정적 백스톱·P3 discipline-reviewer blocker)가 있는 항목은 **라이브에서 차단됨**. **P1a는 긍정 레시피만 깔고 집행 백스톱(Stage4)을 N≥5까지 보류 → Codex 재발 못 막음(라이브 반례)**. 단 Codex 태스크의 멱등성·content-negotiation(406/415)·커스텀 헤더 복잡도가 raw-request로 기운 교락 큼(N=1).
- **P4 ③ 1점**: 둘 다 *새 BC*(inventory/orders) 신설했으나 판정의 집 갈림 — Claude=리치 도메인 애그리거트(`Product.reserve()`)/Codex=`catalog/published_service/stock.py` 함수(트랜잭션 스크립트), 둘 다 평면 ORM엔 판정 0(안티패턴 회피). N≥5 정량화 대상.
- **정직 경계**: N=1·태스크 상이 → 우열결론 아님. "이번 라이브 런에서 집행 작동/실패"까지(영구 보장 아님).
- **잔여(열린 결정)**: ① P1a 집행 백스톱(Stage4: discipline-reviewer가 ninja operation 본문 수제 응답·중앙핸들러 부재 검사 또는 acceptance-tester content-type 검증) 설계 — *이제 라이브 근거 있음* ② 릴리스(eval 브랜치 머지/PR, **P3 `246ccfc` 로컬·미push**) ③ doc 편집(REMAINING-ISSUES·FINAL-SMOKE-PLAN·RETEST-HANDOFF) 미커밋.

### DR-20 ✅ P1a 집행 백스톱 — discipline-reviewer "API 오류 응답 중앙화 규율" (Stage 4)
2026-05-31. DR-19가 노출한 P1a 라이브 재발(긍정 레시피-only로 Codex 못 막음)에 P3와 **동형의 독립 catch 게이트**를 추가. 생산자 보강(coder §6.2)은 이미 최대치라 무용(Codex가 로드하고도 무시) → 유일 레버 = 독립 catch. 단일 스테이지(P3와 달리 design-architect emit 불요 — §6.2는 coder 처방).
- **변경(2미러 byte-identical)**: `discipline-reviewer`(plugin `dddjango/agents/…` + codex `…/dddjango-discipline-reviewer/SKILL.md`)에 "**API 오류 응답 중앙화 규율(책임 배치·DRY)**" 점검 항목 신설 + §경계 한 절. 명세 채택 스택이 Ninja면 operation 본문이 예외를 try/except로 잡아 status를 고르거나 수제 `JsonResponse`/`HttpResponse`로 오류 응답을 만들면 **blocker**(중앙 `@api.exception_handler`/`create_response`가 예외→status 매핑 소유).
- **적대 리뷰 3렌즈(구현 전, 섬세한 코어 규율)**: 표준정합·작문 / 거짓양성 / 거짓음성+경계. 핵심 결함 1개로 수렴 → 판정 본질을 "operation이 `JsonResponse`를 직접 만드나"에서 "**예외→status 매핑이 operation 밖 단일 소유자로 모였나**"로 재정의(Codex식 `_problem()` 헬퍼-위임 거짓음성 + 같은-모듈 헬퍼 거짓양성 *동시* 차단). 거짓양성 carve-out (a)중앙변환점 하나라도 충족(대안 B 핸들러 0개 OK)·(b)성공응답/`(status,Schema)` 튜플 무관·(c)같은파일 헬퍼 정상. 경계: P2 메커니즘-소유권과 **진짜 동형**(책임배치·DRY이지 ninja 관용구 정확성 판정 아님 — Reviewer 3 "fig leaf 아님" 확인, 특정 데코레이터 존재가 아니라 *배치* 판정).
- **검증**: 정적 `claude plugin validate` ✔ · 미러 byte-동일(bullet·§경계) ✔ · **동적 N=9 텍스트-판별 9/9 정확** — known-bad(Codex/B `api_orders.py`) 3/3 **BLOCKER**(3명 모두 "헬퍼 위임이지만 예외→status 매핑이 operation try/except에 잔존" 포착)·known-good(Claude/A) 3/3 **PASS**(carve-out a/c)·음성트리거(합성 같은모듈 Ninja 2/2·plain Django 1/1 적용안함). 정직 경계: *저장 산출물 텍스트-판별*이지 캐시 신선화 라이브 발화는 아님(P3가 받은 확인사살은 D 트랙 라이브-파이어로).
- **커밋/릴리스**: 백스톱 2미러 + doc 커밋(`990efb9`·`bc75714`, 로컬). **⚠️ 후속 DR-21이 이 백스톱의 라이브 재현율 약함을 발견 → 머지 보류·강화 필요(이 DR의 "검증 완료"는 *텍스트-판별* 한정이었음).**

### DR-21 🔴 P1a 백스톱 라이브-파이어 — 재현율 약함 발견 (DR-20 신뢰도 정정)
2026-05-31. DR-20 P1a 백스톱을 캐시 신선화 후 **실제 `/dddjango` 라이브 파이프라인**으로 확인사살(dual-runtime: `~/Desktop/dddjango-p1a-livefire-{codex,claude}`, 같은 smoke2 주문생성 태스크 verbatim, N=1씩). 정본=`workspace/eval/results/LIVEFIRE-RESULTS.md`.
- **결과**: **Codex = textbook 위반인데 백스톱이 blocker로 못 막고 *권고*로 강등** — operation 본문 수제 `JsonResponse`(`api_orders.py:44,49-59,108-117`) + 오류→status 매핑이 application service(`create_order_app.py:92-166`) + 중앙 `@api.exception_handler`는 ValidationError 1개뿐인데, discipline-reviewer가 백스톱 텍스트를 *로드하고도* "application layer에 섞여 책임 배치 약함"을 **권고**로 분류(G2 통과). **Claude = 준수**(operation raise·중앙 핸들러 4종)라 거짓양성0.
- **진단**: 백스톱 **정밀도 OK·재현율 약함**. 같은 런에서 **P3 백스톱은 blocker 발화** → catch 메커니즘 자체는 작동, *P1a 문구가 약함*. 원인 가설: 위반이 "단일 매퍼(app service)+헬퍼" 모양 → "약함(권고)"으로 읽힘 + carve-out (a) "중앙 변환점 하나라도 충족"(ValidationError 핸들러 존재)이 blocker 약화.
- **핵심 교훈**: **N=9 텍스트-판별(고립된 체크를 "적용하라"고 줌) 통과 ≠ 라이브 발화**(전체 에이전트 + carve-out + 홀리스틱 심각도 + 경쟁 발견 맥락에서 강등). DR-20의 "검증 9/9"는 *텍스트-판별* 한정이었고 라이브 발화를 보장 못 함.
- **부수 관측(NEW-2)**: Claude 런 machine 54.6m(>기준 ~40m, +33%)이나 드라이버=coder n=4·architect n=2(무거운 풀 마이그레이션 태스크), discipline-reviewer 1회·무반송 → **하드닝 게이트가 시간 회귀시킨 것 미확인**(태스크 heaviness 주도). 사용자 '회귀 의심' 측정상 부분 반증(레버 #1 교훈). 메모리 `dddjango-cost-token-optimization`.
- **다음**: P1a 백스톱 **문구 강화**(오류→status 생성이 operation/app/domain 어디든=확실 blocker, carve-out (a) 조이기, **새 게이트 추가 없이 기존 discipline-reviewer 문구 강화**) → 구현 전 적대 리뷰 재실행 → 재-라이브파이어 → 릴리스. P1b·P2·P3는 라이브 견고.

### DR-22 🔴 P1a 백스톱 강화 v2 + 사전 시뮬 — 문구 강화만으론 부족 확인 (재현율 0/3)
2026-05-31. DR-21 후속. discipline-reviewer "API 오류 응답 중앙화 규율" bullet을 강화(v2)하고 **사전 시뮬**(저장된 Codex 위반 산출물 `~/Desktop/dddjango-p1a-livefire-codex`에 강화 reviewer N=3 적용)로 검증 → **또 실패**.
- **강화 v2 구현**(2미러 byte-identical·`plugin validate` PASS): ① carve-out (a) ∃→∀("중앙 변환점이 *예외 전부*의 status 매핑 소유 시만 충족", 부분 핸들러=면제 아닌 blocker 명시) ② 레드플래그를 **operation 본문 → operation·application·domain 어디든**으로 확장 ③ **단일 판별 게이트**("status 선택·problem body 생성이 presentation 변환점 밖에서 실행되나") ④ "operation 본문 밖"→"operation·application 계층 밖 presentation 경계" 5곳 치환. **구현 전 적대 리뷰 3렌즈**(거짓양성·거짓음성·정합)로 초안 5변경 중 carve-out (d)·옵션(비교-불변 잠금) 기각, 분량 순증≈0으로 압축.
- **사전 시뮬 결과(N=3, 캐시 신선화 후 강화 reviewer 로드 md5 확인)**: **P1a blocker 0/3**. sim-1·2 = P1a **점검조차 안 함**(catalog 마이그레이션·테스트 구조 누락 등 다른 발견에 주의 쏠림), sim-3 = P1a 점검했으나 **옛 ∃ 논리로 통과 판정**("`@api.exception_handler(ValidationError)` 중앙 핸들러 존재 → 충족" — ∀ 강화 미적용). **세 리뷰어 모두 app service의 오류→status 매핑을 *읽고도*(sim-1은 그 줄 직접 인용) P1a 규율과 연결 못 함.**
- **핵심 발견**: **bullet 문구 강화만으로는 부족.** 적대 리뷰 **렌즈3의 예언이 실증** — "silent downgrade/누락은 bullet이 아니라 *주의 배분·산출 형식*에서 일어나 bullet 강화로 못 막는다." 격리 N=9 통과 ≠ 전체 감사 발화가 *강화 후에도* 재현. 이번엔 **Claude 리뷰어조차 강화 미적용** → 문구 약함이 런타임 무관하게 드러남. (사용자 "A(사전시뮬) 먼저" 판단이 또 정확 — N=9만 믿었으면 v2로 릴리스 후 라이브 재실패했을 것.)
- **다음(v3 방향, 미결정)**: 단순 문구 추가 아닌 구조적 개입 — (가) **명시 판정 강제**(Ninja 스택이면 오류 중앙화를 리포트에 한 줄 필수 판정 → sim-1·2식 *누락* 차단) (나) **생산자 예방**(design-architect가 명세에 "오류→status=presentation 중앙 소유" 박음 → 애초에 app service에 안 두게) (다) **결정적 백스톱**(operation/app에 status 정수 선택 + 핸들러 수<도메인 예외 수 = 기계 탐지; 진단 때 "의미적이라 보류"했으나 *LLM 집행 자체가 약함* 실증으로 재검토) (라) 산출 형식 보강. 직감 (가)+(나), 단 구현 전 적대 리뷰로 우선순위 확정. 릴리스 **계속 보류**.

### DR-23 ✅ P1a v3 — 결정적 백스톱 + 생산자 예방 (LLM 불안정 우회·검증 통과)
2026-05-31. DR-22 후속. v2(문구 강화)가 사전 시뮬 0/3으로 *LLM 집행 자체가 약함*을 보여 → v3 = **결정적 스크립트(다) + 생산자 예방(나) + 강화 v2 reviewer 보조**의 3층. 사용자 두 제약("반드시 적용 + 동작 시간 안 늘림")의 교집합으로 (다)+(나) 선택.
- **방향 근거**: 시간을 늘리는 건 *새 LLM 서브에이전트 라운드*인데, 결정적 백스톱은 coordinator Bash 1회(LLM 라운드 0)라 시간 ~0이면서 결정적이라 "반드시 적용"을 기계 보장. 생산자 예방은 명세 한 줄(반송↓로 오히려 단축). **P2 선례(`check-mechanism-ownership.py`)와 동일 이중 구조**(생산자 가이드 + 결정적 백스톱 — 라이브 작동한 유일 패턴).
- **구현(구현 전 적대 리뷰 3렌즈)**: (다) `check-error-centralization.py` **2미러**(`dddjango/scripts/`+`codex-dddjango/skills/dddjango/scripts/`, md5 일치) — AND[경로 `/application_layer/` · diff-only · 응답신호{`JsonResponse(`/`HttpResponse(` call-paren·`status[_code]=[45]\d\d`·`HttpError([45]\d\d`·`from ninja` import}], P2 골격(SKIP_DIRS·`_is_new_or_modified` diff-only·exit 0/2/1) 차용·`/test/` 제외. (나) `design-architect` 명세 2미러 — "오류→status 변환은 presentation 단일 소유(`@api.exception_handler`/`create_response`), application/domain은 HTTP status·problem body 안 만듦(`implementation-django-ninja §6.2`)". coordinator 배선 2미러(`dddjango.md`+codex `SKILL.md`) — "결정적 백스톱 2종, 하나라도 exit2면 합쳐 반송, ②통과(0)≠reviewer 면제". 적대 리뷰가 HttpError/ninja-import 추가·§6.2 스킬명 명시·단락정책·통과≠면제 교정, carve-out (d)·옵션 기각·거짓양성=하 실증(Claude 준수본 0건).
- **검증(결정적·v2와 대조 핵심)**: `validate`✔·미러 md5·**라이브 Codex 위반본 exit2**(`create_order_app.py` 정확 지목)·**Claude 준수본 exit0**(거짓양성0)·거짓양성 가드(성공status 2xx·외부status 읽기·import-only→exit0 / `JsonResponse status=404`→exit2)·시간 **0.21s**(LLM 라운드 0). **v2 LLM 사전시뮬 0/3(누락·오판) → v3 스크립트 100% 결정적**(위반 항상 exit2·같은 코드→같은 결과). LLM 불안정을 *우회* — P1a actionable(백스톱 재현율) 결정적 해결.
- **3층 정직 경계**: 스크립트는 application_layer HTTP 누수(라이브 위반 형태)만 고정밀. operation 본문 수제·status맵추출·변수우회·body-only는 **비대상** → (나)예방 + 강화 v2 reviewer 분담(적대 리뷰 권고대로, 거짓양성-recall 균형). 미래 진화형(코더가 "리터럴만 피하면 통과" 학습)은 예방이 최우선 레버.
- **✅ 라이브 검증 (B 트랙, 2026-05-31)**: dual-runtime 실제 `/dddjango`(`dddjango-p1a-v3-{codex,claude}`, smoke2 태스크 B, 캐시 신선화). **dual P1a 완전 준수** — 백스톱 exit0(내 직접 재현 일치)·application_layer HTTP 누수 0·중앙 `@api.exception_handler`(Codex 12/Claude 7)·operation은 raise만. **라이브 확인**: ① coordinator(양 런타임)가 G2서 백스톱 2종 실제 호출=**배선 작동**(LLM이 스크립트 호출+exit 분기) ② exit0=**거짓양성0** ③ **(나) 예방 작동**(이전 Codex 위반[핸들러 1개+app service status]→v3 dual 준수; 명세 'presentation 소유'가 코더 행동 바꿈). **미관측(정직)**: exit2→반송은 dual 준수라 위반이 안 나 못 봄 — 예방이 막은 더 강한 성과, exit2 동작은 저장 위반본 결정적 증명+P2 동일 배선으로 갈음(P2 라이브 동형=준수 측면만). P4 ③ 재현(Codex `published_service` 함수 / Claude `Product.deduct_stock()` 리치 이주). → **P1a 릴리스 보류 해소**(릴리스 자체는 사용자 결정·미실행). **⚠️ DR-24가 이 'dual 완전 준수' 결론을 정정 — 아래 참조.**

### DR-24 🔴 C 트랙 심층 감사 — dual v3 산출물 전수 검토 (B 트랙 "완전 준수" 결론 정정)
2026-05-31. DR-23 후속. 사용자 피드백("P1a가 여전히 Codex에 / catalog 처리가 다른데 Codex가 잘못 고른 듯 / 우리 플러그인이 정한 대로 안 한 모든 것을 서브에이전트로 면밀 검토")으로 B 트랙 두 산출물(`dddjango-p1a-v3-{codex,claude}`)을 **5개 병렬 서브에이전트**로 전수 감사(DDD·API/P1a·DB/§9.6·메커니즘·규율/TDD+테스트 실행). 정본=`workspace/eval/results/REMAINING-ISSUES.md` "C 트랙 심층 감사".
- **🔴 핵심 정정**: B 트랙 "dual P1a 완전 준수"는 **백스톱 exit0을 너무 후하게 해석**한 것. Codex는 *옛* P1a(operation 수제 status 선택)는 피했으나 **더 미묘한 구조 변종**이 남았다: 멱등성 스코프 크립이 부른 `IdempotencySnapshot(status:int)`가 **application 계층을 흐르고**(`idempotency_store.py:17-22`), app이 비즈니스 예외를 직접 catch해 status-snapshot으로 변환(`create_order_app.py:70-79`) → 중앙 `@api.exception_handler` 비즈니스 핸들러 3개가 **죽은 코드**, operation은 raw `JsonResponse` 반환(`api_orders.py:69`). ninja §2.2·§6.2의 "오류 raise·성공 return·중앙 단일 변환" 구조가 깨짐(Major; 매핑 *지식*은 presentation에 있어 Critical은 아님). **백스톱은 exit0이 자기 텍스트 계약상 정확**(`status:int`는 plain dataclass라 `JsonResponse(`/`from ninja` 신호 0) — 코드 버그 아니나 **v3 3중 방어망의 의미적 커버리지 갭**. 뿌리=C3 멱등성 크립.
- **Codex 일탈 인벤토리**: C1[Critical] 명세 §7.369 약속한 `test_stock_concurrency.py` **부재** + 재시도 소진→`StockConflict`(409) 경로 **미테스트**(§9.6 Test criteria 부분 집행). C2[Major] 위 P1a 구조 변종. C3[Major] 멱등성 스코프 크립(`Idempotency-Key` **필수**·전용 테이블, task/scope 미지시·G0=확장금지 위반·P1a 뿌리). C4[Major] SQL 판정 복제 `stock__gte=quantity`(`published_service/stock.py:42` — design-architect.md:36이 *동일 예시*로 금지; 단 `can_decrement_stock` 살아있어 빈혈 해악 부분적). C5[Major] 고-blast catalog 트레이드오프 **G1 미상정**(§9 Open Questions 사후기록만; design-architect.md:38/51 위반). C6[Major] ACL 협력 포트가 `application_layer/`(표준=`domain_layer/order/port/`). C7[Major] 죽은 예외 핸들러 5/12. C8·C9[Minor] 레이아웃 비일관·startapp stub 잔존.
- **Claude 일탈 인벤토리**: L1[Major] 기존 `0001_initial` **재작성**(이력 불변 위반·자기명세 §3.5:181 위반; 단 db_table=catalog_product 일치로 실DB 호환·데이터유실 없음). L2[Major] 컨텍스트 경계 누수(ACL이 catalog **구체 infra** `DjangoProductRepository` 직접 import + catalog **OHS 부재**). L3[Minor] 합산 정규화 불변식+UniqueConstraint 과설계(멀티라인 자체는 방어가능·합산이 task 미요구). L4[Minor] `OrderLine.__eq__` product_id만 비교. **P1a·§9.6 8행·메커니즘·CAS 3계층 테스트=Clean**(정석 설계가 구현에서 실현).
- **catalog 직답(사용자 Q2)**: Codex 미이관 *결정 자체*는 방어가능/underdetermined(표준 텍스트 houserules §1.1+§1.2·ddd §3.2:632는 오히려 *이관*으로 기움). 진짜 잘못 = **C4(SQL 판정 복제)+C5(G1 미상정)**이지 "평면 유지" 그 자체 아님. Claude 이관은 표준 정합(§3.2:632 직접 지지)이나 집행 디테일(L1·L2) 흠.
- **테스트 실증**: 둘 다 그린바(Codex 27/27·Claude 62/62)·check 클린·결정적 CAS 스파이 보유(실스레드 의존 탈피=P3 핵심 충족, 커스텀 백엔드 0). 차이=Claude CAS 전분기 3계층 / Codex 수렴 1경로만(소진→409 미테스트=C1).
- **메타(플러그인 갭)**: ① P1a 새 변종 백스톱 미포착(의미적 갭) ② 스코프 규율 갭(양쪽 반대방향 과설계, G0 확장금지 무력) ③ G1 에스컬레이션 비결정(Codex 단독/Claude 상정 — P4 ③의 날카로운 진단) ④ §9.6 Test criteria 집행 갭(Codex 약속파일 누락·미테스트를 reviewer 미포착). **→ P1a 릴리스 보류 재개**(B 트랙 해소 철회). C2·C3는 coder 아닌 **design-spec(architect) 단계**에서 유입.
- **N=1 경계**: 산출물 각 1건. 각 일탈의 표준 위반 여부는 텍스트로 성립하나 "런타임 성향" 일반화는 보류. 미수정·미커밋(기록만).

---

### DR-25 ✅ 평가 시스템 폴더 재구조화 + 관리 규약 + 잔해 정리
2026-05-31. 사용자 요청("루브릭을 만들었으니 스모크 평가를 한 폴더에서 관리 / 평가지·평가결과 관리법을 DEVLOG에 기록 / 불필요 파일 정리"). `workspace/eval/`이 3개 시대(결정성-조사 N=1/2/3 · 최종스모크/라이브파이어 · 새 루브릭)가 뒤섞인 무더기여서 평가 *기준*과 *결과*를 분리·정리.
- **재구조화(git mv·이력 보존)**: `eval/rubric/{RUBRIC.md, EVAL-METHOD.md}`(← `RUBRIC-v1.md`·`EVAL-METHOD-v1.md`; 평가 기준 정본) + `eval/results/{REMAINING-ISSUES, LIVEFIRE-RESULTS, FINAL-SMOKE-PLAN, FINAL-SMOKE-INSIGHTS.html, RETEST-HANDOFF}`(평가 결과·현행) + `eval/README.md`(인덱스로 재작성). rubric 2파일 상호참조·`PROTOCOL.md` 참조 교정(→ `results/RETEST-HANDOFF.md §1`).
- **관리 규약(앞으로)**: ① 채점 기준은 `rubric/` **단일 출처**(새 평가는 항상 RUBRIC[항목]+EVAL-METHOD[방법]로 채점; 기준 변경은 채점 *전*에만 — EVAL-METHOD §5 사전등록). ② 고정 입력 규율 = `results/RETEST-HANDOFF.md §1`(런 리셋·게이트 답). ③ 평가 결과는 `results/`에 누적(라이브=LIVEFIRE-RESULTS, 추적=REMAINING-ISSUES). ④ 정직 경계: 정적 채점="구조적 준수+기능 정확성"까지, "게이트 라이브 발화"는 fresh 위반-주입 런으로만(DR-21), baseline 차별가치는 *안 잼*(규칙 준수가 핵심).
- **삭제 — 시대1 결정성-조사 하니스(git rm, 전부 추적 → git 히스토리 복구 가능)**: `runs/`(3.3M·claude-1~3·codex-1~7)·`baseline/`·`reset.sh`·`PROTOCOL.md`·`RUBRIC.md`·`RUBRIC-conformance.md`·`RESULTS.md`·`comparison*.html`(3)·`gate-questions*`(2)·`{claude,codex}-N-analysis.md`(4). 결론은 **DR-13/14/15/17에 이미 흡수**. **∴ DR-13/14/15/17·§6이 가리키는 이 산출물 경로는 정리 *전* git 히스토리를 가리킨다**(파일 자체는 더 이상 워킹트리에 없음).
- **삭제 — 미추적 실험 잔해(영구, 복구 불가)**: `design/{b1-firetest, b1-verify, crosscontext-firetest, placement-firetest}`(BC 도메인소유·배치·경계 일회성 프로브, 결론 DR-07/14/15/16 흡수) · `plan/`(2026-05-26 빌드 초기 플랜 4문서, DR-03 흡수).
- **보존**: `reference/`(소스 코퍼스·load-bearing) · `tools/`(텔레메트리) · `design/` 상위 설계문서 6개(추적·설계 히스토리).
- **미커밋**(기록만 — 커밋은 사용자 명시 승인 시). 정적 검증: 이동·삭제 후 `eval/` 트리 = rubric/(2) + results/(5) + README.md, 잔해 0.

---

### DR-26 ✅ catalog 컨테이너 §0-1 회귀 — 근본원인(3-leg 부재·architect 코인플립) + 3-leg 수정
2026-06-02. 트리거: 사용자가 smoke6 채점지 의문("catalog를 `application` 밖에 뒀는데 왜 거의 통과") + "이전에도 있던 회귀, 원인 파악·수정계획". 정본=`workspace/design/2026-06-02-catalog-container-regression-fix.md`.
- **회귀 실증(타임라인, 전부 06-02·같은 태스크군)**: smoke4-codex ❌ / smoke4-claude 🟡(§632-2 오독 PASS→정정) / **poc-codex ✅ 이주 이행**(`application/catalog/`) / smoke6-claude ❌ / smoke6-codex ❌. **FAIL→PASS→FAIL 펄럭 = 비결정**(현 코퍼스로 정답 가능한데 architect가 코인플립).
- **3-leg 전부 뚫림(근본원인)**: ① 결정적 백스톱 0/6 위치 미검사(`check-layer-skeleton`은 `application/` *안*만 봄) ② §632-(2) "평면 유지" *위치* 침묵 → architect/coder "루트 OK" 합리화 + §1.1(상위 우선) 탈출구 ③ 평가(나)가 §632-(2)를 위치 면제로 오독 → smoke6-claude SH PASS 오판(eval-측 버그).
- **적대 리뷰 3렌즈(회피·거짓양성·진단)가 진단 절반 정정**: 1차 동인 = *architect 설계단계 코인플립*(coder-출력 백스톱은 사후 청소; 회귀 전부 명세 일치=coder 일탈 아님) / 진짜 축 = *판정-소유 형태*(poc=리치 도메인메서드→§632-1 이주, smoke6=평면 `published_service` 함수→§632-2 데이터소스→평면; 위치는 그 하류) / §1.1이 상위-우선 미닫힌 탈출구(baseline catalog는 `Product`+`0001` 보유라 "startapp stub"보다 확립).
- **수정 = 3-leg(예방 1차·백스톱 2차·감사 3차)**:
  - **Leg-2 예방**: `design-architect` "평면 유지로 결정" 탈출구 폐기(위치는 항상 `application/<app>/`·4계층만 면제·루트는 G1 옵션) ×2 + houserules §1.1 carve-out(touched 데이터소스 루트=확립규약 아님) ×2 + §0-1 위치 명문·§632-(2) "위치 비면제" ×3. **3미러 정합·옛 문구 잔존 0**.
  - **Leg-1 백스톱**: 신규 `check-app-container.py`(루트직속 컨테이너 ∧ git-touched 신규마이그레이션 ∧ 실질 이주증거 G3 ∧ 설정패키지/비-git 면제) → 게이트 **7종**(①~⑦)·`plugin.json 1.0.3`·codex 미러 byte-identical. **적대 검증 거짓양성0**: 실 4픽스처(smoke4/6 차단·poc 면제) + 합성 6종(빈껍데기·src중첩 차단 / 무관앱·설정패키지·비-git·rename 면제).
  - **Leg-3 감사**: RUBRIC 마스크 C **위치/깊이 분리**(MQ1=N는 4계층만 면제·위치는 touched면 FAIL — smoke6 오판 교정) + `discipline-reviewer` 레드플래그를 catalog-touched·빈껍데기·`published_service`-빈혈 변종으로 ×2미러.
- **잔존(정직)**: **leg-1.5(판정-소유 형태 결정적 신호) 미작성** — 결정적 빈혈 탐지 FP 위험으로 보류. 잔존경로 B-1(`application/catalog/`로 옮겼으나 판정은 평면 함수=빈혈)은 reviewer(leg-3)만 덮어 **런타임 의존 리스크**(리뷰어3 경고·DR-21·22 선례). B-1 실재발 시 P-C형 착수.
- **부수**: §3 #7(catalog 미이주 결정) DR-26로 정정. smoke6 채점지 2개(`EVAL-smoke6-{claude,codex}.md`)를 SH-1/4 FAIL(양 런 공유·Codex 판정-소유 가중)로 정정. **N=1·라이브 예방효과 미검증**(별도 `/dddjango` 런 필요).

### DR-27 ✅🔴 NJ-경계 가이드+백스톱(1.0.4) — P-α/P-β 라이브 예방 확정 · C3 스코프크립 라이브 재현(미해결)
2026-06-02. 트리거: 사용자 피드백 — Codex 협상 *미들웨어* 결함 + Claude `application/common/ninja` 이상 폴더. 처방 정본=`~/.claude/plans/shiny-petting-lovelace.md`. 채점지=`workspace/eval/results/20260602-2241-njlive-claude.md`·`20260602-2251-njlive-codex.md`.
- **두 결함 통합 근본원인**: `implementation-django-ninja` 가이드가 *계약(무엇)*은 주나 경계 코드의 *위치/메커니즘(어디·어떻게)*을 안 박음 → 두 런타임이 위치를 추측해 이탈. **P-α(Codex)** 406/415 협상을 전역 Django 미들웨어로 자작(3런 반복=체계적). **P-β(Claude)** problem 헬퍼를 `application/common/ninja/`에 조기 승격+레벨 오류.
- **1.0.4 변경(가이드 주력+얇은 백스톱, 3미러 byte-identical)**: ① ninja §6.1 406·415 추가 + **§6.3 신설**(415=`Parser`/`request.content_type`+`HttpError`·406=`Accept` 검사+`HttpError`·임의 status=`HttpError`+중앙변환 — "ninja 라우팅 밖에 협상 두지 않는다") + §6.2 problem 헬퍼 *위치 규칙*(단일 BC=그 BC `presentation_layer/`·2개+ 공유 시만 루트 `common/`). ② houserules §1 `common/`=프로젝트 루트(=`application/` 형제). ③ architecture-api §7.2↔ninja §6.3 크로스링크. ④ 백스톱 2종 신설(`check-ninja-boundary-middleware`=presentation 미들웨어 자가등록 차단·AST 기반 / `check-common-container`=`application/common/` 차단) → 게이트 **9종**·`plugin.json 1.0.4`·codex 미러 byte-identical. 구현 전 적대 3렌즈(R3가 §6.3 "406=커스텀 Renderer" 기술오류 정정 — ninja BaseRenderer에 Accept 훅 없음→`HttpError(406)`로 수정).
- **라이브 검증(dual `/dddjango`, fixture `dddjango-njlive-{claude,codex}`, clean baseline·ninja 미설치·동일 주문생성 태스크)**: **🟢 P-α/P-β 예방 = 양 런타임 모두 작동**. Codex가 **3런 연속(smoke3·smoke6·final-codexB) 만들던 협상 미들웨어를 안 만듦** — 415/406을 ninja 경계(operation Accept 검사·ValidationError 핸들러 content-type)서 처리(§6.3 레시피대로). 양쪽 `settings.MIDDLEWARE`=스톡 7·`application/common/` 0·백스톱 ⑧⑨ exit0(조정자 직접 재실행). **정직 경계: clean 런이라 백스톱 *발화*는 미stress=미검증**(예방=약한 positive, 위반주입 fresh 런 필요·§4.3).
- **🔴 그러나 Codex 픽스처 치명 FAIL — 1.0.4 직교 미해결 축**: **NJ-2**(operation 비대: 멱등성 오케스트레이션·수동 헤더검증·트랜잭션 경계·비즈예외 catch·raw `JsonResponse` replay) + **SD-6**(중앙핸들러 죽은코드 3종+status:int infra store↔presentation 왕복) 치명 FAIL. **뿌리=C3 멱등성 스코프크립**(`Idempotency-Key` 필수+전용 테이블, 태스크 미요구·G0 위반) — **1.0.4가 손대지 않은 갭**(DR-24 C2/C3/C7 + DR-06 SQLite-lock 토끼굴 라이브 재현; 결국 27/27 그린 수렴). Q-3도 ThreadPool 실스레드 레이스=비결정(DR-24 Q-3 앵커 재현)·루트 `catalog/` 고아 잔존. → **표적 픽스는 정확히 작동·미해결 직교 축에서 떨어짐.**
- **🟢 Claude 픽스처 정적 준수(품질 상)**: 척추·S-HR·NINJA·Q-4 치명 전부 PASS·의미변종 0·60/60. **C3 부재**(D7로 멱등성 명시 범위밖+G1 상정=P4③ 좋은 행동). **DR-24 Claude 잔여 L1(0001 재작성)·L2(ACL OHS 부재) 둘 다 개선** — catalog `application/`로 brownfield-safe 이주(state-only rename·`db_table`/`label` 보존, **DR-26 컨테이너 픽스 라이브 작동**). 흠 Q-5 🟡(재배치 재작성·비파괴).
- **한계(과대주장 차단)**: **N=1·단일태스크·FC 미전수·N_grader=1 → 런타임 우열/결정성 결론 금지**(DR-14·24). 같은 태스크서 Codex 크립·Claude 사수 = *C3 집행 갭의 비결정성 증거*. **후속 후보**: C3 G1 스코프 규율 집행(architect/discipline-reviewer 또는 결정적 백스톱) — 1.0.4 범위 밖. P-α/P-β 백스톱 *발화*는 위반주입 fresh 런으로 확인 필요.

### DR-28 ✅ C3 멱등성 스코프크립 집행 — 코드-탐지 백스톱(10종) + 가드 salience (1.0.5)
2026-06-03. 트리거: 사용자 — DR-27 후 "Claude 쪽은 더이상 문제 없어 보인다" 논의 → "C3가 이전에 해결됐던 회귀인지 조사" → **"C3 먼저 수정하자"**. 처방 정본=`~/.claude/plans/shiny-petting-lovelace.md`.
- **회귀 원인 확정(git/DEVLOG/픽스처 조사)**: "코드 회귀"가 아니다. C3 방지 가드는 **이미 표준에 있었고**(`design-architect.md:36` "미요청 멱등성 silent 의무화=스코프 초과", `ebe116e` 06-02 02:43·양 런타임 미러) DR-27 라이브 런 때도 존재했는데 **architect가 번복**(njlive-codex `design-spec.md`가 `Idempotency-Key` 필수+전용 `orders_idempotency_record`로 silent 의무화 — scope L22 "이번 요청에 명시되지 않았다"인데 G1 미표면화). = **산문 가이드가 집행력 없어 첫 라이브 검증서 무력**. 동인: §9.6 Risky Write "Idempotency storage 행 채워라" framing + `architecture-api §13` 레시피가 architect를 끌어당기고, 가드는 거대 bold 단락에 묻혀 salience 낮음. 9종 백스톱에 C3 검사 0(P1a 백스톱은 좁은 텍스트 계약이라 변종 미포착=DR-24).
- **적대 3렌즈가 초안 재설계(2건 사용자 재확인)**: 원안 "design-spec vs scope 텍스트 대조"를 뒤집음 — **G2 게이트엔 코드가 이미 디스크에 있으니 spec은 프록시일 뿐**, 기존 9종도 전부 코드 기반 → **코드-산출물 탐지(결정 1-A)**. 예방은 가드 *문구*가 이미 충분(Claude가 따름)·진짜 문제는 묻힘이라 §9.6 재작성·api §13 한 줄 **드롭(over-correction)**, **salience 승격만(결정 2-A)**.
- **1.0.5 변경**: ⑩ `check-idempotency-scope-creep.py` 신설(2미러 byte-identical) — `application/` 멱등성 *코드 산출물*(전용 model/store·`Idempotency-Key`·`db_table`) ∧ `.dddjango/*/scope.md` "미요청 단정" ∧ G1 사용자-승인 채택·brownfield 면제 → exit2. 게이트 **9종→10종** 양 미러(`dddjango.md`·codex `SKILL.md`)·`plugin.json 1.0.5`. + `design-architect` 가드 ⚠ salience 마커(문구 보존·`—`→`:`) 2미러.
- **검증**: njlive-codex → **exit 2**(산출물 5 적발)·njlive-claude → **exit 0**(멱등성 코드 0=자명 통과)·clean → 0. 합성 엣지 **5/5**(G1 채택 면제·scope 요청·이름-위장 저recall 미스·양성 차단·`.dddjango` 부재 보수통과). 백스톱 MD5·design-architect body 동기화 확인.
- **한계(정직)**: Leg-2 salience는 **가벼운 마커**(가드가 이미 all-bold 단락 안=리뷰어C "예방 대부분 중복"; 집행 무게는 백스톱이 짐). **이름-위장 저-recall**(`idempotency` 회피 시 미스 — 보류된 reviewer 레그가 후속). **N=1**(njlive 2픽스처+합성)·**라이브 발화 미검증**(위반주입 fresh 런 필요). C3는 DR-24가 P1a 릴리스 보류 재개의 핵심 축으로 지목 → 이제 결정적 집행 추가, **단 라이브 미검증이라 보류 완전 해소는 fresh 런 후**.

### DR-29 ✅ 결정적 백스톱 10종 발화 매트릭스 검증(스크립트-레벨)
2026-06-03. 트리거: 사용자 — DR-27·DR-28이 "백스톱 *발화* 미검증"으로 남긴 갭 정리.
- **검증**: 10종 전부 *위반 입력*에 exit 2(발화)·clean에 exit 0 확인. **실제 위반 픽스처 5종** — ②error-centralization(p1a-livefire-codex)·⑦app-container(smoke4·smoke6-codex·smoke6-claude 루트catalog)·⑧ninja-boundary-middleware/**P-α**(smoke3·smoke6-codex·final-codexB)·⑨common-container/**P-β**(smoke6-claude)·⑩idempotency/**C3**(njlive-codex). **합성 위반 5종** — ①mechanism-ownership(커스텀 `BEGIN IMMEDIATE` 백엔드)·③response-schema-bypass(리터럴 201 raw)·④layer-skeleton(부분 평면)·⑤openapi-error-declaration(404 extra-only)·⑥context-isolation(ACL밖 타BC import). 사용자 우선순위 P-α·P-β·C3는 *실 픽스처* 발화 확정.
- **부수 확인**: ③가 njlive-codex(변수 status replay)엔 미발화 = 설계대로 *보수적 제외*(MISS 아님). smoke2 픽스처는 stock ENGINE 복원이라 ①은 실 위반 픽스처 없어 합성(원 DR-23·26·P2서 각자 실 발화 한 번 확인됐던 것들 재확인).
- **🔴 잔여(유일)**: **라이브 배선 미검증** — 실제 `/dddjango`에서 coordinator가 G2에 백스톱을 호출하고 *exit 2 → 반송*(설계로 되돌림)하는지는 위반-주입 fresh 런 필요. 스크립트 발화는 확정·배선 instruction 텍스트("열 중 하나라도 exit 2면 반송")는 확인·그러나 *exit2→반송 그 자체*는 미관측(과거 부분증거: P1a-v3 coordinator 백스톱 호출=배선 작동·P3 reviewer 라이브 반송). 이 fresh 런이 동시에 C3/P1a 릴리스 보류 해소 증거가 된다.

### DR-30 ✅ 라이브 배선 dual 검증 — exit2 게이트 차단 양 런타임 확정 (Claude 풀 반송 루프)
2026-06-03. 트리거: DR-29가 남긴 "라이브 배선(coordinator exit2→반송) 미검증" 갭을 닫는 dual 실제 `/dddjango` 런(사용자 구동·내가 채점, 런 구동 불가).
- **셋업**: 양 플러그인 캐시 1.0.5 신선화(10종 — `changja88` 로컬마켓 / `dddjango-local` 캐시 수동 동기화). 타깃 `~/Desktop/dddjango-firetest`(Claude)·`-firetest-codex`(Codex), 동일 태스크(재고 기반 주문생성). G0·G1 정상(둘 다 멱등성 범위외=C3 부재; Claude G1서 멱등성 옵션 표면화=C3 가드 작동; 둘 다 ninja 채택). clean G2 도달(10종 exit0) 후 `application/common/ninja/problem.py` 주입(⑨ check-common-container 위반) → "백스톱 10종 다시 실행" 요청.
- **🟢 양 런타임 안전속성 확정**: 백스톱 *실제 실행*(전사 10줄 확인)·check-common-container **exit2 포착**(조정자 독립 실행과 일치=자기보고 신뢰)·"실패/거부"로 처리·**G2 승인 다시 안 띄움** = 나쁜 코드 게이트 통과 차단. **DR-21 강등(집행→권고) 미재발**.
- **행동 차(N=1씩·우열 단정 아님)**: **Codex** = 차단 후 "1개 blocker 실패" 보고하고 **정지**(자발 수정 미구동). **Claude** = "**G2 게이트 거부, 다음 안 감**" 명시 + 죽은코드 3겹위반(위치·조기승격·dead) 진단 + 제거 방향 구동 → 제거 반송 → 10종 재실행 clean → 테스트 재검증 → clean G2 = **풀 자율 반송-수정 루프**(비지시·자발).
- **정직 nuance**: ① 둘 다 *순수 자연흐름*(빌드 중 위반)이 아니라 "clean G2 뒤 주입→재점검" 프록시(단 "exit2를 blocker로 처리하느냐"는 유효 프록시). ② "고치러 가느냐"=*자율성*(안전기능 아님)이라 **Codex 정지도 테스트 합격**(본질=나쁜코드 통과 차단). ③ 이번 런=*주입* 시연, C3/P-α/P-β의 *자연 발화* 아님(clean 빌드라 자연 위반 0).
- **의의**: DR-27·28·29 "라이브 배선 미검증" 갭 **닫힘**. C3/P1a 릴리스 보류(DR-24/28)의 fresh-런 *부분* 증거(자연발화 아닌 주입). 부수 라이브 발견 = **G0 plain-추천 결함**(coordinator G0 ④ 배너가 plain Django 추천·근거 "Django만 설치"=DR-16 위반 — 메모리 `dddjango-g0-plain-recommendation`, §2 DR-31서 예방 처방).

### DR-31 ✅ G0 plain-추천 결함 예방 — API 스택은 G0 결정 축 아님 명시 (1.0.6)
2026-06-03. 트리거: DR-30 부수 발견 — 라이브 배선 검증 중 Claude `/dddjango` coordinator가 G0서 "API 프레임워크" 결정 축을 즉흥 생성하고 plain Django를 옵션1 *추천*(근거 "현재 의존성은 Django만 설치됨").
- **조사(C3 방식·근거 우선)**: 표준 G0 절(`commands/dddjango.md:53-61`·codex `SKILL.md:72-80`)은 G0서 **스코프·lens·배치(①②③)만** 묻게 규정 — API 프레임워크 질문은 *없다*. API 스택은 `design-architect.md:35` §API스택의 **1급 설계 결정**(기본 ninja·"매니페스트에 없음 ≠ 설치 불가" 명문). → 결함 = coordinator가 표준 *침묵*의 빈틈에 즉흥 over-ask + architect §API스택(에이전트 파일 소유)을 안 읽어 plain 추천. 증거: `firetest/.../scope.md:38-40` "결정 축 (G0 확정)" 섹션이 표준 G0 절에 없음. **Codex 대조: firetest-codex scope.md엔 framework 흔적 0**(표준대로 G0서 안 물음) = **Claude-coordinator 특정**.
- **처방(방향 A — 예방 단일 레그)**: G0 절 항목 2(lens) 말미에 음성 경계 추가 — "어느 프레임워크로 구현하나는 G0 결정 축이 아니다; coordinator는 묻거나 추천 안 함; 스택 판정은 `design-architect` 소유(기존 확립 관례 or 기본 ninja·§API스택); 사용자 명시('DRF로')·암시(serializer·ViewSet)는 표현 그대로 스코프 기록·confirm 해석 금지·architect 위임(명시는 1급 입력)". 2미러 byte-identical(`commands/dddjango.md:61`·codex `SKILL.md:80`, md5 일치)·`plugin.json 1.0.6`·`validate` ✔. **결정적 백스톱 없음** — 결함이 *coordinator의 대화 질문 행동*이라 디스크 산출물 0(C3·catalog와 다름). 위치를 항목 2에 둔 건 "음성 경계는 양성 규칙(lens 제안) 옆"이라는 표준 패턴(항목 1 멱등성 "범위 아님"과 동형).
- **구현 전 적대 리뷰 3렌즈**: 표준정합(houserules §1.1 "기존 DRF/plain 관례 존중" 경로 누락 → 보강)·거짓양성("묻기"가 정당 사실확인까지 삼킴 → "결정축·추천"으로 좁힘; "명시 제약"만·*모호한 암시* 공백 → 둘 다 기록·위임)·문구·위치(항목 4 신설 → 항목 2 통합; "즉흥으로 묻는다" 신조어 → 항목 3 어휘로 평이화). **design-architect.md는 미반영** — 리뷰가 "carve-out이 coordinator 기록 의무만 만들고 architect 수용 의무는 §API스택에 없다"며 보강 권고했으나, 이는 N=0 가상 거짓양성(architect는 스코프 메모 제약을 따르는 게 기본 행동)·중복 동기화 부채(전역지침 06)라 라이브서 실제 무시 관측 시 보강.
- **한계**: 예방-only라 검증 = 라이브 *관측*만(coordinator가 G0서 framework 안 띄우는지; 위반-주입 불가). **라이브 관측 미검증**. N=1 결함 근거(firetest 1픽스처). 우열 결론 아님. 정본=이 DR.

### DR-32 ✅ C4 빈혈 SQL 가드 — C형(도메인 메서드 부재) 결정적 백스톱 ⑪ + reviewer 부재-직격 (1.0.7)
2026-06-03. 트리거: C 트랙 백로그 C4(Codex 판정 SQL 복제 `stock__gte=qty`). 사용자 "표준 규칙 재검토(나-3 = atomic 관용구 허용)" 선택 → 구현 전 적대 리뷰 3렌즈가 풀개정 비용을 드러냄 → **(B) "C형만 결정적 집행, B형 보류"로 선회**.
- **조사**: C4 = `filter(stock__gte=qty).update()` 판정 SQL. **Codex 3픽스처 재현**(p1a-v3·final-codexB·smoke4) vs **Claude 0**(CHECK 제약 `Q(quantity__gte=1)`만). `domain_layer` 유무로 C형/B형 갈림 — final-codexB·smoke4 catalog=`domain_layer` 없음(C형 빈혈), p1a-v3 `catalog/domain_layer/.../stock_policy.can_decrement_stock` 호출+SQL(B형 복제).
- **적대 리뷰 정정(자기보고 불신)**: 내가 (나-3) 추천에 든 **"B1금지→version CAS→`time.sleep`(DR-06) 유발" 인과가 거짓**(표준은 sleep 미요구·`time.sleep`은 coder 자의·DR-06=커스텀 백엔드지 CAS 아님). 풀개정은 11곳(결정적 채점 게이트 SD-3 `check-structure.py:214`·인용 권위 `architecture-ddd §3.2` 포함)+ⓑ 도메인 메서드 *프로덕션 선행 호출* 강제(없으면 빈혈 재도입)+경계 3중한정 필요 → 과함·근거 약함. → **(B) 선회: 표준 텍스트 불변, C형만 백스톱.**
- **처방(B, 백스톱+reviewer)**: ⑪ `check-anemic-sql-guard.py`(2미러)= AST로 `.filter()/.exclude(…).update()` 체인의 비-경합 단조비교(`<col>__gte=비리터럴`, col∉{version,id,pk,*_id}) ∧ git-newness ∧ 그 BC(`application/<bc>/` 또는 루트 평면 `<app>/`) `domain_layer/` 도메인 메서드 0개 → exit2. B형(메서드 존재)·CHECK 제약 `Q(…)`·경합 가드·리터럴(`__gte=0`)은 면제. 게이트 **11종**·`1.0.7`. + `discipline-reviewer` "부재형(C형) 직격" 2미러(현행 '복제 무력화' 프레임이 *부재형* 빈혈에 약한 갭 메움 — 적대 리뷰 렌즈2 권고).
- **검증(결정적)**: 발화 **9/9** — final-codexB·smoke4 exit2(C)/p1a-v3 exit0(B, `domain_layer` 면제 **격리입증**: 제거 시 exit2 전환)/njlive-claude·합성 CHECK·version·리터럴 exit0. `validate`✔·스크립트 2미러 md5·reviewer 2미러 byte-identical.
- **한계**: **저-recall**(도메인 메서드를 `domain_layer` 밖[application service]에 두거나 이름-위장→reviewer 위임)·**라이브 배선 미검증**(위반주입 fresh 런, DR-30류)·N(실 C형 2+B형 1+합성). **B형(atomic 관용구 표준 허용=나-3)은 보류**(11곳·근거 약함, 더 강한 근거 모일 때). 정본=이 DR·`REMAINING-ISSUES.md` C4.

### DR-33 ✅ C 트랙 C1(과대평가·스킵)·C6(N=1 reviewer 명확화) (1.0.8)
2026-06-03. C4(DR-32) 후 C 트랙 계속 — C1·C6 직접 재검증(자기보고 불신).
- **C1 = 과대평가·스킵**: DR-24가 Critical로 매긴 "명세 §369 약속 `test_stock_concurrency.py` 부재"는 — (a) **파일명 차이 무해**(`test_stock_published_service.py`가 deterministic CAS-retry[line34]·oversell[line54] 그대로 커버, P3='명시 형태는 닫힌 목록 아님'이라 충족) (b) 소진→409 단일 엣지만 미테스트=Minor·명세 Test criteria(§274)도 미선언. → 표준 갭 아님, 스킵.
- **C6 = 진짜 §2 위반이나 N=1**: 협력 포트(`ProductStockPort`)가 `application_layer/create_order/port/`(표준=`domain_layer/<agg>/port/`, houserules §2 line142·176). 단 **p1a-v3-codex 1개만**(njlive·final·smoke4-codex + Claude 2 = 5 픽스처 준수) = 반복 아닌 단발 비결정 → 백스톱 과함(catalog·C4와 다름). **reviewer 한 줄 명확화**(파일트리 항목에 "협력 포트가 `application_layer` 배치" 레드플래그 추가, 2미러). `1.0.8`.
- **메타(C 트랙 전수의 교훈)**: C 트랙 항목 대부분 N=1 단발/무해/캐스케이드 — **C4만 N=3 진짜 반복 갭**(DR-32 집행). DR-24 인벤토리=한 픽스처 결함 목록이라 N=1 다수 → 표준 보강은 *반복 확인된 것만*. 잔여: C2·C7=C3 캐스케이드(DR-28 부분완화)·C5=P4(N≥5)·C8·C9·L3·L4 Minor·L1·L2(DR-27 라이브 개선 관측). 정본=이 DR·`REMAINING-ISSUES.md`.

### DR-34 ✅ 라이브 검증 dual — G0(DR-31)·C4⑪(DR-32) 처방 + DR-26⑦ 라이브 작동 확정 (1.0.8)
2026-06-03. 1.0.8 캐시 신선화(양 런타임 수동 동기화) 후 dual `/dddjango`(`~/Desktop/dddjango-c4live-{claude,codex}`, sample 재고차감 태스크, **framework 고정답 제거로 G0 자연관측**). 사용자 구동·내 채점.
- **G0(DR-31) ✅**: 양 런타임 G0 배너에 framework 질문 **0**(scope·lens·배치만). **Claude before/after 확정**(1.0.5 firetest=plain Django 추천 → 1.0.8=미띄움 — 처방이 겨냥한 행동 사라짐). Codex는 원래 안 물어 약한 증거. architect가 G1서 ninja 1급 결정(design-spec "design-architect requires Django Ninja as default").
- **C4⑪(DR-32) ✅ 라이브 배선**: Claude clean G2(11/11)서 `legacy_inventory/stock_ops.py`(`stock__gte`·domain_layer 0개) 주입→"11종 재실행"→⑪ **exit2 포착·"G2 통과 불가 반송"**·자율 진단(중복경로·깨진import·죽은코드)·제거→clean G2 복귀. **DR-21 강등 미재발**. (coordinator가 ⑪을 "⑧"로 표기=번호 셈 오류·무해.)
- **DR-26⑦ ✅ 라이브 예방(자연 발화)**: Codex G1 design-spec "keep root-flat catalog, Do not relocate"(touched 데이터소스 root-flat=DR-26 위반) → **G2 ⑦ `check-app-container` 발화→반송→이주**. design-spec G2 갱신 "**Relocate**…`§0 require touched apps under application/<app>/`" §0 인용·`git D catalog/`·⑦ exit0. **catalog 회귀 라이브 예방 미검증 갭 닫힘**(coordinator ⑦ 원출력 미관측이나 §0인용+gitD+G1/G2 불일치 강력 정황).
- **양 런타임 실현**: L1(catalog 0001 불변·state-only 0002·label/table 보존)·L2(catalog import=acl 한 파일)·C3(멱등성 미발명·G1 옵션 위임)·P1a(status 변환 presentation 단일)·④ninja·P1b(1.6.2). 최종 ⑪·⑦ 양 타깃 exit0.
- **P4③ 재현(catalog 판정귀속 갈림)**: Claude=catalog가 판정(`stock>=qty`) 소유→**리치 도메인 4계층**(entity·domain_service·specification·value_object); Codex=catalog 데이터소스(판정=orders `stock_consumption_policy`)→**infra만**(빈 4계층 골격, 위치만 이주). 둘 다 `application/catalog/` 이주(위치 §0-1 충족) but 소유 귀속 갈림(DR-24 직답·smoke2 P4 그대로). **G1 에스컬레이션도 갈림**(Claude 동시성·멱등성 G1 옵션 위임 / Codex 동시성 version CAS 기본채택, DR-24 메타③).
- **부수**: major-1 Claude operation raw HttpRequest 수동파싱(415 우선용)=reviewer 권고. Codex `uv` 실행.
- **정식 채점(33항목, `eval/results/20260603-0508-c4live-{claude,codex}.md`)**: **Claude=FAIL**(치명 **NJ-2** 1 — operation이 raw `HttpRequest` 받아 `json.loads` 수동파싱[`api_orders.py:52`]·선언적 `payload: OrderIn` 미사용; **major-1의 정체** = 라이브 reviewer 권고 강등 vs 루브릭 NJ-2 치명·WEAK금지)·나머지 32 PASS(SD 7/7·FC 골든6/6·mutation3/3 red·SH 10/10·Q 7/7; 0001 byte보존·ACL 격리·naive 무복제). **Codex=PASS**(치명 0·품질 **상**; SD-6/P1a clean[C2 회피]·NJ-4 정통 response선언·협력포트 `domain_layer/order/port`[SH-7]·소진→409 `test_repeated_stale_stock` 실테스트[C1 무관 확인]; 비치명 SH-5🟡 catalog bare `Product`[brownfield 예외]·Q-1🟡 협상 데코 무게). **🔄 반전**: DR-24선 **Codex**가 NJ-2 위반(C2)이었는데 이번엔 **Claude** — **비결정·N=1·우열 아님**(태스크 동일, 같은 NJ-2가 런타임 간 갈림=집행 갭 비결정). **major-1=NJ-2 갭 후속 후보**(415-우선 operation raw파싱을 라이브 reviewer가 권고 강등=DR-21류; §6.3 Parser.parse_body 메커니즘 미사용을 NJ-2가 잡아야).
- **정직**: N=1씩·비결정·우열 아님. 단 신호 강함(G0 before/after 대비·⑦ 자연발화·⑪ 배선차단). 정본=이 DR.

---

### DR-35 ✅ NJ-2 원인규명 → §6.3 콘텐츠 협상 레시피 교체 (ninja 1.6.x `parse_body`→400 wrap 버그·텍스트만·1.0.8)
2026-06-03. DR-34 major-1=NJ-2(Claude operation raw `HttpRequest` 수동 `json.loads`)를 effort-max로 파라 → **표준 §6.3이 ninja 1.6.x에서 작동 안 하는 버그**가 근본임을 코드로 확정. plan mode + 적대 **6렌즈**(근본원인·정합성·over-correction + skill-creator·plugin구조·coder시뮬) 통과 후 구현.
- **원인규명(코드 결정적)**: §6.3(`final.md:422-425`)이 "415=`Parser.parse_body` 오버라이드해 `raise HttpError(415)`" 처방하나, **ninja 1.6.2 `params/models.py:134-141` `BodyModel.get_request_data`가 `parse_body`의 모든 예외를 무조건 `HttpError(400)`으로 재포장** → 415가 400으로 먹혀 §6.3 레시피가 작동 안 함. Claude는 이 버그 발견(`api_orders.py:6-9` docstring·`problem.py:132` stale 주석이 흔적)→operation 진입 수동검사 우회→NJ-2. **P1a/C4와 결정적 차이**: "묻힌 가드"(가드 있는데 안 따름)가 아니라 *표준 처방이 실제 버그*(따르면 작동 안 함) → ⚠️ 단순 차단 백스톱은 coder를 막다른 길로 강제(함정).
- **확정 레시피(ninja 소스 3중 검증)**: 415는 `parse_body` *전* 필요 — ①parse_body 안 raise→400wrap ②operation 본문 raise→parse_body 후라 늦음 ③데코레이터 raise→run 바깥이라 중앙변환(`on_exception`) 못 탐(`_sync_view` operation.py:669-673 try/except 없음). → **유일 작동 = `router.add_decorator(fn, mode="view")` 데코레이터가 content_type 검사 후 중앙 problem 헬퍼로 415 직접 반환**(operation.run 미호출→parse_body 안 탐), operation은 선언적 `payload` 유지=NJ-2 PASS. 모범=c4live-codex `content_negotiation.py`. 406은 응답시점이라 operation raise→중앙변환(유지); 415/406 비대칭은 필연.
- **처방(적대 6렌즈 반영·텍스트만)**: A) **§6.3 3미러** — 415 불릿을 작동 view 데코레이터 레시피(코드 ~16줄·메서드 가드·헬퍼 의존순서·operation 진입 금지사유·§6.2 대안B 비대칭 내장)로 교체 + 구 "GET 면제" 문장 대체(데코레이터는 GET에도 발화) + 406 본문파싱 금지 한정(NJ-2 우회 텍스트 원천 차단) + 귀결문 열거에 view 데코레이터 추가. B) **design-architect 2미러** 입력 선언적 payload·수동 json.loads 금지 종속절 1줄. C) **discipline-reviewer 2미러** "ninja 버그 우회는 방어 사유 아님" 교차참조 1구(라이브 강등 명분 직접 제거). **D) 백스톱 신설 ❌** — N=1·비결정(DR-24 Codex↔DR-34 Claude) + operation 입력파싱은 11종 원리상 사각(`check-error-centralization.py:8-9` presentation 면제) + reviewer 강등은 루브릭-라이브 갭이라 백스톱이 못 고침(P1a/C4=반복·결정적과 다름·DR-33 원칙).
- **coder시뮬 렌즈 핵심**: P1a(DR-22 "문구만 강화→사전시뮬 0/3")와 **구조적으로 다름** — NJ-2 강등은 "§6.3이 버그라 우회 불가피"라는 *객관적으로 사실인 핑계* 때문(채점지 :118). §6.3을 *고쳐* 작동 레시피를 주면 그 핑계가 소멸→reviewer 강등 명분 제거(P1a에 없던 레버). 단 406 잔존문구·헬퍼순서 구멍을 안 막으면 새 §6.3 안에서 핑계 재공급 → 둘 다 처방에 반영.
- **검증(4종)**: 미러 동기(3미러 final.md 동일·구 Parser 레시피 0 잔존·2미러 agents 각 1)·캐시 재복사 반영(버전 범프 불요·복사본이라 누락 시 옛 §6.3)·데코레이터 단위 **6/6**(415분기·GET가드·charset·empty)·c4live-codex 동형 레시피 통합 **19/19**.
- **🔴 한계**: N=1 라이브(c4live 단일 태스크). 근본은 ninja 소스로 결정적 확정이나 **라이브 효과검증(415 요구 태스크 dual `/dddjango`) 미실행**(사용자 구동 준비). 우열 결론 아님. 정본=이 DR + plan `shiny-petting-lovelace.md`. **→ DR-36서 라이브 검증·정식 채점 완료.**

### DR-36 ✅ DR-35 라이브 효과검증 dual + 정식 33항목 채점 — 양 NJ-2 PASS(효과 입증)·반전(Claude 준수/Codex FC-2 경계테스트 FAIL)
2026-06-03. DR-35(§6.3 view 데코레이터 교체) **라이브 효과검증**: 사용자 구동 dual `/dddjango`(415 없는 c4live 동일 입력·캐시 1.0.8) → 양 런 완료, 나는 채점만(자기보고 불신·코드·`.venv` 직접 검증). 픽스처=`~/Desktop/dddjango-nj2live-{claude,codex}`. 정본 결과지=`workspace/eval/results/20260603-1527-nj2live-{claude,codex}.md`.
- **🟢 DR-35 효과 입증(핵심)**: **양 런타임 NJ-2 PASS**. Claude=c4live NJ-2 **FAIL**(operation `_parse_order_in` `json.loads`+`model_validate`)→nj2live **PASS**(operation `api_order.py:46-68` 선언적 `payload: CreateOrderIn`만). design-spec §4.5가 §6.3 `add_decorator(mode="view")`·"ninja 1.6.x가 parse_body 415→400 삼킴"·"operation 진입 수동파싱은 NJ-2 위반" 정확 인용 = **c4live 사고에서 180도 전환**(415를 "범위 밖"으로 결정해 실위반 기회 제거). Codex=operation 얇음(`api_orders.py:57-75`), 415는 ninja `auth=create_order_preflight` 콜백(`_run_checks`=parse_body 전)으로 분리 — DR-35 데코레이터와 *수단은 다르나*(auth 전용) operation 얇음 동일 충족. → **§6.3 교체가 Claude NJ-2 재발을 막은 직접 증거.**
- **🔴 정식 채점 반전**: **Claude=정적 준수(품질 상·치명 FAIL 0)** / **Codex=FC-2 치명 FAIL → 픽스처 FAIL**. Codex FC-2 = 핵심 판정 경계 `create_order_domain_service.py:22 available_quantity < quantity`→`<=` mutation이 **테스트 green**(`.pyc` 철저정리 후 재현·mutation 1곳 적용 확인) = **stock==quantity 경계 회귀 테스트 부재**(unit 2개·api 11개 모두 available≠quantity). ⚠️ **FC-2 FAIL은 *경계 회귀 테스트 부재*이지 *기능 오류*가 아니다** — 코드는 경계 정확(FC-1 G3 재고5·주문5→201·재고0 통과). **c4live-codex는 M2 경계 1 red(경계 테스트 보유) → Codex 런간 테스트 커버리지 비결정**. **DR-34(c4live: Claude NJ-2 FAIL·Codex 준수)에서 또 반전 = P4③·N=1 분산**.
- **부수 발견(양쪽 런간 비결정)**: ① Claude `order_model.py:14 ForeignKey("catalog.ProductModel")` BC 경계 ORM FK(의미흠·SD-4/SD-7 PASS이나 Codex가 design-spec §4서 명시 회피한 결합·도메인은 ID 참조라 규칙3 충족·c4live-claude는 FK 없는 `PositiveIntegerField`). ② Codex 미세: `JsonResponse` idiom(NJ-1🟡·§6.2 처방형태라 경미)·변환점이 orders presentation 아닌 `config/api.py`(SD-6 계층순수 PASS·Q-1 응집 약화 노트)·`auth`를 content-negotiation에 오용(design-spec "Auth: none"과 긴장)·app `except OperationalError`(Django ORM 예외 직접 catch·design-spec §7 명시·status 변환 아님)·`config/api.py:32 exc.message.startswith(...)` fragile 우회·**discipline 후 superpowers:receiving-code-review 외부 플러그인 간섭**(검증 순수성 노트).
- **실측(결정 레인·조정자 직접)**: 양쪽 백스톱 11/11 exit0·FC-1 골든 6/6·`manage.py test` Claude 43 OK/Codex 15 OK(자기보고 일치)·`makemigrations --check` 양쪽 No changes·catalog 0001(Claude **byte-identical** 모범·Codex black reformatting=의미보존 안전 relocation). FC-2 복원 중 stale `.pyc` 거짓-red 발생→`.pyc` 전삭+touch로 양쪽 원상복원 확인.
- **🔴 한계**: N=1·단일 태스크·라이브 발화(§4.3) 미검증(정적 준수까지만). **우열 결론 금지**. major-1 후속=Codex FC-2 경계 테스트 커버리지가 런간 비결정이라 *반복 확인*(same-task N≥3) 전엔 집행 처방 미정(DR-33 원칙: 반복·결정적인 것만 보강). 정본=결과지 2개 + 이 DR + plan `shiny-petting-lovelace.md`.

### DR-37 ✅ BC 경계 ORM FK 금지 — 규칙3 영속성/ORM 확장 (텍스트 16미러·백스톱 보류·1.0.8)
2026-06-03. DR-36 부수발견(nj2live-claude `OrderModel.product=ForeignKey("catalog.ProductModel", on_delete=PROTECT)` = orders BC가 catalog BC를 ORM FK 결합)을 사용자 "우리 스킬상 정답이 뭐냐" 질문으로 파라 표준 처방. plan mode 3갈래 조사 + 3 적대 리뷰.
- **근본 빈틈**: 규칙3(`architecture-ddd/references/final.md:650` "다른 애그리거트는 ID로만 참조")이 **도메인 객체 레벨로만** 쓰여 영속성/ORM 미확장 → 두 런타임이 같은 규칙3 정반대 해석(claude FK ↔ codex no-FK; c4live는 양쪽 no-FK design-spec·Vernon 인용)=P4③ 빈틈 실증.
- **조사(외부 권위 no-FK 압도)**: Vernon Reference-by-Identity는 ORM/DB FK까지·BC 경계 간 특히 금지(Fowler·Noback·Ardalis), 모듈러 모놀리스(Brown·Grzybek·microservices.io·MS Azure·Spring Modulith), Django loose-coupling. 실용주의 FK 예외는 팀<5·단순시스템 한정(dddjango 부적용).
- **적대 리뷰 발굴(반영)**: ① **규칙4 내부 반론** — 규칙4(:658 "동일 DB 복수 애그리거트 수정 용인")가 *표준 내부에서* FK를 방어가능케 함 → nj2 FK는 "이탈"이 아니라 **underdetermined**(과한 단정 회피). 해소=직교 분해(런타임 원자성 ≠ 영속성 FK 결합; codex가 FK없이 같은 atomic 실증) ② **6번째 오염사이트** `implementation-django:1668` OrderItem 복합PK FK 예시(같은 도메인 쌍) ③ N=1 백스톱 위반.
- **처방(텍스트만·16미러 byte-identical, claude 8 + codex 8)**: ① 규칙3 본문 영속성/ORM 확장(3계층=같은 애그리거트 FK자유/같은 BC 다른 애그리거트 FK허용/다른 BC FK금지 + 합법경로 ID저장·ACL검증·**삭제 생애주기** + 출처정직) ② 규칙4 직교 분해 ③ impl-django:1668 오염 제거(BC 경계 단서) ④ design-architect 결과제약 ⑤ discipline-reviewer 레드플래그(cross-context 결합 자매) ⑥ SKILL·houserules·architecture-db 보강.
- **🔴 백스톱 보류(사용자 결정·적대 리뷰 권고)**: cross-BC FK **N=1**(전 픽스처 nj2live-claude만)·채점 부수 → DR-35가 NJ-2를 동일 조건서 "백스톱❌·텍스트만"으로 한 선례·DR-33("반복 확인된 것만") 일관. + BC 판별(FK app_label ≠ BC 디렉토리명 혼동·커스텀label·복수app 위양성)·migration스캔·OneToOne/M2M·brownfield 파일단위 오탐·coder 삭제무결성 막다른길 미해결. **라이브 N≥2 반복·위양성0 확인 후** AST+apps.py BC매핑 재설계(후속 DR).
- 검증: claude·codex 각 7파일 처방 등장·핵심구 byte 일치·오염제거·규칙4 직교 각 1. **🔴 라이브 미검증**(사용자 구동 dual `/dddjango` 후속 — architect FK회피·reviewer 반송·N≥2면 백스톱 재고). N=1·우열 금지. 정본=이 DR + plan `shiny-petting-lovelace.md` + 적대리뷰 리포트.

### DR-38 ⏸️ NJ-1/협상 over-implementation 심층 추적 — §6.3 *허용* 영역 Q-1 경미·결정적 집행 구조적 불가·현 구조 충분 (채점지/RUBRIC Q-1 미세 보정만·미커밋)
2026-06-04. 사용자 "코덱스·클로드 *모두* `orders_api_router.py`에 과다 정의(exception_handler 다수·problem 헬퍼)·필요한가·django-ninja 재구현 아닌가" 발단(NJ-1 의심). 6+ 적대 서브에이전트 라운드.
- **"양쪽 과다" 전제 = 실측 정정**: Claude 5핸들러 = 4도메인(404/409/503/422)+1 framework(ValidationError→problem) = **django-ninja 공식(`/vitalik/django-ninja` errors.md) 1:1 처방·재구현 0**(공식: 예외별 `@api.exception_handler` idiomatic·problem+json 미제공·협상 미제공). Codex도 핸들러는 동일 정당 — **문제는 협상(406)·415 파서 *한 가지*뿐**(나머지 핸들러 Claude와 동형). "양쪽 공통 과다"는 N=1 비대칭(Codex만 협상)을 공통패턴 승격한 곁길.
- **415 판정 3회 진동 → underdetermined**: 1차 "군더더기"→2차 "면죄(§6.3 처방)"→3차 적대정정 "발명 범위이나 literal 위반 아님". 415=§7.2 계약·§6.3 데코레이터 레시피 존재(정당 가능)·Codex 구현은 §6.3 pre-parse 아닌 post-hoc 재라벨(`add_decorator` 0). **406만 명백**(§6.3:443-444 escape-valve "단일표현이면 406 불필요" 직격).
- **원인**: Codex 협상 자작 = 거의 전 런 반복(grep 14 픽스처/명확형태 N≥7: 미들웨어 3 smoke3·6·final + operation 4 smoke2·c4live·p1a-livefire·njlive). 형태 진화로 게이트 ⑧(미들웨어) 회피. 뿌리=**architect가 미요청 협상을 design-spec 능동 명세**(coder 충실 구현)·escape-valve가 architect 비로드 스킬(impl-ninja §6.3)에만(architecture-api 비미러).
- **🔴 처방 시도 전부 기각(적대 다라운드)**: ① 텍스트 가드(design-architect)=약함(멱등성 가드 있었으나 architect 라이브 번복 DR-28 선례) ② **결정적 백스톱=구조적 불가**: §6.3:441-442가 operation 406 협상을 *허용/명령*("협상 필요하면 operation Accept검사→`HttpError(406)`") → 백스톱 신호가 정당 코드와 **동형**(잡으면 FP·안 잡으면 operation 인라인 회피·양립불가) ③ **멱등성 ⑩ 승격=표면 유비**: ⑩ 트리거 기반(scope 미요청 *단정*·§9.6 8행 강제 흔적·중복-치명 무게)이 협상엔 전무(scope 협상 0건·architect 명세라 scope-코드 *모순 없음*·"안 하면 됨" 권고라 8행급 과중) ④ DR-35가 동일표적 "백스톱❌" 이미 기각·4근거 규칙승격 후 생존.
- **전제 붕괴 결정타**: c4live-codex 채점지(`20260603-0508:23,92`)가 협상을 **"G1 상정·범위내 정당화"로 수락**(Q-1 🟡 경미·NJ-2/NJ-4 PASS·TIER-Q 상). 백스톱이 잡을 대상이 채점 합격·그 형태(`content_negotiation.py` 별도 데코레이터)는 DR-35 *모범*. 승격은 DR-31(G0 over-ask 예방)과도 충돌.
- **결론(재프레이밍)**: 협상 over-impl = "해결 없음"이 아니라 **"막을 위반이 아님"** — §6.3 *허용* 영역의 **Q-1 경미 흠**(치명 아님). c4live식 분리(데코레이터·response 선언)면 NJ-2/NJ-4 PASS·Q-1 범위내 = 채점 합격. **현 구조 충분**: ⑧(미들웨어 결정적 차단)+§6.3(operation 올바른 형태 명령)+reviewer(Q-1 표면화). **라이브서 *미들웨어 아닌 동일 신호*로 N≥2 반복** 확인 시만 백스톱 재검토(현재 6형태 drift·미충족).
- **실제 변경(텍스트만·미커밋)**: 채점지 `20260604-0107-fklive-{codex,claude}.md` Q-1·NJ-2 미세 보정(415 균형 underdetermined·architect 협상레이어=Q-1+Q-2 뿌리·p1a-v3 비일관 인지·정정이력) + RUBRIC Q-1 앵커(406 escape-valve 직격 / 415 underdetermined 차등). **EVAL-METHOD·표준 텍스트·백스톱=안 건드림**(Q-c·design-architect 가드·⑫ 백스톱 다 기각/보류).
- **메타 교훈**: 추적 중 곁길 3회(멱등성 가드 비교·"산문<코드예시" 가설·"양쪽 공통 과다")·매번 N=1 비대칭을 공통패턴 승격→적대 리뷰가 매번 정정. 자기보고 불신: 서브에이전트 3종이 django-ninja *공식 문서* 미열람(우리 표준 2차자료만)→사용자 지적으로 context7 직접 검증해 "Claude 정당" 확정. 정본=이 DR + 채점지 2 + RUBRIC 앵커.

### DR-39 ✅ 변수 타입 어노테이션 — §4 권장→공개표면 필수 축소·결정적 백스톱 ⑫ 신설 (1.0.9·미커밋)
2026-06-04. 사용자 "변수에도 타입힌트(가능한 모든 곳)" 발단. plan mode·적대 4렌즈 리뷰.
- **발단 정정**: §4가 이미 "지역 변수 어노테이션 권장(필수 아님)"을 *의도적*으로 정함(노이즈·mypy 미강제) → 코더 누락 아님. 토론: 사용자 "자명/추론 기준이 주관적·전부 적어 손해없다" → 1차 "전부 의무화". "모든 곳"은 문법상 불가 → 실질 "새 변수 첫 단순대입".
- **적대 4렌즈(skill-creator·plugin-creator·자기정합·devil)가 "전부" 기각**: ① **집행 공백**(전부+백스톱보류=reviewer-only인데 reviewer 문구상향은 DR-22서 사전시뮬 0/3 실패한 동형 메커니즘) ② **백스톱 영구보류**(전부=정상 모범코드 85~100% bare 매치 → 거짓양성≈0 백스톱 구조적 불가) ③ **자기모순 ~400**(표준 자신 예시 "좋은 예"가 새 규칙 위반) ④ **한계효용**(mypy 시그니처로 변수 타입 대부분 추론→버그예방≈0·실익=결정성·계약 가독성). → 출구 **"공개 표면(모듈/클래스 변수)만 필수"** 사용자 채택(지역변수 권장 유지).
- **처방(1.0.9·텍스트 미러+백스톱 신설)**: §4 "공개표면 리터럴 상수 첫 대입 필수"+§4.1 효용 정직(버그예방 아닌 결정성·주류 이탈 출처정직)+예시 면제 / reviewer nit→important+백스톱 역할분담(claude L41=codex L42 byte-id) / RUBRIC Q-7 포인터 / **⑫ `check-public-surface-annotation.py`**(모듈·클래스 본문 *직계* bare **리터럴/컬렉션** 대입만; 함수지역·호출식/타입별칭/이름참조 RHS·재대입·언패킹·다중·`self.x=`·선언적클래스[Model/Enum/Form/Schema/AppConfig/ModelAdmin]·던더·urlpatterns 면제·git 신규수정만).
- **백스톱 정밀(사용자 A 결정)**: `router=Router()`·`api=NinjaAPI()` 관용 인스턴스는 **RHS 호출식이라 면제**(타입 자명), **리터럴 상수만 검출**(계약 명시 효용). 3라운드 정제(AppConfig/ModelAdmin 면제→Call 면제→리터럴-only): 픽스처 288→**59 전수 정당**.
- **검증**: 합성 위양성 다수(async·중첩·match·PEP695 `type X`·global·property·언패킹·walrus·TYPE_CHECKING) 통과 / 통합 적대(py3.9·3.12·3.14 교차·**1843파일 62 전수 진성·거짓양성 0 실증**) / 미러 byte-identical·카운트 12종 정합·exit 0/2 계약. **known-limitation**(2단 상속 로컬 base·별칭 import·Exception 리터럴 클래스 상수는 검출 가능·코퍼스 0·막다른길 아님[어노테이트로 통과]·reviewer 보완) docstring 명시.
- 🔴 **라이브 미검증**(사용자 구동 dual `/dddjango` — coder 공개표면 어노테이트·reviewer/⑫ 발화·신규파일 반송빈도)·N=1·**미커밋**. 정본=이 DR + plan `shiny-petting-lovelace.md` + 적대 리뷰 5리포트.

### DR-40 ✅ 산출물 폴더 규약 — `.dddjango/<생성일>-<slug>/`·재빌드 사용자선택·커밋 명문화 (1.1.0·미커밋)
2026-06-04. 사용자 "플러그인이 만든 문서를 어떤 폴더·네이밍으로 관리할지" 브레인스토밍 발단. 적대 4렌즈 리뷰.
- **조사 반전**: spec-kit `.specify/`·Kiro `.kiro/specs/`·OpenSpec — 설계문서 *커밋*이 주류, gitignore는 override·local 전용 → 사용자 첫 직감(gitignore 자동등록)을 *커밋 추적*으로 반전.
- **결정**: ① `.dddjango/` 유지(커밋 대상·민감 레포 ignore 탈출구) ② `scope.md`/`design-spec.md` 유지 ③ 폴더 `<YYYYMMDD-HHMM>-<slug>`·날짜=생성일 고정(신규만 `date` 1회·로컬) ④ 한 기능 한 폴더·최종본만(architect in-place §43/49라 *이미 동작*·단 폴더 재사용 성립할 때만). 면책 boilerplate 미도입. minor 1.1.0.
- **적대 4렌즈 반영**: **B1 slug 비결정**(재빌드 시 코디가 slug 재계산→glob 매칭 키 비결정→폴더 분열; skill-creator·devil 수렴) = **Phase 0에서 기존 `.dddjango/` 폴더 목록을 사용자에게 제시·선택**(glob 자동매칭 폐기)으로 닫음 — B1·구버전 마이그레이션·동일slug 다중매치 동시 해소. **M4 date 결정성 = 검증 후 기각**(eval은 fixture 디렉토리+소스경로로 채점·`.dddjango` 폴더명 짝짓기 안 함 `EVAL-METHOD.md:191` → date 로컬 무해). 보강: 백스톱 ⑩ **실제 스크립트 실행** 회귀검증(glob.glob 재구현 폐기·날짜폴더 exit2/구폴더 동일/혼재 무크래시/codex 사본/음성 exit0)·marketplace version 핀 부재·design-architect 무변경 근거 교정(경로 *주입*, *면책 boilerplate 아님*)·미러 게이트 동적범위.
- **변경**: claude `commands/dddjango.md`(산출물 위치 절+Phase 0 G0 배너 폴더결정 절차)+codex `SKILL.md` 미러(byte-id 변경분)+spawn 경로+plugin.json×2(1.1.0). **백스톱 ⑩ 무변경**(`.dddjango/*/scope.md` glob `*`가 날짜 폴더 매치·실측·명세 본문 서술도 임의폴더 매치 의도라 정확)·**design-architect 무변경**(경로 주입). 부수발견: **Phase 0 step 3이 이미 미러 비대칭**(claude 괄호 1개 더)—이번 범위 밖이라 보존, 변경분만 byte-id 추가.
- **구현 적대 재검증(3렌즈) → B1 부분완화 정정**: (A)계획대로·(B)미러 PASS·(C)skill-creator가 **MAJOR 2건** — ① Phase 0 폴더조회가 *조건부*("재빌드이거나 관련폴더 있으면")라 코디 신규오판 시 우회→slug 발명 재발(비결정이라 라이브 N=1 clean런이면 미포착) ② 수정 모드가 폴더 절차 미참조 — 을 발견. → **무조건화**("G0 전 항상 `ls .dddjango/`·폴더 있으면 무조건 ⓐ/ⓑ·코디 재빌드판정 제거")+**수정모드 step1 cross-ref**(claude·codex 미러·재검증 byte-id·validate). 원인=1차 리뷰 "무조건 선행" 처방을 구현 시 "조건부"로 약화→복원.
- **라이브 채점 항목 추가(별도 관측 트랙)**: DR-40 폴더 규약을 라이브에서 채점하려면 — P1a/P2/P3 위반주입 모델이 *안 맞음*(백스톱 없음) → `EVAL-METHOD §4.3`에 **동작 관측 트랙** 신설(정상 재빌드 시나리오 관측: 신규 date 폴더·재빌드 목록 제시·ⓐ 재사용; 별도 라벨 `폴더 동작: 관측/미관측/미검증`·**§4.4 완료 정의 비산입**). RUBRIC 차원 동결(L151) 유지·정적 미채점(폴더 동작은 단발 fixture로 불가). 채점 *전* 추가라 §5.4 사전등록 정합.
- 🔴 **라이브 미검증**(코디가 신규 date 폴더 생성·재빌드 시 폴더 목록 제시·사용자 선택·재사용하는지 dual `/dddjango` — 릴리스 게이트)·N=1. 커밋 `012cb5f`(표준)·`5c5e41e`(devlog). 정본=`workspace/design/2026-06-04-dddjango-output-folder-convention{,-plan}.md` + 적대 4리포트(설계)+3리포트(구현검증).

### DR-41 ✅ 폴더·파일·클래스 네이밍 규약 + §4 포트/어댑터 헥사고날 개정 (DR-05/37 번복·1.2.0·미커밋)
2026-06-04. 사용자 점검 "파일트리(위치) 규칙은 촘촘한데 폴더/파일/클래스 *명명*은 §3 임베드 패턴+§4 약어금지 1줄뿐"(DR-39 후속) 발단. 브레인스토밍→적대 4렌즈.
- **명명 결정(필수·집행)**: 도메인 3종(값객체·엔티티·애그리거트) bare(유비쿼터스 언어)·역할 객체는 역할 접미사·**파일명=주 클래스 snake_case**(폴더는 종류 그룹). `_app` 폐기(근거 없는 군더더기·`application_layer`와 중복). 이벤트 과거형 `OrderPlacedEvent`·명세 풀네임 `OrderActiveSpecification`(약어금지 §4 준수)·스키마 `OrderIn`/`OrderOut`(ninja 공식)·조회 selector 함수(CQRS 읽기 정상형, command 클래스와 비대칭 정당).
- **§4 포트/어댑터 ⓑ (DR-05/37 번복)**: 기존 "구현=base명 유지(`Django…Port`)"를 헥사고날 정석으로 — **확립 패턴명(PoEAA/GoF: `Repository`·`Gateway`)은 추상·구현 동일**(`OrderRepository`/`DjangoOrderRepository`·`PaymentGateway`/`StripePaymentGateway`), **일반 협력 포트는 `…Port`↔`…Adapter` 쌍**(`ProductLockPort`/`DjangoProductLockAdapter`). 판정: 외부 시스템 관문=`Gateway`·BC협력(ACL)=`Port`. `infra/service/`→`infra/adapter/`(외부서비스 어댑터만; `service` 3겹침[domain_service·app service·infra] 중 infra 1겹 해소). 근본: §4가 `Repository`/`Port`/`Gateway`를 "역할 접미사" 한 묶음으로 봤으나 — `Repository`/`Gateway`=역할명(구현 유지), `Port`=헥사고날 위치 표식(구현은 `Adapter`).
- **외부 자료 근거(자기보고 불신·context7/web 직접)**: ACL 구현을 `Port`라 부르는 사례 0 — `Adapter`/`Translator`/`Facade` 표준(MS Azure·AWS·Java Design Patterns·헥사고날 IG). 내부 이론 코퍼스(architecture-ddd `:1493` 포트=역할·`:1499` 어댑터=구현·`:335` `ERPAnticorruptionLayer`)도 port↔adapter 구분 — houserules §4만 이탈했던 것. ninja 스키마 `XxxIn`/`XxxOut`은 context7 공식 문서 확인.
- **폴더명(권장 수위·백스톱 없음)**: 앱=핵심 애그리거트명 동일(단일 BC)/여러면 대표명·애그리거트 단수·feature 유스케이스 단위. **유사 변형 금지**(`ordering` vs `order` — 같게 하거나 명확히 다른 컨텍스트명; 사용자 발견 "두 비슷한 단어가 헷갈림").
- **적대 4렌즈(houserules 정합·미러 무결·헥사고날 정합·devil) 전원 조건부 GO**: 핵심 결함=`PaymentPort` 통일이 코퍼스 §5.3 `PaymentGateway`와 충돌+자기모순(`Gateway`도 역할명인데 폐기) → **ⓑ 채택으로 해소**. 에이전트 갱신 "검토 필요"→**필수 승격**(미루면 표준-에이전트 분기·라이브서 옛 명명 생성/통과). SKILL.md 미러 **1줄 오프셋**(`user-invocable: false`) 인지(claude 5/codex 4 스킵 diff). 백스톱 영향 0·fixture 레포 내 부재·§0 구조 위반 0 실측.
- **변경**: houserules `references/final.md`+`SKILL.md`(claude+codex byte-id 미러) + agents 4종(`design-architect`·`discipline-reviewer` claude `agents/`+codex `skills/dddjango-*/`) + RUBRIC `SH-6` 채점기준 + plugin.json×2(1.1.0→1.2.0). **백스톱 12종 무변경**(네이밍 미검사·git status 확인). 종료 게이트: `DjangoProductLockPort`(붙여쓴 토큰) grep **0건**(반례는 `Django`+`ProductLockPort` 분리표기로 의미 유지+grep 회피)·미러 final.md/SKILL.md byte-id·`_app` 0건.
- **subagent-driven 실행**: implementer per task + 적대 리뷰(Task1 final.md 통합 적대 리뷰 ✅·작은 task[SKILL·에이전트] 컨트롤러 직접 grep/diff 검증). 커밋 보류(사용자 미승인).
- **백로그**: command/dto 폴더 구조 정렬(`command/`=서비스 거주·`dto/`=Command 거주로 폴더↔객체 어긋남; CQRS 해석 결정 필요한 §0 불변식 변경이라 분리. 이번엔 "파일=거주 객체 반영" 네이밍으로 우회).
- 🔴 **라이브 미검증·N=1**. 정본=`workspace/design/2026-06-04-dddjango-naming-convention{,-plan}.md`+적대 4렌즈 리포트. nj2 cross-BC FK(DR-37)는 별개 미해결.

### DR-42 ✅ pytest 테스트 표준(생태계-우선) + §6.1 부트스트랩 보류 해지 + 부트스트랩 실행자 + eval 하니스 이주 (1.3.0·미커밋)
2026-06-04. 사용자 "테스트 작성 표준을 pytest로 + 추천 생태계(특히 mocking) 패키지 적극 사용"(마지막 기능). 실측: 라이브 픽스처(nj2live·c4live·fklive 양 런타임)가 Django `TestCase`+`self.assertEqual`+raw `unittest.mock`+`manage.py test`로 떨어짐. 브레인스토밍→적대 4렌즈(플랜)→subagent-driven 구현→적대 2렌즈(최종).
- **진단(지식≠의무)**: `implementation-test`는 이미 pytest 생태계(§6·§7·§9·§10·§11·§19·§20) 전부 문서화하나 의무화 0(RUBRIC Q-6 스택불문). + **표준 자기모순**: §7은 raw `unittest.mock`인데 §16.1/§3.3은 `mocker`(pytest-mock) → 생성물이 raw로 떨어지는 직접 원인. + **§6.1 부트스트랩이 "향후 init" 보류** → greenfield는 pytest 미설치라 fallback.
- **사용자 directive "init 보류 기록 삭제·모든것 보류 해지"** → §6.1을 "기능 추가 흐름이 표준 도구셋 직접 다룬다(기존 감지·존중·없으면 §6.2 셋업·구체 레시피=테스트 스택·나머지 동일 원칙)"로 재서술. init 기록 삭제(DEVLOG `향후`줄·smoke-feedback #4/#6→해소). (표준내 "보류" 태그 0 실측.)
- **적대 4렌즈(플랜)=2 NO-GO**가 v1을 구제: ① **부트스트랩 실행자 부재**(coordinator/coder에 설치 단계 0·acceptance-tester가 먼저 실행→greenfield import-death) → **Phase 2 "테스트 러너 준비" 단계 신설**. ② **eval 하니스 결합 치명**(`manage.py test`는 pytest-only[함수형·`@django_db`] 미수집→FC-2 거짓 PASS·검증불가) → **하니스 pytest 이주 인-스코프**(pytest는 TestCase+pytest 양 수집=구·신 양립). ③ **`mocker` carve-out 사실오류**(context7 `/pytest-dev/pytest-mock`: `ANY`/`call`/`PropertyMock`/`AsyncMock`/`seal`/`mock_open` 전부 `mocker.*` 존재·**`create_autospec` standalone만 예외**) → 정정(틀린 carve-out이 reviewer를 raw 축복+`mocker.*` 거짓지적하게 만들던 것 제거). ④ **백스톱 없음=DR-22/영구교훈#10(문구-only 0/3) 재발 + FP≈0 신호 실재**(설정에 `DJANGO_SETTINGS_MODULE` 부재=결정적 깨짐) → 백스톱 ⑬ 부활+집행 다층화.
- **ecosystem-first 3-tier**: Tier1 항상(pytest·pytest-django·`mocker`·factory_boy) / Tier2 필요시 전용도구(freezegun·responses·pytest-cov·hypothesis) / Tier3 toolbox(testcontainers·mutmut·tox 등 자동적용 금지·Q-1 YAGNI 천장). 핵심: **"적극적=경계에서 수제→전용도구 *업그레이드*이지 더 많이 mock·도구추가 아님"**. factory_boy·`mocker`는 *가용성≠적용*(고전 학파·§7.1 교리 불변; 정확필드 행·VO 직접생성·§20.5 `objects.create(stock=,version=)` 스파이 정당).
- **변경(A–J·claude↔codex 미러)**: §6.1 해지(houserules SKILL ×2)+init기록삭제 / 부트스트랩 실행자(commands ×2·acceptance-tester·coder) / implementation-test §7 raw→`mocker`(create_autospec만 예외)·§4.1 설정(`DJANGO_SETTINGS_MODULE` *감지*[실타깃 `config.settings` 플랫이라 하드코딩 금지]·blanket `filterwarnings=["error"]` 제거)·§4.2 conftest 경계(메커니즘-소유권 §16.4)·§9 factory non-blanket·`test/factories/`(트리 §2·§1.3·2차표·reviewer 허용) / discipline-reviewer 명시판정 / discipline-tdd §7.6 도구=`mocker`(학파 불변) / RUBRIC Q-6 pytest·Q-1 앵커 §6.1→§1.1(+채점지 템플릿 `rubric-metrix` 동기화 Q-6·Q-1·Q-7·SH-6 — 사용자 "라이브 전 평가지 준비?" 질문이 잡은 누락) / 하니스(EVAL-METHOD FC-1/2 러너·RETEST-HANDOFF) / **백스톱 ⑬ `check-test-config.py`**(git-diff 신규 pytest 설정에 settings 바인딩[`DJANGO_SETTINGS_MODULE`/`ds`/`--ds=`/`django_find_project`/pytest-env `env=`/conftest 셋업] 부재→exit2·fail-open·게이트 12→13종 양 coordinator)+plugin.json 1.3.0.
- **검증**: 미러 byte-id(references offset0·SKILL user-invocable 1줄만·scripts 동일) / §7 raw 잔존=`create_autospec`+intro 설명만(mocker. 35회) / 표준내 보류 0 / 백스톱 self-test 16/16(py3.9 text-fallback+3.12 tomllib 양 경로)·**최종 적대 AST=SHIP**(FP≈0 입증; 발견된 brownfield pytest-env `env=`·tox `setenv` 2 FP는 *경화*로 0—`_env_has_ds`+tox 본문 fallthrough, REGR 미발생). 전체 적대=FIX-THEN-SHIP(BLOCKER/MAJOR 0·MINOR 3 교정완료: factories 2차표·RETEST Task B 러너·← DEVLOG는 이 항목). **stray 픽스처 4(루트 pyproject/pytest.ini/setup.cfg/tox.ini, G 서브에이전트 git-diff 테스트 잔류) 제거**.
- 🔴 **라이브 미검증·N=1**. 후속(릴리스 게이트): dual `/dddjango`로 ⓐ 생성물이 pytest 관용구·`mocker`·factory 채택 ⓑ greenfield 러너 부트스트랩 작동 ⓒ 백스톱 ⑬ 라이브 발화 ⓓ 하니스 pytest 채점(FC-2 falsifiable—mutation→pytest red) 관측. 백로그: ruff/mypy/uv per-tool 부트스트랩 레시피(§6.1 정책은 해지·이번 구현은 테스트 스택만). 정본=`shiny-petting-lovelace.md` 플랜 v2 + 적대 6렌즈 리포트(플랜 4·최종 2).

---

### DR-43 ✅ R/C/Q 응용 계층 명명 — Request/Command/Query 인터랙터 (DR-41 백로그 해소·1.4.0·미커밋)
2026-06-05. 사용자 발단: `PlaceOrderService`가 `command/` 폴더에 사는 게 명명 규칙과 어긋남(DR-41이 '거주객체 어긋남'으로 남긴 백로그). 긴 설계 논의→D1~D5 결정→스펙 v2→적대 4렌즈→직접 구현(byte-id 미러 통제, subagent 아님).
- **현상태 진단**: '쓰기 응용 유스케이스'가 3곳에서 갈림 — houserules `:187` `class PlaceOrderService`(클래스) / implementation-test `:2619` `ReserveStockApp`(`App`=`:238` `_app` 폐기 위반) / ninja `:151` `place_order(...)`(자유함수). R/C/Q가 인터랙터 연산객체로 통일.
- **결정(D1~D5)**: D1=Way2 인터랙터(읽기도 `…Query` 클래스+repository+`execute(request)`, selector 함수 폐기·application_layer 유스케이스 한정·trivial 보일러플레이트 비용은 통일성·런간 결정성으로 수용) / D2=(c) 코퍼스 Command=메시지 어휘(§3.6 입력DTO·Event Storming·domain commands.py·애그리거트 메서드·services.py=유스케이스)는 이론이라 보존+houserules 어휘노트로 봉합·우리 예제만 재작성·§3.6 포인터 채택 / D3=service/ 유지(오케스트레이션) / D4=컴포지션 루트(인프라 주입)는 배선 축이라 defer(단 예제 함정 금지문+reviewer 레드플래그) / D5=Request 의무(@dataclass).
- **적대 4렌즈=FIX-THEN-SHIP(NO-GO 0)**, 직접검증으로 확인된 결함 반영: B1 **에이전트 미러는 byte-id 아님**(frontmatter·Coordinator/코디네이터·헤더; 단 편집한 본문 불릿은 byte-id) → 미러 모델 정정·body-diff 게이트 삭제. B2 놓친 selector 사이트(ninja `:260/:285`·impl-django HackSoft `:1432/:1450`) → ninja read 예제 Query화·HackSoft는 참조관용 경계노트. B3 Command-메시지 blast radius>§3.6 → 어휘노트 열거+경계. B4 ninja 예제 미정의 `order_repository`/`stock_port` → 금지문(operation서 `Django…()` 직접생성 금지)+reviewer 레드플래그. B5 ⑫가 평문 `…Command`/`…Query` 클래스상수에 발화(`@dataclass …Request`는 면제) → 어노테이트=§4 정합 노트. + RUBRIC SH-3 주입금지(차원동결)·EVAL-METHOD 소급FAIL금지 시점규칙.
- **변경(claude↔codex 미러)**: houserules final.md(트리·표·어휘노트·프로즈·파일명)·SKILL.md(명명요약) / implementation-test §20.5(`ReserveStockApp`→`ReserveStockCommand`·입력→`ReserveStockRequest`·산문 2곳) / ninja(create_order·list_orders read ×2) / architecture-ddd §3.6 포인터 / agents design-architect·discipline-reviewer(R/C/Q 불릿) / plugin.json 1.4.0. 단일=RUBRIC(SH-3 불변·reviewer 위임)·EVAL-METHOD 시점규칙·이 backlog.
- **백스톱 보류**(N=0 live·프로젝트 일관 DR-32/37/39 '관측된 실패만 결정적집행'; 라이브 N≥2 드리프트 시 AST 재검토). 자체발견 정정: 어휘노트 `§428` 등은 코퍼스 *줄번호*인데 §(절)로 오기→개념기반 정정.
- 🔴 **라이브 미검증·N=1·미커밋**. 정본=`workspace/design/2026-06-05-dddjango-rcq-application-naming.md`(스펙 v2) + 적대 4렌즈 리포트(a9e6b1·adcdeb·a522f3·a71ee2).

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
- **설계·로그 문서**: `workspace/design/` (파이프라인 설계·커맨드 설계·필트리 초안·스모크 피드백 로그들).
- **도구·리포트**: `workspace/tools/{session_telemetry.py, smoke_report.py, smoke_timeline.html}`.
- **AGENTS.md**: Claude 전용 파이프라인 구조 설명.
- **Codex 이식**(§2 DR-12): 조사 `workspace/design/2026-05-28-codex-port-research.md` · 빌드 `codex-dddjango/`(스킬 19) · 로컬 마켓플레이스 `.agents/plugins/marketplace.json` · 테스트 픽스처 `/Users/hyun/Desktop/dddjango-smoke`(git 아님, =codex-2 런).
- **평가 시스템 + 결정성-조사 정리**(§2 DR-25): **현행** = `eval/rubric/{RUBRIC,EVAL-METHOD,rubric-metrix}.md`(기준 정본 — RUBRIC=항목·EVAL-METHOD=방법·**rubric-metrix=채점지 템플릿**[33항목 표+작성법, 복사해 채움]) + `eval/results/`(결과·채점 기록, **현행 명명 `<날짜시간>-smoke{N}-{claude|codex}.md`**, 클로드·코덱스 개별) + `eval/README.md`(관리 규약). 채점지 칸=`Result·결정·의미·종합`(§4). DR-13/14/15 결정성-조사 산출물(`comparison*.html`·`RESULTS.md`·`RUBRIC-conformance.md`·`gate-questions*`·`*-N-analysis.md`·`runs/`·`baseline/`·`reset.sh`·`PROTOCOL.md`)은 정리됨 → **git 히스토리**(결론·커밋앵커는 §2 시대2에 압축).
- **표준 빈칸 ③·④ 메움**(§2 DR-16): 14파일 편집 — `architecture-ddd §3.2` 확장(3벌)·`design-review-ddd`/`discipline-reviewer` 2층 탐지(각 2벌)·`design-architect` ③배치+④API스택(2벌)·`implementation-django-ninja` final.md 설치규칙(3벌)+SKILL(2벌). 정적 검증·`plugin validate` 통과, 동적 ⑥ 이연.
- **동적 검증 Tier 2·3 + ④ 보강**(§2 DR-17): Tier 2 = Claude `design-architect` spec(③ migrate + §1.1/§1.2 명시·④ inconclusive). Tier 3 = Codex 전체 스모크 ×3(t3 평면·plain / t3b 이주·plain / t3c POST-boost·Ninja+핀; 산출물 구 `eval/runs/{codex-5,6,7}`은 DR-25 정리·git 히스토리). 보강 = `design-architect` 2미러(headless의 "설치 불확실→plain" 직격 → t3c Ninja 수렴). fixture `~/Desktop/dddjango-codex-{t3,t3b,t3c}`(git 아님)·인터랙티브 미실행 fixture `~/Desktop/dddjango-codex-interactive`. 각 N=1.
- **향후(범위 밖)**: OHS→Published Language DTO 전환 · Codex 품질평가·전체 smoke 루프.
- **개인 메모리 슬러그**(세션 회상용, 정본 아님): dddjango-rebuild-direction · dddjango-work-style · dddjango-audit-ledger · dddjango-standard-hardening-verification · dddjango-bc-boundary-nondeterminism · dddjango-cost-token-optimization. → **내용은 이 DEVLOG에 흡수됨**.
