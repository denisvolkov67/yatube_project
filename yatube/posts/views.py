from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/group.html',
        {
            'page': page,
            'group': group,
        }
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/profile.html',
        {
            'page': page,
            'author': author,
            'count_page': post_list.count(),
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    post_count = post.author.posts.all().count()

    return render(
        request,
        'posts/post.html',
        {
            'post': post,
            'author': post.author,
            'count_page': post_count,
        }
    )


@login_required
def new_post(request):

    form = PostForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            return redirect('index')

    return render(
        request,
        'posts/edit.html',
        {'form': form, 'action': 'new_post', }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)

    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(request.POST or None, instance=post)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)

    return render(
        request,
        'posts/edit.html',
        {
            'form': form,
            'action': 'post_edit',
            'post_id': post_id,
        }
    )
