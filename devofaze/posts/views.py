from django.shortcuts import render,get_object_or_404,redirect,HttpResponseRedirect,reverse
from .models import Post,Comment
from django.contrib.auth.models import User
from .forms import PostForm,CommentForm
from django.http import JsonResponse
from django.db.models import Count
from django.utils.timesince import timesince
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from follow_system.models import FollowSystem

def post_list(request):
    if request.user.is_authenticated:
        posts = Post.objects.order_by('-created_at')
        search = request.GET.get('search')
        len_posts = 0
        if search is not None:
            posts = Post.objects.filter(Q(title__icontains = search)|
                                        Q(topic__icontains = search))
            len_posts = len(posts)
        paginator = Paginator(posts, 10)
        page = request.GET.get('page')
        contacts = paginator.get_page(page)
        popular_posts = Post.objects.annotate(like_count = Count('likes')).order_by('-like_count')[0:10]
        bookmarks = Post.objects.filter(bookmark__username__iexact = request.user.username)
        context = {'posts':contacts,
                   'p':paginator,
                   'len_posts':len_posts,
                   'search':search,
                   'popular_posts':popular_posts,
                   'bookmarks':bookmarks,}
        return render(request,'posts/post_list.html',context)
    else:
        users = User.objects.all().order_by('-date_joined')[0:8]
        posts = Post.objects.annotate(like_count = Count('likes')).order_by('-like_count')[0:6]
        return render(request,'posts/index.html',{'users':users,'posts':posts,})


@login_required
def post_create(request):
    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect(reverse('post-list')+'?search={}'.format(search))
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST or None,request.FILES or None)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.author = request.user
            new_form.save()
            return HttpResponseRedirect(reverse('post-detail',kwargs={'post_slug':new_form.slug}))
    return render(request,'posts/post_create.html',{'form':form})

@login_required
def post_detail(request,post_slug):
    search = request.GET.get('search')
    isFollow = False
    if search:
        return HttpResponseRedirect(reverse('post-list')+'?search={}'.format(search))
    create_form = CommentForm()
    post = get_object_or_404(Post,slug=post_slug)
    followship = FollowSystem.objects.filter(followed=post.author,follower=request.user)
    if followship.exists():
        isFollow = True
    user = request.user
    if user in post.reads.all():
        pass
    else:
        post.reads.add(user)
    comments = Comment.objects.filter(post=post)
    related_posts = post.relatedPosts()[:10]
    context = {'post':post,
               'create_form':create_form,
               'comments':comments,
               'related_posts':related_posts,
               'isFollow':isFollow}
    return render(request,'posts/post_detail.html',context)


@login_required
def post_edit(request,post_slug):
    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect(reverse('post-list')+'?search={}'.format(search))
    post = get_object_or_404(Post,slug=post_slug)
    form = PostForm(instance=post)
    if request.method == 'POST':
        form = PostForm(request.POST or None,request.FILES or None,instance=post)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.draft = True
            new_form.save()
            return HttpResponseRedirect(reverse('post-detail',kwargs={'post_slug':new_form.slug}))
    context = {'form':form}
    return render(request,'posts/post_edit.html',context)


@login_required
def post_delete(request):
    id1 = request.GET.get('id')
    Post.objects.get(id=id1).delete()
    data = {
        'deleted':True
    }
    return JsonResponse(data)

@login_required
def post_delete2(request,post_slug):
    Post.objects.get(slug = post_slug).delete()
    return redirect('post-list')

@login_required
def post_like(request):
    id_ = request.GET.get('id')
    post = get_object_or_404(Post,id=id_)
    user = request.user
    liked = False
    likes_count = post.total_likes()
    unlikes_count = post.total_unlikes()
    if user in post.likes.all():
        liked = False
        post.likes.remove(user)
        likes_count -= 1
    else:
        liked = True
        if user in post.unlikes.all():
            post.unlikes.remove(user)
            unlikes_count -= 1
            post.likes.add(user)
            likes_count +=1
        else:
            post.likes.add(user)
            likes_count +=1
    data = {
        "liked": liked,
        "id_" : post.id,
        'likes_count':likes_count,
        'unlikes_count':unlikes_count,
        }
    return JsonResponse(data)


