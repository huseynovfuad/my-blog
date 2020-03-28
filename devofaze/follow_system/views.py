from django.shortcuts import render
from .models import FollowSystem
from django.contrib.auth.models import User
from django.http import JsonResponse
# Create your views here.


def add_or_delete_following(request):
    if request.method == 'POST':
        followed_ = request.POST.get('followed',None)
        follower_ = request.POST.get('follower',None)
        profilOwner_ = request.POST.get('profilOwner',None)
        print(profilOwner_)
        followed = User.objects.get(username = followed_)
        follower = User.objects.get(username = follower_)
        profilOwner = User.objects.get(username = profilOwner_)
        if followed and follower and profilOwner:
            data = FollowSystem.add_or_delete(followed=followed,follower=follower,profilOwner=profilOwner)
            return JsonResponse(data=data)

