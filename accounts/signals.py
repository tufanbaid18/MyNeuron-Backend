from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from accounts.s3 import s3
from .models import Article, ArticleFigure


# Delete figure image
@receiver(post_delete, sender=ArticleFigure)
def delete_figure_image(sender, instance, **kwargs):
    if instance.image:
        try:
            s3.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=instance.image
            )
        except Exception as e:
            print("S3 delete error:", e)


# Delete article images
@receiver(post_delete, sender=Article)
def delete_article_images(sender, instance, **kwargs):
    if instance.featured_image:
        try:
            s3.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=instance.featured_image
            )
        except Exception as e:
            print("S3 delete error:", e)

    if instance.cover_image:
        try:
            s3.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=instance.cover_image
            )
        except Exception as e:
            print("S3 delete error:", e)