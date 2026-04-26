from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.products.models import Category, Product, Review, Seller


class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Electronics", slug="electronics")
        cls.seller = Seller.objects.create(
            name="Test Seller", email="seller@example.com"
        )
        cls.product = Product.objects.create(
            name="Laptop",
            price=Decimal("1500.00"),
            discount_rate=Decimal("10.00"),
            stock=50,
            category=cls.category,
            seller=cls.seller,
        )

    def test_str(self):
        self.assertEqual(str(self.product), "Laptop")

    def test_discounted_price(self):
        self.assertEqual(self.product.discounted_price, Decimal("1350.00"))

    def test_discounted_price_no_discount(self):
        product = Product.objects.create(
            name="Mouse",
            price=Decimal("30.00"),
            category=self.category,
            seller=self.seller,
        )
        self.assertEqual(product.discounted_price, Decimal("30.00"))


class ProductV1APITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Books", slug="books")
        cls.seller = Seller.objects.create(
            name="Book Store", email="books@example.com"
        )
        cls.product = Product.objects.create(
            name="Django for Professionals",
            price=Decimal("45.00"),
            stock=100,
            category=cls.category,
            seller=cls.seller,
        )

    def test_list_returns_minimal_fields(self):
        response = self.client.get("/api/v1/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(set(result.keys()), {"id", "name", "price", "category_name"})

    def test_list_category_name(self):
        response = self.client.get("/api/v1/products/")
        result = response.data["results"][0]
        self.assertEqual(result["category_name"], "Books")

    def test_detail_returns_minimal_fields(self):
        response = self.client.get(f"/api/v1/products/{self.product.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()), {"id", "name", "price", "category_name"}
        )

    def test_list_excludes_inactive_products(self):
        Product.objects.create(
            name="Archived Book",
            price=Decimal("20.00"),
            status=Product.Status.ARCHIVED,
            category=self.category,
            seller=self.seller,
        )
        response = self.client.get("/api/v1/products/")
        names = [r["name"] for r in response.data["results"]]
        self.assertNotIn("Archived Book", names)

    def test_list_num_queries(self):
        with self.assertNumQueries(2):
            self.client.get("/api/v1/products/")


class ProductV2APITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category_electronics = Category.objects.create(
            name="Electronics", slug="electronics"
        )
        cls.category_books = Category.objects.create(name="Books", slug="books")
        cls.seller = Seller.objects.create(
            name="Tech Shop", email="tech@example.com", is_verified=True
        )
        cls.product = Product.objects.create(
            name="Laptop",
            price=Decimal("1500.00"),
            stock=30,
            discount_rate=Decimal("15.00"),
            category=cls.category_electronics,
            seller=cls.seller,
        )
        Review.objects.create(product=cls.product, rating=5)
        Review.objects.create(product=cls.product, rating=4)

    def test_list_returns_extended_fields(self):
        response = self.client.get("/api/v2/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        expected_fields = {
            "id",
            "name",
            "price",
            "category_name",
            "stock",
            "discount_rate",
            "avg_rating",
            "seller_name",
        }
        self.assertEqual(set(result.keys()), expected_fields)

    def test_list_avg_rating(self):
        response = self.client.get("/api/v2/products/")
        result = response.data["results"][0]
        self.assertEqual(result["avg_rating"], 4.5)

    def test_detail_returns_full_fields(self):
        response = self.client.get(f"/api/v2/products/{self.product.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("seller", response.data)
        self.assertIn("discounted_price", response.data)
        self.assertEqual(response.data["seller"]["name"], "Tech Shop")

    def test_detail_discounted_price(self):
        response = self.client.get(f"/api/v2/products/{self.product.pk}/")
        self.assertEqual(
            Decimal(response.data["discounted_price"]), Decimal("1275.00")
        )

    def test_filter_by_category(self):
        Product.objects.create(
            name="Python Book",
            price=Decimal("40.00"),
            category=self.category_books,
            seller=self.seller,
        )
        response = self.client.get("/api/v2/products/", {"category": "books"})
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Python Book")

    def test_filter_by_price_range(self):
        Product.objects.create(
            name="Cheap Item",
            price=Decimal("10.00"),
            category=self.category_electronics,
            seller=self.seller,
        )
        response = self.client.get(
            "/api/v2/products/", {"min_price": "100", "max_price": "2000"}
        )
        names = [r["name"] for r in response.data["results"]]
        self.assertIn("Laptop", names)
        self.assertNotIn("Cheap Item", names)

    def test_filter_combined_category_and_price(self):
        Product.objects.create(
            name="Expensive Book",
            price=Decimal("200.00"),
            category=self.category_books,
            seller=self.seller,
        )
        Product.objects.create(
            name="Cheap Book",
            price=Decimal("5.00"),
            category=self.category_books,
            seller=self.seller,
        )
        response = self.client.get(
            "/api/v2/products/",
            {"category": "books", "min_price": "50"},
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Expensive Book")

    def test_list_num_queries(self):
        with self.assertNumQueries(2):
            self.client.get("/api/v2/products/")
