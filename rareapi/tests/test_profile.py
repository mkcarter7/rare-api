import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rareapi.models import RareUser, Category, Post


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return RareUser.objects.create_user(username="author", password="x", is_active=True)


@pytest.fixture
def other_user(db):
    return RareUser.objects.create_user(username="other", password="x", is_active=True)


@pytest.fixture
def category(db):
    return Category.objects.create(label="General")


@pytest.fixture
def auth_client(api_client, user):
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


def make_post(user, category, title="Post", approved=True, days_offset=0):
    return Post.objects.create(
        user=user,
        category=category,
        title=title,
        publication_date=date.today() + timedelta(days=days_offset),
        content="content",
        approved=approved,
    )


class TestPostCount:
    def test_zero_posts_returns_zero(self, auth_client, user):
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.status_code == 200
        assert response.json()["post_count"] == 0

    def test_approved_posts_are_counted(self, auth_client, user, category):
        make_post(user, category, title="A")
        make_post(user, category, title="B")
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.json()["post_count"] == 2

    def test_unapproved_posts_not_counted(self, auth_client, user, category):
        make_post(user, category, approved=False)
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.json()["post_count"] == 0

    def test_only_approved_posts_count_in_mix(self, auth_client, user, category):
        make_post(user, category, title="A", approved=True)
        make_post(user, category, title="B", approved=True)
        make_post(user, category, title="C", approved=True)
        make_post(user, category, title="D", approved=False)
        make_post(user, category, title="E", approved=False)
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.json()["post_count"] == 3

    def test_other_users_posts_not_included(self, auth_client, user, other_user, category):
        make_post(other_user, category)
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.json()["post_count"] == 0

    def test_future_dated_approved_post_is_counted(self, auth_client, user, category):
        # Approved but not yet live in feeds — still counts toward post_count
        make_post(user, category, days_offset=7)
        response = auth_client.get(f"/profiles/{user.id}")
        assert response.json()["post_count"] == 1
