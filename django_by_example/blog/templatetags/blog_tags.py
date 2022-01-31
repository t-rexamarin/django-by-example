from django import template
from ..models import Post
from django.db.models import Count


register = template.Library()


@register.simple_tag
# @register.simple_tag(name='my_tag')  # if custom name needed. function name by default
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    context = {
        'latest_posts': latest_posts
    }
    return context


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')
                                   ).order_by('-total_comments')[:count]
