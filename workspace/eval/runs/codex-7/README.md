# dddjango-smoke-sample — 스모크/비교평가 마스터 템플릿

이 폴더는 **단일 마스터(sample)** 다. 여기서 직접 런을 돌리지 않는다 — **복제해서** 런타임별 타깃을 만든다.

```
config/        # Django startproject (config)
catalog/       # startapp: Product(name, price, stock) 모델만 — "재고 있는 상품"만 있는 빈 슬레이트
manage.py
requirements.txt   # Django==4.2.30
PROMPT.md          # 고정 기능 프롬프트 + 고정 게이트 답 + 시드 정의 (테스트 입력)
setup.sh           # venv 생성 + 의존성 설치 + migrate + 시드 + check (멱등)
.gitignore         # .venv/ db.sqlite3 __pycache__/ .dddjango/ 무시
```

## 동일한 테스트를 만드는 법 (정본)

```bash
# sample → 런타임별 타깃 복제 (추적 코드만 = 바이트 동일 보장)
git clone ~/Desktop/dddjango-smoke-sample ~/Desktop/dddjango-claude-index
git clone ~/Desktop/dddjango-smoke-sample ~/Desktop/dddjango-codex-index

# 각 타깃 1회 셋업 (venv·DB·시드는 requirements/시드로 결정적 = 동일)
bash ~/Desktop/dddjango-claude-index/setup.sh
bash ~/Desktop/dddjango-codex-index/setup.sh
```

- **claude-index** = Claude Code `/dddjango` 런 타깃
- **codex-index** = Codex CLI `dddjango` 스킬 런 타깃

`git clone` 으로 **추적 코드가 바이트 동일**, venv·DB·시드는 `requirements.txt`+`setup.sh`로 **결정적으로 동일** → 두 런이 같은 시작점에서 출발한다.

전체 방식·합격 기준·기록처는 레포 `workspace/DEVLOG.md §4 스모크 테스트 방식(정본)`.
