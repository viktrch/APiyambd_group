from rest_framework import permissions


class IsAdminOnly(permissions.BasePermission):
    """Разрешения для администрирования пользователей."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin)
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешения для произведений, категорий, жанров."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin)
        )


class IsAuthorIsModeratorIsAdminOrReadOnly(permissions.BasePermission):
    """Разрешения для комментов и отзывов."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.is_superuser
            or request.user.is_admin
            or request.user.is_moderator
        )
