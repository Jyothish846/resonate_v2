from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings 
from django.conf.urls.static import static 

app_name = "accounts"

urlpatterns = [
    path('', views.home_view, name='home'),
    path('feed/', views.feed, name='feed'),
    path("view_post/<int:post_id>/", views.view_post, name="view_post"),

    # User Auth
    path("signup/", views.signup_view, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Profile Mgt
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_with_username'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
 
    # Password Change
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url=reverse_lazy('accounts:edit_profile'),
        ),
        name="password_change",
    ),


    path(
        'password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            success_url=reverse_lazy('accounts:password_reset_done'),
            email_template_name='accounts/password_reset_email.html' 
        ), 
        name='password_reset'
    ),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    

    path(
        'reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete') # <-- THE NEW FIX
        ), 
        name='password_reset_confirm'
    ),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),


    # Follow/Unfollow 
    path('follow_toggle/<str:username>/', views.follow_toggle, name='follow_toggle'),

    # Posts 
    path("posts/create/", views.post_create, name="post_create"),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    # Likes & Comments
    path('like_toggle/<int:post_id>/', views.like_toggle, name='like_toggle'),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Search
    path("search/", views.search_musicians, name="search_musicians"),
    
    # Musician Detail
    path("musician/<int:user_id>/", views.musician_detail, name="musician_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)