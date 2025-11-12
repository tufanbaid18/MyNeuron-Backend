from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, EventViewSet, MemberViewSet,
    api_register, api_login, api_event_register,
    upload_profile_image, get_personal_detail,
    update_personal_detail, get_professional_detail,
    update_professional_detail, add_comment,
)
from .views import PostViewSet
from .views import  UserProfileViewSet


router = DefaultRouter()
router.register('users', UserViewSet)
router.register('events', EventViewSet)
router.register('members', MemberViewSet)
router.register('user-profile', UserProfileViewSet, basename='user-profile')
router.register('posts', PostViewSet, basename='post')


app_name = 'accounts'

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', api_register),
    path('api/login/', api_login),
    path('api/event-register/', api_event_register),
    path('api/upload-profile-image/', upload_profile_image),
    path('api/profile/personal/', get_personal_detail),
    path('api/profile/personal/update/', update_personal_detail),
    path('api/profile/professional/', get_professional_detail),
    path('api/profile/professional/update/', update_professional_detail),
    path('api/posts/<int:post_id>/comment/', add_comment, name='add_comment'),
]


# urlpatterns = [
#     path('', views.home, name='home'),
#     path('register/', views.register_view, name='register'),
#     path('event-register/', views.event_register_view, name='event_register'),
#     path('api/', include(router.urls)),
#     path('api/register/', api_register, name='api_register'),
#     path('api/login/', api_login, name='api_login'),
#     path('api/event-register/', api_event_register, name='api_event_register'),
#     path('logout/', views.logout_view, name='logout_view'),
#     path('api/upload-profile-image/', upload_profile_image, name='upload-profile-image'),
#     path('api/profile/personal/', views.get_personal_detail, name='get_personal_detail'),
#     path('api/profile/personal/update/', views.update_personal_detail, name='update_personal_detail'),
#     path('api/profile/professional/', views.get_professional_detail, name='get_professional_detail'),
#     path('api/profile/professional/update/', views.update_professional_detail, name='update_professional_detail'),
