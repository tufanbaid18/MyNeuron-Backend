from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .serializers import UserSerializer, EventSerializer, MemberSerializer
from .models import Event, Member, User
from .forms import RegisterForm
from django.http import JsonResponse
from django.contrib.auth import logout
from django.http import HttpResponse;
from rest_framework.response import Response
from rest_framework import status
from .models import PersonalDetail, ProfessionalDetail
from .serializers import UserProfileSerializer, PersonalDetailSerializer, ProfessionalDetailSerializer
from django.core.files.base import ContentFile
import base64, uuid
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post, PostMedia
from .serializers import PostSerializer
from django.db import transaction
from .models import Like, Bookmark, Comment
from .serializers import CommentSerializer




# Web registration
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

# Home page
@login_required
def home(request):
    return render(request, 'accounts/home.html', {'user': request.user})

# Event registration (web)
@login_required
def event_register_view(request):

    events = Event.objects.all()
    if request.method == 'POST':
        event_id = request.POST.get('event')
        role = request.POST.get('role')
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            messages.error(request, 'Selected event does not exist')
            return redirect('accounts:event_register')
        # prevent duplicates
        if Member.objects.filter(user=request.user, event=event, role=role).exists():
            messages.warning(request, 'You are already registered for this event with the same role')
        else:
            Member.objects.create(user=request.user, event=event, role=role)
            messages.success(request, 'Successfully registered for the event')
        return redirect('accounts:home')
    return render(request, 'accounts/event_register.html', {'events': events})

def logout_view(request):
    logout(request)
    return redirect('registration:login')


# API views and viewsets
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.select_related('user','event').all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=201)
    return Response(serializer.errors, status=400)

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

    # login successful
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data
    })


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



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_image(request):
    user = request.user
    image_data = request.data.get('profile_image')

    if not image_data:
        return Response({'error': 'No image provided'}, status=400)

    try:
        # Decode base64 string and save
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        file_name = f"{uuid.uuid4()}.{ext}"
        user.profile_image.save(file_name, ContentFile(base64.b64decode(imgstr)), save=True)

        return Response({
            'message': 'Profile image uploaded successfully',
            'profile_image': user.profile_image.url
        }, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)



# ================================
# 👤 PERSONAL DETAIL VIEWS
# ================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_personal_detail(request):
    """Fetch logged-in user's personal details"""
    try:
        personal_detail = PersonalDetail.objects.get(user=request.user)
    except PersonalDetail.DoesNotExist:
        return Response({'detail': 'Personal details not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PersonalDetailSerializer(personal_detail)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_personal_detail(request):
    """Update logged-in user's personal details"""
    try:
        personal_detail, created = PersonalDetail.objects.get_or_create(user=request.user)
    except PersonalDetail.MultipleObjectsReturned:
        return Response({'detail': 'Duplicate profile found.'}, status=status.HTTP_400_BAD_REQUEST)

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
    """Fetch logged-in user's professional details"""
    try:
        professional_detail = ProfessionalDetail.objects.get(user=request.user)
    except ProfessionalDetail.DoesNotExist:
        return Response({'detail': 'Professional details not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProfessionalDetailSerializer(professional_detail)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_professional_detail(request):
    """Update logged-in user's professional details"""
    try:
        professional_detail, created = ProfessionalDetail.objects.get_or_create(user=request.user)
    except ProfessionalDetail.MultipleObjectsReturned:
        return Response({'detail': 'Duplicate profile found.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProfessionalDetailSerializer(professional_detail, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.decorators import action
from rest_framework.parsers import JSONParser

# --------------------------------------------------------
# 🔹 POST VIEWSET (supports text + media upload)
# --------------------------------------------------------
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        """
        Create a new post with optional media files.
        """
        title = request.data.get('title', '')
        content = request.data.get('content', '')
        files = request.FILES.getlist('files')

        with transaction.atomic():
            # Create post
            post = Post.objects.create(user=request.user, title=title, content=content)

            # Attach any uploaded media
            for file in files:
                PostMedia.objects.create(post=post, file=file)

        # Re-serialize with request context to get full URLs
        serializer = self.get_serializer(post, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        Return all posts (newest first) with full media URLs.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Get single post with media.
        """
        post = self.get_object()
        serializer = self.get_serializer(post, context={'request': request})
        return Response(serializer.data)
    


    # Like a post
    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            return Response({"message": "Unliked"}, status=status.HTTP_200_OK)
        return Response({"message": "Liked"}, status=status.HTTP_201_CREATED)

    # Bookmark a post
    @action(detail=True, methods=["post"])
    def bookmark(self, request, pk=None):
        post = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
        if not created:
            bookmark.delete()
            return Response({"message": "Removed bookmark"}, status=status.HTTP_200_OK)
        return Response({"message": "Bookmarked"}, status=status.HTTP_201_CREATED)

    # Add comment
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        c_content = request.data.get('c_content')  # ✅ FIXED

        if not c_content:
            return Response({'error': 'Comment cannot be empty'}, status=400)

        comment = Comment.objects.create(user=request.user, post=post, c_content=c_content)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=201)




# --------------------------------------------------------
# 🔹 USER PROFILE VIEWSET
# --------------------------------------------------------
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save()



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

    comment = Comment.objects.create(user=request.user, post=post, c_content=c_content)
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=201)
