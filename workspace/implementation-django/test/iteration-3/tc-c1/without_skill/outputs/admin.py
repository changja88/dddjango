from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "view_count", "created_at"]
    list_filter = ["category"]
    search_fields = ["title", "content"]
    readonly_fields = ["view_count"]
