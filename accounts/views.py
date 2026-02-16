from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .serializers import FollowRequestSerializer, FollowUserListSerializer, UserSerializer, EventSerializer, MemberSerializer, UserProfileSerializer, PersonalDetailSerializer, PersonalDetailSerializer, ProfessionalDetailSerializer, EducationSerializer, PastExperienceSerializer, PublicUserProfileSerializer, ProfessionalDetailSerializer, NotificationSerializer, CalendarEventSerializer, ScientificInterestSerializer, FolderItemSerializer, FolderTreeSerializer, FolderCreateSerializer, MessageSerializer, ProgramSerializer, UserMiniSerializer, HandshakeSerializer, CommentSerializer, EducationSerializer, PostSerializer, ArticleSerializer, ArticleReferenceSerializer 
from .models import FollowRequest, Event, Member, User, PersonalDetail, ProfessionalDetail, Education, PastExperience, ScientificInterest, Like, Bookmark, Comment, CalendarEvent, Program, Notification, HandshakeRequest, Folder, FolderItem, Message, Post, PostMedia, EmailVerificationToken, Article, ArticleReference
from .forms import RegisterForm
from .models import ArticleRating
from .serializers import ArticleRatingSerializer
from django.http import JsonResponse
from django.core.files.base import ContentFile
import base64, uuid
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django.core.mail import send_mail
from datetime import timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend


# # Web registration
# def register_view(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Registration successful! Please log in.')
#             return redirect('login')
#     else:
#         form = RegisterForm()
#     return render(request, 'accounts/register.html', {'form': form})

# # Home page
# @login_required
# def home(request):
#     return render(request, 'accounts/home.html', {'user': request.user})

# # Event registration (web)
# @login_required
# def event_register_view(request):

#     events = Event.objects.all()
#     if request.method == 'POST':
#         event_id = request.POST.get('event')
#         role = request.POST.get('role')
#         try:
#             event = Event.objects.get(id=event_id)
#         except Event.DoesNotExist:
#             messages.error(request, 'Selected event does not exist')
#             return redirect('accounts:event_register')
#         # prevent duplicates
#         if Member.objects.filter(user=request.user, event=event, role=role).exists():
#             messages.warning(request, 'You are already registered for this event with the same role')
#         else:
#             Member.objects.create(user=request.user, event=event, role=role)
#             messages.success(request, 'Successfully registered for the event')
#         return redirect('accounts:home')
#     return render(request, 'accounts/event_register.html', {'events': events})

# def logout_view(request):
#     logout(request)
#     return redirect('registration:login')


# API views and viewsets
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]





class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.select_related('user','event').all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]




def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def api_register(request):
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid():
#         user = serializer.save()

#         # 🔐 Create email verification token
#         email_token = EmailVerificationToken.objects.create(user=user)

#         verify_url = f"{settings.FRONTEND_URL}/verify-email?token={email_token.token}"

#         html_message = f"""
# <!DOCTYPE html>
# <html>
# <head>
#   <meta charset="UTF-8" />
#   <title>Verify Your Email</title>
#   <style>
#     body {{
#       margin: 0;
#       padding: 0;
#       background-color: #f4f6f8;
#       font-family: Arial, Helvetica, sans-serif;
#     }}
#     .container {{
#       max-width: 600px;
#       margin: 40px auto;
#       background: #ffffff;
#       border-radius: 8px;
#       overflow: hidden;
#       box-shadow: 0 2px 10px rgba(0,0,0,0.08);
#     }}
#     .header {{
#       background: #1e88e5;
#       color: #ffffff;
#       padding: 20px;
#       text-align: center;
#     }}
#     .content {{
#       padding: 30px;
#       color: #333333;
#       line-height: 1.6;
#     }}
#     .button {{
#       display: inline-block;
#       margin: 30px 0;
#       padding: 14px 28px;
#       background: #1e88e5;
#       color: #ffffff !important;
#       text-decoration: none;
#       border-radius: 6px;
#       font-size: 16px;
#       font-weight: bold;
#     }}
#     .footer {{
#       background: #f0f2f5;
#       text-align: center;
#       padding: 15px;
#       font-size: 12px;
#       color: #777777;
#     }}
#   </style>
# </head>
# <body>
#   <div class="container">
#     <div class="header">
#       <h1>Welcome to MyNeuron</h1>
#     </div>

#     <div class="content">
#       <p>Hi <strong>{user.first_name}</strong>,</p>

#       <p>
#         Thank you for registering with <strong>MyNeuron</strong>.
#         Please confirm your email address to activate your account.
#       </p>

#       <p style="text-align:center;">
#         <a href="{verify_url}" class="button">Verify Email</a>
#       </p>

#       <p>
#         If the button above does not work, copy and paste the following link into your browser:
#       </p>

#       <p style="word-break: break-all;">
#         <a href="{verify_url}">{verify_url}</a>
#       </p>

#       <p>
#         This verification link will expire in <strong>24 hours</strong>.
#       </p>

#       <p>
#         If you did not create this account, you can safely ignore this email.
#       </p>

#       <p>
#         Regards,<br />
#         <strong>MyNeuron Team</strong>
#       </p>
#     </div>

#     <div class="footer">
#       © {now().year} MyNeuron. All rights reserved.
#     </div>
#   </div>
# </body>
# </html>
# """

