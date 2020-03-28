from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models import Count
from itertools import chain

# Create your models here.

def upload_to(instance,filename):
    return '%s/%s/%s/%s'%('posts',instance.author.username,instance.title,filename)

class Post(models.Model):
    title = models.CharField(max_length=120)
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='author')
    slug = models.SlugField(unique = True)
    image = models.ImageField(upload_to = upload_to,default='',null=True,blank=True)
    likes = models.ManyToManyField(User,blank=True,related_name='post_likes')
    unlikes = models.ManyToManyField(User,blank=True,related_name='post_unlikes')
    reads = models.ManyToManyField(User,blank = True,related_name='read')
    bookmark = models.ManyToManyField(User,blank=True,related_name='bookmark')
    topic = models.CharField(max_length = 300)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add = True)
    draft = models.BooleanField(default = False)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return '%s ----> %s' %(self.title,self.author.username)
    
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Post'
        ordering = ['-created_at']
    
    def unique_slug(self,new_slug,original_slug,index):
        if Post.objects.filter(slug=new_slug):
            new_slug = '%s-%s'%(original_slug,index)
            index+=1
            return self.unique_slug(new_slug=new_slug,original_slug=original_slug,index=index)
        return new_slug
    
    def save(self,*args,**kwargs):
        content = self.content
        if len(content)<300:
            raise ValidationError('Min length is 300')
        index=1
        new_slug = slugify(self.title)
        self.slug = self.unique_slug(new_slug=new_slug,original_slug=new_slug,index=index)
        return super(Post,self).save(*args,**kwargs)
    
    def snipped_body(self):
        return self.content[:250] + "..."
    
    def total_likes(self):
        return self.likes.count()
    
    def total_unlikes(self):
        return self.unlikes.count()
    
    def total_reads(self):
        return self.reads.count()
    
    def relatedPosts(self):
        topics = self.topic.split()
        allIn = []
        for i in topics:
            posts = Post.objects.exclude(title = self.title).filter(topic__icontains = i)
            allList = list(chain(posts))
            allIn = allIn + allList
        titleList = []
        for j in allIn:
            titleList.append(j.title)
        cleanAll = Post.objects.filter(title__in = titleList).distinct().annotate(num_likes = Count('likes')).order_by('-num_likes')
        return cleanAll


class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete = models.CASCADE,related_name='post')
    owner = models.ForeignKey(User,on_delete = models.CASCADE,related_name='owner')
    commentary = models.TextField()
    likes = models.ManyToManyField(User,blank=True,related_name='comment_likes')
    unlikes = models.ManyToManyField(User,blank=True,related_name='comment_unlikes')
    created_at = models.DateTimeField(auto_now_add = True)
    draft = models.BooleanField(default = False)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return "%s comment to %s"%(self.owner.username,self.post.title)
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comment'
        ordering = ['-created_at']
    
    def total_likes(self):
        return self.likes.count()
    
    def total_unlikes(self):
        return self.unlikes.count()

