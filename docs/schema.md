# Rare API — Database Schema

## Entity Relationship Diagram

```mermaid
erDiagram
    RareUser {
        int id PK
        string username
        string password
        string first_name
        string last_name
        string email
        bool is_staff
        bool is_active
        datetime date_joined
        string bio
        string profile_image_url
        date created_on
    }

    Category {
        int id PK
        string label
    }

    Tag {
        int id PK
        string label
    }

    Post {
        int id PK
        int user_id FK
        int category_id FK
        string title
        date publication_date
        string image_url
        text content
        bool approved
    }

    PostTag {
        int id PK
        int post_id FK
        int tag_id FK
    }

    Comment {
        int id PK
        int post_id FK
        int author_id FK
        string subject
        text content
        datetime created_on
    }

    Reaction {
        int id PK
        string label
        string image_url
    }

    PostReaction {
        int id PK
        int user_id FK
        int reaction_id FK
        int post_id FK
    }

    Subscription {
        int id PK
        int follower_id FK
        int author_id FK
        date created_on
        datetime ended_on
    }

    DemotionQueue {
        int id PK
        string action
        int admin_id FK
        int approver_one_id FK
    }

    RareUser ||--o{ Post : "writes"
    Category ||--o{ Post : "categorizes"
    Post ||--o{ PostTag : "has"
    Tag ||--o{ PostTag : "applied via"
    Post ||--o{ Comment : "receives"
    RareUser ||--o{ Comment : "authors"
    Post ||--o{ PostReaction : "receives"
    RareUser ||--o{ PostReaction : "gives"
    Reaction ||--o{ PostReaction : "used in"
    RareUser ||--o{ Subscription : "follows (follower)"
    RareUser ||--o{ Subscription : "is followed by (author)"
    RareUser ||--o{ DemotionQueue : "initiates (admin)"
    RareUser ||--o{ DemotionQueue : "approves (approver_one)"
```

---

## Model Reference

### RareUser
Extends Django's `AbstractUser`.

| Field | Type | Notes |
|---|---|---|
| id | AutoField | PK |
| username | CharField | Unique |
| password | CharField | Hashed |
| first_name | CharField | |
| last_name | CharField | |
| email | EmailField | |
| is_staff | BooleanField | `True` = Admin role |
| is_active | BooleanField | `False` = deactivated account |
| date_joined | DateTimeField | Auto-set |
| bio | CharField(500) | |
| profile_image_url | CharField(500) | Path in `media/profile_images/` |
| created_on | DateField | Auto-set on creation |

---

### Post

| Field | Type | Notes |
|---|---|---|
| id | AutoField | PK |
| user | FK → RareUser | `CASCADE`, `related_name='posts'` |
| category | FK → Category | `CASCADE`, `related_name='posts'` |
| title | CharField(300) | |
| publication_date | DateField | |
| image_url | CharField(500) | Optional; path in `media/post_images/` |
| content | TextField | |
| approved | BooleanField | Default `False`; admins auto-publish |

---

### Category

| Field | Type | Notes |
|---|---|---|
| id | AutoField | PK |
| label | CharField(200) | |

---

### Tag

| Field | Type | Notes |
|---|---|---|
| id | AutoField | PK |
| label | CharField(200) | |

---

### PostTag (junction)

| Field | Type | Notes |
|---|---|---|
| id | AutoField | PK |
| post | FK → Post | `CASCADE`, `related_name='post_tags'` |
| tag | FK → Tag | `CASCADE`, `related_name='post_tags'` |

---

### Comment

| Field | Type | Notes |
|---|---|---|
| id | AutoField | PK |
| post | FK → Post | `CASCADE`, `related_name='comments'` |
| author | FK → RareUser | `CASCADE`, `related_name='comments'` |
| subject | CharField(300) | Default `''` |
| content | TextField | |
| created_on | DateTimeField | Auto-set on creation |

---

### Reaction

| Field | Type | Notes |
|---|---|---|
| id | AutoField | PK |
| label | CharField(200) | |
| image_url | CharField(500) | Emoji / icon URL |

---

### PostReaction (junction)

| Field | Type | Notes |
|---|---|---|
| id | AutoField | PK |
| user | FK → RareUser | `CASCADE`, `related_name='post_reactions'` |
| reaction | FK → Reaction | `CASCADE`, `related_name='post_reactions'` |
| post | FK → Post | `CASCADE`, `related_name='post_reactions'` |

---

### Subscription

| Field | Type | Notes |
|---|---|---|
| id | AutoField | PK |
| follower | FK → RareUser | `CASCADE`, `related_name='subscriptions'` |
| author | FK → RareUser | `CASCADE`, `related_name='subscribers'` |
| created_on | DateField | Auto-set on creation |
| ended_on | DateTimeField | `NULL` = active; set on unsubscribe (soft delete) |

---

### DemotionQueue

| Field | Type | Notes |
|---|---|---|
| id | AutoField | PK |
| action | CharField(200) | Format: `"action_type:target_user_id"` |
| admin | FK → RareUser | First admin who initiated the action |
| approver_one | FK → RareUser | Second admin who approved |
| (unique_together) | | `(action, admin, approver_one)` |
