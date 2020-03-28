from django.urls import path
from . import views

urlpatterns = [
    
    path('',views.post_list,name='post-list'),
    path('post/detail/<str:post_slug>/',views.post_detail,name='post-detail'),
    path('post/<str:post_slug>/edit/',views.post_edit,name='post-edit'),
    path('post/create/',views.post_create,name='post-create'),
    path('post/delete/',views.post_delete,name='post-delete'),
    path('post/<str:post_slug>/delete/',views.post_delete2,name='post-delete2'),
    path('post/like/',views.post_like,name='post-like'),
    path('post/unlike/',views.post_unlike,name='post-unlike'),
    path('post/bookmark/',views.post_bookmark,name='post-bookmark'),
    path('comment/create/',views.comment_create,name='comment-create'),
    path('comment/delete/',views.comment_delete,name='comment-delete'),
    path('comment/like/',views.comment_like,name='comment-like'),
    path('comment/unlike/',views.comment_unlike,name='comment-unlike'),
    path('comment/edit',views.comment_edit,name='comment-edit'),
]