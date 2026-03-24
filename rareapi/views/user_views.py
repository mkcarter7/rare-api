from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rareapi.authentication import RareAuthentication
from rareapi.models import RareUser, Subscription


@api_view(['GET'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def profile_detail(request, pk):
    try:
        user = RareUser.objects.get(pk=pk)
    except RareUser.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    is_subscribed = Subscription.objects.filter(
        follower=request.user,
        author=user,
        ended_on__isnull=True
    ).exists()

    subscriber_count = Subscription.objects.filter(
        author=user,
        ended_on__isnull=True
    ).count()

    data = {
        'id': user.id,
        'full_name': f'{user.first_name} {user.last_name}'.strip(),
        'username': user.username,
        'email': user.email,
        'profile_image_url': user.profile_image_url,
        'created_on': user.created_on.strftime('%m/%d/%Y'),
        'user_type': 'Admin' if user.is_staff else 'Author',
        'is_subscribed': is_subscribed,
        'subscriber_count': subscriber_count,
    }
    return Response(data)


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
