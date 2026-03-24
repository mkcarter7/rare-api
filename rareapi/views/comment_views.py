from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rareapi.authentication import RareAuthentication
from rareapi.models import Comment, Post


def serialize_comment(comment):
    return {
        'id': comment.id,
        'subject': comment.subject,
        'content': comment.content,
        'post': comment.post_id,
        'author': {'id': comment.author.id, 'username': comment.author.username},
    }


@api_view(['GET', 'POST'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def post_comments(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)

    if request.method == 'POST':
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            subject=request.data.get('subject', ''),
            content=request.data.get('content', ''),
        )
        return Response(serialize_comment(comment), status=201)

    comments = Comment.objects.select_related('author').filter(post=post)
    return Response([serialize_comment(c) for c in comments])


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def comment_detail(request, pk):
    try:
        comment = Comment.objects.select_related('author').get(pk=pk)
    except Comment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=404)

    if request.method == 'GET':
        return Response(serialize_comment(comment))

    if comment.author != request.user:
        return Response({'error': 'Forbidden'}, status=403)

    if request.method == 'PUT':
        comment.subject = request.data.get('subject', comment.subject)
        comment.content = request.data.get('content', comment.content)
        comment.save()
        return Response(serialize_comment(comment))

    if request.method == 'DELETE':
        comment.delete()
        return Response(status=204)
