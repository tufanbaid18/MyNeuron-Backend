from rest_framework import serializers
from .models import (
    User,
    Event,
    Member,
    PersonalDetail,
    ProfessionalDetail,
    Post, PostMedia, Education,
    CalendarEvent, ScientificInterest, PastExperience, FollowRequest, Folder, FolderItem, Message, Notification, Comment, Program, 
    Article, ArticleSection, ArticleFigure, ArticleKeyword, ArticleKeywordMap, ArticleReference, ArticleRating
)
from .validators import validate_email, validate_password_complexity
from django.utils import timezone


# -------------------------------
# 🔹 USER SERIALIZER (for signup)
# -------------------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    profile_image = serializers.SerializerMethodField()

    

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "title",
            "first_name",
            "middle_name",
            "last_name",
            "profile_title",
            "profile_image",
            "role",
            "is_verified",
            "is_verified_lite",
            "password",
            "confirm_password",
        ]

    def validate_email(self, value):
        validate_email(value)
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        validate_password_complexity(data["password"])
        return data

    # def create(self, validated_data):
    #     validated_data.pop("confirm_password")
    #     password = validated_data.pop("password")
    #     user = User(**validated_data)
    #     user.set_password(password)
    #     user.save()
    #     return user
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=password,
            first_name=validated_data.get("first_name"),
            middle_name=validated_data.get("middle_name"),
            last_name=validated_data.get("last_name"),
            is_email_verified=False,  # 🔒 FORCE FALSE
            is_verified=False,        # 🔒 PAYMENT VERIFICATION
            is_verified_lite=False,
            role="user",              # 🔒 DEFAULT ROLE
        )

        return user
    
    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None




# -------------------------------
# 🔹 USER PROFILE (with personal + professional details)
# -------------------------------

class PersonalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetail
        exclude = ("user",)





class EducationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Education
        exclude = ("user",)

    def validate(self, data):
        degree = data.get("degree", "").lower()

        if degree not in ["phd", "postdoc"]:
            data["topic"] = None
            data["lab_or_department"] = None
            data["research_interests"] = None
            data["research_summary"] = None

        return data

    
class PastExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastExperience
        fields = [
            "id",
            "role",
            "organization",
            "department",
            "start_month",
            "start_year",
            "end_month",
            "end_year",
            "description",
        ]


class ProfessionalDetailSerializer(serializers.ModelSerializer):
    past_experiences = PastExperienceSerializer(
        many=True,
        required=False,
        source="user.past_experiences"
    )

    class Meta:
        model = ProfessionalDetail
        fields = [
            "current_role",
            "current_organization",
            "current_department",
            "current_start_month",
            "current_start_year",
            "current_description",
            "work_email",
            "contact_number",
            "emergency_contact_number",
            "website",
            "lab",
            "work_address",
            "skill_set",
            "languages_spoken",
            "certifications",
            "past_experiences",
        ]
        read_only_fields = ["user"]

    
class ScientificInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScientificInterest
        exclude = ("user",)



