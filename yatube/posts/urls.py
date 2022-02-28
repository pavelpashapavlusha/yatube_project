from django.urls import path

from . import views

app_name = 'posts'
app_name = 'groups'

urlpatterns = [
    path('', views.index, name='posts'),
    path('group/<slug:slug>/', views.group_posts, name='groups'),
]