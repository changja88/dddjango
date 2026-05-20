주문 상세 페이지 관련 코드를 정리해줘.

요구사항:
- `order_detail_context`가 template 표시용 값만 만들고 도메인 상태 전이를 직접 처리하지 않게 해.
- `memo` 같은 선택 표시값이 빈 문자열이면 template에 빈 값이 그대로 나오지 않도록 표시용 fallback 값을 만들어줘.
- template에는 비즈니스 규칙을 넣지 말고 표시 책임만 남겨.
- 필요하면 static CSS와 template 구조를 조금 정리하고, `detail.css`를 유지하거나 수정한다면 template에서 명시적으로 참조해.
- 렌더링 관련 단위 테스트나 최소 compile 검증을 추가하고, 빈 memo가 fallback으로 표시되는 경로도 검증해.
