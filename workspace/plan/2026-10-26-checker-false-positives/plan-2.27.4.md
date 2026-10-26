# dddjango 2.27.4 — framework 쪽 동음 낱말 · public-surface 뿌리 필터 (F4-124 · F4-42 · F4-125)

검사기 코드 · 데이터만 고친다(규범 글 · graph-owned 절 · 메시지 글 무변). 같은 묶음의 F4-123(생성기 창구 send 타입)은 규범 두 곳
(설계자 지시문의 보조 자료 타입 정의 · implementation-python §13.5 send 금지)과 부딪혀 사용자 결정으로 올렸다 — 이 판 밖.

## 재현(현장 사본 · 서버 저장소의 `.py` · 폴더 모양만 옮긴 사본 · 2.27.3 검사기)
- F4-124: `framework/parallel_work/exception.py` #47 ['pool', 'unavailable'] · `parallel_work_port.py` #47 ['key', 'register', 'run', 'seconds', 'wait', 'within', 'work'].
  업무 낱말 0 — 서버 BC 30여 개의 어휘 합집합이 일반 낱말을 덮었다(출처: key 67 · unavailable 89 · seconds 25 · pool 3(열거 값) · wait 7 · work 8 · register 2 · within 2 · run 1).
- F4-42(10-03 · 열림): `framework/pure/json_value.py` #562 ['json', 'sequence'] — 같은 사본에서 지금도 붉다(옛 국소 목록은 `keys` 하나).
- F4-125: #646 · #647 · #650 줄 1,242 가운데 web 1,101(#647 260 · ⓓ#647 820 · ⓓ#650 21) — `web/application/**` 이 «경로 어딘가에 application» 으로 대상에 들었다
  (`to_json(self) -> dict[str, object]` 은 자매 플러그인 dddjango-web 규칙이 정한 꼴).

## 고침
1. `business_vocab.FRAMEWORK_HOMONYMS`(데이터 · 닫지 않음 · 낱말마다 현장 출처 주석) — key · keys · pool · unavailable · seconds · wait · run · within · work ·
   register · json · mapping · sequence. `all_vocab()` 이 이 낱말을 뺀다 — framework · broker 쪽 소비자 전부(#47 · #587 · #617 · ⓓ#448 · ⓓ#425 · #562 · #518 ·
   ⓓ#36)가 같은 판정. `bc_vocab()`(BC 마다 도는 검사) · 전역 STOPWORDS 무변. #562 국소 목록 `_PURE_TECH_STOPWORDS`(keys)는 이 상수로 합치고 지운다.
2. check-public-surface-annotation `_in_rule_roots` = 상대 경로 첫 성분이 `application` · `framework`(뿌리 아래만 — 2.27.3 BC 고르기와 같은 판).
   처음 판 docstring(«루트 안 파일만»)의 뜻으로 돌아간다. 기존 다섯 규칙(#493 등)은 저장소 전체 그대로.
3. Codex byte 미러 · `pregate_symbol_kinds.json` 재소성.

## 적대 검토 반영(설계 1판 → 2판)
- 차단 1: F4-123 은 규범과 부딪힘 → 사용자 결정으로 올리고 이 판에서 뺌.
- 중요 1: 국소 목록(`_check_isolation` 만)은 같은 파일 · 같은 낱말이 #562 · #518 과 ⓓ#448 에서 둘로 갈림 → 데이터 모듈 `all_vocab()` 에서 빼는 자리로(현장 사본에서
  business-vocabulary 출력은 국소 판과 같고 broker · naming · missable-entrance 변화 0 · 전역 STOPWORDS 는 port-adapter-pairing ⓓ#553 글자가 바뀌어 기각).
- 중요 2: work(문헌 식별 값 `WorkId`) · register(가입 `Account.register`)는 실제 업무 뜻과 겹친다 — 사유를 «동음 충돌 수용» 으로 적고 받아들인 한계에 넣음.
- 중요 4: 시험 — 목록 낱말 전부 · 채널 일곱 · 뿌리 밖 두 꼴 · ⓓ#645 로 바뀌는 꼴을 정확 일치로.
- 사소: docstring 정리 · 남는 web 줄(#493 · ⓓ#69 · ⓓ#645)은 범위 밖 · 행동 변화에 재예보와 ⓓ 줄 변화 적음.

## 행동 변화 · 받아들인 한계
1. framework · broker 쪽 업무 어휘 판정에서 동음 낱말이 빠진다 — #47 · #562 줄이 사라지고 ⓓ#448 · ⓓ#425 낱말 목록이 줄거나(낱말이 동음뿐이면) 줄이 사라진다.
   그 낱말을 업무 뜻으로 쓰는 영역의 framework 누설은 이 낱말로는 못 잡는다 — 그 영역의 다른 낱말이 함께 새면 잡는다(`event` 와 같은 처지).
2. 동음 낱말 하나뿐인 framework 칸 이름(예: `framework/pool/`)은 ⓓ#36 물음이 새로 설 수 있다(ⓓ · exit 무관).
3. `web/` · `web_test/` · 뿌리 밖 중첩 컨테이너(`src/application/**`)의 #646 · #647 · #650 줄이 사라진다. 그 자리의 `dict[…, Any]` 는 #647 차단 대신 #645 nested ⓓ 가
   선다(뿌리 밖 파일의 기존 판정과 같음).
4. 진행 중 레인: 앵커 · 현재를 같은 판으로 재므로 거짓 귀속은 안 생긴다. 판을 올리면 검사기 digest 가 바뀌어 pre-gate 재예보가 든다.
   레인이 고친 framework 파일의 빚 줄이 낱말 목록 글자까지 인용했다면 그 줄은 새 글자로 다시 잰다(드묾).

## 시험
- `field_report_checker_smoke.FrameworkHomonymRegression` 3건(목록 = 현장 근거 목록 · 채널 일곱이 동음 낱말을 빼고 업무 낱말은 그대로 · bc_vocab 무변) ·
  `PublicSurfaceRootRegression` 1건(뿌리 application · framework 유지 · web · src/application 빠짐 · #493 유지 · ⓓ#645 로 바뀜 — 출력 전체 정확 일치).
  2.27.3 검사기로 돌리면 4건 모두 붉다.
- `checker_baseline_matrix` · `findings_count_matrix` business-vocabulary 행: ⓓ 후보 하나 줄어듦(픽스처 `framework/pure/canon_json.py` ⓓ#448 ['keys'] — #562 는 옛 판도
  `keys` 를 뺐으니 두 판정이 이제 같다).

## 범위 밖(다음 판 후보)
- F4-123(사용자 결정 대기).
- 저장소 전체를 훑는 public-surface 의 web 쪽 #493 · ⓓ#69 · ⓓ#645 줄(서버 규범의 적용 범위 질문 — 2.27.3 부터 후보).
