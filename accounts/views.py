from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, ProfileForm, PostForm, CommentForm, EditProfileForm
from .models import Profile, Follow, Post, Like, Comment
from django.db.models import Q, Prefetch
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages

def home_view(request):
    return render(request, 'accounts/home.html')

# auth

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect("accounts:profile")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("accounts:profile")
        else:
            return render(request, "accounts/login.html", {"error": "Invalid credentials"})
    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("accounts:login")


#profile

@login_required
def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(Profile, user__username=username).user
    else:
        profile_user = request.user

    profile, created = Profile.objects.get_or_create(user=profile_user)
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    follower_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()


    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()


    if request.method == "POST" and "comment" in request.POST:
        post_id = request.POST.get("post_id")
        comment_text = request.POST.get("comment_text")
        if post_id and comment_text:
            post = get_object_or_404(Post, id=post_id)
            Comment.objects.create(user=request.user, post=post, text=comment_text)
            if username:
                return redirect("accounts:profile_with_username", username=username)
            else:
                return redirect("accounts:profile")

    liked_posts = set(
        Like.objects.filter(user=request.user, post__in=posts).values_list("post_id", flat=True)
    )

    comments_by_post = {
        post.id: Comment.objects.filter(post=post).order_by('-created_at')
        for post in posts
    }

    form = ProfileForm(instance=profile) if request.user == profile_user else None

    context = {
        "profile_user": profile_user,
        "profile": profile,
        "posts": posts,
        "follower_count": follower_count,
        "following_count": following_count,
        "total_posts": posts.count(),
        "liked_posts": liked_posts,
        "comments_by_post": comments_by_post,
        "form": form,
        "is_following": is_following,
    }

    return render(request, "accounts/profile.html", context)

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile_with_username', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {
        "form": form,
        "profile_user": request.user,
    })


#follow



@login_required
def follow_toggle(request, username):
   
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    target_user = get_object_or_404(User, username=username)

    if request.user == target_user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    follower = request.user
    
    follow_instance = Follow.objects.filter(follower=follower, following=target_user)
    is_following = follow_instance.exists()

    if is_following:
        follow_instance.delete()
        new_status = False
    else:
        Follow.objects.create(follower=follower, following=target_user)
        new_status = True
        
    new_follower_count = Follow.objects.filter(following=target_user).count()
        
    return JsonResponse({
        'status': 'success',
        'is_following': new_status, 
        'follower_count': new_follower_count
    })


#posts

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("accounts:profile")
    else:
        form = PostForm()
    return render(request, "accounts/post_create.html", {"form": form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request, "You are not allowed to delete this post.")
        return redirect('accounts:profile')

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('accounts:profile')

    return render(request, 'accounts/delete_post.html', {'post': post})


#feed

@login_required
def feed(request):
    posts = Post.objects.select_related(
        'author', 
        'author__profile' 
    ).prefetch_related(
        'likes', 
        'comments' 
    ).order_by('-created_at')

    for post in posts:
        post.is_liked_by_user = post.likes.filter(user=request.user).exists()
        
    comments_by_post = {post.id: Comment.objects.filter(post=post).order_by('-created_at') for post in posts} 

    if request.method == "POST" and "comment" in request.POST:
        pass

    return render(request, "accounts/feed.html", {
        "posts": posts,
        "comments_by_post": comments_by_post,
    })

#like & comment

@login_required
def like_toggle(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    
    if not created:
        like.delete()
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/feed/')) 

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('accounts:feed')))
            
    return redirect('accounts:view_post', post_id=post.id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        messages.error(request, "You are not allowed to delete this comment.")
        return redirect('accounts:feed')

    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted successfully!")
        return redirect('accounts:feed')

    return render(request, 'accounts/delete_comment.html', {'comment': comment})


#musician detail

@login_required
def musician_detail(request, user_id):
    musician = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=musician)
    posts = Post.objects.filter(author=musician).order_by('-created_at')

    for post in posts:
        post.has_liked = post.likes.filter(user=request.user).exists()

    is_following = Follow.objects.filter(follower=request.user, following=musician).exists()

   
    if request.method == "POST":
        if "comment" in request.POST:
            post_id = request.POST.get("post_id")
            text = request.POST.get("comment_text")
            if text.strip():
                post = get_object_or_404(Post, id=post_id)
                Comment.objects.create(post=post, user=request.user, text=text)
        return redirect("accounts:musician_detail", user_id=musician.id)

    comments_by_post = {post.id: Comment.objects.filter(post=post).order_by("-created_at") for post in posts}

    return render(request, "accounts/musician_detail.html", {
        "musician": musician,
        "profile": profile,
        "posts": posts,
        "is_following": is_following,
        "total_posts": posts.count(),
        "follower_count": Follow.objects.filter(following=musician).count(),
        "following_count": Follow.objects.filter(follower=musician).count(),
        "comments_by_post": comments_by_post,
    })


#search

def search_musicians(request):
    query = request.GET.get("q", "")
    if query:
        results = Profile.objects.filter(
            Q(user__username__icontains=query) |
            Q(bio__icontains=query) |
            Q(instrument__icontains=query)
        )
    else:
        results = Profile.objects.all()
    
    return render(request, "accounts/search.html", {"query": query, "results": results})

@login_required
def view_post(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author').prefetch_related( 
            Prefetch(
                'comments', 
                queryset=Comment.objects.select_related('user__profile') 
            )
        ), 
        id=post_id
    )

    is_liked_by_user = post.likes.filter(user=request.user).exists()
    comment_form = CommentForm()

    if request.method == "POST":
        if 'comment_submit' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user 
                comment.post = post
                comment.save()
                messages.success(request, "Comment added successfully!")
                return redirect('accounts:view_post', post_id=post.id)
            else:
                comment_form = form

    context = {
        "post": post,
        "is_liked_by_user": is_liked_by_user, 
        "comment_form": comment_form,
    }
    return render(request, "accounts/view_post.html", context)