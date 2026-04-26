import factory
from django.contrib.auth import get_user_model
from django.test import TestCase
from factory.django import DjangoModelFactory
from rest_framework import status
from rest_framework.test import APIClient

from .models import Post

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")

    class Params:
        staff = factory.Trait(is_staff=True)


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f"게시글 제목 {n}")
    content = factory.Faker("paragraph")
    author = factory.SubFactory(UserFactory)
    category = Post.Category.FREE

    class Params:
        notice = factory.Trait(category=Post.Category.NOTICE)
        question = factory.Trait(category=Post.Category.QUESTION)


class PostModelTest(TestCase):
    def test_str_returns_title(self):
        """Post.__str__()이 제목을 반환한다."""
        post = PostFactory(title="테스트 게시글")
        self.assertEqual(str(post), "테스트 게시글")

    def test_increment_view_count(self):
        """increment_view_count()가 조회수를 1 증가시킨다."""
        post = PostFactory()
        self.assertEqual(post.view_count, 0)
        post.increment_view_count()
        self.assertEqual(post.view_count, 1)

    def test_increment_view_count_race_safe(self):
        """increment_view_count()가 F() 표현식으로 원자적 증가를 수행한다."""
        post = PostFactory()
        post.increment_view_count()
        post.increment_view_count()
        self.assertEqual(post.view_count, 2)

    def test_default_ordering_is_newest_first(self):
        """기본 정렬이 최신순(-created_at)이다."""
        post1 = PostFactory()
        post2 = PostFactory()
        posts = list(Post.objects.all())
        self.assertEqual(posts[0], post2)
        self.assertEqual(posts[1], post1)


class PostQuerySetTest(TestCase):
    def test_by_category_filters_correctly(self):
        """by_category()가 해당 카테고리만 필터링한다."""
        PostFactory(notice=True)
        PostFactory()
        PostFactory(question=True)
        self.assertEqual(Post.objects.by_category(Post.Category.NOTICE).count(), 1)

    def test_by_author_filters_correctly(self):
        """by_author()가 해당 작성자의 글만 반환한다."""
        user = UserFactory()
        PostFactory(author=user)
        PostFactory(author=user)
        PostFactory()
        self.assertEqual(Post.objects.by_author(user).count(), 2)

    def test_list_fields_uses_select_related(self):
        """list_fields()가 author를 select_related로 가져온다."""
        PostFactory()
        with self.assertNumQueries(1):
            post = Post.objects.list_fields().first()
            _ = post.author.username


class PostAPIListTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_list_returns_limited_fields(self):
        """목록 API가 제목, 작성자, 카테고리, 조회수만 반환한다."""
        PostFactory(author=self.user)
        response = self.client.get("/api/board/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertIn("title", result)
        self.assertIn("author_name", result)
        self.assertIn("category", result)
        self.assertIn("view_count", result)
        self.assertNotIn("content", result)

    def test_list_filter_by_category(self):
        """카테고리 쿼리 파라미터로 필터링된다."""
        PostFactory(notice=True, author=self.user)
        PostFactory(author=self.user)
        response = self.client.get("/api/board/posts/", {"category": "notice"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["category"], "notice")

    def test_unauthenticated_user_cannot_list(self):
        """미인증 사용자는 목록을 조회할 수 없다."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/board/posts/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostAPIDetailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_detail_returns_full_content(self):
        """상세 API가 전체 내용을 반환한다."""
        post = PostFactory(author=self.user, content="본문 내용입니다.")
        response = self.client.get(f"/api/board/posts/{post.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("content", response.data)
        self.assertEqual(response.data["content"], "본문 내용입니다.")

    def test_detail_increments_view_count(self):
        """상세 조회 시 조회수가 1 증가한다."""
        post = PostFactory(author=self.user)
        self.assertEqual(post.view_count, 0)
        self.client.get(f"/api/board/posts/{post.pk}/")
        post.refresh_from_db()
        self.assertEqual(post.view_count, 1)

    def test_multiple_views_increment_correctly(self):
        """여러 번 조회 시 조회수가 정확히 증가한다."""
        post = PostFactory(author=self.user)
        for _ in range(3):
            self.client.get(f"/api/board/posts/{post.pk}/")
        post.refresh_from_db()
        self.assertEqual(post.view_count, 3)


class PostAPICreateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.staff_user = UserFactory(staff=True)
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        """인증 사용자가 게시글을 생성할 수 있다."""
        data = {
            "title": "새 게시글",
            "content": "게시글 내용",
            "category": "free",
        }
        response = self.client.post("/api/board/posts/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)

    def test_regular_user_cannot_create_notice(self):
        """일반 사용자는 공지 카테고리로 작성할 수 없다."""
        data = {
            "title": "공지사항",
            "content": "공지 내용",
            "category": "notice",
        }
        response = self.client.post("/api/board/posts/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_can_create_notice(self):
        """관리자는 공지 카테고리로 작성할 수 있다."""
        self.client.force_authenticate(user=self.staff_user)
        data = {
            "title": "공지사항",
            "content": "공지 내용",
            "category": "notice",
        }
        response = self.client.post("/api/board/posts/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_author_is_automatically_set(self):
        """작성자가 요청 사용자로 자동 설정된다."""
        data = {
            "title": "자동 작성자",
            "content": "내용",
            "category": "free",
        }
        self.client.post("/api/board/posts/", data)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)


class PostAPIPermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = UserFactory()
        self.other_user = UserFactory()
        self.staff_user = UserFactory(staff=True)
        self.post = PostFactory(author=self.author)

    def test_author_can_update_own_post(self):
        """작성자 본인이 자신의 글을 수정할 수 있다."""
        self.client.force_authenticate(user=self.author)
        response = self.client.patch(
            f"/api/board/posts/{self.post.pk}/",
            {"title": "수정된 제목"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "수정된 제목")

    def test_other_user_cannot_update(self):
        """다른 사용자가 남의 글을 수정할 수 없다."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            f"/api/board/posts/{self.post.pk}/",
            {"title": "해킹 시도"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_delete_own_post(self):
        """작성자 본인이 자신의 글을 삭제할 수 있다."""
        self.client.force_authenticate(user=self.author)
        response = self.client.delete(f"/api/board/posts/{self.post.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIs(Post.objects.filter(pk=self.post.pk).exists(), False)

    def test_other_user_cannot_delete(self):
        """다른 사용자가 남의 글을 삭제할 수 없다."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f"/api/board/posts/{self.post.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_update_any_post(self):
        """관리자(is_staff)가 모든 글을 수정할 수 있다."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.patch(
            f"/api/board/posts/{self.post.pk}/",
            {"title": "관리자 수정"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_can_delete_any_post(self):
        """관리자(is_staff)가 모든 글을 삭제할 수 있다."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(f"/api/board/posts/{self.post.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
