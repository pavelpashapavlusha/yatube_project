from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404

from .models import Post, Group

LONG = 10


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, LONG)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Group.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, LONG)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    count = Post.objects.filter(author_username=username).count()
    post_list = Post.objects.filter(author_username=username)
    paginator = Paginator(post_list, LONG)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'count': count,
        'page_obj': page_obj,
        'author_name': username,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, slug=post_id)
    group = post.group
    author = post.author
    posts = Post.objects.all()
    count = Post.objects.filter(author=author).count()
    context = {
        'post': post,
        'group': group,
        'author': author,
        'posts': posts,
        'count': count,
    }
    return render(request, 'posts/post_detail.html', context)
