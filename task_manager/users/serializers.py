from rest_framework import serializers
from django.contrib.auth.models import User
from task_manager.tasks.models import Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        author_set = serializers.PrimaryKeyRelatedField(
            many=True, queryset=Task.objects.all())
        executor_set = serializers.PrimaryKeyRelatedField(
            many=True, queryset=Task.objects.all())

        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'date_joined',
            'password',
            'author_set',
            'executor_set',
        )
        read_only_fields = (
            'author_set',
            'executor_set',
            'date_joined',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password', None)
            instance.set_password(password)
        return super().update(instance, validated_data)
