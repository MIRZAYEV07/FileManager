from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_superuser


class HasScopePermission(permissions.BasePermission):
    required_scopes = []

    def has_permission(self, request, view):
        # Ensure the token has the required scopes
        token_scopes = request.auth.get('scopes', [])
        return any(scope in token_scopes for scope in self.required_scopes)