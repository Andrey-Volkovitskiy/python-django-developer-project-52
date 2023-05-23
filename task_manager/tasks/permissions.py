from rest_framework import permissions


class DeleteOnlyByAuthor(permissions.BasePermission):
    """Custom permission: only the author can delete a task."""
    def has_object_permission(self, request, view, obj):
        if request.method != 'DELETE':
            return True

        return obj.author == request.user
