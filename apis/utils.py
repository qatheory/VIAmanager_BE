
from apis.serializers import UserFullSerializer


def custom_jwt_response_handler(token, user=None, request=None):
    return {
        "token": token,
        "user": UserFullSerializer(user, context={"request": request}).data
    }
