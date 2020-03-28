from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class FollowSystem(models.Model):
    followed = models.ForeignKey(User,on_delete = models.CASCADE,related_name='followed')
    follower = models.ForeignKey(User,on_delete = models.CASCADE,related_name='follower')
    created_time = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-created_time']
        verbose_name = 'FollowSystem'
        verbose_name_plural = 'FollowSystem'
    
    def __str__(self):
        return "%s follow %s"%(self.follower,self.followed)
    
    @staticmethod
    def get_followers(user):
        followers = FollowSystem.objects.filter(followed = user)
        return followers
    
    @staticmethod
    def get_followers_count(user):
        followers_count = FollowSystem.objects.filter(followed = user).count()
        return followers_count
    
    @staticmethod
    def get_followeds(user):
        followeds = FollowSystem.objects.filter(follower = user)
        return followeds
    
    @staticmethod
    def get_followeds_count(user):
        followeds_count = FollowSystem.objects.filter(follower = user).count()
        return followeds_count
    
    @staticmethod
    def add_or_delete(followed,follower,profilOwner):
        data = {}
        follow = FollowSystem.objects.filter(followed=followed,follower=follower)
        if follow.exists():
            follow.delete()
            followings_count = FollowSystem.get_followeds_count(follower)
            print(followings_count)
            data = {'msg':'FOLLOW','action':False,'followings_count':followings_count}
        else:
            FollowSystem.objects.create(followed=followed,follower=follower)
            image_url = followed.profile.get_image_or_default()
            print(image_url)
            followed_full_name = followed.get_full_name()
            print(followed_full_name)
            followed_username = followed.username
            follower_username = follower.username
            profilOwner_username = profilOwner.username
            print(followed_username)
            followings_count = FollowSystem.get_followeds_count(follower)
            data = {'msg':'UNFOLLOW',
                    'action':True,
                    'followings_count':followings_count,
                    'image_url':image_url,
                    'followed_full_name':followed_full_name,
                    'followed_username':followed_username,
                    'follower_username':follower_username,
                    'profilOwner_username':profilOwner_username,}
        return data
    
    @staticmethod
    def follow_status(me,other):
        has_follow = FollowSystem.objects.filter(followed=other,follower=me).exists()
        return has_follow