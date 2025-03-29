from rest_framework_simplejwt.authentication import JWTAuthentication
from bson import ObjectId
from api.models import User  

class MongoDBJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")

        if not user_id:
            return None

        try:
            return User.objects.get(id=ObjectId(user_id))
        except User.DoesNotExist:
            return None
