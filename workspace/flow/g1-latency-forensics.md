# G1 설계 지연 포렌식 — relive 31분의 해부 (2026-06-11)

> **발단**: relive 라이브 런(6/10 23:36)의 G1(설계)이 ~34분 체감 — 사용자 "뭔가 문제가 있다". 진행 방식(사용자 지정) = 원인 파악 → 적대 리뷰 → 수정 계획 → 계획 적대 리뷰 → 구현 → 완성도 확인.
> **방법**: 세션 transcript(메인+`subagents/agent-*.jsonl`) 타임스탬프·`totalDurationMs`·턴·tool_use 분해. 적대 2렌즈(방법론·인과) + claude-code-guide 사실 확인 반영 — **초기 가설(effort)이 적대 리뷰로 기각되고 진짜 원인이 교체됨**.

## 1. 측정 (3런 대조 — 동일 태스크·동일 모델 opus-4-8·동일 CC 2.1.170)

**G0응답→G1배너 기계구간** (휴먼 대기 0 검증 — ASK 이벤트 전수 분리):

| 런 | 구동 | 기계구간 | architect 초안 | architect 반영 | 비고 |
|---|---|---|---|---|---|
| finallive | 6/10 16:16 | **17.3m** | 4.3m·22턴·툴16 | 5.2m·14턴·툴9 | 최속 |
| lastlive | 6/10 20:23 | **18.6m** | 5.8m·37턴·툴25 | 5.1m·15턴·툴9 | +배너후 Y-override 5.4m(L1 ② 설계상)+휴먼대기 ~6m = "31분" 체감 |
| relive | 6/10 23:36 | **31.0m** | **11.8m·55턴·툴35** | **11.8m·36턴·툴22** | 둔화는 architect 2호출에 **국한** |

- 같은 relive 세션의 **다른 서브에이전트는 전부 정상/더 빠름**: 리뷰 3종 1.5~1.8m(타런 동등), tester 3.0m(타런보다 빠름), coder 10.2m/5.9m(타런보다 빠름).
- **처리율 불변**: 초안 60.2/54.6/58.4 tok/s·Write 블록 106~145 c/s(심야 relive가 오히려 최고). **모델이 느려진 게 아니라 같은 속도로 2.1~2.6배 더 출력했다.**
- 둔화의 100%가 모델 시간(파일IO 0.1~0.6%).

## 2. 원인 (확정 — relive vs finallive +844s의 분해)

| 원인 | 기여 | 증거 |
|---|---|---|
| ① **전량 재작성 2회** — 자기일관성 스캔이 실결함 적발(환영 §5.6 참조 2곳·order/catalog 이중 `InsufficientStock` 번역 모호·§4.5→§3.5 오참조) → **Edit 시도 → `No such tool available: Edit`** → 2~3줄 고치려고 26.8KB/34.2KB 전량 재Write | **~430s (51%)** | transcript 원문 14:46:27 «Edit isn't available — only Write», 15:01:02 «full-file Write with line 141 corrected»; 2차 Write 184.7s+245.4s |
| ② 추가 정독·검증 턴 — 코디네이터의 architect 프롬프트 변이(relive에만 "스킬을 로드해 근거로" 지시·Y후보 3개 vs finallive 1개) → ninja SKILL+final 590줄 등 추가 정독 | ~330s (39%) | 코디 프롬프트 3,503/3,341/4,354자 상이·Read 10→21·Grep 2→8 |
| ③ 1차 스펙 비대 | ~80s (10%) | 1차 Write 25,801 vs 20,593c·처리량 동일 |

**상류 구조**: 런간 비결정(초안 결함률·자기스캔 발화 여부·코디 프롬프트 합성) × **Edit 부재가 비용 증폭기**(스캔이 무엇이든 적발하는 순간 ~200s/건 재작성 강제). 자기스캔 자체는 품질 +(실결함 적발) — 절단 금지.

- `design-architect.md` frontmatter: `tools: Read, Grep, Glob, Write` — **Edit 없음** (coder만 Edit 보유). 이전 4호출(finallive·lastlive)은 스캔이 재작성을 유발하지 않아 증폭기가 침묵했을 뿐.

## 3. 기각된 가설 (박제 — 같은 헛길 재방문 금지)

| 가설 | 기각 근거 |
|---|---|
| **effort=xhigh가 relive 주범** (초기 진단) | `/effort max`는 **"this session only"**(stdout 실측·공식 문서)·settings.json `effortLevel: xhigh`는 **2026-05-05 백업부터 존재 = 3런 공통** → finallive(최속)가 직접 반례. 6/10 22:09 실행은 인자 없는 `/effort`(조회). 동일 세션 7 서브에이전트 평탄/가속. architect thinking 블록 0 |
| DR-55/56 텍스트 의무 증가 | reflect가 finallive 5.2m ↔ lastlive 5.1m **동일**(같은 스킬을 읽는 호출이 안 늘었다). draft +1.5m는 프롬프트 변이/비결정과 비식별 |
| 측정 비대칭(mtime) | transcript 재현 17.31/18.62/31.00m 초 단위 일치·창 내 휴먼 이벤트 0 (각주: lastlive 끝점 ASK 1건이 InputValidationError 실패 호출 — 진짜 배너 기준 19.28m·결론 불변) |
| 스킬 비대 누적 | reflect 불변이 반박 |
| 심야 API 지연 | 동세션 통제군 전부 정상·Write 처리량 심야가 주간보다 빠름(126~145 vs 106~119 c/s) |
| CC 버전·모델 차이 | 3런 동일(2.1.170·claude-opus-4-8 — jsonl 실측) |
| lastlive "31분 둔화" | +13m 본체 = L1 ② Y-override 호출(5.4m·**설계상 정합 비용**) + 휴먼 대기 — 결함 아님 |

## 4. 측정 방법론 노트 (적대 lens A 정정 반영 — 재사용 시 주의)

- assistant 엔트리 timestamp = **블록 생성 완료 시점** → 턴간격 = 그 턴의 생각+생성 시간 (대형 Write의 전갭 184~269s·후갭 17~49ms로 입증).
- Agent `totalDurationMs` = spawn→return 벽시계와 ±4s 일치 (29호출 전수).
- **`usage.output_tokens` 회계 함정**: 스트리밍 usage 스냅샷이 누락되는 엔트리가 있어(finallive/lastlive 반영 행 2.7k/2.4k는 아티팩트·보정 시 24.6k/23.0k) 런 간 비교 전 Write 토큰/바이트 비(~0.29 tok/B)로 보정 필요.
- 휴먼 대기: ASK→사용자응답 구간을 명시 분리해야 "기계시간" 주장 가능.

## 5. 처방 (Phase C — 비저하 하드 게이트 통과 필수)

| # | 처방 | 판정 |
|---|---|---|
| **C-1** | **`design-architect.md` frontmatter에 Edit 추가** (`tools: Read, Grep, Glob, Edit, Write`) — 증폭기 제거. 자기스캔 적발 시 소수정이 ~200s 재Write → 수초 Edit. 모델이 이미 자발적으로 Edit를 시도했다(양 호출 각 1회·도구만 열면 쓴다) | **✅ 채택·구현 완료** (적대 2렌즈 양 GO·plugin 1.12.0·캐시 신선화 byte-id — relive 런 종료 확인 후) |
| C-2 | 코디네이터 architect 프롬프트 변이 축소 | **보류** — 기여가 비결정 추정(~39%)·L2 인접·비저하 검증 곤란 |
| C-3 | acceptance-tester에도 Edit | **보류** — 미관측(3.0~3.7m 정상)·"반복 관측만 처방"(DR-35 계보) |

