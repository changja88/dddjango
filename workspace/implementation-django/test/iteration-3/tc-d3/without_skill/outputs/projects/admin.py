from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "team", "owner", "created_at")
    list_filter = ("team",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
