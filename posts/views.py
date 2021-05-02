from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Post, Group, Follow
from .forms import PostForm, CommentForm

User = get_user_model()


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:11]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_count = author.posts.count()
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if not request.user.is_anonymous:
        following = Follow.objects.filter(
            author=author, user=request.user
        )
    else:
        following = Follow.objects.filter(
            author=author, user=author
        )
    context = {
        'author': author,
        'page': page,
        'posts_count': posts_count,
        'posts': posts,
        'following': following
    }
    return render(request, 'profile/profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    posts_count = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'author': post.author,
        'posts_count': posts_count,
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'profile/post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user == post.author:
        form = PostForm(instance=post)
        if request.method == 'POST':
            form = PostForm(
                request.POST or None, files=request.FILES, instance=post
            )
            if form.is_valid():
                form = form.save(commit=False)
                form.save()
            return redirect('post', username=username, post_id=post_id)
        return render(request, 'new.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        created_comment = form.save(commit=False)
        created_comment.author = request.user
        created_comment.post = post
        created_comment.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'profile/post.html', {
        'form': form, 'post': post
    })


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(reverse('profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)
