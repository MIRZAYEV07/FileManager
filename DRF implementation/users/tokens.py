from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    refresh['is_superuser'] = user.is_superuser
    refresh['scopes'] = ['admin'] if user.is_superuser else ['user']

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }