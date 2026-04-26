# 뷰 패턴: CBV vs FBV

## 선택 기준 [TSD] [DDoc]

| 상황 | 권장 | 이유 |
|------|------|------|
| 표준 CRUD | Generic CBV | ListView, DetailView 등이 보일러플레이트를 제거 |
| 폼 처리 | CBV (FormView, CreateView) | 폼 유효성 검증 흐름이 내장 |
| 복잡한 커스텀 로직 | FBV | 흐름이 명시적이고 디버깅이 쉬움 |
| 간단한 유틸리티 뷰 | FBV | 함수로 충분할 때 클래스화 불필요 |
| 코드 재사용 필요 | CBV + Mixin | 상속/합성으로 중복 제거 |

**원칙: 가능하면 Generic CBV로 시작, 필요하면 CBV로 내려가고, 정말 세밀한 제어가 필요할 때 FBV를 사용한다.** [TSD]

## CBV 올바른 사용 [DDoc]

```python
# 좋은 예: Generic CBV 활용
from django.views.generic import ListView, DetailView, CreateView

class ArticleListView(ListView):
    model = Article
    queryset = Article.objects.published().select_related("author")
    paginate_by = 20
    context_object_name = "articles"

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy("article-list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
```

## Mixin 활용 패턴 [TSD]

```python
# 좋은 예: 단일 책임 Mixin 조합
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class AuditMixin:
    """생성/수정 시 감사 로그를 기록하는 Mixin."""
    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            action=f"{self.model.__name__} saved",
            object_id=self.object.pk,
        )
        return response

class ArticleUpdateView(StaffRequiredMixin, AuditMixin, UpdateView):
    model = Article
    form_class = ArticleForm
```

- Mixin은 **왼쪽에서 오른쪽으로** MRO(Method Resolution Order)가 적용된다.
- 하나의 Mixin은 하나의 관심사만 담당한다.
- Mixin 체인이 3개 이상이면 복잡성을 재검토한다.

## FBV 올바른 사용 [DDoc]

```python
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET", "POST"])
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect("article-detail", pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, "articles/create.html", {"form": form})
```
