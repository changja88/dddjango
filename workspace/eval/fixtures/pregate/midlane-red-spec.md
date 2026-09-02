# 미니 설계 명세 — orders BC 레인 마커 «red» 변형 (midlane 픽스처 — 재발화 판형 E1′/E2′)

`midlane-spec.md` 와 같은 add 경로에 **스텁 자체가 red 인 심볼 2개**(#267 — 값 객체 파일에 공개 클래스 2)를 적는다.
러너가 두 상태로 돌린다 — E1′ 계획 add 가 기준선 «이후 커밋»에 실존(같은 2클래스 실물) · E2′ 같은 실물이 미커밋
WIP — 둘 다 `--base <기준선>` 으로 **exit 2 · 같은 안정 ID** 여야 한다(5단계 리뷰 MAJOR A: 기실현 add 실물이
앵커 스냅숏에 남으면 스텁 진단이 L∩N 잔존으로 빠져 E2′ 가 exit 0 이 되던 오염의 회귀 가드 — «해소(L∖N) 0 ∧
check-domain-model anchor 열 0» 을 함께 단언한다).

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/orders/domain_layer/shared_value_object/lane_marker.py	# 값 객체(의도 위반 — 2클래스)
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/orders/domain_layer/shared_value_object/lane_marker.py::LaneMarker {value: str}
application/orders/domain_layer/shared_value_object/lane_marker.py::LaneMarkerTwin {value: str}
```
