# dddjango 2.27.3 — 후보 물음의 낱말 판정: 애그리거트 낱말의 규칙 복수형(F4-113) · 아는 동사 목록 넓힘과 사실대로 말하는 글(F4-114) (10-26)

## 바탕
- 바탕: main(dddjango 2.27.2 봉인 뒤). 2.27.3 은 patch — 후보(ⓓ · exit 불산입) 두 규칙의 낱말 판정 고침(새 규칙 · 새 질문 · 새 기록 칸 · 규범 문면 변경 없음).
  같은 판에 다른 고침이 함께 나간다(각 고침의 계획은 따로). 매니페스트 판은 `make release` 가 올린다. dddjango-web 무변.
- 결함 1(장부 F4-113): ⓓ#311(check-domain-model · 도메인 서비스 파일 이름) 이 `rewind_turn_across_visits.py` 에 «파일명에 주어가 되는 애그리거트 어휘가 없다»고 물었다.
  파일 이름에는 애그리거트 `visit` 의 복수형 `visits` 가 있다. 판정이 `_` 로 가른 낱말의 글자 그대로 일치라 복수형을 못 봤다.
- 결함 2(장부 F4-114): ⓓ#485(check-port-adapter-pairing · 포트 메서드 이름) 가 `grant` 에 «첫 토큰이 동사도 묻는 꼴도 아니다»고 말했다.
  `grant` 는 동사다. 판정 재료는 «아는 동사 목록»(32 낱말)인데 글은 «동사가 아니다»로 단정했다.
