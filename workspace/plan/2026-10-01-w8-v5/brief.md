# 설계 지시서 — dddjango-web W8 v5: G2 전 시안 기계 대조 + 입력 쪽 요소별 정확값 표 (2026-10-01)

너는 설계자다. **플러그인 코드·규범 문서를 고치지 않는다.** 결과는 이 폴더(`workspace/plan/2026-10-01-w8-v5/`)에만 쓴다. 한국어로 쓴다. 쉬운 말을 먼저 쓰고 근거를 뒤에 둔다.

## 왜 하나 — 사용자 결정과 원칙
- 사용자 원칙: «목표는 속도 개선 · 퀄리티는 양보할 수 없다» · «새 결함은 배포 전에 고친다».
- 사용자 결정(2026-10-01 20시대 · 원문): W8 은 «web 배포 뒤 바로 (권장)» — 다음 작업 1순위로 **W8 + 입력 쪽 정확값 표**를 설계·구현한다(K1~K3 보다 먼저). dddjango-web v1.2.0 은 방금 배포됐다(main `78a731bd`).
- 현장 web 레인에서 가장 오래 걸리는 것은 G2 반복이다(레인당 6.6~7.9시간). 반송 대부분이 «시안과 다르게 그림»이었다.
- 자매 플러그인 dddart(Flutter)는 같은 종류 시안을 거의 그대로(사용자 체감 99%) 그려서 사용자가 직접 판정했다. dddjango-web 은 자주 다르게 그려서 레인 자체 검증을 붙였고 그래서 느리다. 목표는 «처음부터 시안대로»에 가깝게 + 어긋나면 G2 전에 기계가 잡기.

## 입력(읽기만)
1. **W8 설계 v4.1(동결)**: 저장소 `workspace/plan/2026-09-30-speed-improvement/design-W8.md`(머리에 사용자 결정 두 줄). 이전 판과 실측 자료: scratch `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/design-W8/`(`design-W8-v1~v4.1.md` · `src/`(대조기 `compare_census_v4.py` · 측정 스니펫 `style_census_dv4.js`) · `frozen-v4-run/` · `run/` · `judge-p1g2/`(독립 판정 라벨 · 요약) · `plant/`(심은 결함) · `reg/` · `exp/`).
2. **시안 충실도 실험 보고**: `workspace/plan/2026-09-30-speed-improvement/exp-fidelity-p1-report.md` — P1 G2 첫 제출 실제 차이 T 35묶음: 명세 손실 34 · 코드 1 · CSS 환경 0 · 표현 불가 0. 잃은 것은 숫자보다 **요소↔토큰·variant·자식 효과(윤광 등)·부모 배치의 연결**. 막을 수 있음: (가) 입력 쪽 요소별 정확값 표 — 예 23 · 부분 12 / (나) W8 G2 전 대조 — 35/35. 처방 §4 를 읽는다. 실험 자료: scratch `exp-fidelity/`.
3. **현장 시간 분석**: scratch `problem-lanes/problem1-time-analysis.md`(P1 = lane-6-3-11) · `problem2-time-analysis.md`(P2 = lane-8-B-3) · `review-persistence.md`.
4. **속도 로드맵**: `workspace/plan/2026-09-30-speed-improvement/roadmap-v1.md`(W8 · W2 · W5~W7 행) · `design-W5-7.md`.
5. **현재 플러그인(v1.2.0)**: `dddjango-web/commands/dddjango-web.md`(Coordinator) · `agents/*.md` · `skills/*/references/final.md`(특히 `architecture-web` §8 «시각 값은 foundation 토큰만»·«정확한 값 대응» · `implementation-ui` §2·§7 · `design-acquisition.md` · `discipline-web-houserules`) · `scripts/`(`render_audit.js` · `check_design_evidence` · 시안 절단 도구 · `backstop.py`). Codex 미러 `codex-dddjango-web/`. 개발 절차 `docs/DEVELOPMENT.md`(web 은 산문 정본 · Codex 미러: scripts·assets·references 는 byte, 역할·Coordinator·SKILL 은 의미 미러) · `AGENTS.md`.

