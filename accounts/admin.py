from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Event, Member,  Post, PostMedia, Like, Bookmark, Comment, HandshakeRequest, Program
from .models import PersonalDetail, Education, ProfessionalDetail


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    ordering = ('email',)
    search_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'profile_image')}),
        ('Role info', {'fields': ('role',)}),
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
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Bookmark)
admin.site.register(HandshakeRequest)

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "speaker", "venue", "topic", "date", "start_time", "end_time")
    list_filter = ("event", "date")
    search_fields = ("topic", "speaker__email", "event__name")
