# 미니 설계 명세 — 설정 배선 update 만 (계약 실존 update-only 픽스처 — kkebi S2 판형)

file-plan 이 `update` 뿐이라 실체화 0(게이트 미호출)인데 boundary-imports 에 ⑵ 자리표시자 결손 1건이 있으면
«실체화 0 · 실존 결손 1건» 문면으로 **exit 5**(4 가 아니다)임을 고정한다 — kkebi notification-settings-http S1
(`dd876b7` 두 published_error 0B) 의 기계 표현. 실존 확인 행 1건을 함께 두어 update 소비자의 판정 포함을 증명한다.

## 파일 계획

<!-- machine: file-plan -->
```paths
update	config/settings/base.py	# 설정 배선(시뮬레이션 밖 — 실존 판정 소비자)
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
config/settings/base.py	from framework.test.frozen_clock import FrozenClock
config/settings/base.py	from framework.test.placeholder_helper import Helper
```