#         # 📧 Send verification email
#         send_mail(
#             subject="Verify your email – MyNeuron",
#             message=f"Verify your email: {verify_url}",  # fallback (plain text)
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#             html_message=html_message,   # 👈 IMPORTANT
#             fail_silently=False,
#         )

#         return Response(
#             {
#                 "message": "Registration successful. Please check your email to verify your account."
#             },
#             status=201
#         )

#     return Response(serializer.errors, status=400)

def verification_email_html(user, verify_url):
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Verify Your Email</title>
</head>
<body style="background:#f4f6f8;font-family:Arial;padding:20px;">
  <div style="max-width:600px;margin:auto;background:#fff;border-radius:8px;overflow:hidden;">
    <div style="background:#1e88e5;color:#fff;padding:20px;text-align:center;">
      <h1>Welcome to MyNeuron</h1>
    </div>

    <div style="padding:30px;color:#333;">
      <p>Hi <strong>{user.first_name}</strong>,</p>

      <p>Please confirm your email address to activate your account.</p>

      <p style="text-align:center;">
        <a href="{verify_url}"
           style="background:#1e88e5;color:#fff;padding:14px 28px;
                  text-decoration:none;border-radius:6px;font-weight:bold;">
          Verify Email
        </a>
      </p>

      <p>If the button doesn’t work, copy this link:</p>
      <p style="word-break:break-all;">
        <a href="{verify_url}">{verify_url}</a>
      </p>

      <p>This link expires in <strong>24 hours</strong>.</p>

      <p>– MyNeuron Team</p>
    </div>

    <div style="background:#f0f2f5;text-align:center;padding:12px;font-size:12px;">
      © {now().year} MyNeuron
    </div>
  </div>
</body>
</html>
"""





@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    email = request.data.get("email")

     # ✅ ADD THIS BLOCK
    if not email:
        return Response(
            {"email": ["Email is required"]},
            status=400
        )

    # 🔍 Check if user already exists
    existing_user = User.objects.filter(email=email).first()

    if existing_user:
        # 🟡 User exists but email NOT verified → resend email
        if not existing_user.is_email_verified:
            # ⏱ Rate limit
            last_token = EmailVerificationToken.objects.filter(
                user=existing_user,
                created_at__gte=now() - timedelta(minutes=1)
            ).first()

            if last_token:
                return Response(
                    {"detail": "Please wait 1 minute before requesting another email."},
                    status=429
                )
            EmailVerificationToken.objects.filter(user=existing_user).delete()

            token = EmailVerificationToken.objects.create(user=existing_user)
            verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token.token}"

            send_mail(
                subject="Verify your email – MyNeuron",
                message=f"Verify your email: {verify_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[existing_user.email],
                html_message=verification_email_html(existing_user, verify_url),
            )

            return Response(
                {
                    "detail": "Account already exists but is not verified. Verification email resent.",
                    "resend": True,
                },
                status=200,
            )

        # 🔴 User exists AND verified → block
        return Response(
            {"email": ["User with this email already exists. Please log in."]},
            status=400,
        )

    # 🆕 Fresh registration
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    token = EmailVerificationToken.objects.create(user=user)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token.token}"

    send_mail(
        subject="Verify your email – MyNeuron",
        message=f"Verify your email: {verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=verification_email_html(user, verify_url),
    )

    return Response(
        {
            "detail": "Registration successful. Verification email sent.",
            "resend": False,
        },
        status=201,
    )




@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'detail': 'Email and password are required'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=404)

    if not user.check_password(password):
        return Response({'detail': 'Invalid credentials'}, status=400)

    # 🚫 BLOCK UNVERIFIED EMAILS
    if not user.is_email_verified:
        return Response(
            {'detail': 'Please verify your email before logging in.'},
            status=403
        )
    
    tokens = get_tokens_for_user(user)

    return Response({
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_image': user.profile_image.url if user.profile_image else None,
            'role': user.role,
            'is_verified': user.is_verified,
            'is_email_verified': user.is_email_verified
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    token = request.data.get("token")

    if not token:
        return Response({"detail": "Token is required"}, status=400)

    try:
        record = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        return Response({"detail": "Invalid or expired token"}, status=400)

    # ⏳ Check expiry AFTER fetching record
    if record.is_expired():
        record.delete()
        return Response({"detail": "Token expired"}, status=400)

    user = record.user
    user.is_email_verified = True
    user.save()

    record.delete()  # one-time use

    return Response(
        {"message": "Email verified successfully. You can now log in."},
        status=200
    )



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

from .models import User, EmailVerificationToken


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_verification_email(request):
    email = request.data.get("email")

    if not email:
        return Response({"detail": "Email is required"}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    if user.is_email_verified:
        return Response(
            {"detail": "Email is already verified"},
            status=400
        )

    # 🔥 Delete old tokens
    EmailVerificationToken.objects.filter(user=user).delete()

    # 🔐 Create new token
    token = EmailVerificationToken.objects.create(user=user)

    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token.token}"

    html_message = f"""
    <html>
      <body style="font-family: Arial; background:#f4f6f8; padding:20px;">
        <div style="max-width:600px; margin:auto; background:#fff; padding:30px; border-radius:8px;">
          <h2 style="color:#1e88e5;">Verify your email</h2>
          <p>Hi {user.first_name},</p>
          <p>Please click the button below to verify your email:</p>
          <p style="text-align:center;">
            <a href="{verify_url}"
               style="background:#1e88e5;color:#fff;padding:12px 24px;
                      text-decoration:none;border-radius:6px;">
              Verify Email
            </a>
          </p>