class UserProfileSerializer(serializers.ModelSerializer):
    personal_detail = PersonalDetailSerializer(required=False)
    professional_detail = ProfessionalDetailSerializer(required=False)
    education = EducationSerializer(many=True, required=False)
    scientific_interest = ScientificInterestSerializer(required=False)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    is_following = serializers.SerializerMethodField()
    follow_request_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "title",
            "profile_title",
            "profile_image",
            "personal_detail",
            "professional_detail",
            "education",
            "scientific_interest",
            "followers_count",
            "following_count",
            "is_following",
            "follow_request_status",
        ]

    # -----------------------
    # COUNTS
    # -----------------------
    def get_followers_count(self, obj):
        return FollowRequest.objects.filter(
            following=obj,
            status="accepted"
        ).count()

    def get_following_count(self, obj):
        return FollowRequest.objects.filter(
            follower=obj,
            status="accepted"
        ).count()

    # -----------------------
    # USER STATE
    # -----------------------
    def get_is_following(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False

        return FollowRequest.objects.filter(
            follower=request.user,
            following=obj,
            status="accepted"
        ).exists()

    def get_follow_request_status(self, obj):
        """
        returns: pending | accepted | rejected | none
        """
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return "none"

        fr = FollowRequest.objects.filter(
            follower=request.user,
            following=obj
        ).first()

        return fr.status if fr else "none"
    

    def update(self, instance, validated_data):
        personal_data = validated_data.pop("personal_detail", {})
        professional_data = validated_data.pop("professional_detail", {})
        education_data = validated_data.pop("education", [])
        scientific_data = validated_data.pop("scientific_interest", {})

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
            professional_instance, _ = ProfessionalDetail.objects.get_or_create(user=instance)

            serializer = ProfessionalDetailSerializer(
                professional_instance,
                data=professional_data,
                partial=True,
                context=self.context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # ---------------- EDUCATION ----------------
        existing_ids = []
        for edu in education_data:
            edu_id = edu.get("id")
            if edu_id:
                Education.objects.filter(id=edu_id, user=instance).update(**edu)
                existing_ids.append(edu_id)
            else:
                new_obj = Education.objects.create(user=instance, **edu)
                existing_ids.append(new_obj.id)

        Education.objects.filter(user=instance).exclude(id__in=existing_ids).delete()

        # ---------------- SCIENTIFIC INTEREST ----------------
        if scientific_data:
            ScientificInterest.objects.update_or_create(
                user=instance,
                defaults=scientific_data
            )

        return instance

    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image and request:
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
# 🔹 POST + MEDIA SERIALIZERS
# -------------------------------
class UserMiniSerializer(serializers.ModelSerializer):
    """Minimal user info for posts (for displaying author name & image)."""
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'profile_image', 'is_following',]

    def get_is_following(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False

        return FollowRequest.objects.filter(
            follower=request.user,
            following=obj,
            status="accepted"
        ).exists()


class PostMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = ['id', 'file_url', 'is_video']

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

    like_count = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    comments = CommentSerializer(many=True, read_only=True)
    link_preview = serializers.JSONField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "title",
            "content",
            "media",
            "link_preview",
            "created_at",
            "like_count",
            "bookmark_count",
            "comment_count",
            "is_liked",
            "is_bookmarked",
            "comments",
        ]

    # -----------------------
    # COUNTS
    # -----------------------
    def get_like_count(self, obj):
        return obj.likes.count()

    def get_bookmark_count(self, obj):
        return obj.bookmarks.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    # -----------------------
    # USER STATE
    # -----------------------
    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.likes.filter(user=request.user).exists()

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.bookmarks.filter(user=request.user).exists()


    
    
from .models import HandshakeRequest

class HandshakeSerializer(serializers.ModelSerializer):
    sender_details = serializers.SerializerMethodField()
    receiver_details = serializers.SerializerMethodField()

    class Meta:
        model = HandshakeRequest
        fields = [
            'id', 'sender', 'receiver',
            'status', 'created_at', 'responded_at',
            'sender_details', 'receiver_details'
        ]

    def get_sender_details(self, obj):
        request = self.context.get("request")

        return {
            "id": obj.sender.id,
            "name": f"{obj.sender.first_name} {obj.sender.last_name}",
            "email": obj.sender.email,
            "profile_image": request.build_absolute_uri(obj.sender.profile_image.url)
            if obj.sender.profile_image else None
        }

    def get_receiver_details(self, obj):
        request = self.context.get("request")

        return {
            "id": obj.receiver.id,
            "name": f"{obj.receiver.first_name} {obj.receiver.last_name}",
            "email": obj.receiver.email,
            "profile_image": request.build_absolute_uri(obj.receiver.profile_image.url)
            if obj.receiver.profile_image else None
        }






class NotificationSerializer(serializers.ModelSerializer):
    actor_details = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "actor",
            "actor_details",
            "action",
            "post",
            "handshake",
            "is_read",
            "created_at",
        ]

    def get_actor_details(self, obj):
        if not obj.actor:
            return None
        
        return {
            "id": obj.actor.id,
            "name": obj.actor.first_name,
            "email": obj.actor.email,
        }





class ProgramSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source="event.name", read_only=True)
    speaker_name = serializers.SerializerMethodField()
    speaker_image = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = [
            "id",
            "event",
            "event_name",
            "speaker",
            "speaker_name",
            "speaker_image",
            "venue",
            "topic",
            "date",
            "start_time",
            "end_time",
        ]

    def get_speaker_name(self, obj):
        if not obj.speaker:
            return None
        return f"{obj.speaker.first_name} {obj.speaker.last_name}".strip()


    def get_speaker_image(self, obj):
        request = self.context.get("request")

        if obj.speaker and obj.speaker.profile_image:
            return request.build_absolute_uri(obj.speaker.profile_image.url)

        return None



class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.first_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.first_name', read_only=True)

    sender_image = serializers.SerializerMethodField()
    receiver_image = serializers.SerializerMethodField()

    post_preview = serializers.SerializerMethodField()

    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'receiver',
            'content',
            'timestamp',
            'is_read',
            'sender_name',
            'receiver_name',
            'sender_image',
            'receiver_image',
            'post_preview',
        ]

    def get_sender_image(self, obj):
        request = self.context.get("request")
        if obj.sender.profile_image:
            return request.build_absolute_uri(obj.sender.profile_image.url)
        return None

    def get_receiver_image(self, obj):
        request = self.context.get("request")
        if obj.receiver.profile_image:
            return request.build_absolute_uri(obj.receiver.profile_image.url)
        return None

    
    def get_post_preview(self, obj):
        """
        Lightweight post preview for inbox
        """
        if not obj.post:
            return None

        request = self.context.get("request")

        media = obj.post.media.first()
        media_url = (
            request.build_absolute_uri(media.file.url)
            if media else None
        )

        return {
            "id": obj.post.id,
            "title": obj.post.title,
            "content": obj.post.content[:120],
            "media": media_url,
        }


class FolderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderItem
        fields = ['id', 'title', 'url', 'created_at', 'folder']



class FolderTreeSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    subfolders = serializers.SerializerMethodField()
    items = FolderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'parent', 'subfolders', 'items']


    def get_subfolders(self, obj):
        children = obj.subfolders.all()
        return FolderTreeSerializer(children, many=True).data
    
    
class FolderCreateSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Folder.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Folder
        fields = ["id", "name", "parent"]




class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = "__all__"
        read_only_fields = ["user", "created_at"]




class PublicPersonalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetail
        fields = [
            "biosketch",
            "research_links",
            "x_handle",
            "linkedin",
            "city",
            "country",
            "articles_journals",
            "book_chapters",
        ]

class PublicEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            "degree",
            "course_name",
            "specialization",
            "university",
            "institute",
            "place",
            "country",
            "start_year",
            "end_year",
            "is_current",
            "topic",
            "lab_or_department",
            "research_interests",
            "research_summary",
        ]

class PublicPastExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastExperience
        fields = [
            "role",
            "organization",
            "department",
            "start_month",
            "start_year",
            "end_month",
            "end_year",
            "description",
        ]

class PublicProfessionalDetailSerializer(serializers.ModelSerializer):
    past_experiences = PublicPastExperienceSerializer(
        many=True,
        source="user.past_experiences",
        read_only=True
    )

    class Meta:
        model = ProfessionalDetail
        fields = [
            "current_role",
            "current_organization",
            "current_department",
            "current_start_month",
            "current_start_year",
            "current_description",
            "lab",
            "skill_set",
            "languages_spoken",
            "past_experiences",
        ]

class PublicScientificInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScientificInterest
        fields = [
            "research_area_of_expertise",
            "major_focus",
            "specific_research_areas",
            "organ_sites",
            "additional_research_areas",
            "brief_description",
        ]



class PublicUserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    personal_detail = PublicPersonalDetailSerializer(read_only=True)
    professional_detail = PublicProfessionalDetailSerializer(read_only=True)
    education = PublicEducationSerializer(many=True, read_only=True)
    scientific_interest = PublicScientificInterestSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "title",
            "first_name",
            "middle_name",
            "last_name",
            "profile_title",
            "role",
            "profile_image",
            "personal_detail",
            "professional_detail",
            "education",
            "scientific_interest",
        ]

    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None


class FollowUserListSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "profile_image",
            "is_following",
        ]

    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def get_is_following(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False

        return FollowRequest.objects.filter(
            follower=request.user,
            following=obj,
            status="accepted"
        ).exists()


class FollowRequestSerializer(serializers.ModelSerializer):
    follower = UserMiniSerializer(read_only=True)
    following = UserMiniSerializer(read_only=True)

    class Meta:
        model = FollowRequest
        fields = [
            "id",
            "follower",
            "following",
            "status",
            "created_at",
            "responded_at",
        ]
        read_only_fields = ["status", "responded_at"]



class ArticleSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleSection
        fields = (
            "id",
            "section_type",
            "title",
            "content",
            "order",
        )


class ArticleFigureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleFigure
        fields = (
            "id",
            "section",
            "image",
            "caption",
            "figure_number",
        )
        read_only_fields = ("figure_number",)

class ArticleKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleKeyword
        fields = ("id", "name")

class ArticleReferenceSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ArticleReference
        fields = ("id", "user", "user_email", "created_at")

    def validate_user(self, user):
        request_user = self.context["request"].user

        is_follower = FollowRequest.objects.filter(
            follower=user,
            following=request_user,
            status="accepted"
        ).exists()

        if not is_follower:
            raise serializers.ValidationError(
                "You can only reference users who are following you."
            )

        return user

class ArticleSerializer(serializers.ModelSerializer):
    sections = ArticleSectionSerializer(many=True, required=False)
    figures = ArticleFigureSerializer(many=True, required=False, read_only=True)
    references = ArticleReferenceSerializer(many=True, read_only=True)

    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "specialization",
            "abstract",
            "featured_image",
            "cover_image",
            "acknowledgements",
            "author_contributions",
            "funding",
            "competing_interests",
            "disclosures_ethics",
            "is_published",
            "published_at",
            "author_name",
            "sections",
            "figures",
            "references",
            "created_at",
            "updated_at",
            "average_rating",
            "rating_count",
        )
        read_only_fields = ("author_name", "published_at")

    def get_author_name(self, obj):
        return obj.author_name()

    def create(self, validated_data):
        sections_data = validated_data.pop("sections", [])
        article = Article.objects.create(
            author=self.context["request"].user,
            **validated_data
        )

        for section in sections_data:
            ArticleSection.objects.create(article=article, **section)

        return article

    def update(self, instance, validated_data):
        sections_data = validated_data.pop("sections", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if instance.is_published and not instance.published_at:
            instance.published_at = timezone.now()

        instance.save()

        if sections_data is not None:
            instance.sections.all().delete()
            for section in sections_data:
                ArticleSection.objects.create(article=instance, **section)

        return instance



class ArticleRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRating
        fields = ("id", "article", "rating", "created_at")
        read_only_fields = ("created_at",)

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        article = validated_data["article"]

        rating_obj, _ = ArticleRating.objects.update_or_create(
            user=user,
            article=article,
            defaults={"rating": validated_data["rating"]}
        )
        return rating_obj
