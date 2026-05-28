# workspace/eval — dddjango Codex 포트 코드 품질 평가

Codex 포트(`codex-dddjango/`)의 **산출 코드 품질**을 평가하는 하니스. PoC는 메커니즘(spawn_agent·평문 게이트·설치)만 검증했고, 여기서는 *생성된 코드*를 본다.

## 평가 설계 (확정)

- **비교 기준**: 동일 입력에 대한 **Claude 신규 런 1회**(`claude-1`) ↔ Codex 산출 1:1 비교.
- **결정성**: Codex **2~3회** 반복(`codex-2`,`codex-3`[,`codex-4`])으로 런 간 변동 관찰.
- **도구**: **산출물 정적 평가만**(세션 로그 파서 없음). 토큰·시간은 런타임 요약값 수기 기록.
- **질문 분리**: Q1 포트 충실도(Claude 대비 동등성, 주) / Q2 dddjango 표준 부합(런타임 무관, 부).

## 파일

| 경로 | 내용 |
|---|---|
| `PROTOCOL.md` | 매 런 고정 입력(프롬프트·게이트 답)·리셋·캡처·메타 기록 절차. |
| `RUBRIC.md` | 정적 평가 루브릭 — Q1 동등성 10차원 / Q1′ 결정성 / Q2 표준. |
| `reset.sh` | 타깃 프로젝트를 baseline으로 초기화(.venv 보존). 매 런 사이 필수. |
| `baseline/` | 표준 시작 상태(Product-only). 모든 런의 단일 출발점. |
| `runs/codex-1/` | PoC 보존본(참고용 — 빌드 중 스킬 재설치 이력 있음). |
| `runs/<run>/` | 각 런 산출물 캡처 + `meta.md`. |
| `RESULTS.md` | (런 완료 후 생성) 최종 비교·결정성·결론. |

## 진행 상태

- [x] baseline 정본 + reset.sh (검증 완료, dddjango-smoke 초기화됨)
- [x] PoC 산출물 `codex-1` 보존
- [x] 루브릭·프로토콜
- [ ] `claude-1` 런 (비교 기준)
- [ ] `codex-2`,`codex-3` 런
- [ ] `RESULTS.md` 작성

## 대상 프로젝트

`/Users/hyun/Desktop/dddjango-smoke` (Django 4.2.30, py3.9, config+catalog.Product). git 아님. `.venv` 보존.
