# 테스트 코드 리뷰 및 리팩토링

## 1. 리뷰

### 잘 된 점

- `setup_method`로 Mock 객체를 테스트마다 초기화하여 격리성을 확보하고 있다.
- `send_welcome`에 대해 이메일만 보내는 경우, SMS 포함 경우, 사용자 미존재 경우를 각각 테스트한다.
- `send_bulk`에 대해 전체 성공, 부분 실패, 예외 발생 경로를 모두 커버한다.
- Mock의 `side_effect`를 활용해 순차적으로 다른 반환값을 제공하는 패턴이 적절하다.

### 개선이 필요한 점

#### (1) 테스트 데이터가 테스트 메서드마다 인라인으로 중복 정의됨

`{'name': 'Alice', 'email': 'a@t.com'}` 같은 사용자 딕셔너리가 여러 테스트에 걸쳐 반복된다. 하나의 fixture 또는 팩토리 함수로 추출하면 변경 시 한 곳만 수정하면 된다.

#### (2) Mock 호출 검증이 과도하게 구체적임 (over-specification)

`test_send_welcome_email_only`에서 `assert_called_once_with`로 모든 인자를 한 줄씩 검증한다. 이는 프로덕션 코드의 내부 구현 순서나 인자 형태가 조금만 바뀌어도 테스트가 깨지는 **취약한 테스트(fragile test)** 를 만든다. 반면 `test_send_welcome_with_sms`에서는 `assert_called_once()`만 사용해 일관성도 없다.

핵심 행위(어떤 채널로 보냈는가)를 검증하되, 내부 호출 순서까지 결합하지 않는 것이 좋다.

#### (3) 반환값 검증이 부분적임

`test_send_welcome_with_sms`에서 `'sms' in result['channels']`만 확인하고 `'email'`이 포함되는지, `status`가 `'sent'`인지 확인하지 않는다. 검증 수준이 테스트마다 들쭉날쭉하다.

#### (4) 에러 메시지 내용을 테스트에 하드코딩

`'사용자 2 없음'` 같은 문자열을 테스트에 직접 넣으면, 메시지 문구가 바뀔 때 테스트도 같이 수정해야 한다. 에러가 존재하는지 여부(길이)나 패턴 매칭이 더 안정적이다.

#### (5) `send_bulk`의 빈 리스트 입력 케이스가 없음

경계 조건(empty list)에 대한 테스트가 빠져 있다.

#### (6) pytest fixture를 활용하지 않음

`setup_method` 대신 `@pytest.fixture`를 사용하면 pytest 생태계와 더 잘 어울리고, fixture 간 조합과 스코프 관리가 유연해진다.

---

## 2. 리팩토링 코드