- 판정: 둘 다 결함. 근거 — #311 규범은 이름에 «주어가 되는 애그리거트/도메인 어휘»를 담으라 하고 복수형도 그 어휘다. #485 규범은 «무엇을 시키는지 말하는 이름
  (시키면 명령형 동사구)»을 묻고 `grant` 는 명령형 동사다. 동사 목록은 소켓 라이브러리 목록(#367)처럼 «데이터라 닫지 않는다».
- 설계: 1판(재현 · 현장 대조 · 시제품) → 적대 검토(고친 뒤 구현 · 차단 0 · 중요 2 · 사소 7) → 구현.

## 고침
- check-domain-model ⓓ#311: 애그리거트 폴더 이름의 낱말마다 규칙 복수형(-s · s·x·z·ch·sh 뒤 -es · 자음+y → -ies)을 함께 만든다(세 글자 이상 낱말만).
  파일 이름 낱말 집합(`_` 경계)과 그 집합이 겹치지 않을 때만 묻는다. 부분 문자열은 보지 않는다(`count_visitors` · `revisit_turn` 은 계속 묻는다).
  복수형 함수는 쓰는 곳이 하나라 이 검사기 안에 둔다.
- check-port-adapter-pairing ⓓ#485:
  - 아는 동사 목록 32 → 71 낱말. 더한 39 는 현장 포트 메서드에서 동사로 쓰인 낱말이다 — grant · read · calculate · check · split · detect · digest · load ·
    replace · review · stream · ask · confirm · draw · prepare · reserve · search · validate · wait · choose · compose · consume · decide · hash · inspect · link ·
    locate · parse · phrase · pull · quote · redact · require · rewind · store · summarize · classify · proceed · rank.
  - 후보 글을 사실대로: «포트 메서드 `x` 의 첫 토큰 `y` 이 아는 동사 목록에도 묻는 꼴에도 없다». 이름이 `_` 로 시작해 첫 토큰이 비면
    «포트 메서드 `x` 이 `_` 로 시작해 첫 토큰이 없다 — 아는 동사로도 묻는 꼴로도 읽히지 않는다». 물음 문구 «이 이름이 무엇을 시키는지 말하나» 는 그대로.
  - 확정 판정(이름이 `notify · handle · execute · process · run · do` · `_command`/`_query` 접미)과 그 판정이 먼저 도는 순서는 그대로.
- 판정 대상 · exit · 확정 줄 무변. 규범 문면 · 온톨로지 · LEDGER · rulepack 무변.
- Codex byte 미러 둘 · `pregate_symbol_kinds.json` 재소성(검사기 소스가 바뀜) · 기대표 두 값:
  findings_count_matrix port-adapter 지문(픽스처 bad_rules 의 후보 글 4줄) · checker_cross_matrix `context_isolation` × port-adapter ⓓ 열(`load_deck` ·
  `load_rows` 가 이제 아는 동사라 ⓓ#485 2 → 0). predicates 311 · 485 행.

## 적대 검토 반영
- 중요 1: 더한 낱말 가운데 명사로도 쓰는 것이 있어 그 낱말이 머리인 명사구 이름은 묻지 않고 지나간다(아래 한계 3). 목록은 현장 근거대로 두고, 코드 주석 · 시험 이름 ·
  이 문서를 실제 기준(«현장에서 동사로 쓰인 낱말만 — 명사 겸용 낱말도 있다»)으로 바로잡았다.
- 중요 2: `run` 은 확정 목록의 모호 동사와 같은 부류라 동사 목록에 넣지 않는다(40 → 39). `run_<목적어>` 는 `process_<목적어>` · `handle_<목적어>` 처럼 계속 묻는다.
  두 목록이 서로 반대 뜻을 말하는 자리가 없다.
- 사소: 복수형은 세 글자 이상 낱말만(두 글자 이하 낱말의 +s 는 `as` · `its` 같은 기능어가 된다 — 업무 어휘 모듈의 세 글자 바닥과 같은 기준) · `_` 로 시작하는 이름의 글 ·
  더한 39 낱말을 모두 지나가게 하는 시험(목록 철자 실수 잡기) · 받아들인 한계 넓힘(아래 1 · 2) · 같은 방향 규칙 #36 을 범위 밖 표에 · 문서의 낡은 사실(옛 목록 32 낱말).

## 행동 변화 · 받아들인 한계
1. ⓓ#311 은 파일 이름 낱말이 애그리거트 낱말의 규칙 복수형이면 묻지 않는다. 그래도 묻는 꼴(놓침): 불규칙 복수(`people`) · 이 판이 만들지 않는 규칙 꼴(-o 뒤 -es `heroes` · -f → -ves `leaves` · z 겹침 `quizzes`) ·
   애그리거트 이름이 이미 복수이고 파일 이름이 단수(`settings` ↔ `apply_setting`).
2. ⓓ#311 은 복수형 철자가 다른 낱말과 같으면 지나간다 — `news`(`new` +s) · `matches`(3인칭 동사) · 여러 낱말 애그리거트 앞 낱말의 복수(`birth_chart` → `births` —
   옛 규칙 «낱말 하나만 맞아도 어휘가 있다»의 연장) · 도메인 층에 잘못 둔 종류 폴더(`entity/` → `entities`).
3. ⓓ#485 동사 목록에는 명사로도 쓰는 낱말(wait · review · link · store · stream · hash · digest · rank · quote · search · check · load · draw · split · pull ·
   phrase · read)이 있다. 그 낱말이 머리인 명사구 이름(`wait_seconds` · `link_url` · `review_count`)은 묻지 않는다 — 같은 꼴이라도 목록 밖 명사(`timeout_seconds`)는 묻는다.
4. ⓓ#485 는 3인칭 동사 머리(`holds_` · `satisfies_`)와 모호 동사 머리(`run_` · `process_` …)를 계속 묻는다.
5. ⓓ#485 후보 글이 바뀐다. pre-gate 처분 · 검토 ID 는 규칙+경로로, 빚 잔존 후보 대조는 `[ⓓ#N]` + 경로로 맞추므로 글 바꿈에 흔들리지 않는다.

