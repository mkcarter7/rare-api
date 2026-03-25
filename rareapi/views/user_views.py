import os
from django.conf import settings
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rareapi.authentication import RareAuthentication
from rareapi.models import RareUser, Subscription, DemotionQueue


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
            'active': user.active,
        }
        for user in users
    ]
    return Response(data)


@api_view(['PUT'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def deactivate_user(request, pk):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=403)

    try:
        user = RareUser.objects.get(pk=pk)
    except RareUser.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    if user.is_staff:
        action = f"deactivate:{pk}"

        if DemotionQueue.objects.filter(action=action, admin=request.user).exists():
            return Response(
                {'error': 'You have already voted to deactivate this admin. A second admin must also approve.'},
                status=400
            )

        existing_votes = DemotionQueue.objects.filter(action=action)
        if existing_votes.exists():
            remaining_admins = RareUser.objects.filter(is_staff=True, active=True).exclude(pk=pk).count()
            if remaining_admins == 0:
                return Response(
                    {'error': 'Cannot deactivate the last admin. Make someone else an admin first.'},
                    status=400
                )
            existing_votes.delete()
            user.active = False
            user.save()
            return Response(status=204)

        DemotionQueue.objects.create(action=action, admin=request.user, approver_one=request.user)
        return Response(
            {'message': 'Deactivation request queued. A second admin must also approve to complete this action.'},
            status=202
        )

    user.active = False
    user.save()
    return Response(status=204)


@api_view(['PUT'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def reactivate_user(request, pk):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=403)

    try:
        user = RareUser.objects.get(pk=pk)
    except RareUser.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    user.active = True
    user.save()
    return Response(status=204)


@api_view(['PUT'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def change_user_type(request, pk):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=403)

    try:
        user = RareUser.objects.get(pk=pk)
    except RareUser.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    user_type = request.data.get('user_type')
    if user_type == 'Admin':
        user.is_staff = True
        user.save()
        return Response(status=204)
    elif user_type == 'Author':
        if user.is_staff:
            action = f"demote:{pk}"

            if DemotionQueue.objects.filter(action=action, admin=request.user).exists():
                return Response(
                    {'error': 'You have already voted to demote this admin. A second admin must also approve.'},
                    status=400
                )

            existing_votes = DemotionQueue.objects.filter(action=action)
            if existing_votes.exists():
                remaining_admins = RareUser.objects.filter(is_staff=True, active=True).exclude(pk=pk).count()
                if remaining_admins == 0:
                    return Response(
                        {'error': 'Cannot change the last admin to Author. Make someone else an admin first.'},
                        status=400
                    )
                existing_votes.delete()
                user.is_staff = False
                user.save()
                return Response(status=204)

            DemotionQueue.objects.create(action=action, admin=request.user, approver_one=request.user)
            return Response(
                {'message': 'Demotion request queued. A second admin must also approve to complete this action.'},
                status=202
            )

        user.is_staff = False
        user.save()
        return Response(status=204)
    else:
        return Response({'error': 'Invalid user_type'}, status=400)


@api_view(['GET'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def demotion_queue_list(request):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=403)

    queue_items = DemotionQueue.objects.select_related('admin').all()
    data = []
    for item in queue_items:
        parts = item.action.split(':')
        action_type = parts[0]
        target_id = int(parts[1])
        try:
            target = RareUser.objects.get(pk=target_id)
            target_username = target.username
        except RareUser.DoesNotExist:
            target_username = 'Unknown'

        data.append({
            'id': item.id,
            'action': item.action,
            'action_type': action_type,
            'target_id': target_id,
            'target_username': target_username,
            'initiated_by_id': item.admin.id,
            'initiated_by': item.admin.username,
        })

    return Response(data)


@api_view(['PUT'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def upload_profile_image(request, pk):
    if request.user.id != pk:
        return Response({'error': 'Forbidden'}, status=403)

    if 'image' not in request.FILES:
        return Response({'error': 'No image provided'}, status=400)

    image = request.FILES['image']
    filename = f"profile_{pk}_{image.name}"
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'profile_images')
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)
    with open(filepath, 'wb+') as dest:
        for chunk in image.chunks():
            dest.write(chunk)

    relative_url = f"{settings.MEDIA_URL}profile_images/{filename}"
    absolute_url = request.build_absolute_uri(relative_url)

    try:
        user = RareUser.objects.get(pk=pk)
    except RareUser.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    user.profile_image_url = absolute_url
    user.save()

    return Response({'profile_image_url': absolute_url})


@api_view(['DELETE'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def cancel_demotion_queue_item(request, pk):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=403)

    try:
        item = DemotionQueue.objects.get(pk=pk)
    except DemotionQueue.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    if item.admin != request.user:
        return Response({'error': 'You can only cancel your own votes.'}, status=403)

    item.delete()
    return Response(status=204)
