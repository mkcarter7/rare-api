from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rareapi.authentication import RareAuthentication
from rareapi.models import Reaction, PostReaction, Post


@api_view(['GET', 'POST'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def reaction_list(request):
    if request.method == 'POST':
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=403)
        reaction = Reaction.objects.create(
            label=request.data.get('label'),
            image_url=request.data.get('image_url')
        )
        return Response({'id': reaction.id, 'label': reaction.label, 'image_url': reaction.image_url}, status=201)

    reactions = Reaction.objects.order_by('label')
    data = [{'id': r.id, 'label': r.label, 'image_url': r.image_url} for r in reactions]
    return Response(data)


@api_view(['GET', 'POST'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def post_reaction_list(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)

    if request.method == 'POST':
        reaction_id = request.data.get('reaction_id')
        try:
            reaction = Reaction.objects.get(pk=reaction_id)
        except Reaction.DoesNotExist:
            return Response({'error': 'Reaction not found'}, status=404)
        PostReaction.objects.create(user=request.user, post=post, reaction=reaction)
        return Response(status=201)

    reactions = Reaction.objects.order_by('label')
    user_reaction_ids = set(
        PostReaction.objects.filter(post=post, user=request.user).values_list('reaction_id', flat=True)
    )
    data = []
    for r in reactions:
        count = PostReaction.objects.filter(post=post, reaction=r).count()
        data.append({
            'id': r.id,
            'label': r.label,
            'image_url': r.image_url,
            'count': count,
            'user_reacted': r.id in user_reaction_ids,
        })
    return Response(data)


@api_view(['DELETE'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def post_reaction_detail(request, pk, reaction_id):
    try:
        post_reaction = PostReaction.objects.get(post_id=pk, reaction_id=reaction_id, user=request.user)
    except PostReaction.DoesNotExist:
        return Response({'error': 'Reaction not found'}, status=404)
    post_reaction.delete()
    return Response(status=204)
