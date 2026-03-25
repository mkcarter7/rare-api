from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rareapi.models import RareUser


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = RareUser.objects.get(username=username)
        if user.check_password(password) and user.active:
            return Response({
                'valid': True,
                'token': user.id,
                'is_staff': user.is_staff
            })
        else:
            return Response({'valid': False})
    except RareUser.DoesNotExist:
        return Response({'valid': False})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register_user(request):
    new_user = RareUser.objects.create_user(
        username=request.data.get('username'),
        password=request.data.get('password'),
        first_name=request.data.get('first_name'),
        last_name=request.data.get('last_name'),
        email=request.data.get('email'),
        bio=request.data.get('bio', ''),
        active=True
    )

    return Response({
        'valid': True,
        'token': new_user.id,
        'is_staff': new_user.is_staff
    })
