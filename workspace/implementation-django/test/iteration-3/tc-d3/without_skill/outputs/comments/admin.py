from django.contrib import admin

from .models import Comment, Mention


class MentionInline(admin.TabularInline):
    model = Mention
    extra = 0
    readonly_fields = ("user", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at")
    search_fields = ("body",)
    raw_id_fields = ("task", "author")
    inlines = [MentionInline]


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ("comment", "user", "created_at")
    raw_id_fields = ("comment", "user")
