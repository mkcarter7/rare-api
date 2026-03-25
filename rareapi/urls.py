from django.urls import path
from .views import login_user, register_user, tags, tag_detail, post_list, post_detail, post_tags, category_list, category_detail, my_post_list, post_comments, comment_detail, profile_list, profile_detail, deactivate_user, reactivate_user, change_user_type, user_post_list, subscribe, unsubscribe, subscribed_posts

urlpatterns = [
    path('login', login_user, name='login'),
    path('register', register_user, name='register'),
    path('tags', tags, name='tags'),
    path('tags/<int:pk>', tag_detail, name='tag_detail'),
    path('categories', category_list, name='category_list'),
    path('categories/<int:pk>', category_detail, name='category_detail'),
    path('posts', post_list, name='post_list'),
    path('posts/<int:pk>', post_detail, name='post_detail'),
    path('posts/<int:pk>/tags', post_tags, name='post_tags'),
    path('myposts', my_post_list, name='my_post_list'),
    path('posts/<int:pk>/comments', post_comments, name='post_comments'),
    path('comments/<int:pk>', comment_detail, name='comment_detail'),
    path('profiles', profile_list, name='profile_list'),
    path('profiles/<int:pk>', profile_detail, name='profile_detail'),
    path('profiles/<int:pk>/deactivate', deactivate_user, name='deactivate_user'),
    path('profiles/<int:pk>/reactivate', reactivate_user, name='reactivate_user'),
    path('profiles/<int:pk>/type', change_user_type, name='change_user_type'),
    path('profiles/<int:user_id>/posts', user_post_list, name='user_post_list'),
    path('profiles/<int:author_id>/subscribe', subscribe, name='subscribe'),
    path('profiles/<int:author_id>/unsubscribe', unsubscribe, name='unsubscribe'),
    path('subscribedposts', subscribed_posts, name='subscribed_posts'),
]
