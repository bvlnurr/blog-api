from django.contrib import admin, messages
from django.db.models import Count
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from unfold.sections import TableSection

from .models import Category, Comment, Post, Tag


class CategoryPostsSection(TableSection):
    verbose_name = "Posts"
    related_name = "posts"
    fields = ["title", "status", "created_at"]

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("id", "name", "slug", "posts_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_sections = [CategoryPostsSection]
    list_per_page = 20

    def get_queryset(self, request):
        return (
            super().get_queryset(request).annotate(total_posts=Count("posts")).prefetch_related("posts")
        )

    @admin.display(description="Posts", ordering="total_posts")
    def posts_count(self, obj):
        return obj.total_posts
    


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("id", "name", "slug", "posts_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_posts=Count("posts")
        )
    
    @admin.display(description="Posts", ordering="total_posts")
    def posts_count(self, obj):
        return obj.total_posts


class CommentInline(TabularInline):
    model = Comment
    extra = 0
    autocomplete_fields = ("author",)



@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "category",
        "colored_status",
        "tags_count",
        "created_at",
    )
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "body", "author__email", "category__name", "tags__name",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CommentInline]
    autocomplete_fields = ("author", "category", "tags")
    date_hierarchy = "created_at"
    save_on_top = True
    actions = ["punlish_posts", "make_drafts"]
    list_filter_sheet = True
    list_fullwidth = True
    list_display_links = ("id", "title")
    list_select_related = ("author", "category")
    ordering = ("-created_at",)
    list_per_page = 20
    

    @admin.action(description="Publish selected posts")
    def publish_posts(self, request, queryset):
        count = queryset.update(status=Post.Status.PUBLISHED)
        self.message_user(
            request,
            f"{count} posts publised",
            messages.SUCCESS,
        )

    @admin.action(description="Move selected posts to drafts")
    def make_drafts(self, request, queryset):
        count = queryset.update(status=Post.Status.DRAFT)
        self.message_user(
            request,
            f"{count} posts moved to drafts",
            messages.SUCCESS,
        )


    def get_queryset(self, request):
        return(
            super().get_queryset(request).annotate(total_tags=Count("tags"))
        )
    
    @admin.display(description="Tags", ordering="total_tags")
    def tags_count(self, obj):
        return obj.total_tags
    
    @display(
        description="Status",
        label={
            Post.Status.PUBLISHED: "success",
            Post.Status.DRAFT: "warning",
        },

    )

    def colored_status(self, obj):
        return obj.status

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("id", "post", "author", "short_body", "created_at")
    search_fields = ("body", "post__title", "author__email",)
    list_filter = ("created_at",)
    list_select_related = ("post", "author")
    list_display_links = ("id", "short_body")
    autocomplete_fields = ("post", "author")
    ordering = ("-created_at",)
    list_per_page = 20
    date_hierarchy = "created_at"

    @admin.display(description="Comment")
    def short_body(self, obj):
        return obj.body[:60]

