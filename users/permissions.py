from rest_framework.permissions import BasePermission

from users.models import User


class IsOrganizerPermission(BasePermission):
    """
    Разрешает доступ только пользователям которые организаторы.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.RoleChoices.ORGANIZER)
