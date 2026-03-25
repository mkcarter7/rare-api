from .auth_views import login_user, register_user
from .user_views import profile_list, profile_detail, deactivate_user, reactivate_user, change_user_type
from .tag_views import tags, tag_detail
from .post_views import post_list, post_detail, post_tags, my_post_list, user_post_list, subscribed_posts
from .category_views import category_list, category_detail
from .comment_views import post_comments, comment_detail
from .subscription_views import subscribe, unsubscribe
