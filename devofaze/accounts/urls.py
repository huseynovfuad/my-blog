from django.urls import path
from . import views


urlpatterns = [
    path('login/',views.login_view,name='login'),
    path('signup/',views.signup_view,name='signup'),
    path('logout/',views.logout_view,name='logout'),
    path('password-change/',views.password_change,name='password_change'),
    path('password/reset/',views.password_reset,name='password-reset'),
    path('password-reset-confirm/',views.password_reset_confirm,name='password-reset-confirm'),
    path('password-reset/done/<str:hash>/',views.password_reset_done,name='password-reset-done'),
    path('user-profile-photo/',views.user_upload_photo,name='profile-photo'),
    path('@<str:username>/edit/',views.profile_edit,name='profile-edit'),
    path('@<str:username>/',views.profile_view,name='profile-view'),
]
