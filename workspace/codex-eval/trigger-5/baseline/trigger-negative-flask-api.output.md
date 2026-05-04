현재 워크스페이스가 읽기 전용이라 파일 생성이 거부됐습니다. 그래서 직접 적용은 못 했습니다.

생성하려던 구성은 다음과 같습니다.

`app.py`
```python
from datetime import datetime, timezone
from itertools import count

from flask import Flask, jsonify, request

app = Flask(__name__)

todos = []
todo_ids = count(1)


def validation_error(message):
    return jsonify({"error": message}), 400


@app.post("/todos")
def create_todo():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return validation_error("JSON body is required.")

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return validation_error("title is required.")

    completed = data.get("completed", False)
    if not isinstance(completed, bool):
        return validation_error("completed must be a boolean.")

    todo = {
        "id": next(todo_ids),
        "title": title.strip(),
        "completed": completed,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    todos.append(todo)

    return jsonify(todo), 201


@app.get("/todos")
def list_todos():
    return jsonify(todos)


if __name__ == "__main__":
    app.run(debug=True)
```

`requirements.txt`
```txt
Flask>=3.0,<4
```

사용 예:
```bash
pip install -r requirements.txt
flask --app app run
curl -X POST http://127.0.0.1:5000/todos \
  -H 'Content-Type: application/json' \
  -d '{"title":"Buy milk"}'
```

응답은 `201 Created`와 함께 생성된 todo JSON을 반환합니다.