```python
import pytest
from unittest.mock import Mock, call


# ===== 프로덕션 코드 =====

class NotificationService:
    def __init__(self, user_repo, template_engine, email_client, sms_client):
        self.user_repo = user_repo
        self.template_engine = template_engine
        self.email_client = email_client
        self.sms_client = sms_client

    def send_welcome(self, user_id: int) -> dict:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f'사용자 {user_id}을 찾을 수 없습니다')
        html = self.template_engine.render('welcome', {'name': user['name']})
        self.email_client.send(user['email'], '환영합니다', html)
        if user.get('phone'):
            self.sms_client.send(user['phone'], f'{user["name"]}님, 가입을 환영합니다!')
        return {'status': 'sent', 'channels': ['email'] + (['sms'] if user.get('phone') else [])}

    def send_bulk(self, user_ids: list[int], template_name: str, context: dict) -> dict:
        results = {'sent': 0, 'failed': 0, 'errors': []}
        for uid in user_ids:
            try:
                user = self.user_repo.find_by_id(uid)
                if not user:
                    results['failed'] += 1
                    results['errors'].append(f'사용자 {uid} 없음')
                    continue
                html = self.template_engine.render(template_name, {**context, 'name': user['name']})
                self.email_client.send(user['email'], context.get('subject', '알림'), html)
                results['sent'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
        return results


# ===== 테스트 헬퍼 =====

def _make_user(name: str, email: str, phone: str | None = None) -> dict:
    """테스트용 사용자 딕셔너리를 생성하는 팩토리 함수."""
    user = {'name': name, 'email': email}
    if phone:
        user['phone'] = phone
    return user


# ===== Fixtures =====

@pytest.fixture()
def mock_deps():
    """모든 의존성 Mock을 한 번에 생성하여 dict로 반환한다."""
    return {
        'user_repo': Mock(),
        'template_engine': Mock(),
        'email_client': Mock(),
        'sms_client': Mock(),
    }


@pytest.fixture()
def service(mock_deps):
    return NotificationService(**mock_deps)


# ===== send_welcome 테스트 =====

class TestSendWelcome:
    """send_welcome 메서드의 행위를 검증한다."""

    def test_email_only_user_receives_email_and_no_sms(self, service, mock_deps):
        user = _make_user('Alice', 'alice@test.com')
        mock_deps['user_repo'].find_by_id.return_value = user
        mock_deps['template_engine'].render.return_value = '<h1>Welcome</h1>'

        result = service.send_welcome(1)

        # 핵심 행위: 이메일은 전송되고 SMS는 전송되지 않는다
        mock_deps['email_client'].send.assert_called_once()
        mock_deps['sms_client'].send.assert_not_called()

        # 반환값 전체 구조를 검증한다
        assert result == {'status': 'sent', 'channels': ['email']}

    def test_user_with_phone_receives_both_email_and_sms(self, service, mock_deps):
        user = _make_user('Bob', 'bob@test.com', phone='010-1234-5678')
        mock_deps['user_repo'].find_by_id.return_value = user
        mock_deps['template_engine'].render.return_value = '<h1>Welcome</h1>'

        result = service.send_welcome(2)

        mock_deps['email_client'].send.assert_called_once()
        mock_deps['sms_client'].send.assert_called_once()

        # SMS 수신 번호가 올바른지만 확인한다 (메시지 문구에 결합하지 않는다)
        actual_phone = mock_deps['sms_client'].send.call_args[0][0]
        assert actual_phone == '010-1234-5678'

        assert result == {'status': 'sent', 'channels': ['email', 'sms']}

    def test_nonexistent_user_raises_value_error(self, service, mock_deps):
        mock_deps['user_repo'].find_by_id.return_value = None

        with pytest.raises(ValueError, match='사용자 999'):
            service.send_welcome(999)

        # 사용자가 없으면 이메일/SMS 모두 전송하지 않는다
        mock_deps['email_client'].send.assert_not_called()
        mock_deps['sms_client'].send.assert_not_called()


# ===== send_bulk 테스트 =====

class TestSendBulk:
    """send_bulk 메서드의 행위를 검증한다."""

    def test_all_users_receive_email_successfully(self, service, mock_deps):
        mock_deps['user_repo'].find_by_id.side_effect = [
            _make_user('Alice', 'a@t.com'),
            _make_user('Bob', 'b@t.com'),
        ]
        mock_deps['template_engine'].render.return_value = '<p>promo</p>'

        result = service.send_bulk([1, 2], 'promo', {'subject': '세일'})

        assert result['sent'] == 2
        assert result['failed'] == 0
        assert result['errors'] == []
        assert mock_deps['email_client'].send.call_count == 2

    def test_missing_user_is_counted_as_failure(self, service, mock_deps):
        mock_deps['user_repo'].find_by_id.side_effect = [
            _make_user('Alice', 'a@t.com'),
            None,
            _make_user('Charlie', 'c@t.com'),
        ]
        mock_deps['template_engine'].render.return_value = '<p>hi</p>'

        result = service.send_bulk([1, 2, 3], 'info', {'subject': '공지'})

        assert result['sent'] == 2
        assert result['failed'] == 1
        assert len(result['errors']) == 1

    def test_email_client_exception_is_counted_as_failure(self, service, mock_deps):
        mock_deps['user_repo'].find_by_id.return_value = _make_user('Alice', 'a@t.com')
        mock_deps['template_engine'].render.return_value = '<p>hi</p>'
        mock_deps['email_client'].send.side_effect = ConnectionError('SMTP 연결 실패')

        result = service.send_bulk([1], 'alert', {'subject': '긴급'})

        assert result['sent'] == 0
        assert result['failed'] == 1
        assert len(result['errors']) == 1

    def test_empty_user_list_returns_zero_counts(self, service, mock_deps):
        """경계 조건: 빈 리스트를 전달하면 아무 작업도 하지 않는다."""
        result = service.send_bulk([], 'promo', {'subject': '세일'})

        assert result == {'sent': 0, 'failed': 0, 'errors': []}
        mock_deps['user_repo'].find_by_id.assert_not_called()
        mock_deps['email_client'].send.assert_not_called()

    def test_missing_subject_falls_back_to_default(self, service, mock_deps):
        """context에 subject가 없으면 기본값 '알림'이 사용된다."""
        mock_deps['user_repo'].find_by_id.return_value = _make_user('Alice', 'a@t.com')
        mock_deps['template_engine'].render.return_value = '<p>hi</p>'

        service.send_bulk([1], 'notice', {})

        actual_subject = mock_deps['email_client'].send.call_args[0][1]
        assert actual_subject == '알림'
```

---

## 3. 변경 사항 요약

| 항목 | 원본 | 리팩토링 후 |
|---|---|---|
| **테스트 데이터** | 딕셔너리 리터럴 인라인 반복 | `_make_user` 팩토리 함수로 통일 |
| **Mock 생성** | `setup_method` + `self` 참조 | `@pytest.fixture`로 주입, 클래스 인스턴스 상태에 의존하지 않음 |
| **Mock 검증 수준** | `assert_called_once_with`로 모든 인자를 검증하거나, 반대로 `assert_called_once()`만 사용하는 등 불일관 | 핵심 행위(호출 여부, 횟수)를 `assert_called_once` / `assert_not_called`로 통일. 특정 인자가 중요한 경우만 `call_args`로 개별 확인 |
| **반환값 검증** | 일부 필드만 부분 검증 | 전체 dict를 `==`로 비교하여 누락 없이 검증 |
| **에러 메시지 검증** | 정확한 문자열 일치 | `len(result['errors'])`로 존재 여부만 확인하여 메시지 변경에 강건함 |
| **예외 검증** | `pytest.raises(ValueError)`만 사용 | `match` 파라미터로 핵심 정보(사용자 ID) 포함 여부도 확인 + 후속 호출이 없었음을 검증 |
| **테스트 클래스 구조** | 단일 클래스에 모든 테스트 | `TestSendWelcome` / `TestSendBulk`로 분리하여 메서드별 관심사 격리 |
| **경계 조건** | 없음 | 빈 리스트, 기본 subject 폴백 테스트 추가 |
| **테스트 이름** | `test_send_bulk_partial_failure` 등 약식 | `test_missing_user_is_counted_as_failure` 등 행위를 서술하는 이름 |