## 설계할 것 — v5 = v4.1 의 W8 + 실험 처방 (가)
1. **입력 쪽 요소별 정확값 표(G0/G1)**: 시안을 렌더해 보이는 요소마다 계산 스타일(배경·테두리·반경·그림자·흐림·글꼴·줄 높이·자간·색·아이콘 크기·요소 사이 틈·최소/최대 높이)과 **요소↔토큰·부품 variant·자식 효과·부모 배치 관계**를 뽑는다. 누가(도구 · Coordinator · architect) 만들고, 명세가 어떻게 인용하며, coder 가 어떻게 «이 값대로» 쓰는가. 실험 §4 처방(배치는 부모 관계와 함께 · 공용 부품 재사용은 이름이 아니라 렌더 계약으로)을 반영한다. 기존 규칙(foundation 토큰만 · 근접 토큰 금지 · 공용 부품 재사용)과 충돌하는 곳이 있으면 짚고 해소안을 낸다.
2. **W8 G2 전 대조**: v4.1 을 바탕으로 하되 (1) 의 표와 같은 측정·짝짓기를 쓰도록 맞춘다(입력 표 = 대조의 기대값). 차단 기준 · 데이터 차이(D) · 짝짓기 오류(F) · 무관(H) 처리(오탐 관리) · 반송 라운드 재관찰 축소 조건.
3. **도입 순서**: 경고 모드 먼저(이전 결정 «W8 경고 모드 먼저»)인지, v4.1 의 그림자 레인 관문인지, 차단 전환 기준은 무엇인지. 진행 중인 현장 레인에 영향을 주지 않는 방법.
4. **두 플랫폼**: Claude · Codex 각각 무엇을 바꾸나(파일 목록 · byte 미러 · 의미 미러).
5. **품질 논증**: 검사를 더하는 쪽인지, 빠지는 검증이 있는지(있으면 근거). 육안 대조·독립 시각 감사와의 관계.
6. **속도 효과**: 보수적으로. [실측] / [추정] 을 구분한다. v4.1 의 보수 셈(⑤ 단계만 확실 · P1 중앙값 −75 · P2 −70분)을 출발점으로, 입력 표가 더하는 것(첫 제출 차이 감소 → G2 라운드 감소)을 따로 센다.
7. **검증 계획**: 픽스처 · 재생(P1·P2 보관 입력으로 — 정답 = 실험 T 35 · 발주자 반송 항목) · 심은 결함 · `make verify-web`. 리허설에 무엇을 쓰나.
8. **구현 계획**: 커밋 단위 · 규모(일) · 순서.

필요하면 `$TMPDIR` 사본에서 기존 대조기·스니펫을 돌려 프로토타입으로 확인해도 된다(서버 기동·DB·네트워크 금지 · 보관 자료로만).

## 결과물 — `./design-w8-v5.md`
1. 결론 10줄 이내(무엇을 · 왜 · 효과 · 품질)
2. 쉬운 말 요약(사용자용 · 번호 목록)
3. 설계 본문(위 1~8)
4. 사용자에게 물을 것 — **정말 사용자만 정할 수 있는 것만**(목적·기존 결정·플러그인 정의에서 답이 나오면 묻지 말고 설계로 처리). 있으면 쉬운 말로 «배경 → 실례 → 바꾸면 → 위험».
5. 확신이 낮은 것 · 자료 한계
마지막 줄에 `REPORT-DONE`.

## 금지
- 이 폴더 밖에 쓰지 않는다. 커밋 · push 금지.
- `/Users/hyun/Desktop/dddjango`(main 작업 폴더) · `/Users/hyun/Desktop/spring_dream_server` · `~/.herdr/worktrees/spring_dream_server/**` · `~/.codex` · `~/.claude` 는 읽기만(쓰기 · `git status` 금지). scratch 자료는 읽기만.
- 서버 기동 · DB · 네트워크 금지. 다른 프로세스를 죽이거나 건드리지 않는다. Serena · Graphify 를 쓰지 않는다.
- 판단이 막히면 추측하지 말고 질문한다.
