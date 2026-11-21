from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    full_name = models.CharField(max_length=150, blank=True)
    member_code = models.CharField(max_length=24, unique=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    department_or_grade = models.CharField(max_length=100, default='General Reader')
    avatar = models.ImageField(upload_to='member_avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.member_code and self.user_id:
            self.member_code = f"LIB-{10000 + self.user_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name or self.user.username} ({self.member_code})"

@receiver(post_save, sender=User)
def create_member_profile(sender, instance, created, **kwargs):
    if created:
        MemberProfile.objects.create(
            user=instance,
            full_name=f"{instance.first_name} {instance.last_name}".strip() or instance.username,
            member_code=f"LIB-{10000 + instance.id}"
        )
