from .models import Post, Group

from django.shortcuts import render, get_object_or_404

long = 10


def index(request):
    posts = Post.objects.order_by('-pub_date')[:long]
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:long]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
