from django import forms
from .models import Post,Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'image',
            'content',
            'topic',
        ]
       
    def clean(self,*args,**kwargs):
        content = self.cleaned_data['content']
        if len(content)<300:
            raise forms.ValidationError('Min length of content must be 300')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'commentary',
        ]
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commentary'].widget.attrs.update({'class': 'form-control'})
