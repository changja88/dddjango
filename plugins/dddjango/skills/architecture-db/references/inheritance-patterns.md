# 상속과 다형성 패턴 레퍼런스

객체지향의 상속 관계를 RDB에 매핑하는 3가지 패턴과 다형적 연관.

---

## 상속 패턴 비교

| 패턴 | 설명 | 적합 | 트레이드오프 |
|------|------|------|------------|
| **Single Table (STI)** | 모든 타입 한 테이블 + type 구분자 | 속성 80%+ 공유 | NULL 많음, 테이블 비대 |
| **Class Table (CTI)** | 계층별 테이블, 공유 PK로 조인 | 속성이 크게 다름, 무결성 중요 | JOIN 필요 |
| **Concrete Table (TPC)** | 구체 타입별 독립 테이블 | 타입이 완전 독립 | FK 제약 불가, 스키마 중복 |

---

## Single Table Inheritance (STI)

```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY,
    type VARCHAR(20) NOT NULL,  -- 'car', 'truck', 'motorcycle'
    brand VARCHAR(100),
    -- 공통 속성
    engine_cc INTEGER,
    -- car 전용
    trunk_capacity_liters INTEGER,
    -- truck 전용
    payload_tons DECIMAL,
    -- motorcycle 전용
    has_sidecar BOOLEAN
);
```

---

## Class Table Inheritance (CTI)

```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    brand VARCHAR(100),
    engine_cc INTEGER
);

CREATE TABLE cars (
    vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(id),
    trunk_capacity_liters INTEGER
);

CREATE TABLE trucks (
    vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(id),
    payload_tons DECIMAL
);
```

---

## 다형적 연관 (Polymorphic Associations)

하나의 자식 엔티티가 여러 부모 타입과 관계를 맺는 패턴.

```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    body TEXT,
    commentable_type VARCHAR(50),  -- 'Article', 'Video', 'Photo'
    commentable_id INTEGER         -- 해당 타입의 PK
);
```

**한계**: DB 레벨에서 FK 제약을 강제할 수 없다. 참조 무결성은 애플리케이션 레벨에서 보장해야 한다.

---

## 선택 가이드

| 상황 | 권장 패턴 |
|------|----------|
| 타입 간 속성 대부분 공유 | STI (단순, JOIN 없음) |
| 타입별 속성이 크게 다름, 데이터 무결성 중요 | CTI (정규화, FK 제약) |
| 타입이 완전 독립, 접근 패턴 다름 | TPC (성능 우선) |
| 여러 부모 타입에 댓글/태그 연결 | Polymorphic Association |
