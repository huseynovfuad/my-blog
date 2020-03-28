from django.shortcuts import render,redirect,get_object_or_404,HttpResponseRedirect,reverse,HttpResponse
from django.contrib.auth import(
    authenticate,
    get_user_model,
    login,
    logout,
)
from .forms import(
    UserLoginForm,
    UserRegisterForm,
    UserEditForm,
    ProfileEditForm,
    UserPhotoForm,
    PasswordChangeForm,PasswordChangeForm
)
from follow_system.models import FollowSystem
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import check_password
import hashlib
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def login_view(request):
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username = username,password = password)
        login(request,user)
        if next:
            return redirect(next)
        return redirect('/')
    context = {
        'form':form
    }
    return render(request,'acc/login.html',context)

def signup_view(request):
    next = request.GET.get('next')
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password1')
        user.set_password(password)
        user.save()
        new_user = authenticate(username = user.username,password = password)
        login(request,new_user)
        if next:
            return redirect(next)
        return redirect('post-list')
    context = {
        'form':form
    }
    return render(request,'acc/signup.html',context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('post-list')

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('post-list')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request,'acc/password_change.html',{'form':form})

@login_required
def profile_view(request,username):
    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect(reverse('post-list')+'?search={}'.format(search))
    user_ = get_object_or_404(User,username=username)
    followship = FollowSystem.objects.filter(followed=user_,follower=request.user)
    isFollow = False
    if followship.exists():
        isFollow = True
    posts_count = user_.author.count()
    bookmarkeds_count = user_.bookmark.count()
    followings = FollowSystem.objects.filter(follower = user_)
    followings_count = FollowSystem.get_followeds_count(user_)
    followers = FollowSystem.objects.filter(followed = user_)
    followers_count = FollowSystem.get_followers_count(user_)
    context = {'user':user_,
    'isFollow':isFollow,
    'followers': followers,
    'followings':followings,
    'followings_count':followings_count,
    'followers_count':followers_count,
    'posts_count':posts_count,
    'bookmarkeds_count':bookmarkeds_count,}
    return render(request,'acc/profile.html',context)

@login_required
def profile_edit(request,username):
    user = get_object_or_404(User,username=username)
    if user == request.user:
        user_form = UserEditForm(instance = request.user)
        profile_form = ProfileEditForm(instance = request.user.profile)
        if request.method == 'POST':
            user_form = UserEditForm(instance = request.user,data=request.POST)
            profile_form = ProfileEditForm(
                instance = request.user.profile,
                data = request.POST,
                files = request.FILES,)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                return HttpResponseRedirect(reverse('profile-view',kwargs={'username':request.user.username}))
        context = {
            'user_form':user_form,
            'profile_form':profile_form,
            'user':user,
        }
        return render(request,'acc/profile_edit.html',context)
    else:
        return HttpResponse('<h1>It is not your Profile</h1>')
    


def user_upload_photo(request):
    if request.method == 'POST':
        form = UserPhotoForm(instance=request.user.profile,data=request.POST,files=request.FILES)
        if form.is_valid():
            userphoto = form.save(commit=True)
            data = {'image-url' : userphoto.photo.url,'is_valid':True}
            return JsonResponse(data)
        else:
            data={'is_valid':False}
            return JsonResponse(data)


def password_reset(request):
    return render(request,'acc/password_reset.html',{})

@require_http_methods(['POST'])
def password_reset_confirm(request):
    email = request.POST.get('email')
    try:
        user = User.objects.get(email = email)
    except:
        # error message
        return redirect('password-reset')
    username = user.username
    hashing_info = hashlib.sha256("{}".format(email).encode('utf-8')).hexdigest()
    userprofile = Profile.objects.get(user=user)
    userprofile.password_reset_hash = hashing_info
    userprofile.save()
    link = 'http://127.0.0.1:8000/accounts/password-reset/done/{}/'.format(hashing_info)
    print(link)
    info = 'Password Reset Email'
    message_ = "Hi {}. Please follow this link for reset password\n{}".format(username,link)
    sender_ = settings.EMAIL_HOST_USER
    sending_ = [user.email]
    send_mail(info,message_,sender_,sending_,fail_silently=False,)
    #message
    return redirect('login')




def password_reset_done(request,hash):
    userprofile = get_object_or_404(Profile,password_reset_hash = hash)
    user = userprofile.user
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password_confirm')
        if new_password == new_password2:
            user.set_password(new_password)
            user.save()
            return redirect('login')
    return render(request,'acc/password_reset_done.html',{'user':userprofile})


