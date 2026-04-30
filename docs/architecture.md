# Rare API — Architecture Overview

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (component-based, feature-organized) |
| Backend | Django 4.2 + Django REST Framework |
| Auth | DRF Token Authentication |
| Database | PostgreSQL |
| Media Storage | Local filesystem (`media/`) |
| Infrastructure | Docker Compose |

---

## High-Level Architecture

```mermaid
graph TD
    Client["React Client\n(rare-client · localhost:3000)"]

    subgraph Docker ["Docker Compose"]
        subgraph Backend ["Django REST API (rare-api · localhost:8000)"]
            Auth["Auth Views\n/login  /register  /me"]
            PostV["Post Views\n/posts  /myposts  /subscribedposts\n/approvedposts  /unapprovedposts"]
            CommentV["Comment Views\n/posts/:id/comments  /comments/:id"]
            UserV["User / Profile Views\n/profiles  /profiles/:id"]
            SubV["Subscription Views\n/profiles/:id/subscribe\n/profiles/:id/unsubscribe"]
            ReactionV["Reaction Views\n/reactions  /posts/:id/reactions"]
            CatV["Category Views\n/categories  /categories/:id/posts"]
            TagV["Tag Views\n/tags  /tags/:id/posts"]
            DemotionV["Demotion Queue Views\n/demotionqueue"]
        end

        subgraph DB ["PostgreSQL Database"]
            RareUser
            Post
            Category
            Tag
            PostTag
            Comment
            Reaction
            PostReaction
            Subscription
            DemotionQueue
        end
    end

    Media["Media Storage\nmedia/post_images\nmedia/profile_images"]

    Client -->|"HTTP + Token · CORS allowed"| Auth
    Client -->|"HTTP + Token"| PostV
    Client -->|"HTTP + Token"| CommentV
    Client -->|"HTTP + Token"| UserV
    Client -->|"HTTP + Token"| SubV
    Client -->|"HTTP + Token"| ReactionV
    Client -->|"HTTP + Token"| CatV
    Client -->|"HTTP + Token"| TagV
    Client -->|"HTTP + Token"| DemotionV

    DemotionV --> AdminSvc
    AdminSvc --> DemotionQueue

    PostV --> Post
    PostV --> Media
    CommentV --> Comment
    UserV --> RareUser
    UserV --> Media
    SubV --> Subscription
    ReactionV --> PostReaction
    CatV --> Category
    TagV --> Tag
    Auth --> RareUser

    Post --> RareUser
    Post --> Category
    PostTag --> Post
    PostTag --> Tag
    Comment --> Post
    Comment --> RareUser
    PostReaction --> Post
    PostReaction --> RareUser
    PostReaction --> Reaction
    Subscription --> RareUser
    DemotionQueue --> RareUser
```

---

## Request / Response Flow

```mermaid
sequenceDiagram
    participant C as React Client
    participant MW as DRF Token Middleware
    participant V as View Function
    participant S as Serializer
    participant DB as PostgreSQL

    C->>MW: HTTP Request + Authorization: Token <token>
    MW->>DB: Validate token → fetch RareUser
    MW->>V: request.user attached
    V->>DB: Query / Mutation
    DB-->>V: QuerySet / Model instance
    V->>S: Serialize data
    S-->>V: Validated / serialized dict
    V-->>C: JSON Response (200/201/204/400/403/404)
```

---

## Feature Modules

| Module | Endpoints | Key Behavior |
|---|---|---|
| Auth | `/login`, `/register`, `/me` | Issues DRF tokens; `me` returns the authenticated user's profile |
| Posts | `/posts`, `/myposts`, `/subscribedposts`, `/approvedposts`, `/unapprovedposts` | Admin posts auto-approve; regular posts enter moderation queue |
| Comments | `/posts/:id/comments`, `/comments/:id` | Full CRUD; only author can edit/delete |
| Profiles | `/profiles`, `/profiles/:id` | Admin-only list; two-vote system for demotion/deactivation |
| Subscriptions | `/profiles/:id/subscribe`, `/profiles/:id/unsubscribe` | Soft-delete model via `ended_on` field |
| Reactions | `/reactions`, `/posts/:id/reactions` | Returns per-reaction counts and `user_reacted` flag |
| Categories | `/categories`, `/categories/:id/posts` | Admin CRUD; any user can filter posts by category |
| Tags | `/tags`, `/tags/:id/posts` | Admin CRUD; authors can tag their own posts |

---

## Admin Two-Vote System

Sensitive admin actions (demoting an admin, deactivating an admin account) require approval from two separate administrators before execution. The `DemotionQueue` table tracks pending votes. Promotions and non-admin account changes execute immediately.

```mermaid
flowchart TD
    A[Admin requests sensitive action] --> B{Target is an Admin?}
    B -- No --> C[Execute immediately]
    B -- Yes --> D{DemotionQueue entry exists?}
    D -- No --> E[Record first vote in DemotionQueue]
    D -- Yes --> F[Second admin approves → Execute action]
    F --> G[DemotionQueue entry removed]
```
