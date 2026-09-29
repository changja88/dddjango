# R8-I2 변이 가드 증거 — 재실행 방법

`check-transaction-boundary.py` #195 는 인자 있는 도메인 컬렉션 팩토리 호출에 «본문 증명»을 요구한다(R8-I2).
이 장치는 그 증명의 조건을 하나씩 뗀 변이체 22종이 탐침이나 fixture 에서 잡히는지 다시 보인다. 인자 없는
호출은 R8-D2 의 선언 전파(P1z) 그대로다. 그래서 «무인자에도 증명 요구»(MUT-noargproof)도 변이체로 둔다.

진단·리뷰 때 scratch 에만 있던 탐침 생성기와 케이스표를 옮겨 왔다. 탐침 트리(약 15MB)는 저장하지 않고,
실행할 때마다 임시 디렉터리에 만든다.

## 실행

```sh
python3 workspace/plan/2026-09-26-refactor-path-repair/evidence/i2-mutants/run_mutants.py --check
```

- 저장소 루트에서 돌린다.
- 대상은 173개, 판은 23개(구현 + 변이체 22)다.
- 16코어 기계에서 벽시계 약 30초(CPU 약 370초)다. 코어 수만큼 병렬로 돌리므로, 코어가 적으면 그만큼 길어진다.
- `--check` 는 결과를 `expected.md` 와 byte 대조한다. 다르면 diff 를 찍고 exit 1 이다.
- 인자를 주지 않으면 표만 찍는다. `--write` 는 `expected.md` 를 다시 쓴다.
- `--scripts DIR` 는 다른 검사기 디렉터리를, `--fixtures DIR` 는 다른 transaction_boundary fixture 를 쓴다.

## 파일

| 파일 | 역할 |
|---|---|
| `base_tree.json` | 탐침 바탕 트리(diag-D2 `c_domain_seed_inline` · 19 파일)를 `{경로: 본문}` 으로 묶은 것 |
| `make_probes_i2.py` | 진단 탐침 81개(h 계열 green · B 계열 세탁 공격 red · fc·lim). 케이스표 = 파일 안 `case(..)` 호출 |
| `make_attacks.py` | 적대 리뷰 탐침 67개(RC·RA·RR·RE·RK 세탁 공격 · G 리팩토링 모양) |
| `make_impl_probes.py` | 구현 리뷰·최종 재검토 탐침 23개(N 무인자 · D1 클래스 본문 데코레이터 가림 · S sorted/reversed · R 역순 반복자 별칭 · G1 모듈 함수 `global` 내장 가림) |
| `run_mutants.py` | 변이체 정의(`MUTANTS`)와 실행기 |
| `expected.md` | 구현 기준 기대 결과 |

- 두 생성기 `make_probes_i2.py`·`make_attacks.py` 는 scratch 원본과 경로 상수·`build()` 서명만 다르다.
  새로 만든 트리가 scratch 트리와 byte 동일함을 확인했다.
- 생성기는 따로 돌릴 수도 있다: `python3 make_probes_i2.py <바탕 디렉터리> <출력 디렉터리>`.

## 읽는 법

- 기대 열
  - `green` = 원소가 도메인 본문에서 새로 태어난다
  - `red` = 조회된(받은) 인스턴스가 원소로 나온다
  - `fc` = 이상은 green 이지만 fail-closed red 를 받아들인다
  - `lim` = 이상은 red 이지만 문서화한 한계(green)를 받아들인다. 무인자 호출의 클래스·모듈 상태 세탁(N1–N5)이 여기 든다
- `expected.md` §1 의 `✗` 는 RA10 하나다. `__eq__` 로 누적 이름에 원소를 들이는 비교 상대이고, 검사기 docstring 이
  가정 밖으로 적은 모양이다.
- §2 는 변이체마다 판정이 바뀐 탐침과 bad_rules fixture 발견 수를 적는다. «잡히지 않은 변이체: 없음» 이 합격선이다.
- fixture 가 직접 무는 변이체는 넷이다: MUT-P1·MUT-anyclscall·MUT-noreadcheck·MUT-noinitcheck(bad_rules 의
  select·retouch·merge·followup_orders). 나머지는 탐침으로만 문다.

## 검사기가 바뀌면

- 변이체는 검사기 문자열 치환이다. 원문이 정확히 한 번 나오지 않으면 실행기가 그 변이체 이름과 함께 멈춘다.
- #195 도메인 증명 코드를 고치면 `MUTANTS` 의 원문을 새 코드에 맞춘다. 결과가 달라졌으면 사유를 확인한 뒤
  `--write` 로 `expected.md` 를 갱신한다.
- 옛 구현을 다시 보려면 그 커밋을 `git worktree add` 로 꺼내 `--scripts <꺼낸 곳>/dddjango/scripts` 로 돌린다.
