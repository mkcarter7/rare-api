from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rareapi.authentication import RareAuthentication
from rareapi.models import RareUser, Subscription


@api_view(['POST'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def subscribe(request, author_id):
    try:
        author = RareUser.objects.get(pk=author_id)
    except RareUser.DoesNotExist:
        return Response({'error': 'Author not found'}, status=404)

    subscription, created = Subscription.objects.get_or_create(
        follower=request.user,
        author=author
    )

    if not created and subscription.ended_on is not None:
        subscription.ended_on = None
        subscription.save()
        return Response({'message': 'Resubscribed successfully'}, status=200)

    if created:
        return Response({'message': 'Subscribed successfully'}, status=201)
    return Response({'message': 'Already subscribed'}, status=200)


@api_view(['DELETE'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def unsubscribe(request, author_id):
    try:
        subscription = Subscription.objects.get(
            follower=request.user,
            author_id=author_id,
            ended_on__isnull=True
        )
    except Subscription.DoesNotExist:
        return Response({'error': 'Subscription not found'}, status=404)

    subscription.ended_on = timezone.now()
    subscription.save()
    return Response({'message': 'Unsubscribed successfully'}, status=200)
