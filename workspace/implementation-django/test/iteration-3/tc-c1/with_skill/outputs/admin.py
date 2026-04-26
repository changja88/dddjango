from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "view_count", "created_at"]
    list_filter = ["category", "has_attachment", "created_at"]
    search_fields = ["title", "content", "author__username"]
    readonly_fields = ["view_count", "created_at", "updated_at"]
    raw_id_fields = ["author"]
