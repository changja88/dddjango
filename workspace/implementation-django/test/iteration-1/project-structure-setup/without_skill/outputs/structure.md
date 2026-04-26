# Online Bookstore - Django Project Structure

## Project Name: `bookstore`

```
bookstore/
├── manage.py
├── requirements.txt
├── bookstore/                  # 프로젝트 설정 패키지
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                   # 사용자(User) 앱
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # 커스텀 User 모델
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── test_views.py
│   └── migrations/
│       └── __init__.py
├── books/                      # 도서(Book) + 리뷰(Review) 앱
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Book, Review 모델
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── test_views.py
│   └── migrations/
│       └── __init__.py
└── orders/                     # 주문(Order) 앱
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py               # Order, OrderItem 모델
    ├── views.py
    ├── urls.py
    ├── serializers.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_models.py
    │   └── test_views.py
    └── migrations/
        └── __init__.py
```

## App Responsibilities

### `accounts` (사용자 관리)
- 커스텀 User 모델 (AbstractUser 확장)
- 회원가입, 로그인, 프로필 관리

### `books` (도서 + 리뷰)
- Book 모델: 제목, 저자, 가격, ISBN, 출판일, 카테고리
- Review 모델: 별점(1-5), 내용, 작성자(FK -> User), 도서(FK -> Book)
- Review는 Book과 강하게 결합되므로 같은 앱에 배치

### `orders` (주문)
- Order 모델: 주문자, 주문일, 상태, 총액
- OrderItem 모델: 주문 내 개별 도서 항목

## Design Decisions

1. **커스텀 User 모델**: Django 공식 권장에 따라 프로젝트 초기부터 AbstractUser를 확장한다. 나중에 변경하면 마이그레이션이 매우 복잡해진다.
2. **Review를 books 앱에 배치**: Review는 Book 없이 존재할 수 없고, 도서 상세 페이지에서 함께 표시되므로 같은 bounded context에 둔다.
3. **OrderItem 분리**: 하나의 주문에 여러 도서가 포함될 수 있으므로 Order와 OrderItem을 분리한다.
4. **AUTH_USER_MODEL 설정**: settings.py에서 `AUTH_USER_MODEL = 'accounts.User'`로 지정하여 모든 FK가 커스텀 모델을 참조하게 한다.
