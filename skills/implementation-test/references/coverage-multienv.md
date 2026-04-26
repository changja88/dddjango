# 커버리지와 멀티환경 테스트 레퍼런스

coverage.py 설정, tox, nox를 사용한 멀티환경 테스트의 상세 규칙과 예시.

---

## 1. coverage.py pyproject.toml 종합 설정

```toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/__init__.py",
    "*/conftest.py",
]
parallel = true

[tool.coverage.report]
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
    "raise NotImplementedError",
    "pass",
    "\\.\\.\\.",
    "@abstractmethod",
]
exclude_also = [
    "if typing.TYPE_CHECKING:",
]
show_missing = true
precision = 2
skip_empty = true

[tool.coverage.html]
directory = "htmlcov"
title = "My Project Coverage"

[tool.coverage.xml]
output = "coverage.xml"
```

---

## 2. 활용 명령어

```bash
coverage run -m pytest tests/    # 커버리지 측정 실행
coverage report                  # 콘솔 리포트
coverage html                    # HTML 리포트
coverage xml                     # XML 리포트 (CI 연동)
coverage combine                 # 여러 실행 결과 결합
```

---

여러 Python 버전과 의존성 조합에서 테스트를 자동 실행하는 도구이다. 라이브러리 개발 시 필수적이다.

## 3. tox: 선언적 설정

```toml
[tool.tox]
env_list = ["py311", "py312", "py313", "lint", "typecheck"]

[tool.tox.env_run_base]
description = "run tests"
deps = [
    "pytest>=8.0",
    "pytest-cov",
]
commands = [
    ["pytest", "--cov=src", "tests/"],
]

[tool.tox.env.lint]
description = "run linters"
deps = ["ruff"]
commands = [["ruff", "check", "src/"]]

[tool.tox.env.typecheck]
description = "run type checker"
deps = ["mypy"]
commands = [["mypy", "src/"]]
```

```bash
tox              # 모든 환경 실행
tox -e py312     # 특정 환경만
tox -p auto      # 병렬 실행
```

---

## 4. nox: Python 코드 기반 설정

tox보다 유연하며, 설정 파일이 일반 Python 코드이므로 복잡한 로직을 작성할 수 있다.

```python
# noxfile.py
import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["tests", "lint"]

@nox.session(python=["3.11", "3.12", "3.13"])
def tests(session):
    session.install("pytest", "pytest-cov")
    session.install("-e", ".")
    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "tests/",
    )

@nox.session
def lint(session):
    session.install("ruff")
    session.run("ruff", "check", "src/", "tests/")

@nox.session
def typecheck(session):
    session.install("mypy", ".")
    session.run("mypy", "src/")

# 파라미터화: Django 버전별 테스트
@nox.session
@nox.parametrize("django", ["4.2", "5.0", "5.1"])
def test_django(session, django):
    session.install(f"django=={django}", "pytest", "pytest-django")
    session.install("-e", ".")
    session.run("pytest", "tests/")
```

```bash
# 기본 세션 실행
nox

# 특정 세션
nox -s tests

# 가상환경 재사용 (개발 시 빠른 반복)
nox -R

# 사용 가능한 세션 목록
nox -l
```

---

## 5. tox vs nox 비교

| 항목 | tox | nox |
|------|-----|-----|
| 설정 형식 | INI/TOML (선언적) | Python 코드 (프로그래밍 가능) |
| 유연성 | 중간 | 높음 (조건문, 반복문 사용 가능) |
| 커뮤니티 | 더 오래됨, 넓은 사용자 기반 | 성장 중, Google 프로젝트에서 사용 |
| 추천 | 단순한 멀티버전 테스트 | 복잡한 빌드/테스트 워크플로 |
| 학습 곡선 | 낮음 | 약간 높음 |

> 출처: [Coverage.py Configuration Reference](https://coverage.readthedocs.io/en/latest/config.html)

> 출처: [tox Documentation](https://tox.wiki/en/latest/user_guide.html), [Nox Documentation](https://nox.thea.codes/)
