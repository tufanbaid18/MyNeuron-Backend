from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Event, Member,  Post, PostMedia, Like, Bookmark, Comment, HandshakeRequest, Program
from .models import PersonalDetail, Education, ProfessionalDetail, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_verified', 'is_verified_lite')
    ordering = ('email',)
    search_fields = ('email', 'first_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name',
                'middle_name',
                'last_name',
                'profile_image',
                'profile_title',
            )
        }),
        ('Role info', {'fields': ('role','is_verified', 'is_verified_lite')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )

admin.site.register(Event)
admin.site.register(Member)
admin.site.register(PersonalDetail)
admin.site.register(Education)
admin.site.register(ProfessionalDetail)
admin.site.register(Post)
admin.site.register(PostMedia)
admin.site.register(Notification)
admin.site.register(Like)
admin.site.register(HandshakeRequest)
admin.site.register(Comment)
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "speaker", "venue", "topic", "date", "start_time", "end_time")
    list_filter = ("event", "date")
    search_fields = ("topic", "speaker__email", "event__name")
