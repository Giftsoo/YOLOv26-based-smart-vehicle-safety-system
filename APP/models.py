from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

# =========================
# USER PROFILE MODEL
# =========================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='profile_images',
        default='profile_images/default.jpg',
        blank=True
    )
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

    # Resize image safely
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.avatar and os.path.exists(self.avatar.path):
            img = Image.open(self.avatar.path)

            if img.height > 150 or img.width > 150:
                img.thumbnail((150, 150))
                img.save(self.avatar.path)


# =========================
# USER PERSONAL DETAILS
# =========================
class UserPersonalModel(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    age = models.IntegerField()
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


# =========================
# GENERIC DETECTIONS
# =========================
class Detected(models.Model):
    frame_number = models.IntegerField()
    class_name = models.CharField(max_length=100)
    confidence = models.IntegerField()
    coordinates = models.CharField(max_length=100)

    def __str__(self):
        return f"Frame {self.frame_number} - {self.class_name} ({self.confidence}%)"


# =========================
# VEHICLE DETECTIONS
# =========================
class DetectedVehicle(models.Model):
    frame_number = models.IntegerField()
    class_name = models.CharField(max_length=50)
    confidence = models.FloatField()
    coordinates = models.CharField(max_length=100)
    distance = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.class_name} - {self.distance}"