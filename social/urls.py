from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Posts
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Social
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('search/', views.search, name='search'),
    path('notifications/', views.notifications, name='notifications'),

    # Profile
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('settings/profile/', views.edit_profile, name='edit_profile'),
    path('settings/password/', views.change_password, name='change_password'),
]

path("messages/", views.inbox, name="inbox"),
path("chat/<int:user_id>/", views.chat, name="chat"),