# R5 첫 조각 설계 — 코퍼스 소스-미러 동기 (검사 + 재동기)

> 진단(DIAGNOSIS.md v2) 처방 "기반 먼저" ①R5. **소스-미러 drift = 회귀 메커니즘 그 자체**(다음 빌드가 stale 소스로 재생성하면 DR 조용히 되돌림). 결정적·LLM무관이라 가장 싸고 확실. 이 문서는 구현 전 skill-creator·plugin-creator 리뷰 대상.

## 1. 코퍼스 3계층과 두 동기 불변식

| 계층 | 경로 | 역할 |
|---|---|---|
| **소스(빌드 입력)** | `workspace/reference/<skill>/reference/final.md` | 재생성 출처. **P1 Source Sufficiency 블록**(빌드타임 메타)을 유일하게 보유 |
| **배포본(Claude)** | `dddjango/skills/<skill>/references/final.md` | `/dddjango`가 읽는 실제 코퍼스 |
| **배포본(Codex)** | `codex-dddjango/skills/<skill>/references/final.md` | Codex 포트. 현재 Claude 배포본과 byte-identical |

- **불변식 1 (drift 축)**: 소스 *본문* ≡ 배포 *본문*. 소스는 본문 위에 P1 블록·출처 blockquote 등 attribution을 더 가질 수 있으나 **본문은 같아야** 함.
- **불변식 2**: 배포본(Claude) ≡ 배포본(Codex), **전체 파일 byte-identical**.

## 2. 현재 상태 (결정적 측정 — 2026-06-06)

11개 스킬 측정 결과(`/tmp/measure_body.py` 방법론, 아래 §4):

**불변식 1 — 본문 IN-SYNC (3)**: `discipline-cleancode`·`implementation-django-web`·`implementation-python`.
**불변식 1 — 본문 DRIFT (8)**, 방향 **100% 균일(소스 stale / 배포 current)**:

| 스킬 | 본문 drift(src-only/dep-only) | 원인 DR |
|---|---|---|
| architecture-api | 0/1 | DR-44/45 CAS 재시도 소진 경계 |
| architecture-db | 0/1 | DR-37 BC 경계 FK 금지 |
| architecture-ddd | 0/4 | DR-37 영속성/ORM FK·DR-43 Command 어휘노트 |
| discipline-houserules | 27/42 | DR-41/43 파일트리 명명(`_app`→command/query/dto, service→adapter, selector 폐기) |
| discipline-tdd | 1/1(치환) | DR-42 mocker carve-out 문장 추가 |
| implementation-django | 0/1 | DR-37 BC FK 데모 주석 |
| implementation-django-ninja | 3/4 | DR-43 R/C/Q(`place_order`→`place_order_command.execute` 등) |
| implementation-test | 94/93(절반 재작성) | DR-42 pytest 이주(`testpaths`/`pythonpath`→`DJANGO_SETTINGS_MODULE`) |

- **모든 src-only 라인 = 교체된 옛 버전**(houserules `_app`·ninja `place_order`·test `testpaths`). 소스에만 있는 *새로운 가치* 라인은 0건 → **재동기(소스 본문 ← 배포 본문)는 무손실**.
- **불변식 2 — 전부 IDENTICAL**(11/11 md5 일치). 현재 액션 불필요, 앞으로 가드 대상.

## 3. 비교 모델 (왜 이렇게)

### 3.1 본문 경계 = "P1이 아닌 첫 `## ` 헤딩부터 EOF"
attribution 영역이 파일마다 **비균일**해서 구조 파싱은 깨진다(hand-rolled awk가 2회 깨진 원인):
- 소스: `# Title` → `## P1 Source Sufficiency`(표) → [출처 blockquote] → `---` → 본문. **단 houserules는 P1 없음**(자작 표준, 외부출처 없음).
- 배포본: **두 형태** — (A) ddd/api/db: 출처·`---` 전부 제거, `# Title` → 본문 직행. (B) cleancode/web/python/ninja: 출처 blockquote+`---` 보존, P1 표만 제거.

