from django.contrib.auth.models import User
from django.db import models


# Create your models here.
def default_profile_image():
    return 'profile_images/dummy-image.png'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="profile_images", null=True, blank=True, default=default_profile_image)


