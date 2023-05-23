from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.id')

    class Meta:
        model = Task
        fields = '__all__'
