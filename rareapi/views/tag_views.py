from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rareapi.authentication import RareAuthentication
from rareapi.models import Tag


@api_view(['GET', 'POST'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def tags(request):
    if request.method == 'GET':
        all_tags = Tag.objects.order_by('label')
        tag_list = [{'id': tag.id, 'label': tag.label} for tag in all_tags]
        return Response(tag_list)

    if request.method == 'POST':
        new_tag = Tag.objects.create(label=request.data.get('label'))
        return Response({'id': new_tag.id, 'label': new_tag.label}, status=201)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([RareAuthentication])
@permission_classes([IsAuthenticated])
def tag_detail(request, pk):
    try:
        tag = Tag.objects.get(pk=pk)
    except Tag.DoesNotExist:
        return Response({'error': 'Tag not found'}, status=404)

    if request.method == 'GET':
        return Response({'id': tag.id, 'label': tag.label})

    if request.method == 'PUT':
        tag.label = request.data.get('label', tag.label)
        tag.save()
        return Response({'id': tag.id, 'label': tag.label})

    if request.method == 'DELETE':
        tag.delete()
        return Response(status=204)
