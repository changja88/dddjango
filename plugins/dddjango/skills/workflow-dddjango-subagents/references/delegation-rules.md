# Delegation Rules

Prefer subagent-driven execution only when it improves independence, coverage, or
review quality. Do not use subagents to create ceremony for small tasks.

## Use Role Decomposition

Use subagents or sequential roles when the task includes at least two of:

- DDD or bounded-context design
- database schema, indexes, migrations, or transaction boundaries
- Django Ninja API contract or endpoint implementation
- Django service/model/queryset implementation
- TDD, pytest, fixtures, or integration tests
- clean architecture review or refactoring

Strong signals:

- orders, payments, refunds, inventory, reservations, coupons, ledgers, or auth
- state transitions and invariants
- DRF-to-Django-Ninja migration
- multiple modules or file ownership boundaries
- user asks for "subagent", "role-based", "분담", "병렬", "설계와 테스트까지"

## Avoid Delegation

Keep the work in one flow when:

- the task is a small single-file edit
- the user only asks for a short explanation
- file ownership cannot be separated
- the needed domain contract is already explicit and only one implementation
  detail remains
- delegation would require external credentials, production access, or long
  running work not approved by the user

## Ordering

Use this default order:

1. Coordinator scopes the work and identifies risks.
2. Domain Agent or Architecture Agent defines contracts if business rules or
   architecture boundaries are unclear.
3. DB/API/Django/Test roles run in parallel only after the needed domain
   contracts are stable.
4. Review Agent checks the integrated plan or patch.
5. Coordinator resolves conflicts and produces the final answer.

## Parallel Safety

- Parallelize only independent read-only analysis or disjoint file edits.
- Do not assign the same file to multiple editing roles.
- If two roles need the same file, make one role produce a recommendation and
  let the Coordinator apply the final edit.
- Do not expose another role's expected answer when forward-testing a skill.

## Sequential Fallback

If subagents are not available, run the same role sequence in the main thread.
State only: "subagent를 사용할 수 없어 같은 역할 분해를 순차로 진행합니다." Then
continue. Do not stop and ask the user unless the missing subagent capability is
the user's explicit deliverable.

