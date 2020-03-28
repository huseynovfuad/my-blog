from django import forms
from .models import Profile
from django.contrib.auth import(
    authenticate,get_user_model
)
from bootstrap_datepicker_plus import DatePickerInput
User = get_user_model()
from collections import OrderedDict

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length =120,widget = forms.TextInput(attrs={'placeholder':'Username','class':'form-control'}),label='')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password','class':'form-control'}),label='')
    def clean(self,*args,**kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username = username,password=password)
            if not user:
                raise forms.ValidationError('User does not exist')
            if not user.check_password(password):
                raise forms.ValidationError('Wrong password')
            if not user.is_active:
                raise forms.ValidationError("User does not active")
        return super(UserLoginForm,self).clean(*args,**kwargs)


class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(max_length =120,widget = forms.TextInput)
    first_name = forms.CharField(max_length =120,widget = forms.TextInput)
    last_name = forms.CharField(max_length =120,widget = forms.TextInput)
    email = forms.EmailField(widget=forms.EmailInput)
    password1 = forms.CharField(min_length=8,max_length=30,widget = forms.PasswordInput)
    password2 = forms.CharField(widget = forms.PasswordInput)
    class Meta:
        model = User
        fields=[
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]
    def clean(self,*args,**kwargs):
        email = self.cleaned_data.get('email')
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        email_qs = User.objects.filter(email = email)
        username = self.cleaned_data.get('username')
        username_qs = User.objects.filter(username=username)
        if not password1 == password2:
            raise forms.ValidationError("Password didn't match")
        if email_qs.exists():
            raise forms.ValidationError('This email already exist')
        if username_qs.exists():
            raise forms.ValidationError('This username already exist')
        return super(UserRegisterForm,self).clean(*args,**kwargs)
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].label = ''
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Password Confirm'})


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]
    def __init__(self, *args, **kwargs):
        super(UserEditForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'gender',
            'date_of_birth',
            'bio',
        ]
        widgets = {
            'date_of_birth': DatePickerInput(
                options={
                    "format": "DD/MM/YYYY", # moment date-time format
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                    "viewMode": "years",
                }), # specify date-frmat
        }
    def __init__(self, *args, **kwargs):
        super(ProfileEditForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['date_of_birth'].input_formats = ['%d-%m-%Y']



class UserPhotoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']





class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(label=(""),
                                    widget=forms.PasswordInput(attrs={'placeholder':'New Password'}))
    new_password2 = forms.CharField(label=(""),
                                    widget=forms.PasswordInput(attrs={'placeholder':'Confirm New Password'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user



class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': ("Your old password was entered incorrectly. "
                                "Please enter it again."),
    })
    old_password = forms.CharField(label=(""),
                                   widget=forms.PasswordInput(attrs={'placeholder':'Old Password'}))

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password
    


PasswordChangeForm.base_fields = OrderedDict(
    (k, PasswordChangeForm.base_fields[k])
    for k in ['old_password', 'new_password1', 'new_password2']
)