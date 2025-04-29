from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Community, Post, Comment
from .forms import CommunityForm, PostForm, CommentForm

@login_required
def upvote_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.upvotes.all():
        post.upvotes.remove(request.user)
        upvoted = False
    else:
        post.upvotes.add(request.user)
        post.downvotes.remove(request.user)  # Remove downvote if exists
        upvoted = True
    return JsonResponse({"upvotes": post.total_upvotes(), "downvotes": post.total_downvotes(), "upvoted": upvoted})

@login_required
def downvote_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.downvotes.all():
        post.downvotes.remove(request.user)
        downvoted = False
    else:
        post.downvotes.add(request.user)
        post.upvotes.remove(request.user)  # Remove upvote if exists
        downvoted = True
    return JsonResponse({"upvotes": post.total_upvotes(), "downvotes": post.total_downvotes(), "downvoted": downvoted})


@login_required
def community_list(request):
    """
    Display all communities (optionally, you could filter by trending topics).
    """
    communities = Community.objects.all().order_by('-created_at')
    return render(request, 'community/community_list.html', {
        'communities': communities
    })

@login_required
def community_detail(request, slug):
    """
    Display details for a specific community, including its posts.
    Handles new post creation within the community.
    """
    community = get_object_or_404(Community, slug=slug)
    posts = community.posts.all().order_by('-created_at')

    if request.method == "POST" and 'post_submit' in request.POST:
        post_form = PostForm(request.POST, request.FILES)  # Include image upload
        if post_form.is_valid():
            new_post = post_form.save(commit=False)
            new_post.author = request.user
            new_post.community = community
            new_post.save()
            return redirect('community:community_detail', slug=slug)
    else:
        post_form = PostForm()

    context = {
        'community': community,
        'posts': posts,
        'post_form': post_form,
    }
    return render(request, 'community/community_detail.html', context)

@login_required
def community_create(request):
    """
    Allow a user to create a new community.
    The creator is automatically added as a member.
    """
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.created_by = request.user
            community.save()
            community.members.add(request.user)
            return redirect('community:community_detail', slug=community.slug)
    else:
        form = CommunityForm()
    return render(request, 'community/community_create.html', {'form': form})

@login_required
def community_join(request, slug):
    """
    Add the logged-in user as a member of the community.
    """
    community = get_object_or_404(Community, slug=slug)
    community.members.add(request.user)
    return redirect('community:community_detail', slug=slug)

@login_required
def community_leave(request, slug):
    """
    Remove the logged-in user from the community's members.
    """
    community = get_object_or_404(Community, slug=slug)
    community.members.remove(request.user)
    return redirect('community:community_detail', slug=slug)

@login_required
def comment_create(request, post_id):
    """
    Create a new comment for a specific post, with optional image upload.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)  # Include image upload
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('community:community_detail', slug=post.community.slug)
    else:
        form = CommentForm()
    return render(request, 'community/comment_create.html', {
        'form': form,
        'post': post
    })

@login_required
def delete_post(request, post_id):
    """
    Allow the author of a post to delete it.
    """
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    return JsonResponse({"message": "Post deleted successfully"}, status=200)

@login_required
def delete_comment(request, comment_id):
    """
    Allow the author of a comment to delete it.
    """
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    comment.delete()
    return JsonResponse({"message": "Comment deleted successfully"}, status=200)
