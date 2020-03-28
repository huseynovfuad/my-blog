from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
# Create your models here.

def upload_to(instance,filename):
    return '%s/%s/%s'%('user',instance.user.username,filename)


class Profile(models.Model):
    GENDER = [
        ('m','male'),
        ('f','female'),
        ('o','other'),
    ]
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    date_of_birth = models.DateField(blank=True,null=True)
    bio = models.TextField(max_length=350,blank=True)
    password_reset_hash = models.TextField(blank=True,null=True)
    gender = models.CharField(max_length=1,choices=GENDER,blank=True)
    photo = models.ImageField(upload_to = upload_to,blank=True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profile'
        ordering = ['-created_at']
    
    def get_image_or_default(self):
        if self.photo and hasattr(self.photo,'url'):
            return self.photo.url
        return '/media/download.png/'
    

def create_profile(sender,**kwargs):
    if kwargs['created']:
        profile = Profile.objects.create(
            user = kwargs['instance']
        )

post_save.connect(create_profile,sender=User)