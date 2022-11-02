from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from apps.utils.enums import UserGroup


def staff_access_only():
    """
    Grant permission to staff alone
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.groups.filter(name=UserGroup.STAFF).exists():
                return Response(
                    {
                        "status": status.HTTP_403_FORBIDDEN,
                        "message": "You currently do not have access to this resource",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            response = func(request, *args, **kwargs)
            return response

        return wrapper

    return decorator
