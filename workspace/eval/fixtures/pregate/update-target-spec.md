# 미니 설계 명세 — orders BC 프로모션 값 객체 보강 (update 대상 픽스처 · 차단 모드 E4)

file-plan 이 `update` 한 행뿐인 명세다. 러너가 같은 명세를 저장소 상태 셋으로 돌린다:
ⓐ mini_repo 그대로(`promo.py` 기준선 부재) → «형식 red — update 대상 부재» exit 3(add 를 update 로 재라벨해
실체화 0 으로 도피하는 경로 봉쇄) · ⓑ 기준선에 유효 승격 형태 `promo/__init__.py` + `promo/promo.py` 커밋 →
승격 형태 예외로 실존 · update 뿐이라 실체화 0 · 결손 0 → skip exit 4 · ⓒ 승격 폴더를 write 만 하고 커밋하지
않음(오버레이 실존) → 기준선 부재라 exit 3(오버레이는 판정에 넣지 않는다).

## 파일 계획

<!-- machine: file-plan -->
```paths
update	application/orders/domain_layer/shared_value_object/promo.py	# 기존 값 객체 보강(정형 append)
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/orders/domain_layer/shared_value_object/promo.py::Promo {code: str, rate: int}
```

## 영구 테스트 입장 표

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| Promo 비율 검증 | 값 객체 불변식 | 음수 비율 유입 | `application/orders/test/unit/test_promo.py` | reuse | `application/orders/test/unit/test_promo.py` |
