Django라면 보통 **각 app 내부에 `services.py` 또는 `services/` 패키지**를 두는 게 가장 무난합니다.

예시:

```text
orders/
  models.py
  views.py
  serializers.py
  services.py
```

또는 서비스가 커지면:

```text
orders/
  services/
    __init__.py
    checkout.py
    refund.py
    pricing.py
```

기준은 이렇게 잡으면 됩니다.

- 특정 도메인/app에만 관련된 로직: `app/services.py`
- 파일이 커지거나 기능별 분리가 필요함: `app/services/`
- 여러 app을 조율하는 유스케이스: 별도 `usecases/`, `application/`, 또는 상위 app의 `services/`
- Django 모델의 단순 불변식/짧은 동작: `model` 메서드나 custom manager/queryset에 둬도 됨
- view/serializer에서는 orchestration만 하고, 트랜잭션·외부 API·복잡한 상태 변경은 service로 빼는 게 좋음

개인적으로는 처음부터 전역 `services/` 디렉터리를 루트에 두기보다, **도메인 app 안에 두고 필요할 때만 상위 orchestration 계층을 추가**하는 쪽을 추천합니다. Django의 app 경계와 잘 맞고, 의존성도 덜 흐려집니다.