<p>If the button doesn’t work, copy this link:</p>
      <p style="word-break:break-all;">
        <a href="{verify_url}">{verify_url}</a>
      </p>

          <p>This link will expire in <b>24 hours</b>.</p>
          
          <p>– MyNeuron Team</p>
        </div>
      </body>
    </html>
    """

    send_mail(
        subject="Verify your email – MyNeuron",
        message=f"Verify your email: {verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )

    return Response(
        {"message": "Verification email sent successfully"},
        status=200
    )



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}
    


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = UserSerializer(
        request.user,
        context={"request": request}
    )
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([AllowAny])
def api_event_register(request):
    
    email = request.data.get('email')
    event_id = request.data.get('event_id')
    role = request.data.get('role')
    if not email or not event_id or not role:
        return Response({'detail':'email, event_id and role required'}, status=400)
    user = User.objects.filter(email=email).first()
    if not user:
        user_data = {
            'email': email,
            'first_name': request.data.get('first_name',''),
            'last_name': request.data.get('last_name',''),
        }
        password = request.data.get('password')
        if password:
            from .validators import validate_password_complexity
            try:
                validate_password_complexity(password)
            except Exception as e:
                return Response({'password': str(e)}, status=400)
            user = User(**user_data)
            user.set_password(password)
            user.save()
        else:
            user = User.objects.create(email=email, first_name=user_data['first_name'], last_name=user_data['last_name'])
            user.set_unusable_password()
            user.save()
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return Response({'detail':'Event not found'}, status=404)
    if Member.objects.filter(user=user, event=event, role=role).exists():
        return Response({'detail':'Already registered'}, status=400)
    member = Member.objects.create(user=user, event=event, role=role)
    return Response({'member_id': member.id}, status=201)



# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def upload_profile_image(request):
#     user = request.user
#     image_data = request.data.get('profile_image')

#     if not image_data:
#         return Response({'error': 'No image provided'}, status=400)

#     try:
#         # Decode base64 string and save
#         format, imgstr = image_data.split(';base64,')
#         ext = format.split('/')[-1]
#         file_name = f"{uuid.uuid4()}.{ext}"
#         user.profile_image.save(file_name, ContentFile(base64.b64decode(imgstr)), save=True)

#         return Response({
#             'message': 'Profile image uploaded successfully',
#             'profile_image': user.profile_image.url
#         }, status=200)

#     except Exception as e:
#         return Response({'error': str(e)}, status=500)
    


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
import base64, uuid

import uuid
import base64
from django.core.files.base import ContentFile

import uuid
import base64
from django.core.files.base import ContentFile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_image(request):
    user = request.user
    image_file = request.FILES.get('profile_image')
    image_base64 = request.data.get('profile_image')

    try:
        if image_file:
            ext = image_file.name.split('.')[-1]
            file_name = f"{uuid.uuid4()}.{ext}"
            user.profile_image.save(file_name, image_file, save=True)
        elif image_base64:
            format, imgstr = image_base64.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"{uuid.uuid4()}.{ext}"
            user.profile_image.save(file_name, ContentFile(base64.b64decode(imgstr)), save=True)
        else:
            return Response({'error': 'No image provided'}, status=400)

        return Response({
            'message': 'Profile image uploaded successfully',
            'profile_image': f"{request.scheme}://{request.get_host()}{user.profile_image.url}"
        }, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)








# --------------------------------------------------------
# 🔹 USER PROFILE VIEWSET
# --------------------------------------------------------
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow access to the authenticated user's profile
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_context(self):
        return {"request": self.request}

    def list(self, request, *args, **kwargs):
        # GET /profile/ → return current user's profile
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # GET /profile/{id}/ → only allow self
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # PUT / PATCH → update current user's profile
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        # PATCH → update current user's profile partially
        return self.update(request, *args, **kwargs)


    @action(detail=False, methods=['patch'], url_path='update-current')
    def update_current(self, request):
        """
        PATCH /api/user-profile/update-current/
        Update the currently logged-in user's profile.
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)









