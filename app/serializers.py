from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class AuthTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)


        token['user_id'] = user.user_id
        token['nazwa'] = user.nazwa
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        return token