**Phase D 적대 리뷰 결과 (2렌즈 양 GO — 근거 격상)**:
- **품질 렌즈**: "Write-only는 의도적 설계"라는 근거가 git·플랜·설계 정본·DEVLOG 어디에도 없음(`d2e4c8f` 축은 producer-vs-critic). 오히려 **본문 :23 "해당 절만 제자리 갱신·전체 재작성 금지"·:52·coordinator :20 "제자리 수정"이 이미 제자리-수정을 명령하는데 도구가 못 따라가는 본문↔도구 모순** — C-1은 모순 해소. 환영 §5.6·오참조 ~8곳의 *생산* 모달리티가 전량 Write임을 transcript로 확정(1차 Write가 L366에 "§5.6=Z1을 가리킴" 각주 땜빵까지 — 순차 생성 중 위로 못 돌아가는 모달리티의 산물). 전량 재작성도 미전파 모순을 새로 만듦(D-nit4 §3.4 반영하며 트리 L141 미갱신). **결정 발견: Write-only는 발견한 결함의 수정 포기를 유도**(14:46:27 "two cosmetic pointer fixes"로 강등 — 비용이 자기스캔을 사실상 절단하는 형태). 반대 증거 정직 기재: 전문 재독이 L30 결함을 부수 적발한 사례 1건 — 단 ~430s 지불의 부산물·비대칭적으로 해로움. body 지침 추가 비권고(이미 :23·:52에 실질 존재·DR-22 문구강화 계보).
- **집행 렌즈**: 런타임 거부 메시지 원문 "Edit exists but is not enabled in this context" = frontmatter allowlist가 유일 게이트·`Edit` 토큰 유효(같은 세션 coder 17회 성공). 미러 면제 실측(`corpus_mirror_sync.py:17` "스코프 밖: agents/*.md"·Codex 대응물 frontmatter tools 메커니즘 없음·body 도구명 일반화 "네이티브 파일 탐색 도구"). 백스톱 16종 frontmatter 비참조(grep 8히트 전부 docstring 역할명). validate baseline PASS. 조건 1건=버전 결정 명시 → **1.12.0 bump 채택**(도구 가용성=행동 변경·DR-55/56 계보).

**C-1 비저하 게이트 사전 검토**: ① 품질 — 검사·스캔·리뷰 절단 0. 전량 재작성은 무관 절 회귀 위험이 있고 Edit는 표적 수정이라 오히려 안전 방향. 반대 벡터(부분수정으로 절 간 정합 깨짐)는 적대 리뷰가 공격. ② 시간 — 새 호출·새 읽기 0·순수 절감. ③ Codex 미러 — Codex 대응물(`dddjango-design-architect/SKILL.md`)은 frontmatter tools 메커니즘 자체가 없어 **대응 변경 불필요**(body 무변경 = 미러 드리프트 0·DR-48 "frontmatter 런타임별·body byte-id" 선례).

**기대 효과 정직**: G1 중앙값(15~20m)은 런간 분산이라 그대로 — C-1은 **상한**(재작성 경로 발화 시 31m→~24m)을 깎는 처방. "34분이 안 나오게"가 목표이지 "10분이 되게"가 아님.

## 6. 라이브 관측 백로그

- C-1 적용 후 다음 라이브 런에서: ① architect의 Edit 실사용 여부 ② **명세 내부 참조 정합 grep 검증**(§참조 댕글링 0) ③ **L60형 표적 검증 오판**(전문 재독 생략으로 인접 결함 통과) 발생 여부 — N≥2 반복 관측 시에만 백스톱 논의(DR-35 계보) ④ G1 기계시간(중앙값 15~20m 분산은 그대로·재작성 경로 상한만 하락 기대). 측정은 §4 방법론 노트 레시피 재사용.
- dual 채점 시 런타임 간 수정 모달리티 차이(Claude=Edit 가능·Codex=항상 전량) 프로세스 메모.
- relive 런 종료(00:51 "4단계 완료" 확인) — 캐시 신선화 완료(1.12.0 byte-id). G2 포함 전체 telemetry 합산(A-5)은 채점 시 병행 가능.
