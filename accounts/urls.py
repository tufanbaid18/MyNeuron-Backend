from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    api_register, api_login, api_event_register,
    upload_profile_image, get_personal_detail,
    update_personal_detail, get_professional_detail,
    update_professional_detail, add_comment, get_education_details, add_education_detail,
    update_education_detail, delete_education_detail, get_speakers, get_speaker_by_id, get_past_experiences, add_past_experience,
    update_past_experience, delete_past_experience, get_public_users, get_public_user_by_id, search_public_users, me, generate_qr_from_url,
    get_scientific_interest, update_scientific_interest,
    UserViewSet, EventViewSet, MemberViewSet,ResearchNewsAPIView, OpenGraphMetaAPIView,
    ConversationViewSet, FolderViewSet, FolderItemViewSet, ProgramViewSet, MessageViewSet,
    HandshakeViewSet, NotificationViewSet, UserProfileViewSet, PostViewSet, CalendarEventViewSet
)




router = DefaultRouter()
router.register('users', UserViewSet)
router.register('events', EventViewSet)
router.register('members', MemberViewSet)
router.register('user-profile', UserProfileViewSet, basename='user-profile')
router.register('posts', PostViewSet, basename='post')
router.register("handshake", HandshakeViewSet, basename="handshake")
router.register("notifications", NotificationViewSet, basename='notifications')
router.register('programs', ProgramViewSet, basename='programs')
router.register('messages', MessageViewSet, basename='messages')
router.register("folders", FolderViewSet, basename="folders")
router.register("folder-items", FolderItemViewSet, basename="folder-items")
router.register("calendar-events", CalendarEventViewSet, basename="calender-events")



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
    path('api/profile/education/', get_education_details),
    path('api/profile/education/add/', add_education_detail),
    path('api/profile/education/<int:pk>/update/', update_education_detail),
    path('api/profile/education/<int:pk>/delete/', delete_education_detail),
    path("api/speakers/", get_speakers),
    path("api/speakers/<int:id>/", get_speaker_by_id, name="get_speaker_by_id"),
    path("api/conversations/", ConversationViewSet.as_view({"get": "list"})),

        # 🔥 ADD THESE — PAST EXPERIENCE 🔥
    path('api/profile/past-experience/', get_past_experiences),
    path('api/profile/past-experience/add/', add_past_experience),
    path('api/profile/past-experience/<int:pk>/update/', update_past_experience),
    path('api/profile/past-experience/<int:pk>/delete/', delete_past_experience),

    path("api/public/users/", get_public_users, name="public-users"),
    path("api/public/users/<int:id>/", get_public_user_by_id, name="public-user-by-id"),
    path("api/public/users/search/", search_public_users, name="public-user-search"),
    # urls.py
    path("api/news/", ResearchNewsAPIView.as_view()),
    path("api/og-meta/", OpenGraphMetaAPIView.as_view(), name="og-meta"),
    path("api/me", me),
    path("api/qr/", generate_qr_from_url),
    path(
        "api/profile/scientific-interest/",
        get_scientific_interest,
        name="get-scientific-interest"
    ),
    path(
        "api/profile/scientific-interest/update/",
        update_scientific_interest,
        name="update-scientific-interest"
    ),

]
