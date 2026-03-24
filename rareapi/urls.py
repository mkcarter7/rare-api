from django.urls import path
from .views import login_user, register_user, tags, post_list, post_detail, post_tags

urlpatterns = [
    path('login', login_user, name='login'),
    path('register', register_user, name='register'),
    path('tags', tags, name='tags'),
    path('posts', post_list, name='post_list'),
    path('posts/<int:pk>', post_detail, name='post_detail'),
    path('posts/<int:pk>/tags', post_tags, name='post_tags'),
]
