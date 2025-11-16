from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    # academic major (free text) and academic year (choice)
    major = models.CharField(max_length=200, blank=True)
    YEAR_CHOICES = [
        ('Freshman', 'Freshman'),
        ('Sophomore', 'Sophomore'),
        ('Junior', 'Junior'),
        ('Senior', 'Senior'),
        ('Master', 'Master'),
        ('PhD', 'PhD'),
        ('Other', 'Other'),
    ]
    year = models.CharField(max_length=20, choices=YEAR_CHOICES, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"


class Mentor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    bio = models.TextField(blank=True)
    subjects = models.CharField(max_length=300, blank=True)
    # comma-separated list of class codes the mentor can teach (codes come from accounts.constants.CLASSES)
    class_codes = models.CharField(max_length=300, blank=True, default="")
    approved = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    avatar = models.ImageField(upload_to='mentor_avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mentor({self.user.username})"
