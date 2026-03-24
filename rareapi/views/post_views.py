from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rareapi.authentication import RareAuthentication
from rareapi.models import Post, Tag, PostTag, Category


def serialize_post(post):
    tags = [
        {'id': pt.tag.id, 'label': pt.tag.label}
        for pt in post.post_tags.select_related('tag').all()
    ]
    return {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'publication_date': post.publication_date,
        'image_url': post.image_url,
        'approved': post.approved,
        'user': {'id': post.user.id, 'username': post.user.username},
        'category': {'id': post.category.id, 'label': post.category.label} if post.category else None,
        'tags': tags,
    }


@api_view(['GET', 'POST'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def post_list(request):
    if request.method == 'POST':
        try:
            category = Category.objects.get(pk=request.data.get('category_id'))
        except Category.DoesNotExist:
            return Response({'error': 'Invalid category'}, status=400)

        post = Post.objects.create(
            user=request.user,
            category=category,
            title=request.data.get('title'),
            content=request.data.get('content'),
            image_url=request.data.get('image_url', ''),
            publication_date=timezone.now().date(),
            approved=True,
        )
        return Response(serialize_post(post), status=201)

    posts = (
        Post.objects
        .select_related('user', 'category')
        .filter(approved=True, publication_date__lte=timezone.now().date())
        .order_by('-publication_date')
    )
    data = [
        {
            'id': post.id,
            'title': post.title,
            'publication_date': post.publication_date,
            'user': {'id': post.user.id, 'username': post.user.username},
            'category': {'id': post.category.id, 'label': post.category.label} if post.category else None,
        }
        for post in posts
    ]
    return Response(data)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def post_detail(request, pk):
    try:
        post = Post.objects.select_related('user', 'category').get(pk=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    if request.method == 'DELETE':
        if post.user != request.user:
            return Response({'error': 'Forbidden'}, status=403)
        post.delete()
        return Response(status=204)

    if request.method == 'PUT':
        if post.user != request.user:
            return Response({'error': 'Forbidden'}, status=403)

        try:
            category = Category.objects.get(pk=request.data.get('category_id'))
        except Category.DoesNotExist:
            return Response({'error': 'Invalid category'}, status=400)

        post.title = request.data.get('title', post.title)
        post.content = request.data.get('content', post.content)
        post.image_url = request.data.get('image_url', post.image_url)
        post.category = category
        post.save()

    return Response(serialize_post(post))


@api_view(['GET'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def my_post_list(request):
    posts = (
        Post.objects
        .select_related('user', 'category')
        .filter(user=request.user)
        .order_by('-publication_date', '-id')
    )
    data = [
        {
            'id': post.id,
            'title': post.title,
            'publication_date': post.publication_date,
            'approved': post.approved,
            'user': {'id': post.user.id, 'username': post.user.username},
            'category': {'id': post.category.id, 'label': post.category.label} if post.category else None,
        }
        for post in posts
    ]
    return Response(data)


@api_view(['GET'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def user_post_list(request, user_id):
    posts = (
        Post.objects
        .select_related('user', 'category')
        .filter(user_id=user_id, approved=True)
        .order_by('-publication_date', '-id')
    )
    data = [
        {
            'id': post.id,
            'title': post.title,
            'publication_date': post.publication_date,
            'user': {'id': post.user.id, 'username': post.user.username},
            'category': {'id': post.category.id, 'label': post.category.label} if post.category else None,
        }
        for post in posts
    ]
    return Response(data)


@api_view(['GET'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def subscribed_posts(request):
    subscribed_author_ids = request.user.subscriptions.values_list('author_id', flat=True)
    posts = (
        Post.objects
        .select_related('user', 'category')
        .filter(
            user_id__in=subscribed_author_ids,
            approved=True,
            publication_date__lte=timezone.now().date()
        )
        .order_by('-publication_date')
    )
    data = [
        {
            'id': post.id,
            'title': post.title,
            'publication_date': post.publication_date,
            'user': {'id': post.user.id, 'username': post.user.username},
            'category': {'id': post.category.id, 'label': post.category.label} if post.category else None,
        }
        for post in posts
    ]
    return Response(data)


@api_view(['PUT'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def post_tags(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    if post.user != request.user:
        return Response({'error': 'Forbidden'}, status=403)

    tag_ids = request.data.get('tag_ids', [])
    PostTag.objects.filter(post=post).delete()
    for tag_id in tag_ids:
        try:
            tag = Tag.objects.get(pk=tag_id)
            PostTag.objects.create(post=post, tag=tag)
        except Tag.DoesNotExist:
            pass

    return Response(serialize_post(post))
