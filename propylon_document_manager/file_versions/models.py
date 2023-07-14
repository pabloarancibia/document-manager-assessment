from django.db import models

def custom_directory_path(instance, filename):
    path = instance.url_setted
    return '{0}/{1}'.format(path, filename)

class FileVersion(models.Model):
    file_name = models.fields.CharField(max_length=512, blank=True)
    version_number = models.fields.IntegerField(blank=True, default=1)
    url_file = models.FileField(upload_to=custom_directory_path)
    url_setted = models.CharField(max_length=512)
    file_user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.file_name
    