→ attribution을 파싱하지 않고 **첫 비-P1 `## ` 헤딩**을 본문 시작 앵커로 삼으면 모든 변종을 무해하게 건너뛴다. 측정상 11/11 앵커 텍스트 일치 확인됨.

### 3.2 strip_p1의 함정 (교훈)
초기 측정은 "`## P1` ~ 첫 `---`"를 통째 제거했는데, 그 사이에 **양쪽 공통인 출처 blockquote**가 들어 있어 cleancode/web/python에 가짜 drift(+14~16)를 만들었다. 본문-앵커 방식이 이를 해소.

### 3.3 측정 vs 게이트의 엄격도
- **측정(ground truth)**: 비공백 라인 시퀀스 동등 — attribution/공백 노이즈에 강건.
- **게이트(영구)**: 재동기 후엔 본문이 byte 동일해지므로 **본문 영역 byte-exact**가 더 민감·정확(앞으로 공백 변경도 drift로 포착). 불변식 2는 **전체 파일 byte-exact**.
- 알려진 한계: (a) 본문이 `## ` 헤딩 없이 시작하면 앵커 실패 → 게이트가 명시적 에러로 처리. (b) attribution 영역 자체의 drift는 본문 비교에서 제외(스코프 밖, 별도 명시).

## 4. 두 산출물

### 산출물 A — `check-corpus-mirror-sync.py` (빌드타임/메인테이너 검사, **런타임 게이트 아님**)
- 13개 런타임 게이트는 *사용자 생성 코드*를 검사. 이건 *플러그인 자체 코퍼스 무결성*을 검사 → **레포 dev 도구**(수동/CI/pre-commit), `/dddjango` 게이트 세트에 등록 안 함.
- 위치 후보: `dddjango/scripts/`(기존 게이트와 동거하나 런타임 미배선) 또는 `workspace/tools/`(파서류와 동거). **plugin.json hooks·coordinator 산문에 배선하지 않음.**
- 동작: 11스킬 × {불변식1 본문 byte-exact, 불변식2 전체 byte-exact} 검사. drift 시 per-skill 차이 요약 출력 + exit2. clean이면 exit0.

### 산출물 B — 일회성 재동기 (소스 본문 ← 배포 본문, 8스킬)
- 라인 splice: `new_source = source_lines[:앵커] + deployed_lines[앵커:]`. 소스 preamble(title+P1+출처+`---`) 보존, 본문만 배포본 verbatim 교체.
- 결과: 소스 본문 == 배포 본문 byte-exact. cleancode/web/python은 이미 동기라 no-op(멱등).
- 검증: 재동기 후 산출물 A exit0.

## 5. 리뷰어에게 묻는 열린 질문
1. **본문 앵커**("첫 비-P1 `## ` 헤딩")가 강건한가? 미래 스킬이 본문을 `### ` 또는 prose로 시작하면? 더 안전한 앵커가 있나?
2. **게이트 배치**: 빌드타임 dev 도구로 두는 게 맞나? CI/pre-commit 배선까지 이 단계에서 할지, 아니면 검사 스크립트만 먼저?
3. **splice 재동기 vs 수동 편집**: 8스킬 자동 splice가 안전한가, 아니면 houserules(27/42 치환)·test(94/93)처럼 큰 건 사람이 검수 후 적용?
4. **불변식 2(codex)**: 현재 깨끗인데 게이트가 양방향(배포→codex 누가 truth?) 중 무엇을 truth로? 현재 배포본 변경 시 codex 수동 재복사 워크플로 가정 맞나?
5. **attribution 영역 drift**를 스코프 밖으로 두는 것이 R5 목적(DR 본문 회귀 방지)에 충분한가?
6. P1 Source Sufficiency 블록을 소스만 갖는 현 구조가 옳은가, 아니면 이것도 동기 대상인가?

