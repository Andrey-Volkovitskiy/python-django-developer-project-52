from django.db import models
from task_manager.statuses.models import Status
from task_manager.labels.models import Label
from django.contrib.auth.models import User


class Task(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
    )
    description = models.TextField(
        blank=True,
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
    )
    executor = models.ForeignKey(
        User,
        related_name='executor_set',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        User,
        related_name='author_set',
        on_delete=models.PROTECT,
    )
    labels = models.ManyToManyField(
        Label,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
