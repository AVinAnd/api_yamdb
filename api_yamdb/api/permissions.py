from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        """Доступно администратору"""
        return request.user.is_authenticated and (
                request.user.role == 'admin' or request.user.is_superuser)


class IsSuperUserIsAdminIsModeratorIsAuthor(permissions.BasePermission):
    """
    Разрешает анонимному пользователю только безопасные запросы.
    POST запросы разрешаются авторизированным пользователям.
    Доступ к запросам PATCH и DELETE предоставляется только
    пользователям с правами администратора или модераторам,
    а также автору объекта.
    """
    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.role == 'admin'
                 or request.user.role == 'moderator'
                 or request.user == obj.author)
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает редактирование пользователям с правами администратора"""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.role == 'admin')
        )