---

## 6. 리뷰 반영 결정 (skill-creator·plugin-creator 2렌즈, 구현 전)

두 적대 리뷰 모두 **"수정 후 GO"**. 핵심 정량 주장(앵커 11/11 일치·재동기 무손실·불변식2 references byte-identical·splice seam 안전)은 실파일로 재현됨. 반영한 결정:

| # | 리뷰 지적 | 결정 |
|---|---|---|
| 1 | 배치: `dddjango/scripts/`는 배포 오염 + 게이트 동류 오인 | **`workspace/tools/`**, `check-` 접두사 제거 |
| 2 | 게이트 fail-open을 베끼면 메인테이너 검사에서 drift 은폐 | **fail-CLOSED**, exit 0/2/3/1 |
| 3 | 불변식 1엔 재동기 두면서 불변식 2(codex)엔 안 두면 비대칭 | `--write`가 둘 다 해소(소스←배포 splice + codex←배포 복사) |
| 4 | "전체 파일 byte-identical"은 codex final.md 11개에만 참(codex는 독립 자산 보유) | 불변식2 스코프 = **final.md 11개 한정** |
| 5 | 위치 앵커가 미래(본문이 `### `/prose 시작)에 취약 | preamble 오염(첫 `## ` 앞 비-attribution 라인) 시 **fail-fast(exit3)** |
| 6 | SKILL.md·agents도 DR 거주면(skill-creator [중대]) | **해소**: DEVLOG:45 계약 — 이들은 plugin-native(미러 없음·재생성 경로 없음 → R5 회귀 메커니즘 밖). houserules는 미러 보유라 불변식1 대상. R5 = references 한정 명시 |
| 7 | 빌드 생성기가 SKILL.md를 references에서 파생하면 [중대]→[치명] | **해소**: 자동 빌드 파이프라인 부재(빌드스크립트0·CI0·pre-commit0). 재생성은 수동/LLM 재저작이 소스 코퍼스를 참조 → 회귀는 "자동 되돌림"이 아닌 "byte-identical 계약 잠복 위반". severity 하향 |
| 8 | 배선 없는 검사 = A1(팬텀 완료) 재생산, plugin-creator "타협 불가" | **사용자 결정으로 보류** — 단 근거가 다름: "검사 *방법*이 검증돼야 자동 차단에 묶는다". 검증 완료(§7) 후 배선은 라이브 발화 검증을 추가 전제로 별도 단계 |

## 7. 검증 결과 (사용자가 배선의 전제로 건 조건)

- **현실 코퍼스**: 8 drift 정확 탐지(api/db/ddd/houserules/tdd/django/ninja/test)·codex 11/11 in-sync·exit2 — ground truth 100% 일치.
- **합성 13케이스 전부 PASS**: 거짓양성0(in-sync) · true positive(불변식1·2 drift→exit2) · **fail-CLOSED**(앵커오염·src부재·codex부재→exit3) · 동기 정확성 · **P1 보존** · **멱등**(--write 2회=동일).
- **검증이 실버그 적발**: docstring이 광고한 `--check` 플래그 미구현(argparse 에러) → 추가·상호배타로 수정.

## 8. 완료 (R5 첫 조각)

- **재동기 실행**: 변경 = 소스 미러 **8개에만** 국한(codex·배포본 무변경)·P1 보존(7개 P1=1·houserules 0)·본문 byte-exact 8/8·사후 `--check` exit0. DR-37/41/42/43/44 본문이 소스에 복원됨.
- **보류**: 밸브(pre-commit/CI) 배선 — 검사 방법은 검증됐으나 자동 차단 도입은 라이브 발화 검증을 추가 전제로 다음 단계.
- **다음(R5 잔여·백로그)**: attribution 영역(P1·출처) drift는 본 게이트 스코프 밖(별도 백로그) · 배선(검증 후) · 그 다음 처방 ②측정 R2 N≥5.
