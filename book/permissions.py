from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBookAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user == obj.author and obj.author.role == 1


class IsAuthorRole(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 1
    

class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.commenter
        