from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Category, Product, Seller


class ProductAPITestBase(TestCase):
    """Shared setup for product API tests."""

    def setUp(self):
        self.client = APIClient()

        self.category_electronics = Category.objects.create(
            name="Electronics", slug="electronics"
        )
        self.category_books = Category.objects.create(name="Books", slug="books")

        self.seller = Seller.objects.create(
            name="Test Seller",
            email="seller@example.com",
            phone="010-1234-5678",
            is_verified=True,
        )

        self.product1 = Product.objects.create(
            name="Laptop",
            price=Decimal("1500000.00"),
            category=self.category_electronics,
            stock=10,
            discount_rate=Decimal("10.00"),
            rating=Decimal("4.50"),
            seller=self.seller,
            description="A high-end laptop",
        )
        self.product2 = Product.objects.create(
            name="Python Book",
            price=Decimal("35000.00"),
            category=self.category_books,
            stock=50,
            discount_rate=Decimal("0.00"),
            rating=Decimal("4.80"),
            seller=self.seller,
            description="Learn Python programming",
        )
        self.inactive_product = Product.objects.create(
            name="Discontinued Item",
            price=Decimal("10000.00"),
            category=self.category_electronics,
            stock=0,
            seller=self.seller,
            is_active=False,
        )


class ProductV1ListTests(ProductAPITestBase):
    """Tests for GET /api/v1/products/"""

    def test_list_returns_active_products(self):
        response = self.client.get("/api/v1/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

    def test_list_excludes_inactive_products(self):
        response = self.client.get("/api/v1/products/")
        results = response.data["results"]
        product_names = [p["name"] for p in results]
        self.assertNotIn("Discontinued Item", product_names)

    def test_list_returns_only_v1_fields(self):
        response = self.client.get("/api/v1/products/")
        results = response.data["results"]
        first_product = results[0]
        expected_keys = {"id", "name", "price", "category_name"}
        self.assertEqual(set(first_product.keys()), expected_keys)

    def test_list_does_not_include_v2_fields(self):
        response = self.client.get("/api/v1/products/")
        results = response.data["results"]
        first_product = results[0]
        self.assertNotIn("stock", first_product)
        self.assertNotIn("discount_rate", first_product)
        self.assertNotIn("rating", first_product)
        self.assertNotIn("seller", first_product)


class ProductV1DetailTests(ProductAPITestBase):
    """Tests for GET /api/v1/products/<pk>/"""

    def test_detail_returns_product(self):
        response = self.client.get(f"/api/v1/products/{self.product1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Laptop")

    def test_detail_returns_only_v1_fields(self):
        response = self.client.get(f"/api/v1/products/{self.product1.pk}/")
        expected_keys = {"id", "name", "price", "category_name"}
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_detail_inactive_product_returns_404(self):
        response = self.client.get(f"/api/v1/products/{self.inactive_product.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_nonexistent_product_returns_404(self):
        response = self.client.get("/api/v1/products/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProductV2ListTests(ProductAPITestBase):
    """Tests for GET /api/v2/products/"""

    def test_list_returns_active_products(self):
        response = self.client.get("/api/v2/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

    def test_list_includes_v2_fields(self):
        response = self.client.get("/api/v2/products/")
        results = response.data["results"]
        first_product = results[0]
        self.assertIn("stock", first_product)
        self.assertIn("discount_rate", first_product)
        self.assertIn("discounted_price", first_product)
        self.assertIn("rating", first_product)
        self.assertIn("seller", first_product)

    def test_list_seller_info_structure(self):
        response = self.client.get("/api/v2/products/")
        results = response.data["results"]
        seller_data = results[0]["seller"]
        expected_keys = {"id", "name", "email", "phone", "is_verified"}
        self.assertEqual(set(seller_data.keys()), expected_keys)

    def test_filter_by_category(self):
        response = self.client.get("/api/v2/products/?category=electronics")
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Laptop")

    def test_filter_by_category_no_results(self):
        response = self.client.get("/api/v2/products/?category=nonexistent")
        results = response.data["results"]
        self.assertEqual(len(results), 0)

    def test_filter_by_min_price(self):
        response = self.client.get("/api/v2/products/?min_price=100000")
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Laptop")

    def test_filter_by_max_price(self):
        response = self.client.get("/api/v2/products/?max_price=50000")
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Python Book")

    def test_filter_by_price_range(self):
        response = self.client.get(
            "/api/v2/products/?min_price=10000&max_price=50000"
        )
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Python Book")

    def test_filter_invalid_price_ignored(self):
        response = self.client.get("/api/v2/products/?min_price=invalid")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

    def test_filter_negative_price_ignored(self):
        response = self.client.get("/api/v2/products/?min_price=-100")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

    def test_discounted_price_calculation(self):
        response = self.client.get("/api/v2/products/")
        results = response.data["results"]
        laptop = next(p for p in results if p["name"] == "Laptop")
        expected_discounted = Decimal("1500000.00") * Decimal("0.90")
        self.assertEqual(
            Decimal(str(laptop["discounted_price"])),
            expected_discounted,
        )


class ProductV2DetailTests(ProductAPITestBase):
    """Tests for GET /api/v2/products/<pk>/"""

    def test_detail_returns_product(self):
        response = self.client.get(f"/api/v2/products/{self.product1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Laptop")

    def test_detail_includes_v2_fields(self):
        response = self.client.get(f"/api/v2/products/{self.product1.pk}/")
        self.assertIn("stock", response.data)
        self.assertIn("discount_rate", response.data)
        self.assertIn("rating", response.data)
        self.assertIn("seller", response.data)
        self.assertIn("description", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_detail_inactive_product_returns_404(self):
        response = self.client.get(f"/api/v2/products/{self.inactive_product.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_nonexistent_product_returns_404(self):
        response = self.client.get("/api/v2/products/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
