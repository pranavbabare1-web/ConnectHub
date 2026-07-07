# ConnectHub — Modern Social Media Platform

A production-ready social media platform built with Django 5+, featuring a dark/light UI inspired by Instagram, Threads, and X.

---

## Features

- **Authentication** — Register, login, logout, password change
- **User Profiles** — Profile picture, cover photo, bio, location, website
- **Social Feed** — Paginated home feed of posts from followed users
- **Posts** — Create with text & images, delete own posts
- **Likes** — AJAX-powered, no page reload
- **Comments** — AJAX add/delete, live count updates
- **Follow System** — Follow/unfollow with real-time toggle
- **Notifications** — Follow, like, and comment events with unread counter
- **Search** — Find users by name or username
- **Admin Dashboard** — Full Django admin with search, filters, actions
- **Dark/Light Mode** — Persistent theme toggle

---

## Tech Stack

- **Backend**: Django 5+, Python 3.12+
- **Database**: SQLite (dev) — easily migratable to PostgreSQL/MySQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (no frameworks)
- **Media**: Pillow for image handling

---

## Project Structure

```
connecthub/
├── manage.py
├── requirements.txt
├── connecthub/              # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── social/                  # Main app
│   ├── models.py            # Profile, Post, Comment, Like, Follow, Notification
│   ├── views.py             # All views
│   ├── forms.py             # RegisterForm, PostForm, ProfileUpdateForm, etc.
│   ├── urls.py              # URL routing
│   ├── admin.py             # Admin configuration
│   ├── signals.py           # Auto-profile creation
│   ├── context_processors.py
│   ├── templatetags/
│   │   └── social_tags.py   # is_liked_by, is_following filters
│   ├── templates/social/    # All HTML templates
│   └── management/commands/
│       └── create_sample_data.py
├── static/
│   ├── css/style.css        # Full design system
│   ├── js/main.js           # AJAX interactions, theme toggle
│   └── images/default.png   # Default profile picture
└── media/                   # User-uploaded files (gitignored)
```

---

## Setup & Installation

### 1. Clone / Copy the project

```bash
cd connecthub
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Load sample test data (optional)

```bash
python manage.py create_sample_data
```

This creates:
| Username | Password | Role |
|----------|----------|------|
| alice | password123 | User |
| bob | password123 | User |
| carol | password123 | User |
| admin | admin123 | Superuser |

### 6. Collect static files (for production)

```bash
python manage.py collectstatic
```

### 7. Run the development server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

Admin panel: **http://127.0.0.1:8000/admin**

---

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/home/` | Social feed (auth required) |
| `/register/` | Create account |
| `/login/` | Sign in |
| `/profile/<username>/` | User profile |
| `/settings/profile/` | Edit profile |
| `/notifications/` | Notification center |
| `/search/?q=` | Search users |
| `/admin/` | Django admin |

---

## Database Models

| Model | Key Fields |
|-------|-----------|
| Profile | user, profile_image, cover_image, bio, location, website |
| Post | user, content, image, created_at |
| Comment | user, post, text, created_at |
| Like | user, post (unique_together) |
| Follow | follower, following (unique_together) |
| Notification | sender, receiver, type, post, is_read |

---

## Migrating to PostgreSQL

In `settings.py`, replace the `DATABASES` block:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'connecthub_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Then: `pip install psycopg2-binary` and re-run migrations.

---

## Security Notes

- Change `SECRET_KEY` in `settings.py` before deploying
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` with your domain
- Use environment variables (python-decouple) for secrets
