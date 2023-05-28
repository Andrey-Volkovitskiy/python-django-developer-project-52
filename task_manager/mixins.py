from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class CustomLoginRequiredMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        messages.add_message(
            self.request,
            messages.ERROR,
            self.permission_denied_message)
        return super().handle_no_permission()
