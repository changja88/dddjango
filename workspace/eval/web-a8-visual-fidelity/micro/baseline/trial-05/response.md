이름 입력 UI의 구조 수정을 완료했습니다.

- `feature.css`의 `.people-scroll`에 누락된 원본 패딩 `2px 2px 4px`을 기존 토큰으로 복원했습니다.
- `python3 smoke.py`가 통과했습니다.
- 임시 정적 검사에서 원본 CSS 16개 규칙의 선언 값, 본문 DOM 관계, source selector/import 미사용을 확인했습니다.
- 실제 읽은 파일, 수정 전 코드·해시, 검증 명령과 출력, 후속 검증을 [handoff.md](/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/baseline/trial-05/handoff.md)에 기록했습니다.

**시각 검증은 미검증입니다.** 제공된 실행 조건에서는 브라우저 관찰을 수행할 수 없어, 후속 담당자가 390×844의 원본·구현 렌더와 입력 포커스·그림자 클리핑을 확인해야 합니다.

Serena/Graphify는 작업 디렉터리에 opt-in 표식이 없어 사용하지 않았습니다.
