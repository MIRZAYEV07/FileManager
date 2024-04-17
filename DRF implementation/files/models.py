from django.db import models
from users.models import User



class Folder(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='folders', on_delete=models.CASCADE)

class File(models.Model):
    filename = models.CharField(max_length=255)
    path = models.CharField(max_length=500)
    owner = models.ForeignKey(User, related_name='files', on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, related_name='files', on_delete=models.CASCADE)

class Permission(models.Model):
    file = models.ForeignKey(File, related_name='permissions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='permissions', on_delete=models.CASCADE)
    can_read = models.BooleanField(default=False)
    can_change = models.BooleanField(default=False)

class FileVersion(models.Model):
    file = models.ForeignKey(File, related_name='versions', on_delete=models.CASCADE)
    version_number = models.IntegerField(default=1)
    file_path = models.CharField(max_length=500)