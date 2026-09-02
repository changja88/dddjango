"""고정 시계 — pre-gate 계약 실존 e2e 픽스처의 «실존 확인» 대상(framework.* 는 27종 방향 규칙의 주어가 아니다)."""


class FrozenClock:
    """계약 실존 ⑶ 확인 대상."""

    def now(self) -> int:
        return 0
