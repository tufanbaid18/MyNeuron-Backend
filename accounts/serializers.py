from rest_framework import serializers
from .models import (
    User,
    Event,
    Member,
    PersonalDetail,
    ProfessionalDetail,
    Post,
    PostMedia,
    Education,
)
from .validators import validate_email, validate_password_complexity
from .models import Like, Bookmark, Comment

# -------------------------------
# 🔹 USER SERIALIZER (for signup)
# -------------------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'profile_image',
            'role',
            'password',
            'confirm_password',
        ]

    def validate_email(self, value):
        validate_email(value)
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered')
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})
        validate_password_complexity(data['password'])
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def get_profile_image(self, obj):
        request = self.context.get('request')
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None


# -------------------------------
# 🔹 EVENT & MEMBER SERIALIZERS
# -------------------------------
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name']


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user'
    )
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), write_only=True, source='event'
    )

    class Meta:
        model = Member
        fields = ['id', 'user', 'user_id', 'event', 'event_id', 'role', 'created_at']
        read_only_fields = ['created_at', 'event', 'user']

    def create(self, validated_data):
        return super().create(validated_data)


# -------------------------------
# 🔹 USER PROFILE (with personal + professional details)
# -------------------------------


class PersonalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetail
        fields = '__all__'
        read_only_fields = ['user']



class ProfessionalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalDetail
        fields = '__all__'
        read_only_fields = ['user']
        

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ('user',)   # HIDE THE USER FIELD
        extra_kwargs = {
            'degree': {"required": False, "allow_blank": True},
            'course_name': {"required": False, "allow_blank": True},
        }


 
class UserProfileSerializer(serializers.ModelSerializer):
    personal_detail = PersonalDetailSerializer(required=False)
    professional_detail = ProfessionalDetailSerializer(required=False)
    education = EducationSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'profile_image',
            'personal_detail',
            'professional_detail',
            'education',
        ]

    def update(self, instance, validated_data):
        personal_data = validated_data.pop('personal_detail', {})
        professional_data = validated_data.pop('professional_detail', {})
        education_data = validated_data.pop('education', [])

        # ---------------- USER CORE FIELDS ----------------
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # ---------------- PERSONAL DETAIL ----------------
        if personal_data:
            PersonalDetail.objects.update_or_create(
                user=instance,
                defaults=personal_data
            )

        # ---------------- PROFESSIONAL DETAIL ----------------
        if professional_data:
            ProfessionalDetail.objects.update_or_create(
                user=instance,
                defaults=professional_data
            )

        # ---------------- EDUCATION (ADD / UPDATE) ----------------
        existing_ids = []
        for edu in education_data:
            edu_id = edu.get("id")

            if edu_id:
                # UPDATE
                Education.objects.filter(id=edu_id, user=instance).update(**edu)
                existing_ids.append(edu_id)
            else:
                # CREATE
                new_obj = Education.objects.create(user=instance, **edu)
                existing_ids.append(new_obj.id)

        # ---------------- DELETE OLD EDUCATION ----------------
        Education.objects.filter(user=instance).exclude(id__in=existing_ids).delete()

        return instance


# -------------------------------
# 🔹 POST + MEDIA SERIALIZERS
# -------------------------------
class UserMiniSerializer(serializers.ModelSerializer):
    """Minimal user info for posts (for displaying author name & image)."""

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'profile_image']


class PostMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'file_url', 'is_video']

    def get_file_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url) if obj.file else None
    


class CommentSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "c_content", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    bookmark_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "user", "title", "content", "media",
            "created_at", "like_count", "bookmark_count",
            "comment_count", "comments"
        ]

    
    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_bookmarks_count(self, obj):
        return obj.bookmarks.count()

