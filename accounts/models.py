from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.conf import settings



class User(AbstractUser):
    username = None

    title = models.CharField(max_length=20, blank=True, null=True)

    email = models.EmailField('email address', unique=True)
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    profile_title = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(
        ("verified status"),
        default=False,
        help_text=("Designates whether the user has done payment or not."),
    )
    
    ROLE_CHOICES = (
        ('user', 'User'),
        ('speaker', 'Speaker'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email




class PersonalDetail(models.Model):
    """
    Extended personal & research profile
    """

    user = models.OneToOneField( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="personal_detail" )

    # Bio
    biosketch = models.TextField( blank=True, null=True)

    # Research / Academic links (multiple allowed via JSON)
    research_links = models.JSONField(blank=True, null=True, help_text="List of links like ResearchGate, PubMed, Google Scholar, NCBI" )

    # Social
    x_handle = models.CharField(max_length=255, blank=True, null=True, help_text="Twitter/X username without URL")

    linkedin = models.URLField( blank=True, null=True)
    # Location & demographics
    city = models.CharField( max_length=255, blank=True, null=True)

    country = models.CharField( max_length=100, blank=True, null=True)


    gender = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    dob = models.DateField( blank=True, null=True)


    # Publications
    articles_journals = models.TextField( blank=True, null=True)

    book_chapters = models.TextField( blank=True, null=True)

    def __str__(self):
        return f"Personal Detail - {self.user.email}"
    




    
class Education(models.Model):
    user = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="education" )

    # --------------------
    # Core education info
    # --------------------


    degree = models.CharField( max_length=50)
    course_name = models.CharField( max_length=255, blank=True, null=True )
    specialization = models.CharField( max_length=255, blank=True, null=True)
    university = models.CharField( max_length=255, blank=True, null=True)
    institute = models.CharField( max_length=255, blank=True, null=True)
    place = models.CharField( max_length=255, blank=True, null=True, help_text="City / State")
    country = models.CharField( max_length=100, blank=True, null=True)
    start_year = models.PositiveIntegerField( blank=True, null=True)
    end_year = models.PositiveIntegerField( blank=True, null=True)
    is_current = models.BooleanField( default=False)

    # --------------------
    # Research-specific (PhD / PostDoc)
    # --------------------

    topic = models.CharField( max_length=500, blank=True, null=True, help_text="Thesis / Research topic")
    lab_or_department = models.CharField( max_length=255, blank=True, null=True)
    research_interests = models.JSONField( blank=True, null=True, help_text="List of research interests (only for PhD/PostDoc)")
    research_summary = models.TextField( blank=True, null=True, help_text="Brief discussion of research work")

    # --------------------
    # Utility
    # --------------------

    order = models.PositiveIntegerField( default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-start_year"]

    def __str__(self):
        return f"{self.degree} - {self.course_name} ({self.university or self.institute})"




class ProfessionalDetail(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professional_detail"
    )

    # ===== CURRENT EXPERIENCE =====
    current_role = models.CharField(max_length=255, blank=True, null=True)
    current_organization = models.CharField(max_length=255, blank=True, null=True)
    current_department = models.CharField(max_length=255, blank=True, null=True)

    MONTH_CHOICES = [(i, i) for i in range(1, 13)]
    current_start_month = models.IntegerField(choices=MONTH_CHOICES, blank=True, null=True)
    current_start_year = models.IntegerField(blank=True, null=True)
    current_description = models.TextField(blank=True, null=True)

    # ===== PROFESSIONAL CONTACT =====
    work_email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    lab = models.CharField(max_length=255, blank=True, null=True)
    work_address = models.TextField(blank=True, null=True)

    # ===== SKILLS =====
    skill_set = models.TextField(blank=True, null=True)
    languages_spoken = models.CharField(max_length=255, blank=True, null=True)

    certifications = models.FileField(
        upload_to="certifications/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Professional Detail - {self.user.email}"
    


class PastExperience(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="past_experiences"
    )

    role = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True, null=True)

    start_month = models.IntegerField(
        choices=[(i, i) for i in range(1, 13)]
    )
    start_year = models.IntegerField()

    end_month = models.IntegerField(
        choices=[(i, i) for i in range(1, 13)]
    )
    end_year = models.IntegerField()

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Brief description of work done"
    )

    def __str__(self):
        return f"{self.role} at {self.organization}"

    class Meta:
        ordering = ["-end_year", "-end_month"]






class ScientificInterest(models.Model):
    """
    Scientific / Research interests of the user
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scientific_interest"
    )

    # 1️⃣ Research Area of Expertise (single)
    research_area_of_expertise = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # 2️⃣ Major Focus (multi-select)
    major_focus = models.JSONField(
        blank=True,
        null=True,
        help_text="List of major research focus areas"
    )

    # 3️⃣ Specific Research Areas (multi-select)
    specific_research_areas = models.JSONField(
        blank=True,
        null=True,
        help_text="List of specific research areas"
    )

    # 4️⃣ Organ Sites (multi-select)
    organ_sites = models.JSONField(
        blank=True,
        null=True,
        help_text="List of organ sites"
    )

    # 5️⃣ Additional Research Areas (multi-select)
    additional_research_areas = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional research expertise areas"
    )

    brief_description = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Scientific Interest - {self.user.email}"



class Event(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id} - {self.name}"
    



class Member(models.Model):
    ROLE_CHOICES = (
        ('participant', 'Participant'),
        ('speaker', 'Speaker'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='members')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','event','role')

    def __str__(self):
        return f"Member {self.id}: {self.user.email} -> {self.event.name} ({self.role})"





class Program(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="programs")
    speaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'speaker'},  # Only speakers visible in admin
        related_name="programs"
    )
    venue = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"Program {self.id} - {self.topic} ({self.event.name})"




class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=255, blank=True)  # ✅ new field
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    link_preview = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Post by {self.user.email} on {self.created_at:%Y-%m-%d}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def bookmark_count(self):
        return self.bookmarks.count()

    @property
    def comment_count(self):
        return self.comments.count()




class PostMedia(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media'
    )
    file = models.FileField(upload_to='posts/media/')
    is_video = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Auto-detect video based on file extension
        if self.file and self.file.name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            self.is_video = True
        else:
            self.is_video = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Media for Post {self.post.id}"
    




class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")  # prevents multiple likes





class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")





class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    c_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"Comment by {self.user.email} on {self.post.title}"





class HandshakeRequest(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sent_handshakes",
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="received_handshakes",
        on_delete=models.CASCADE
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("declined", "Declined"),
        ],
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"





from firebase_admin import db

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)

    post = models.ForeignKey("Post", null=True, blank=True, on_delete=models.CASCADE)
    handshake = models.ForeignKey("HandshakeRequest", null=True, blank=True, on_delete=models.CASCADE)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor} {self.action}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Push to Firebase realtime database
        ref = db.reference(f"notifications/{self.user.id}")
        ref.push({
            "id": self.id,
            "actor_id": self.actor.id,
            "actor_name": self.actor.first_name,
            "action": self.action,
            "post": self.post.id if self.post else None,
            "handshake": self.handshake.id if self.handshake else None,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        })

    



class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_messages',
        on_delete=models.CASCADE
    )

    # 🔥 NEW (optional)
    post = models.ForeignKey(
        Post,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="shared_messages"
    )

    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        if self.post:
            return f"{self.sender} → {self.receiver}: shared a post"
        return f"{self.sender} → {self.receiver}: {self.content[:20]}"







def user_file_upload_path(instance, filename):
    # uploaded as: user_<id>/folders/<folder_id>/<filename>
    return f"user_{instance.user.id}/folders/{instance.folder.id}/{filename}"


class Folder(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="folders"
    )
    name = models.CharField(max_length=255, blank=True, null=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subfolders"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Folder"
        verbose_name_plural = "Folders"
        ordering = ["name"]

    def __str__(self):
        return self.name
    



class FolderItem(models.Model):
    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        related_name="items"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="folder_items"
    )

    
    url = models.CharField(max_length=500, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

# file = models.FileField(upload_to=user_file_upload_path, null=True, blank=True)
    # file_name = models.CharField(max_length=255)
    # file_type = models.CharField(max_length=50)   # pdf, docx, png, etc.


class CalendarEvent(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calendar_events"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    remind_before = models.IntegerField(default=10)  # minutes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user}"
