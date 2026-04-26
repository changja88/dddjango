from django.contrib import admin

from .models import Membership, Team


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1
    fields = ("user", "role", "is_active")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MembershipInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "team", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__username", "team__name")