## 시험
- `field_report_checker_smoke.CandidateWordRegression` 6 건 — 줄 글자 정확 일치:
  - #311 복수형 통과(`visits` · `categories` · `batches` · 여러 낱말 애그리거트 앞 낱말의 `contents`).
  - #311 물음 유지(낱말 경계 `visitors` · `revisit` · 불규칙 `people` · 어휘 없음 · 한 글자 낱말 `as`).
  - #311 세 글자 바닥(`day` → `count_days` 통과 · 두 글자 `ad` → `rank_ads` 물음) — 바닥을 2 · 4 로 바꾼 변이가 각각 붉다.
  - #485 `grant` · `read_balance` 통과 · 더한 39 낱말 모두 통과.
  - #485 물음 유지(목록 밖 명사 `timeout_seconds` · 목록 밖 동사 `transmit_payload` · 모호 동사 `run_searches` · `_` 로 시작하는 이름의 글).
  - 2.27.2 검사기로 돌리면 5 건이 붉고 유지 꼴 하나만 통과, 고친 판에서 6 건 모두 통과.
- 좁은 실행: fixture_matrix 114/114 · findings_count_matrix 73/73 · checker_baseline_matrix 73/73 · findings_smoke 15/15 · checker_cross_matrix 의 두 검사기 열(60 실행)
  차이 0 · spec_lint · checker_lint 위반 0 · gen_pregate_symbol_kinds --check in-sync.

## 현장 대조(읽기만 — 서비스 저장소의 `.py` 만 옮긴 사본)
- ⓓ#311 80 → 74 — 사라진 6 줄 모두 애그리거트 낱말의 복수형을 담은 이름.
- ⓓ#485 123 → 39 — 사라진 84 줄 모두 동사 머리 이름. 남은 줄은 목록 밖 낱말 · 3인칭 머리 · `run_` 머리 넷 등. `_` 로 시작하는 포트 메서드는 없다.
- 그 밖의 줄 · exit 무변(두 검사기 모두 그 규칙 줄을 뺀 출력이 byte 같음).
- 시간(옛 · 새 번갈아 · CPU 중앙값 · BC 둘 사본): domain-model 5.24 → 5.15s · port-adapter 18.79 → 18.64s. 느려지는 검사기 없음.

## 범위 밖(다음 판 후보)
같은 낱말 판정을 쓰는 다른 규칙은 이번에 맞추지 않는다.

| 규칙 · 자리 | 무엇을 견주나 | 복수형 · 동사 목록을 넣으면 | 이번 판 |
|---|---|---|---|
| #151 check-context-isolation | OHS 창구 이름 = 애그리거트 이름이면 후보 | 후보가 는다 | 안 함 — 방향이 반대 · 신고 없음 |
| #191 check-usecase-dto-placement | 유스케이스 폴더 이름 = 애그리거트 이름이면 후보 | 후보가 는다 | 안 함 — 같은 까닭 |
| #594 수단 낱말 목록 | 능력 폴더 낱말이 `client · cache · queue …` 면 후보 | `clients · queues` 도 잡혀 후보가 는다 | 안 함 — 신고 없음 |
| 업무 어휘 모듈(#47 · #52 · #587 · #617 …) | framework 쪽 이름에 BC 어휘가 새면 확정 위반 | 확정 줄이 는다(빚 지문 영향) | 안 함 — 위험이 크고 신고 없음 |
| #36 check-naming | framework 칸 이름이 트리 · 기술 · 업무 어휘 어디에도 없으면 후보(#311 과 같은 «없음 → 물음» 방향) | 복수형 칸(`visits`)의 물음이 사라진다 · 다만 재료가 업무 어휘 모듈이라 그 모듈을 바꾸면 위 확정 규칙도 바뀐다 · 글도 «어디에도 없다» 단정 | 안 함 — 신고 없음 · 다음 판 후보 |
| #597 리포지토리 쓰기 접두 금지 | 리포지토리 쓰기 이름의 금지 접두 | #485 동사 목록과 자리 · 뜻이 다르다 | 영향 없음 |

- 그 밖의 다음 판 후보: #485 3인칭 동사 머리(`holds_` · `satisfies_`)를 묻는 꼴로 받을지.
