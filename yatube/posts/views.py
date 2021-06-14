from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


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

    following = (request.user.is_authenticated
                 and author.following.filter(user=request.user).exists())

    return render(
        request,
        'posts/profile.html',
        {
            'page': page,
            'author': author,
            'following': following,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    following = (request.user.is_authenticated
                 and post.author.following.filter(user=request.user).exists())
    comments = post.comments.all()
    form = CommentForm()

    return render(
        request,
        'posts/post.html',
        {
            'post': post,
            'author': post.author,
            'comments': comments,
            'form': form,
            'following': following,
            'template': 'post_view',
        }
    )


@login_required
def add_comment(request, username, post_id):

    form = CommentForm(request.POST or None)

    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()

            return redirect('post', username, post_id)

    return render(
        request,
        'posts/comments.html',
        {'form': form, }
    )


@login_required
def new_post(request):

    form = PostForm(request.POST or None, files=request.FILES or None)

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

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

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
            'post': post,
        }
    )


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'posts/follow.html',
        {'page': page, }
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (request.user == author):
        return redirect('profile', username)
    Follow.objects.get_or_create(
        user=request.user,
        author=author,
    )
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    follow = get_object_or_404(Follow, user=request.user,
                               author__username=username)
    follow.delete()
    return redirect('profile', username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
