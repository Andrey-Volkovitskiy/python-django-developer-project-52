from rest_framework import serializers
from django.contrib.auth.models import User


# class UserSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     username = serializers.CharField(max_length=150)
#     first_name = serializers.CharField(max_length=150, required=False)
#     last_name = serializers.CharField(max_length=150, required=False)
#     password = serializers.CharField()

#     def create(self, validated_data):
#         return User.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         instance.username = validated_data.get('username', instance.username)
#         instance.first_name = validated_data.get(
#           'first_name', instance.first_name)
#         instance.last_name = validated_data.get(
#           'last_name', instance.last_name)
#         instance.password = validated_data.get('password', instance.password)
#         instance.save()
#         return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'date_joined'
        )
