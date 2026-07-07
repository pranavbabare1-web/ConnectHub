from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import (
    Post,
    Comment,
    Like,
    Follow,
    Notification,
    Profile,
    Message,
)
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, PostForm, CommentForm, PasswordChangeForm


def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'social/landing.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome to ConnectHub, {user.username}! 🎉')
        return redirect('home')
    return render(request, 'social/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get('next', 'home')
        messages.success(request, f'Welcome back, {user.username}!')
        return redirect(next_url)
    return render(request, 'social/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def home(request):
    # Get posts from followed users + own posts
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(
        Q(user__in=following_users) | Q(user=request.user)
    ).select_related('user', 'user__profile').prefetch_related('likes', 'comments')

    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)
    posts_page = paginator.get_page(page)

    post_form = PostForm()

    # Suggested users: not followed, not self
    followed_ids = list(following_users) + [request.user.id]
    suggested_users = User.objects.exclude(id__in=followed_ids).select_related('profile')[:5]

    return render(request, 'social/home.html', {
        'posts': posts_page,
        'post_form': post_form,
        'suggested_users': suggested_users,
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created!')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('home')


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def like_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
            # Send notification if not own post
            if post.user != request.user:
                Notification.objects.get_or_create(
                    sender=request.user,
                    receiver=post.user,
                    notification_type='like',
                    post=post
                )
        return JsonResponse({'liked': liked, 'count': post.likes.count()})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            # Send notification if not own post
            if post.user != request.user:
                Notification.objects.create(
                    sender=request.user,
                    receiver=post.user,
                    notification_type='comment',
                    post=post
                )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'username': request.user.username,
                    'text': comment.text,
                    'created_at': comment.created_at.strftime('%b %d, %Y'),
                    'comment_id': comment.id,
                    'count': post.comments.count(),
                    'profile_image': request.user.profile.profile_image.url if request.user.profile.profile_image else '',
                })
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    post_id = comment.post.id
    comment.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post = get_object_or_404(Post, id=post_id)
        return JsonResponse({'success': True, 'count': post.comments.count()})
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def follow_user(request, username):
    if request.method == 'POST':
        target = get_object_or_404(User, username=username)
        if target == request.user:
            return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
        follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if not created:
            follow.delete()
            following = False
        else:
            following = True
            Notification.objects.get_or_create(
                sender=request.user,
                receiver=target,
                notification_type='follow'
            )
        return JsonResponse({
            'following': following,
            'followers_count': Follow.objects.filter(following=target).count()
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_user).select_related('user', 'user__profile').prefetch_related('likes', 'comments')
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    followers = Follow.objects.filter(following=profile_user).count()
    following = Follow.objects.filter(follower=profile_user).count()

    return render(request, 'social/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'followers': followers,
        'following': following,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'social/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['old_password']):
                messages.error(request, 'Current password is incorrect.')
            else:
                request.user.set_password(form.cleaned_data['new_password1'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully.')
                return redirect('edit_profile')
    else:
        form = PasswordChangeForm()
    return render(request, 'social/change_password.html', {'form': form})


@login_required
def notifications(request):
    notifs = Notification.objects.filter(receiver=request.user).select_related('sender', 'sender__profile', 'post')
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'social/notifications.html', {'notifications': notifs})


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    users = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).exclude(id=request.user.id).select_related('profile')[:20]
    return render(request, 'social/search.html', {'users': users, 'query': query})


def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=profile_user).select_related('follower', 'follower__profile')
    return render(request, 'social/followers_list.html', {'profile_user': profile_user, 'followers': followers, 'list_type': 'Followers'})


def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=profile_user).select_related('following', 'following__profile')
    return render(request, 'social/following_list.html', {'profile_user': profile_user, 'following': following, 'list_type': 'Following'})


# ===========================
# MESSAGE / CHAT SYSTEM
# ===========================

@login_required
def inbox(request):
    users = User.objects.exclude(id=request.user.id).select_related("profile")

    return render(request, "social/inbox.html", {
        "users": users
    })


@login_required
def chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        text = request.POST.get("message")

        if text and text.strip():
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                message=text.strip()
            )

            return redirect("chat", user_id=other_user.id)

    chat_messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by("timestamp")

    chat_messages.filter(
        receiver=request.user,
        sender=other_user,
        is_read=False
    ).update(is_read=True)

    return render(request, "social/chat.html", {
        "other_user": other_user,
        "messages": chat_messages
    })