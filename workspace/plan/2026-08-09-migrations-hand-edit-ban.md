---
날짜: 2026-08-09
대상: 저장소의 **`dddjango/`** — 여기가 정본이다. `references/final.md` 는 `workspace/tools/corpus_mirror_sync.py --write` 가 `workspace/reference/` 와 `codex-dddjango/` 로 전파한다. **미러를 직접 편집하지 않는다.**
근거: 수정안 트리 120행 (`docs/work_flow.html` sha `c56379aa3860975a`) · **T37** · D43 카드의 「대량 «데이터» 채우기의 자리」 절
상태: **명세 확정 · 코드 미적용** — 명세는 **4번 ⓑ** 로 편입, 적용은 **6번(플러그인을 만든다)**
편입: 이 문서는 **4번이 만들 명세**(`workspace/design/<날짜>-tree-revision-spec.md`)의 ⓑ 로 그대로 편입된다. ⓐ 는 `2026-08-07-plugin-path-contract-and-fail-open-fix.md` 다.
---

# 명세 조각 ② — `migrations/` 손수 편집 금지

## 0. 무엇을 정했나

**결정 (2026-08-09 · 사용자):**

> 「migrations 폴더 안은 사람이 직접 절대 손대면 안 되는 걸로 알고 있어. django 가 자동생성하는 파일만 들어가는 게 맞을 거 같아. 왜냐면 migrations 폴더 안에 있는 파일은 실제로 많이 쌓이게 되면 압축(squash)하는 경우도 있기 때문이야.」

**`application/<app>/infra_layer/django_<bc>/migrations/` 에는 `makemigrations` 가 생성한 것만 둔다.** 사람이 `RunPython` 으로 데이터를 채우는 파일을 만들지 않는다.

대량 데이터 채우기는 **파일의 자리 문제가 아니라 배포 절차의 한 «단계»** 다 — Expand → **Backfill** → Contract (`architecture-db` §11.1). Backfill 단계의 코드는 트리 **밖**인 저장소 루트 `scripts/` 에 둔다(D22 — 「임시 · 일회성」 · **규정하지 않는다**).

## 1. 왜 — 근거 셋

### ⑴ 마이그레이션은 「돌았다 / 안 돌았다」 두 상태뿐이다

`architecture-db` §11.2 가 대형 backfill 에 요구하는 것:

- batch 크기와 pause 정책을 정한다
- 실패한 batch 를 재실행해도 안전하도록 idempotent 하게 만든다
- 진행률, 오류율, lag, query latency 를 모니터링한다
- 부분 완료 상태에서 rollback 할지 forward-fix 할지 미리 정한다

**마이그레이션은 이 넷을 하나도 못 한다.** 중간에 죽으면 그 마이그레이션이 미완료로 남고 「어디까지 했나 · 여기부터 다시」가 없다. 같은 스킬이 §11 에서 요구하는 것을 §10.2 예제가 구조적으로 못 만족시키는 **내부 모순**이다.

### ⑵ squash 최적화가 그 자리에서 끊긴다

Django 6.0 소스 `django/db/migrations/operations/base.py:160-170`:

```python
def reduce(self, operation, app_label):
    if self.elidable:        return [operation]   # elidable 이면 «지워진다»
    elif operation.elidable: return [self]
    return False                                  # 기본값이면 «최적화가 막힌다»
```

공식 문서 축자 — *"…if you have any `RunSQL` or `RunPython` operations **(which can't be optimized through unless they are marked as `elidable`)**"*.

**기본값(`elidable=False`)에서는 보존되고, 대신 그 지점에서 최적화가 막힌다.** 지워지는 것은 `elidable=True` 를 명시했을 때뿐이다.

### ⑶ 현행 예제가 상한 없는 루프다

`implementation-django` §10.2 의 예제가 `for user in User.objects.filter(...)` 를 상한 없이 돌며 건마다 `.save()` 한다. 100만 행이면 **한 트랜잭션 안에서 100만 번 저장**한다.

## 2. 고칠 곳 — 셋

전문을 훑어(`RunPython`·`RunSQL`·`--empty`·`separate_database_and_state`·`elidable`·`squashmigrations`) 대상이 **한 파일**임을 확인했다. `architecture-db` §11 은 *「Django `RunPython`, `apps.get_model()`, `sqlmigrate`, migration class 작성은 `implementation-django`로 넘긴다」* 로 위임만 하므로 안 건드린다. 백스톱 `check-app-container.py` 는 마이그레이션을 **읽기만** 하므로 무관하다.

| # | 어디 | 무엇 |
|---|---|---|
| **S-M1** | `implementation-django` §10.2 「데이터 마이그레이션」 | **금지로 바꾼다.** 「`migrations/` 에는 `makemigrations` 가 생성한 것만 둔다 · 데이터 채우기는 `scripts/` 로 · 순서는 Expand → Backfill → Contract 로 사람이 관리한다(§11.1)」 |
| **S-M2** | 같은 절의 예제 코드 | **상한 없는 루프 `.save()` 예제를 제거한다.** 남긴다면 「이렇게 하지 않는다」의 반례로만 |
| **S-M3** | 같은 절의 squash 서술 | **정정.** 옛: 「데이터 마이그레이션은 `squashmigrations`에서 **보존되지 않으므로** 별도 관리한다」 → 새: 「기본값(`elidable=False`)에서는 **보존되며 그 지점에서 최적화가 끊긴다**. `elidable=True` 를 달면 squash 때 지워진다」 |

## 3. 남는 회색 — 정직하게

**스키마 변경과 «순서»가 묶여야 하는 소량 정리**(예: NOT NULL 을 걸기 전에 NULL 을 채워야 함)가 `scripts/` 로 나가면 순서를 **사람이 배포 절차로** 지켜야 한다. 마이그레이션에 넣으면 순서가 코드로 보장되는 대신 §11.2 의 넷을 잃는다.

**이 결정은 후자를 택했다.** §11.1 Expand / Backfill / Contract 자체가 「사람이 절차로 관리하는 3단계」라는 것이 그 근거다 — 마이그레이션 파일 하나로 접으라는 뜻이 아니었다.

## 4. 트리 쪽 짝

정본 `migrations/` 행(트리 360행 근처 · `rd-` 는 재생성마다 확인)에 같은 문장이 들어갔다.

> **`makemigrations` 가 «생성한 것»만 둔다** — 사람이 손으로 데이터를 채우는 파일(`RunPython`)을 넣지 않는다. 마이그레이션은 「돌았다 / 안 돌았다」 두 상태뿐이라 배치 크기·부분 재실행·진행률이 구조적으로 안 된다. 대량 채우기는 파일이 아니라 **배포 절차의 한 «단계»** 다(Expand → Backfill → Contract) · 덤 — `elidable` 을 안 달면 그 자리에서 squash 최적화가 끊긴다

**`scripts/` 에는 한 글자도 안 적었다.** 사용자 지시 — 「scripts 는 임시로 쓰고 버리는 일회성이 많으니까 아무런 규칙도 없는 게 좋겠다」. D22 자신이 이미 「규정하지 않는다 — 이름도 화살표도 앎의 범위도」이고, 트리 **밖**이라 예외가 아니라 **관할 밖**이다.
