`feature.css`의 `.people-scroll`에 누락된 원본 패딩 `2px 2px 4px`을 기존 토큰으로 복원했습니다. 입력 컴포넌트의 기본·포커스·자식 효과와 주변 DOM/CSS를 직접 대조했으며, 다른 구현 파일은 변경하지 않았습니다.

`python3 smoke.py`는 exit 0으로 통과했습니다.

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

브라우저와 캡처가 제공되지 않아 **시각 검증은 미검증**입니다. 후속 담당자는 390×844에서 기본·포커스·입력 상태, 전체 배치 및 포커스 효과의 clipping을 실제 렌더로 확인해야 합니다.

읽은 파일, 수정 전후 hash, 실행 명령과 출력, 대조 근거 및 남은 검증은 [handoff.md](/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/baseline/trial-03/handoff.md)에 기록했습니다.

Serena는 정확한 CSS 선언 확인과 한 줄 수정이므로 생략했습니다.
