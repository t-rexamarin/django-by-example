from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .feeds import LatestPostsFeed


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.get_context_data, name='post_list'),
    # path('page/<int:page>/', views.post_list, name='page'),
    path('page/<int:page>/', views.PostListView.get_context_data, name='page'),
    path('tag/<slug:tag_slug>/', views.PostListView.get_context_data, name='post_list_by_tag'),
    # path('', views.PostListView.as_view(), name='post_list'),
    # path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
    path('search/<int:page>/', views.post_search, name='search_page'),
    path('comment/<int:pk>/approve/', views.CommentUpdateView.comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', views.CommentUpdateView.comment_delete, name='comment_delete'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
