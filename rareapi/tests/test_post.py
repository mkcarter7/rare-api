import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rareapi.models import RareUser, Category, Post


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def regular_user(db):
    return RareUser.objects.create_user(username="author", password="x", is_active=True)


@pytest.fixture
def staff_user(db):
    return RareUser.objects.create_user(username="admin", password="x", is_active=True, is_staff=True)


@pytest.fixture
def category(db):
    return Category.objects.create(label="General")


@pytest.fixture
def regular_client(api_client, regular_user):
    token = Token.objects.create(user=regular_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.fixture
def staff_client(api_client, staff_user):
    token = Token.objects.create(user=staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


def make_post(user, category, approved=True, days_offset=0):
    return Post.objects.create(
        user=user,
        category=category,
        title="Test Post",
        publication_date=date.today() + timedelta(days=days_offset),
        content="content",
        approved=approved,
    )


def post_payload(category):
    return {
        "title": "My Post",
        "content": "Some content",
        "category_id": category.id,
    }


class TestPostCreation:
    def test_nonstaff_post_enters_moderation_queue(self, regular_client, category):
        response = regular_client.post("/posts", post_payload(category))
        assert response.status_code == 201
        assert response.json()["approved"] is False

    def test_staff_post_is_auto_approved(self, staff_client, category):
        response = staff_client.post("/posts", post_payload(category))
        assert response.status_code == 201
        assert response.json()["approved"] is True

    def test_post_with_invalid_category_returns_400(self, regular_client):
        response = regular_client.post("/posts", {"title": "X", "content": "Y", "category_id": 99999})
        assert response.status_code == 400


class TestPublicPostList:
    def test_only_approved_posts_are_visible(self, regular_client, regular_user, category):
        approved = make_post(regular_user, category, approved=True)
        make_post(regular_user, category, approved=False)
        response = regular_client.get("/posts")
        ids = [p["id"] for p in response.json()]
        assert approved.id in ids
        assert len(ids) == 1

    def test_future_dated_post_is_hidden(self, regular_client, regular_user, category):
        make_post(regular_user, category, approved=True, days_offset=1)
        response = regular_client.get("/posts")
        assert response.json() == []


class TestUnapprovedPostList:
    def test_nonstaff_gets_403(self, regular_client, regular_user, category):
        make_post(regular_user, category, approved=False)
        response = regular_client.get("/unapprovedposts")
        assert response.status_code == 403

    def test_staff_sees_only_unapproved(self, staff_client, regular_user, category):
        unapproved = make_post(regular_user, category, approved=False)
        approved = make_post(regular_user, category, approved=True)
        response = staff_client.get("/unapprovedposts")
        assert response.status_code == 200
        ids = [p["id"] for p in response.json()]
        assert unapproved.id in ids
        assert approved.id not in ids


class TestPostSearch:
    def test_author_filter_returns_only_that_authors_posts(self, db, regular_client, category):
        author_a = RareUser.objects.create_user(username="alice", password="x", is_active=True)
        author_b = RareUser.objects.create_user(username="bob", password="x", is_active=True)
        post_a = Post.objects.create(
            user=author_a, category=category, title="Alpha post",
            publication_date=date.today(), content="x", approved=True,
        )
        Post.objects.create(
            user=author_b, category=category, title="Beta post",
            publication_date=date.today(), content="x", approved=True,
        )
        response = regular_client.get(f"/posts/search?q=post&author={author_a.id}")
        assert response.status_code == 200
        ids = [p["id"] for p in response.json()]
        assert ids == [post_a.id]

    def test_author_filter_with_no_q_returns_empty(self, db, regular_client, category):
        author_a = RareUser.objects.create_user(username="alice2", password="x", is_active=True)
        response = regular_client.get(f"/posts/search?author={author_a.id}")
        assert response.status_code == 200
        assert response.json() == []

    def test_search_without_author_returns_all_matching(self, db, regular_client, category):
        author_a = RareUser.objects.create_user(username="alice3", password="x", is_active=True)
        author_b = RareUser.objects.create_user(username="bob3", password="x", is_active=True)
        post_a = Post.objects.create(
            user=author_a, category=category, title="Gamma post",
            publication_date=date.today(), content="x", approved=True,
        )
        post_b = Post.objects.create(
            user=author_b, category=category, title="Delta post",
            publication_date=date.today(), content="x", approved=True,
        )
        response = regular_client.get("/posts/search?q=post")
        ids = [p["id"] for p in response.json()]
        assert post_a.id in ids
        assert post_b.id in ids


class TestApprovePost:
    def test_nonstaff_gets_403(self, regular_client, regular_user, category):
        post = make_post(regular_user, category, approved=False)
        response = regular_client.put(f"/posts/{post.id}/approve")
        assert response.status_code == 403

    def test_staff_approves_post(self, staff_client, regular_user, category):
        post = make_post(regular_user, category, approved=False)
        response = staff_client.put(f"/posts/{post.id}/approve")
        assert response.status_code == 200
        assert response.json()["approved"] is True


class TestUnapprovePost:
    def test_nonstaff_gets_403(self, regular_client, regular_user, category):
        post = make_post(regular_user, category, approved=True)
        response = regular_client.put(f"/posts/{post.id}/unapprove")
        assert response.status_code == 403

    def test_staff_unapproves_post(self, staff_client, regular_user, category):
        post = make_post(regular_user, category, approved=True)
        response = staff_client.put(f"/posts/{post.id}/unapprove")
        assert response.status_code == 200
        assert response.json()["approved"] is False
