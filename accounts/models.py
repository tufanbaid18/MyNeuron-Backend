from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    
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

from django.db import models
from django.conf import settings

class PersonalDetail(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='personal_detail')
    biosketch = models.TextField(blank=True, null=True)
    researchgate_link = models.URLField(blank=True, null=True)
    pubmed_link = models.URLField(blank=True, null=True)
    google_scholar_link = models.URLField(blank=True, null=True)
    x_handle = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)    

    # Publications
    articles_journals = models.TextField(blank=True, null=True)
    book_chapters = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Personal Details - {self.user.email}"
    
class Education(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(blank=True, null=True, max_length=200)
    course_name = models.CharField(blank=True, null=True, max_length=200)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.degree} - {self.course_name}"


class ProfessionalDetail(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='professional_detail')
    current_experience = models.TextField(blank=True, null=True)
    past_experiences = models.TextField(blank=True, null=True)
    skill_set = models.TextField(blank=True, null=True)
    languages_spoken = models.CharField(max_length=255, blank=True, null=True)
    certifications = models.FileField(upload_to='certifications/', null=True, blank=True)

    def __str__(self):
        return f"Professional Details - {self.user.email}"


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=255, blank=True)  # ✅ new field
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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

