from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group').all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username, following=False):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    number_of_posts = posts.count()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author,
            user=request.user
        ).exists()
    context = {
        'author': author,
        'username': username,
        'number_of_posts': number_of_posts,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    title = str(post.text)[:30]
    number_of_posts = Post.objects.filter(author=post.author).count()
    form = CommentForm()
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'title': title,
        'number_of_posts': number_of_posts,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request, is_edit=False):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {
        'form': form,
        'is_edit': is_edit
    }
    if form.is_valid():
        data = form.save(commit=False)
        data.author = request.user
        data.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(
        request.POST or None
    )
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = 'Все посты ваших подписок'
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.follow_can_be_created(request.user, author):
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