@login_required
def post_unlike(request):
    id_ = request.GET.get('id')
    post = get_object_or_404(Post,id=id_)
    user = request.user
    liked = False
    likes_count = post.total_likes()
    unlikes_count = post.total_unlikes()
    if user in post.unlikes.all():
        liked = False
        post.unlikes.remove(user)
        unlikes_count -= 1
    else:
        liked = True
        if user in post.likes.all():
            post.likes.remove(user)
            likes_count -= 1
            post.unlikes.add(user)
            unlikes_count +=1
        else:
            post.unlikes.add(user)
            unlikes_count +=1
    data = {
        "liked": liked,
        "id_" : post.id,
        'likes_count':likes_count,
        'unlikes_count':unlikes_count,
        }
    return JsonResponse(data)

@login_required
def post_bookmark(request):
    id_ = request.GET.get('id')
    post = get_object_or_404(Post,id = id_)
    user = request.user
    bookmarked = False
    if user.is_authenticated:
        if user in post.bookmark.all():
            bookmarked = False
            post.bookmark.remove(user)
        else:
            bookmarked = True
            post.bookmark.add(user)
    data = {
        'bookmarked' : bookmarked,
    }
    return JsonResponse(data)


@login_required
def comment_create(request):
    if request.method == 'POST':
        slug = request.POST.get('post_slug')
        commentary = request.POST.get('commentary')
        post = get_object_or_404(Post,slug=slug)
        create_form = CommentForm(request.POST)
        if create_form.is_valid():
            new_form = create_form.save(commit=False)
            new_form.owner = request.user
            new_form.post = post
            new_form.save()
            comment_count = len(Comment.objects.filter(post=post))
            timesince_ = timesince(new_form.created_at)
            data = {
                'commentary': commentary,
                'id':new_form.id,
                'image_url': new_form.owner.profile.get_image_or_default(),
                'user':new_form.owner.get_full_name(),
                'total_likes':post.total_likes(),
                'total_unlikes':post.total_unlikes(),
                'count': comment_count,
                'timesince':timesince_,
                }
            return JsonResponse(data)

@login_required
def comment_delete(request):
    comment_id = request.GET.get('id')
    comment = get_object_or_404(Comment,id=comment_id)
    post = comment.post
    comment.delete()
    comment_count = len(Comment.objects.filter(post=post))
    data = {
        'deleted':True,
        'count': comment_count,
    }
    return JsonResponse(data)

@login_required
def comment_like(request):
    comment_id = request.GET.get('id')
    comment = get_object_or_404(Comment,id=comment_id)
    user = request.user
    liked = False
    likes_count = comment.total_likes()
    unlikes_count = comment.total_unlikes()
    if user in comment.likes.all():
        liked = False
        comment.likes.remove(user)
        likes_count -= 1
    else:
        liked = True
        if user in comment.unlikes.all():
            comment.unlikes.remove(user)
            unlikes_count -= 1
            comment.likes.add(user)
            likes_count +=1
        else:
            comment.likes.add(user)
            likes_count +=1
    data = {
        "liked": liked,
        "id_" : comment.id,
        'likes_count':likes_count,
        'unlikes_count':unlikes_count,
        }
    return JsonResponse(data)

@login_required
def comment_unlike(request):
    comment_id = request.GET.get('id')
    comment = get_object_or_404(Comment,id=comment_id)
    user = request.user
    liked = False
    likes_count = comment.total_likes()
    unlikes_count = comment.total_unlikes()
    if user in comment.unlikes.all():
        liked = False
        comment.unlikes.remove(user)
        unlikes_count -= 1
    else:
        liked = True
        if user in comment.likes.all():
            comment.likes.remove(user)
            likes_count -=1
            comment.unlikes.add(user)
            unlikes_count +=1
        else:
            comment.unlikes.add(user)
            unlikes_count +=1
    data = {
        "liked": liked,
        "id_" : comment.id,
        'likes_count':likes_count,
        'unlikes_count':unlikes_count,
        }
    return JsonResponse(data)

@login_required
def comment_edit(request):
    id1 = request.GET.get('id', None)
    text1 = request.GET.get('text', None)
    comment = Comment.objects.get(id=id1)
    comment.commentary = text1
    comment.save()
    info = {'id':comment.id,'text':comment.commentary}
    data = {
            'info': info
    }
    return JsonResponse(data)

from django.shortcuts import render_to_response
def error_404(request, exception, template_name="404.html"):
    response = render_to_response(template_name)
    response.status_code = 404
    return response
