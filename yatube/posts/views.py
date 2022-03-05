from django.shortcuts import render, get_object_or_404

from .models import Post, Group


def index(request):
    long = 10
    posts = Post.objects.order_by('-pub_date')[:long]
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    long = 10
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:long]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
