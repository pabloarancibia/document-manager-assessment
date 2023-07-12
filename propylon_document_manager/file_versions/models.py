from django.db import models

class FileVersion(models.Model):
    file_name = models.fields.CharField(max_length=512)
    version_number = models.fields.IntegerField()
    url_file = models.FileField(upload_to='files')
    url_setted = models.CharField(max_length=512)
    file_user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.file_name