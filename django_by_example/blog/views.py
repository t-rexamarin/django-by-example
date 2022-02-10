from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, UpdateView
from django.core.mail import send_mail
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from .forms import EmailPostForm, CommentForm, SearchForm
from .models import Post, Comment
from taggit.models import Tag
from django.db.models import Count


# Create your views here.
class PostListView(ListView):
    template_name = 'blog/post/list2.html'

    def get_context_data(self, *args, **kwargs):
        object_list = Post.published.all()
        tag = None

        tag_slug = kwargs['tag_slug'] if 'tag_slug' in kwargs else None
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            object_list = object_list.filter(tags__in=[tag])

        paginator = Paginator(object_list, 2)  # 3 posts per page
        page = kwargs['page'] if 'page' in kwargs else 1

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            posts = paginator.page(paginator.num_pages)

        context = {
            'page': page,
            'posts': posts,
            'tag': tag
        }

        return render(self, 'blog/post/list2.html', context=context)


def post_list(request, page=1, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 2)  # 3 posts per page
    page = request.GET.get('page')
    # page = kwargs['pk'] if 'pk' in kwargs else 1

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    context = {
        'page': page,
        'posts': posts,
        'tag': tag
    }

    return render(request, 'blog/post/list2.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post/detail2.html'
    # template_name = 'blog:post_detail.html'

    def get_object(self, *args, **kwargs):
        post = get_object_or_404(Post,
                                 slug=self.kwargs['post'],
                                 status='published',
                                 publish__year=self.kwargs['year'],
                                 publish__month=self.kwargs['month'],
                                 publish__day=self.kwargs['day'])

        return post

    def get_context_data(self, *args, **kwargs):
        post = self.object
        if self.request.user.is_superuser:
            comments = post.comments.all()
        else:
            comments = post.comments.filter(active=True)
        new_comment = None

        if self.request.method == 'POST':
            # A comment was posted
            comment_form = CommentForm(data=self.request.POST)

            if comment_form.is_valid():
                # Create Comment object but don't save to database yet
                new_comment = comment_form.save(commit=False)
                # Assign the current post to the comment
                new_comment.post = post
                new_comment.name = self.request.user
                # Save the comment to the database
                new_comment.save()

                post_url = post.get_absolute_url()
                return HttpResponseRedirect(post_url)
        else:
            comment_form = CommentForm()

        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids) \
            .exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                            .order_by('-same_tags', '-publish')[:2]

        context = {
            'post': post,
            'comments': comments,
            'new_comment': new_comment,
            'comment_form': comment_form,
            'similar_posts': similar_posts
        }

        return context


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    # List of active comments for this post
    # comments = post.comments.filter(active=True)
    comments = post.comments.all()
    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            new_comment.name = request.user
            # Save the comment to the database
            new_comment.save()

            post_url = post.get_absolute_url()
            return HttpResponseRedirect(post_url)
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
        .order_by('-same_tags', '-publish')[:2]

    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts
    }

    return render(request, 'blog/post/detail2.html', context)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)

        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # ... send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read" \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    context = {
        'post': post,
        'form': form,
        'sent': sent
    }

    return render(request, 'blog/post/share.html', context)


def post_search(request, page=1):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)

        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            # search with trigram
            # results = Post.published.annotate(
            #     similarity=TrigramSimilarity('title', query),
            # ).filter(similarity__gt=0.1).order_by('-similarity')

            # simple search
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.3).order_by('-rank')

        paginator = Paginator(results, 1)  # 3 posts per page
        # page = kwargs['page'] if 'page' in kwargs else 1
        if 'page' in request.GET:
            page = request.GET.get('page')
        else:
            page = page

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            posts = paginator.page(paginator.num_pages)

        context = {
            # 'form': form,
            'query': query,
            'posts': posts
        }

    return render(request, 'blog/post/list2.html', context)


class CommentUpdateView(UpdateView):
    model = Comment
    template_name = 'blog/post/list2.html'

    def comment_approve(self, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['pk'])
        comment.approve()
        return redirect('blog/post/list2.html', pk=comment.post.pk)

    def comment_delete(self, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['pk'])
        comment.delete()
        return redirect('blog/post/list2.html', pk=comment.post.pk)
