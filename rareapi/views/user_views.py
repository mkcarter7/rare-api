from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rareapi.authentication import RareAuthentication
from rareapi.models import RareUser


@api_view(['GET'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def profile_list(request):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=403)

    users = RareUser.objects.order_by('username')
    data = [
        {
            'id': user.id,
            'full_name': f'{user.first_name} {user.last_name}'.strip(),
            'username': user.username,
            'user_type': 'Admin' if user.is_staff else 'Author',
        }
        for user in users
    ]
    return Response(data)
