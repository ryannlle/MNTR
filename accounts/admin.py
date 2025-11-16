from django.contrib import admin
from .models import Profile, Mentor


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('user', 'approved', 'rating')
    list_filter = ('approved',)
    search_fields = ('user__username', 'subjects')
    actions = ['approve_mentors']

    def approve_mentors(self, request, queryset):
        queryset.update(approved=True)
    approve_mentors.short_description = 'Approve selected mentors'
