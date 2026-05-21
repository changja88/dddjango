# architecture-ddd P3 reference 후속 계획

## 수정 이유

`architecture-ddd` source reference가 implementation-pattern 전용 source가 생긴 뒤에도 layered/DIP, hexagonal, CQRS, package structure, Data Mapper, Repository/UoW 결정을 넓게 포함하고, 일부 문구는 해당 source가 향후 분리될 예정이라고 말한다. Reference 경계 정리를 별도 작업으로 수행해야 runtime skill과 source reference의 책임 기준이 장기적으로 어긋나지 않는다.

## 수정 범위

- `workspace/reference/architecture-ddd/reference/final.md`

## 수정하지 말아야 할 범위

- 이번 P3 skill 수정 범위에서는 source reference를 직접 수정하지 않는다.
- `dddjango/skills/architecture-ddd/**`에 source reference의 세부 구현 패턴 내용을 복사하지 않는다.
- `workspace/reference/architecture-implementation-patterns/reference/final.md`는 충돌 확인 대상으로만 보고, 별도 gap이 확인되기 전에는 수정하지 않는다.
- eval case, answer oracle, evaluator, runtime cache는 reference 후속 작업 범위가 아니다.

## 작업 체크리스트

- [ ] `architecture-ddd` source reference에서 implementation-pattern 전용 세부 결정을 식별한다.
- [ ] DDD source가 계속 소유해야 하는 전략/전술 DDD 결정과 implementation-patterns source로 넘길 결정을 분리한다.
- [ ] stale `향후 분리` 및 fallback wording을 현재 dedicated source 존재에 맞게 갱신한다.
- [ ] 의사결정 요약의 architecture/package rows가 DDD source 책임인지, implementation-patterns source 책임인지 재분류한다.
- [ ] reference 변경 후 관련 validator와 skill/source parity 영향을 확인한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
```

## 완료 조건

- `architecture-ddd` source reference는 DDD 전략/전술 모델링 책임 중심으로 정리된다.
- implementation-pattern 전용 결정은 `architecture-implementation-patterns` source와 충돌하지 않는다.
- stale future-split/fallback wording이 제거되거나 현재 source 구조에 맞게 바뀐다.
- 후속 reference 작업의 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
