from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Post

User = get_user_model()


class PostAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="user2", password="testpass123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", password="testpass123"
        )
        self.post = Post.objects.create(
            title="테스트 게시글",
            content="테스트 내용입니다.",
            author=self.user,
            category=Post.Category.FREE,
        )

    # ── 목록 조회 ──

    def test_list_returns_limited_fields(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("post-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data[0]
        self.assertIn("title", result)
        self.assertIn("author", result)
        self.assertIn("category", result)
        self.assertIn("view_count", result)
        self.assertNotIn("content", result)

    # ── 상세 조회 + 조회수 ──

    def test_detail_returns_all_fields(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("post-detail", args=[self.post.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("content", response.data)
        self.assertIn("has_attachment", response.data)

    def test_view_count_increments_on_retrieve(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("post-detail", args=[self.post.pk])

        self.assertEqual(self.post.view_count, 0)
        self.client.get(url)
        self.post.refresh_from_db()
        self.assertEqual(self.post.view_count, 1)

        self.client.get(url)
        self.post.refresh_from_db()
        self.assertEqual(self.post.view_count, 2)

    # ── 생성 ──

    def test_create_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("post-list")
        data = {
            "title": "새 게시글",
            "content": "새 내용",
            "category": "free",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], str(self.user))

    def test_notice_creation_by_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("post-list")
        data = {
            "title": "공지사항",
            "content": "공지 내용",
            "category": "notice",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_notice_creation_by_admin_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("post-list")
        data = {
            "title": "공지사항",
            "content": "공지 내용",
            "category": "notice",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ── 수정 권한 ──

    def test_author_can_update_own_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("post-detail", args=[self.post.pk])
        response = self.client.patch(url, {"title": "수정된 제목"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "수정된 제목")

    def test_other_user_cannot_update_post(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("post-detail", args=[self.post.pk])
        response = self.client.patch(url, {"title": "해킹 시도"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_post(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("post-detail", args=[self.post.pk])
        response = self.client.patch(url, {"title": "관리자 수정"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ── 삭제 권한 ──

    def test_author_can_delete_own_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("post-detail", args=[self.post.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete_post(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("post-detail", args=[self.post.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_any_post(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("post-detail", args=[self.post.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # ── 비인증 사용자 ──

    def test_unauthenticated_user_cannot_access(self):
        url = reverse("post-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
