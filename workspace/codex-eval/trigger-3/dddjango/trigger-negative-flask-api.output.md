파일 생성이 필요한 작업이지만 현재 세션이 `read-only` sandbox이고 승인도 비활성화되어 있어 패치가 거부되었습니다.

적용하려던 구성은 다음입니다:

- `app.py`: Flask 앱
  - `POST /todos`: todo 생성
  - `GET /todos`: todo 목록 조회
  - `title` 필수 검증
- `requirements.txt`: `Flask>=3.0,<4.0`
- `README.md`: 실행 및 curl 예시

쓰기 가능한 세션으로 다시 열면 바로 파일을 생성해서 구현까지 마무리할 수 있습니다.