# ================================
# 👤 PERSONAL DETAIL VIEWS
# ================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_personal_detail(request):
    """Fetch logged-in user's personal details"""
    personal_detail, _ = PersonalDetail.objects.get_or_create(user=request.user)
    serializer = PersonalDetailSerializer(personal_detail)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_personal_detail(request):
    """Update logged-in user's personal details"""
    personal_detail, _ = PersonalDetail.objects.get_or_create(user=request.user)
    serializer = PersonalDetailSerializer(personal_detail, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ================================
# 💼 PROFESSIONAL DETAIL VIEWS
# ================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_professional_detail(request):
    """Fetch logged-in user's professional details (with past experiences)"""
    professional_detail, _ = ProfessionalDetail.objects.get_or_create(user=request.user)
    serializer = ProfessionalDetailSerializer(professional_detail)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_professional_detail(request):
    """Update logged-in user's professional details (including past experiences)"""
    professional_detail, _ = ProfessionalDetail.objects.get_or_create(user=request.user)
    serializer = ProfessionalDetailSerializer(professional_detail, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ================================
# 🎓 EDUCATION VIEWS
# ================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_education_details(request):
    """Fetch logged-in user's education details"""
    education = Education.objects.filter(user=request.user)
    serializer = EducationSerializer(education, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_education_detail(request):
    """Add new education detail for logged-in user"""
    serializer = EducationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_education_detail(request, pk):
    """Update specific education detail"""
    try:
        education = Education.objects.get(id=pk, user=request.user)
    except Education.DoesNotExist:
        return Response({'detail': 'Education record not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = EducationSerializer(education, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_education_detail(request, pk):
    """Delete specific education detail"""
    try:
        education = Education.objects.get(id=pk, user=request.user)
    except Education.DoesNotExist:
        return Response({'detail': 'Education record not found.'}, status=status.HTTP_404_NOT_FOUND)

    education.delete()
    return Response({'detail': 'Education deleted successfully.'}, status=status.HTTP_200_OK)


# ================================
# 📝 PAST EXPERIENCE VIEWS
# ================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_past_experiences(request):
    """Fetch logged-in user's past professional experiences"""
    experiences = PastExperience.objects.filter(user=request.user)
    serializer = PastExperienceSerializer(experiences, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_past_experience(request):
    """Add a new past experience"""
    serializer = PastExperienceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_past_experience(request, pk):
    """Update a specific past experience"""
    try:
        experience = PastExperience.objects.get(id=pk, user=request.user)
    except PastExperience.DoesNotExist:
        return Response({'detail': 'Experience not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PastExperienceSerializer(experience, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_past_experience(request, pk):
    """Delete a specific past experience"""
    try:
        experience = PastExperience.objects.get(id=pk, user=request.user)
    except PastExperience.DoesNotExist:
        return Response({'detail': 'Experience not found.'}, status=status.HTTP_404_NOT_FOUND)

    experience.delete()
    return Response({'detail': 'Experience deleted successfully.'}, status=status.HTTP_200_OK)




# ================================
# 🔬 SCIENTIFIC INTEREST VIEWS
# ================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scientific_interest(request):
    """Fetch logged-in user's scientific interests"""
    scientific_interest, _ = ScientificInterest.objects.get_or_create(
        user=request.user
    )
    serializer = ScientificInterestSerializer(scientific_interest)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_scientific_interest(request):
    """Update logged-in user's scientific interests"""
    scientific_interest, _ = ScientificInterest.objects.get_or_create(
        user=request.user
    )
    serializer = ScientificInterestSerializer(
        scientific_interest,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=404)

    c_content = request.data.get("c_content", "").strip()
    if not c_content:
        return Response({"error": "Comment cannot be empty"}, status=400)
    return Response({"HI"}, status=200)
    comment = Comment.objects.create(user=request.user, post=post, c_content=c_content)
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=201)


def extract_youtube_id(url):
    patterns = [
        r"youtu\.be\/([^?&]+)",
        r"youtube\.com\/watch\?v=([^?&]+)",
        r"youtube\.com\/embed\/([^?&]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_youtube_preview(url):
    video_id = extract_youtube_id(url)
    if not video_id:
        return None

    return {
        "type": "youtube",
        "video_id": video_id,
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        "watch_url": f"https://www.youtube.com/watch?v={video_id}",
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
    }






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_speakers(request):
    speakers = User.objects.filter(role='speaker')
    serializer = UserSerializer(speakers, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_speaker_by_id(request, id):
    try:
        speaker = User.objects.get(id=id, role='speaker')
    except User.DoesNotExist:
        return Response({"detail": "Speaker not found"}, status=404)

    serializer = UserSerializer(speaker, context={'request': request})
    return Response(serializer.data)



# views.py
@api_view(["GET"])
@permission_classes([AllowAny])
def get_public_users(request):
    users = User.objects.all().select_related(
        "personal_detail",
        "professional_detail"
    ).prefetch_related(
        "education",
        "past_experiences"
    )

    serializer = PublicUserProfileSerializer(
        users, many=True, context={"request": request}
    )
    return Response(serializer.data)


# views.py

@api_view(["GET"])
@permission_classes([AllowAny])
def get_public_user_by_id(request, id):
    try:
        user = User.objects.select_related(
            "personal_detail",
            "professional_detail"
        ).prefetch_related(
            "education",
            "past_experiences"
        ).get(id=id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    serializer = PublicUserProfileSerializer(
        user, context={"request": request}
    )
    return Response(serializer.data)


from django.db.models import Q
from rest_framework.permissions import AllowAny

@api_view(["GET"])
@permission_classes([AllowAny])
def search_public_users(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return Response([])

    users = User.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).select_related(
        "personal_detail",
        "professional_detail"
    )[:10]  # limit results

    serializer = PublicUserProfileSerializer(
        users, many=True, context={"request": request}
    )
    return Response(serializer.data)






class HandshakeViewSet(viewsets.ModelViewSet):
    queryset = HandshakeRequest.objects.all()
    serializer_class = HandshakeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def send(self, request):
        receiver_id = request.data.get("receiver_id")
        sender = request.user

        if not receiver_id:
            return Response({"error": "receiver_id is required"}, status=400)

        if int(receiver_id) == sender.id:
            return Response({"error": "You cannot send handshake to yourself"}, status=400)

        # Prevent duplicate request
        existing = HandshakeRequest.objects.filter(sender=sender, receiver_id=receiver_id).first()
        if existing:
            return Response({
                "message": "Handshake already sent",
                "status": existing.status
            })

        # Create handshake
        handshake = HandshakeRequest.objects.create(
            sender=sender,
            receiver_id=receiver_id,
            status="pending"
        )

        # Fetch receiver
        receiver = User.objects.get(id=receiver_id)

        # ------- SEND EMAIL -------
        subject = "You received a Handshake Request"
        message = f"Hello {receiver.first_name},\n\nYou have received a handshake request from {sender.first_name} {sender.last_name}.\n\nPlease check your dashboard to respond."
        
        send_mail(
            subject,
            message,
            None,  # uses DEFAULT_FROM_EMAIL
            [receiver.email],
            fail_silently=False,  # for debugging
        )

        return Response(HandshakeSerializer(handshake, context={'request': request}).data)



    # Speaker accepts handshake
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        handshake = self.get_object()

        if handshake.receiver != request.user:
            return Response({"error": "Not allowed"}, status=403)

        handshake.status = "accepted"
        handshake.responded_at = now()
        handshake.save()
        # ⭐ Notify sender
        Notification.objects.create(
            user=handshake.sender,
            actor=handshake.receiver,
            action="accepted your handshake request",
            handshake=handshake,
        )
        from accounts.firebase_utils import push_notification_to_firebase

        push_notification_to_firebase(
            user_id=handshake.sender.id,
            data={
                "action": "accepted your handshake request",
                "actor": handshake.receiver.id,
                "handshake": handshake.id,
                "created_at": str(notification.created_at),
                "is_read": False
            }
        )
        return Response({"message": "Handshake accepted"})

    # Speaker declines handshake
    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        handshake = self.get_object()

        if handshake.receiver != request.user:
            return Response({"error": "Not allowed"}, status=403)

        handshake.status = "declined"
        handshake.responded_at = now()
        handshake.save()
        # ⭐ Notify sender
        Notification.objects.create(
            user=handshake.sender,
            actor=handshake.receiver,
            action="declined your handshake request",
            handshake=handshake,
        )
        from accounts.firebase_utils import push_notification_to_firebase

        push_notification_to_firebase(
            user_id=handshake.sender.id,
            data={
                "action": "declined your handshake request",
                "actor": handshake.receiver.id,
                "handshake": handshake.id,
                "created_at": str(notification.created_at),
                "is_read": False
            }
        )
        return Response({"message": "Handshake declined"})

    # Logged-in user requests (both sent & received)
    @action(detail=False, methods=["get"])
    def my_handshakes(self, request):
        user = request.user
        sent = HandshakeRequest.objects.filter(sender=user).order_by("-created_at")
        received = HandshakeRequest.objects.filter(receiver=user).order_by("-created_at")

        return Response({
            "sent": HandshakeSerializer(sent, many=True, context={"request": request}).data,
            "received": HandshakeSerializer(received, many=True, context={"request": request}).data,
        })

    
    # --------------------------------------------------------
    # CANCEL HANDSHAKE (only sender can cancel)
    # --------------------------------------------------------
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        handshake = self.get_object()

        if handshake.sender != request.user:
            return Response({"error": "Not allowed"}, status=403)

        if handshake.status != "pending":
            return Response({"error": "Only pending requests can be cancelled"}, status=400)

        handshake.delete()

        return Response({"message": "Handshake request removed"})









class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Logged-in user should only see *their* notifications.
        """
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """
        Return the count of unread notifications
        """
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread": count})
    
    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user).update(is_read=True)
        return Response({"message": "All notifications marked as read"})
    
    @action(detail=True, methods=["delete"])
    def delete_notification(self, request, pk=None):
        notification = self.get_object()
        notification.delete()
        return Response({"message": "Notification deleted"})
    
    
    # ✅ THIS IS THE IMPORTANT FIX
    @action(detail=False, methods=["delete"])
    def clear_all(self, request):
        Notification.objects.filter(user=request.user).delete()
        return Response({"message": "All notifications cleared"})







class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all().order_by("-id")
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend,]
    filterset_fields = ["speaker"]   # 👈 ADD THIS
    search_fields = ["topic", "venue", "speaker__first_name", "event__name"]
    ordering_fields = ["date", "start_time"]

    # Prevent assigning a non-speaker user
    def perform_create(self, serializer):
        speaker = serializer.validated_data["speaker"]
        if speaker.role != "speaker":
            raise ValidationError("Selected user is not a speaker.")
        serializer.save()




from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        User can only see their own messages
        """
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related(
            "sender", "receiver"
        ).prefetch_related(
            "post__media"
        ).order_by("timestamp")

    def get_serializer_context(self):
        return {"request": self.request}

    def create(self, request, *args, **kwargs):
        """
        Send a message
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="chat/(?P<user_id>[^/.]+)")
    def chat_history(self, request, user_id=None):
        """
        Get chat history with a specific user
        """
        user = request.user

        messages = Message.objects.filter(
            Q(sender=user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=user)
        ).select_related(
            "sender", "receiver"
        ).prefetch_related(
            "post__media"
        ).order_by("timestamp")

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["post"], url_path="mark-read/(?P<user_id>[^/.]+)")
    def mark_read(self, request, user_id=None):
        user = request.user

        Message.objects.filter(
            sender_id=user_id,
            receiver=user,
            is_read=False
        ).update(is_read=True)

        return Response({"status": "ok"})

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """
        Return latest 3 messages (sent or received)
        """
        messages = (
            Message.objects
            .filter(Q(sender=request.user) | Q(receiver=request.user))
            .order_by("-timestamp")[:3]
        )

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="latest-conversations")
    def latest_conversations(self, request):
        user = request.user

        messages = (
            Message.objects
            .filter(Q(sender=user) | Q(receiver=user))
            .select_related("sender", "receiver")
            .order_by("-timestamp")
        )

        conversations = {}
        for msg in messages:
            other_user = msg.receiver if msg.sender == user else msg.sender

            if other_user.id not in conversations:
                conversations[other_user.id] = {
                    "user": UserMiniSerializer(
                        other_user,
                        context={"request": request}
                    ).data,
                    "last_message": MessageSerializer(
                        msg,
                        context={"request": request}
                    ).data,
                }

            if len(conversations) == 3:
                break

        return Response(list(conversations.values()))


from rest_framework.viewsets import ViewSet


class ConversationViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    
    def list(self, request):
        user = request.user

        messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related(
            "sender", "receiver"
        ).prefetch_related(
            "post__media"
        ).order_by("-timestamp")

        conversations = {}

        for msg in messages:
            other_user = msg.receiver if msg.sender == user else msg.sender

            # take only latest message per user
            if other_user.id not in conversations:
                conversations[other_user.id] = {
                    "user": UserSerializer(
                        other_user,
                        context={"request": request}
                    ).data,
                    "last_message": MessageSerializer(
                        msg,
                        context={"request": request}
                    ).data,
                    "unread_count": Message.objects.filter(
                        sender=other_user,
                        receiver=user,
                        is_read=False
                    ).count()
                }

        return Response(
            sorted(
                conversations.values(),
                key=lambda x: x["last_message"]["timestamp"],
                reverse=True
            )
        )







class FolderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Folder.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "rename", "move"]:
            return FolderCreateSerializer
        return FolderTreeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # GET /api/folders/tree/
    @action(detail=False, methods=['get'])
    def tree(self, request):
        roots = Folder.objects.filter(user=request.user, parent=None)
        serializer = FolderTreeSerializer(roots, many=True)
        return Response(serializer.data)

    # ------------------------------
    # 🔹 RENAME FOLDER
    # POST /api/folders/<id>/rename/
    # ------------------------------
    @action(detail=True, methods=["post"])
    def rename(self, request, pk=None):
        folder = self.get_object()
        new_name = request.data.get("name")

        if not new_name:
            return Response({"error": "Folder name required"}, status=400)

        folder.name = new_name
        folder.save()
        return Response({"message": "Folder renamed successfully"})

    # ------------------------------
    # 🔹 MOVE FOLDER
    # POST /api/folders/<id>/move/
    # ------------------------------
    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        folder = self.get_object()
        new_parent_id = request.data.get("parent_id")

        if new_parent_id is None:
            folder.parent = None
        else:
            try:
                new_parent = Folder.objects.get(id=new_parent_id, user=request.user)
                folder.parent = new_parent
            except Folder.DoesNotExist:
                return Response({"error": "Invalid parent folder"}, status=400)

        folder.save()
        return Response({"message": "Folder moved successfully"})

    # ------------------------------
    # DELETE folder is already built-in (DELETE /folders/<id>/)
    # ------------------------------







class FolderItemViewSet(viewsets.ModelViewSet):
    serializer_class = FolderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FolderItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ------------------------------
    # 🔹 RENAME FILE
    # POST /api/folder-items/<id>/rename/
    # ------------------------------
    @action(detail=True, methods=["post"])
    def rename(self, request, pk=None):
        item = self.get_object()
        new_name = request.data.get("name")

        if not new_name:
            return Response({"error": "Name required"}, status=400)

        item.name = new_name
        item.save()
        return Response({"message": "File renamed successfully"})

    # ------------------------------
    # 🔹 MOVE FILE
    # POST /api/folder-items/<id>/move/
    # ------------------------------
    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        item = self.get_object()
        new_parent_id = request.data.get("parent_id")

        try:
            new_parent = Folder.objects.get(id=new_parent_id, user=request.user)
            item.parent = new_parent
            item.save()
            return Response({"message": "File moved successfully"})
        except Folder.DoesNotExist:
            return Response({"error": "Invalid folder"}, status=400)


from rest_framework.viewsets import ModelViewSet

class CalendarEventViewSet(ModelViewSet):
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CalendarEvent.objects.filter(user=self.request.user).order_by("start_time")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


        

import feedparser
from rest_framework.response import Response
from rest_framework.views import APIView
import re
from datetime import datetime



class ResearchNewsAPIView(APIView):
    def get(self, request):
        feeds = [
            "https://www.biopatrika.com/rss"
        ]

        news_items = []

        for url in feeds:
            feed = feedparser.parse(url)

            source_name = feed.feed.get("title", "Unknown Source")

            # ✅ ROOT / CHANNEL IMAGE (fallback thumbnail)
            root_thumbnail = None
            if "image" in feed.feed:
                root_thumbnail = feed.feed.image.get("href")

            for entry in feed.entries[:5]:
                thumbnail = None

                # 1️⃣ media_content (future-proof)
                if hasattr(entry, "media_content"):
                    thumbnail = entry.media_content[0].get("url")

                # 2️⃣ enclosures
                elif hasattr(entry, "enclosures") and entry.enclosures:
                    thumbnail = entry.enclosures[0].get("href")

                # 3️⃣ extract <img> from description/summary
                elif hasattr(entry, "summary"):
                    match = re.search(
                        r'<img[^>]+src="([^">]+)"',
                        entry.summary,
                        re.IGNORECASE
                    )
                    if match:
                        thumbnail = match.group(1)

                # 4️⃣ FINAL FALLBACK → ROOT IMAGE ✅
                if not thumbnail:
                    thumbnail = root_thumbnail

                # Published date
                published = ""
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(
                        *entry.published_parsed[:6]
                    ).isoformat()

                news_items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": published,
                    "source": source_name,
                    "thumbnail": thumbnail
                })

        # Sort newest first
        news_items.sort(
            key=lambda x: x["published"] or "",
            reverse=True
        )

        return Response(news_items[:10])


import requests
from bs4 import BeautifulSoup
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class OpenGraphMetaAPIView(APIView):
    def post(self, request):
        url = request.data.get("url")

        if not url:
            return Response(
                {"error": "URL is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            og_data = {}

            for tag in soup.find_all("meta"):
                prop = tag.get("property") or tag.get("name")
                if prop and prop.startswith("og:"):
                    og_data[prop] = tag.get("content")

            return Response({
                "url": url,
                "og": og_data
            })

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



import json
import qrcode
import base64
from io import BytesIO

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def generate_qr_from_url(request):
    try:
        data = json.loads(request.body)
        url = data.get("url")

        if not url:
            return JsonResponse(
                {"error": "URL is required"},
                status=400
            )

        # Create QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to Base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return JsonResponse({
            "url": url,
            "qr_base64": f"data:image/png;base64,{qr_base64}"
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )



class FollowRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FollowRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FollowRequest.objects.filter(
            Q(follower=user) | Q(following=user)
        ).select_related("follower", "following")

    # -----------------------
    # FOLLOW (send request)
    # -----------------------
    def create(self, request, *args, **kwargs):
        following_id = request.data.get("following")

        if not following_id:
            return Response(
                {"detail": "following field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if str(request.user.id) == str(following_id):
            return Response(
                {"detail": "You cannot follow yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        following_user = get_object_or_404(User, id=following_id)

        fr, created = FollowRequest.objects.get_or_create(
            follower=request.user,
            following=following_user
        )

        if not created:
            if fr.status == "accepted":
                return Response({"detail": "Already following"}, status=400)
            if fr.status == "pending":
                return Response({"detail": "Follow request already sent"}, status=400)
            if fr.status == "rejected":
                fr.status = "pending"
                fr.save()

        serializer = self.get_serializer(fr)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    # -----------------------
    # ACCEPT
    # -----------------------
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        fr = get_object_or_404(
            FollowRequest,
            id=pk,
            following=request.user,
            status="pending"
        )
        fr.status = "accepted"
        fr.responded_at = timezone.now()
        fr.save()

        return Response({"detail": "Follow request accepted"})

    # -----------------------
    # REJECT
    # -----------------------
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        fr = get_object_or_404(
            FollowRequest,
            id=pk,
            following=request.user,
            status="pending"
        )
        fr.status = "rejected"
        fr.responded_at = timezone.now()
        fr.save()

        return Response({"detail": "Follow request rejected"})

        # -----------------------
    # UNFOLLOW
    # -----------------------
    @action(detail=False, methods=["post"])
    def unfollow(self, request):
        following_id = request.data.get("following")

        if not following_id:
            return Response(
                {"detail": "following field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        fr = get_object_or_404(
            FollowRequest,
            follower=request.user,
            following_id=following_id,
            status="accepted"
        )
        fr.delete()

        return Response({"detail": "Unfollowed successfully"})
    
    # -----------------------
    # REMOVE FOLLOWER
    # -----------------------
    @action(detail=False, methods=["post"])
    def remove_follower(self, request):
        follower_id = request.data.get("follower")

        if not follower_id:
            return Response(
                {"detail": "follower field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        fr = get_object_or_404(
            FollowRequest,
            follower_id=follower_id,
            following=request.user,
            status="accepted"
        )

        fr.delete()

        return Response(
            {"detail": "Follower removed successfully"},
            status=status.HTTP_200_OK
        )

    
        # -----------------------
    # INCOMING REQUESTS
    # -----------------------
    @action(detail=False, methods=["get"])
    def incoming(self, request):
        qs = FollowRequest.objects.filter(
            following=request.user,
            status="pending"
        ).select_related("follower")

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    # -----------------------
    # OUTGOING REQUESTS
    # -----------------------
    @action(detail=False, methods=["get"])
    def outgoing(self, request):
        qs = FollowRequest.objects.filter(
            follower=request.user,
            status="pending"
        ).select_related("following")

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    

    
    @action(detail=False, methods=["get"], url_path="my-following")
    def my_following(self, request):
        qs = FollowRequest.objects.filter(
            follower=request.user,
            status="accepted"
        ).select_related("following")

        users = [f.following for f in qs]

        serializer = FollowUserListSerializer(
            users,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)







class UserFollowViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    # -----------------------
    # FOLLOWERS
    # -----------------------
    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        qs = FollowRequest.objects.filter(
            following_id=pk,
            status="accepted"
        ).select_related("follower")

        users = [f.follower for f in qs]
        serializer = FollowUserListSerializer(
            users,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    # -----------------------
    # FOLLOWING
    # -----------------------
    @action(detail=True, methods=["get"])
    def following(self, request, pk=None):
        qs = FollowRequest.objects.filter(
            follower_id=pk,
            status="accepted"
        ).select_related("following")

        users = [f.following for f in qs]
        serializer = FollowUserListSerializer(
            users,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)



# --------------------------------------------------------
# 🔹 POST VIEWSET (supports text + media upload)
# --------------------------------------------------------
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        title = request.data.get('title', '')
        content = request.data.get('content', '')
        files = request.FILES.getlist('files')

        # 🔹 Detect YouTube link & build preview
        youtube_preview = get_youtube_preview(content)

        with transaction.atomic():
            post = Post.objects.create(
                user=request.user,
                title=title,
                content=content,
                link_preview=youtube_preview  # ✅ ADD THIS
            )

            # Attach any uploaded media
            for file in files:
                PostMedia.objects.create(post=post, file=file)

        serializer = self.get_serializer(post, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


    def list(self, request, *args, **kwargs):
        """
        Feed:
        - My posts
        - Posts from users I follow (accepted only)
        """
        user = request.user

        # ✅ Users I follow (accepted only)
        following_ids = FollowRequest.objects.filter(
            follower=user,
            status="accepted"
        ).values_list("following_id", flat=True)

        queryset = Post.objects.filter(
            Q(user=user) | Q(user__id__in=following_ids)
        ).select_related("user") \
        .prefetch_related("media", "likes", "comments") \
        .order_by("-created_at")

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)


    def retrieve(self, request, *args, **kwargs):
        """
        Get single post with media.
        """
        post = self.get_object()
        serializer = self.get_serializer(post, context={'request': request})
        return Response(serializer.data)
    
    def _check_owner(self, request, post):
        if post.user != request.user:
            raise PermissionDenied("You do not have permission to modify this post.")
        
    def update(self, request, *args, **kwargs):
        post = self.get_object()
        self._check_owner(request, post)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        self._check_owner(request, post)

        return super().destroy(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        post = self.get_object()
        self._check_owner(request, post)

        title = request.data.get('title', post.title)
        content = request.data.get('content', post.content)
        files = request.FILES.getlist('files')

        post.title = title
        post.content = content
        post.link_preview = get_youtube_preview(content)
        post.save()

        if files:
            post.media.all().delete()
            for file in files:
                PostMedia.objects.create(post=post, file=file)

        serializer = self.get_serializer(post, context={'request': request})
        return Response(serializer.data)


    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()

        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )

        if created:
            is_liked = True

            # 🔔 Notify post owner
            if post.user != request.user:
                notification = Notification.objects.create(
                    user=post.user,
                    actor=request.user,
                    action="liked your post",
                    post=post,
                )

                from accounts.firebase_utils import push_notification_to_firebase
                push_notification_to_firebase(
                    user_id=post.user.id,
                    data={
                        "action": "liked your post",
                        "actor": request.user.id,
                        "post": post.id,
                        "created_at": str(notification.created_at),
                        "is_read": False
                    }
                )
        else:
            like.delete()
            is_liked = False

        return Response(
            {
                "id": post.id,
                "is_liked": is_liked,
                "like_count": post.likes.count()
            },
            status=status.HTTP_200_OK
        )


    # Add comment
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        c_content = request.data.get('c_content')

        if not c_content:
            return Response({'error': 'Comment cannot be empty'}, status=400)

        comment = Comment.objects.create(
            user=request.user,
            post=post,
            c_content=c_content
        )

        if post.user != request.user:
            notification = Notification.objects.create(
                user=post.user,
                actor=request.user,
                action="commented on your post",
                post=post,
            )

            from accounts.firebase_utils import push_notification_to_firebase
            push_notification_to_firebase(
                user_id=post.user.id,
                data={
                    "action": "commented on your post",
                    "actor": request.user.id,
                    "post": post.id,
                    "created_at": str(notification.created_at),
                    "is_read": False
                }
            )

        serializer = CommentSerializer(comment, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_latest(self, request):
        """
        Return posts by logged-in user.
        """
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        post = self.get_object()

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            post=post
        )

        if created:
            is_bookmarked = True
        else:
            bookmark.delete()
            is_bookmarked = False

        return Response(
            {
                "id": post.id,
                "is_bookmarked": is_bookmarked,
                "bookmark_count": post.bookmarks.count()
            },
            status=status.HTTP_200_OK
        )

    

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def share(self, request, pk=None):
        post = self.get_object()
        receiver_id = request.data.get("receiver")

        if not receiver_id:
            return Response(
                {"error": "Receiver is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Receiver not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ Use existing Message model
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            post=post,
            content="Shared a post"
        )

        # Notification
        if receiver != request.user:
            notification = Notification.objects.create(
                user=receiver,
                actor=request.user,
                action="shared a post with you",
                post=post
            )

            from accounts.firebase_utils import push_notification_to_firebase
            push_notification_to_firebase(
                user_id=receiver.id,
                data={
                    "action": "shared a post with you",
                    "actor": request.user.id,
                    "post": post.id,
                    "created_at": str(notification.created_at),
                    "is_read": False
                }
            )

        return Response(
            {"message": "Post shared successfully"},
            status=status.HTTP_201_CREATED
        )



class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

  
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if self.request.method in permissions.SAFE_METHODS:
            return Article.objects.filter(is_published=True)

        return Article.objects.filter(author=user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        article = self.get_object()

        if article.is_published:
            return Response(
                {"detail": "Article already published."},
                status=status.HTTP_400_BAD_REQUEST
            )

        article.is_published = True
        article.published_at = timezone.now()
        article.save()

        return Response(
            {"detail": "Article published successfully."}
        )


class ArticleReferenceViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleReferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ArticleReference.objects.filter(
            article__author=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            referenced_by=self.request.user
        )


class ArticleRatingViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ArticleRating.objects.filter(
            article__is_published=True
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
