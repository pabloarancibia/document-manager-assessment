from rest_framework import serializers

from file_versions.models import FileVersion

class FileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileVersion
        fields = "__all__"

# class CreateFileVersionSerializer(serializers.ModelSerializer):
#     file_name = serializers.Charfield()
#     version_number = serializers.IntegerField()
#     url_file = serializers.FileField()
#     url_setted = serializers.CharField()

    # assign file_name = name of file
    # def validate_file_name(self,value):
    #     filename = self.validated_data['url_file']
    #     value = filename
    #     return value

    # search same url_setted in db
    # def validate(self, attrs):
    #     similar_url = FileVersion.objects.filter(url_setted=attrs['url_setted'])


    # # assign version = len of url_setted in db
    # pass