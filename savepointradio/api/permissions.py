from rest_framework import permissions


class IsAdminOrOwner(permissions.BasePermission):
    message = 'Only an admin user or owner can access this.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated():
            return request.user.is_staff or request.user == obj.user
        else:
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    message = 'Only an admin user can make changes.'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return (request.user.is_authenticated and
                    request.user.is_staff and
                    not request.user.is_dj)


class IsAdminOwnerOrReadOnly(permissions.BasePermission):
    message = 'Only an admin user or the owner can change this object.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user.is_authenticated:
                return ((request.user.is_staff or
                        request.user == obj.user) and
                        not request.user.is_dj)
            else:
                return False


class IsDJ(permissions.BasePermission):
    message = 'Only the DJ can request the next song.'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_dj
        else:
            return False
