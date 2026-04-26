# Django Code Review: Product Model & View

## 1. Model Layer (`Product`)

### 1-1. `price` 필드에 `FloatField` 사용 -- 심각도: HIGH

```python
price = models.FloatField()
```

`FloatField`는 IEEE 754 부동소수점을 사용하므로 금액 계산 시 정밀도 손실이 발생한다. 예를 들어 `0.1 + 0.2 != 0.3` 같은 문제가 실제 결제/정산 로직에서 버그로 이어진다.

**권장 수정:**

```python
price = models.DecimalField(max_digits=10, decimal_places=2)
```

### 1-2. Boolean 플래그 3개 난립 -- 심각도: MEDIUM

```python
is_active = models.BooleanField(default=True)
is_featured = models.BooleanField(default=False)
is_on_sale = models.BooleanField(default=False)
```

Boolean 필드가 늘어날수록 상태 조합이 지수적으로 증가하고, 쿼리 조건도 복잡해진다. `is_active`는 소프트 딜리트 용도로 남기되, `is_featured`와 `is_on_sale`은 별도 관계 모델이나 태그 시스템으로 분리하는 것을 고려할 수 있다. 현재 3개 수준이면 당장 문제는 아니지만, 추가 확장 시 주의가 필요하다.

### 1-3. `on_delete=models.CASCADE` -- 심각도: LOW

```python
category = models.ForeignKey('Category', on_delete=models.CASCADE)
```

Category 삭제 시 해당 카테고리의 모든 Product가 연쇄 삭제된다. 비즈니스 요구에 따라 의도된 동작일 수 있으나, 일반적으로 상품 데이터를 보존해야 하는 경우가 많다. `PROTECT` 또는 `SET_NULL`(nullable 전환 필요)을 검토할 수 있다.

### 1-4. `ordering = ['-id']` -- 심각도: LOW

모든 쿼리에 기본 정렬이 적용되어 의도치 않은 성능 저하를 유발할 수 있다. 필요한 View에서만 명시적으로 `.order_by()`를 사용하는 편이 예측 가능하다.

---

## 2. View Layer (`ProductListView`)

### 2-1. N+1 쿼리 문제 -- 심각도: HIGH

```python
products = Product.objects.all()
for p in products:
    result.append({
        ...
        'category': p.category.name,  # 매 반복마다 DB 쿼리 발생
    })
```

`p.category.name` 접근 시 각 Product마다 Category를 별도 쿼리로 가져온다. Product가 1000개면 1001번의 쿼리가 실행된다.

**권장 수정:**

```python
products = Product.objects.select_related('category').all()
```

### 2-2. 페이지네이션 없음 -- 심각도: HIGH

```python
products = Product.objects.all()
```

전체 레코드를 한 번에 조회하므로, 데이터가 늘어나면 메모리 사용량과 응답 시간이 선형으로 증가한다. 운영 환경에서 OOM이나 타임아웃 장애로 직결될 수 있다.

**권장 수정:** Django의 `Paginator`를 사용하거나 DRF의 pagination 클래스를 적용한다.

### 2-3. 수동 직렬화 대신 Serializer 사용 권장 -- 심각도: MEDIUM

```python
result.append({
    'name': p.name,
    'category': p.category.name,
    'price': p.price,
})
```

수동 딕셔너리 구성은 필드 추가/변경 시 누락 위험이 있고, 입력 검증이나 역직렬화가 필요해지면 코드가 급격히 복잡해진다. Django REST Framework의 `ModelSerializer`나 최소한 `django.forms.model_to_dict`를 사용하면 유지보수성이 크게 개선된다.

### 2-4. `is_active` 필터 누락 -- 심각도: MEDIUM

```python
products = Product.objects.all()
```

`is_active=False`인 비활성 상품까지 모두 반환된다. `is_active` 필드를 정의해 놓고 조회 시 필터링하지 않으면 해당 필드의 존재 의미가 없다.

**권장 수정:**

```python
products = Product.objects.filter(is_active=True).select_related('category')
```

또는 커스텀 Manager를 정의하여 기본 QuerySet에서 비활성 상품을 제외한다.

### 2-5. FBV가 아닌 CBV 사용은 적절하나 DRF 미활용 -- 심각도: LOW

`View`를 직접 상속하여 `JsonResponse`를 반환하는 방식은 동작하지만, API를 구축한다면 DRF의 `ListAPIView`가 content negotiation, throttling, authentication 등을 기본 제공하므로 더 적합하다.

---

## 3. Signal Layer

### 3-1. Signal에서 무거운 작업 동기 실행 -- 심각도: HIGH

```python
@receiver(post_save, sender=Product)
def update_search_index(sender, instance, **kwargs):
    rebuild_search_index(instance)
```

`post_save` signal은 요청-응답 사이클 안에서 동기적으로 실행된다. `rebuild_search_index`가 외부 서비스 호출이나 무거운 연산이라면 다음 문제가 발생한다:

- 상품 저장 응답이 느려짐
- 인덱스 서비스 장애 시 상품 저장 자체가 실패할 수 있음
- Admin에서의 단순 수정도 영향을 받음

**권장 수정:** Celery 등 비동기 태스크 큐로 오프로드한다.

```python
@receiver(post_save, sender=Product)
def update_search_index(sender, instance, **kwargs):
    rebuild_search_index.delay(instance.pk)
```

### 3-2. `created` 플래그 미활용 -- 심각도: LOW

`post_save` signal의 `kwargs`에는 `created` 인자가 포함된다. 생성과 수정 시 인덱스 갱신 전략이 다를 수 있으므로(예: 생성 시에만 알림 발송), `created` 값을 확인하는 것이 좋다.

---

## 4. 요약

| 항목 | 심각도 | 핵심 |
|---|---|---|
| `FloatField`로 가격 저장 | HIGH | `DecimalField` 사용 |
| N+1 쿼리 | HIGH | `select_related` 적용 |
| 페이지네이션 미적용 | HIGH | `Paginator` 또는 DRF pagination |
| Signal 동기 실행 | HIGH | 비동기 태스크 큐 사용 |
| `is_active` 필터 누락 | MEDIUM | `.filter(is_active=True)` |
| 수동 직렬화 | MEDIUM | Serializer 도입 검토 |
| Boolean 플래그 확장성 | MEDIUM | 현재는 수용 가능, 확장 시 주의 |
| `CASCADE` 삭제 정책 | LOW | 비즈니스 요구에 맞는지 확인 |
| 기본 ordering | LOW | 명시적 order_by 권장 |
| `created` 플래그 미활용 | LOW | 생성/수정 분기 검토 |
