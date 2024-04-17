from django.urls import path
from .views import UserDetailView, UserCreateView, UserMeView, ChangePasswordView

urlpatterns = [
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/me/', UserMeView.as_view(), name='user-me'),
    path('users/change-password/', ChangePasswordView.as_view(), name='change-password'),
]