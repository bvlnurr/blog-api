import json

from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.db.models import Count

from .models import Category, Comment, Post

User = get_user_model()


def dashboard_callback(request, context):
    context["log_entries"] = (
        LogEntry.objects.select_related("user", "content_type")
        .order_by("-action_time")
    )

    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(
        status=Post.Status.PUBLISHED
    ).count()
    draft_posts = Post.objects.filter(
        status=Post.Status.DRAFT
    ).count()

    categories = (
        Category.objects.annotate(post_count=Count("posts"))
        .order_by("name")
    )

    chart_data = {
        "labels": [category.name for category in categories],
        "datasets": [
            {
                "label": "Posts",
                "data": [
                    category.post_count for category in categories
                ],
                "backgroundColor": "#6366f1",
            }
        ],
    }

    top_authors = (
        User.objects.annotate(post_count=Count("posts"))
        .filter(post_count__gt=0)
        .order_by("-post_count", "email")[:5]
    )

    context.update({
        "total_users": User.objects.count(),
        "total_posts": total_posts,
        "published_posts": published_posts,
        "draft_posts": draft_posts,
        "total_comments": Comment.objects.count(),
        "category_chart": json.dumps(chart_data),
        "top_authors": top_authors,
        "published_percent": (
            round(published_posts / total_posts * 100)
            if total_posts else 0
        ),
        "draft_percent": (
            round(draft_posts / total_posts * 100)
            if total_posts else 0
        ),
    })

    return context