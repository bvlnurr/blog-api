# blog-api

Blog API project built with Django and Django REST Framework.

## Features

- Custom User model with email authentication
- Posts
- Categories
- Tags
- Comments

## ERD Diagram

![ERD Diagram](docs/ERD.png)


## Installation

```bash
pip install -r requirements/dev.txt
python3 manage.py migrate
python3 manage.py seed
python3 manage.py createsuperuser
python3 manage.py runserver
```

## Database Seeding

Default: 20 users, 100 posts, 500 comments.

```bash
python3 manage.py seed
```

Custom arguments:

```bash
python3 manage.py seed --users 50 --posts 300 --comments 1500
```

Clear data (except superusers):

```bash
python3 manage.py seed --clear
```

## Admin Screenshots

### Dashboard
![Dashboard](docs/screenshots/Dashboard.png)

### Posts with Filters
![Posts](docs/screenshots/PostsFilter.png)

### Post Edit
![Post Edit](docs/screenshots/PostsEditPage.png)

### Users
![Users](docs/screenshots/Users.png)

### Categories
![Categories](docs/screenshots/Categories.png)

### Comments
![Comments](docs/screenshots/Comments.png)

### Tags
![Tags](docs/screenshots/Tags.png)
