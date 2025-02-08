import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post
from game.models import Animations


@pytest.mark.django_db
class TestBlogViews:
    
    def setup_method(self):
        """Create a test user and sample data."""
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.post = Post.objects.create(title="Test Post", content="Sample content", author=self.user)
        self.animation = Animations.objects.create(user=self.user, animation_name="Test Animation")

    def test_post_list_authenticated(self, client):
        """Ensure an authenticated user can access post_list."""
        client.login(username="testuser", password="password123")
        url = reverse("blog:post_list")
        response = client.get(url)
        assert response.status_code == 200
        assert "posts" in response.context
        assert "all_files" in response.context

    def test_post_list_unauthenticated(self, client):
        """Ensure unauthenticated users are redirected from post_list."""
        url = reverse("blog:post_list")
        response = client.get(url)
        assert response.status_code == 302  # Redirects to login

    def test_post_edit_authenticated(self, client):
        """Test if an authenticated user can edit a post."""
        client.login(username="testuser", password="password123")
        url = reverse("blog:post_edit", args=[self.post.id])
        response = client.post(url, {"title": "Updated Title", "content": "Updated Content"})
        self.post.refresh_from_db()
        assert response.status_code == 302  # Redirect after successful update
        assert self.post.title == "Updated Title"
        assert self.post.content == "Updated Content"

    def test_post_edit_no_changes(self, client):
        """Ensure no update occurs when data is unchanged."""
        client.login(username="testuser", password="password123")
        url = reverse("blog:post_edit", args=[self.post.id])
        response = client.post(url, {"title": self.post.title, "content": self.post.content})
        assert response.status_code == 302  # Redirected with a message
        assert self.post.title == "Test Post"

    def test_post_edit_unauthenticated(self, client):
        """Ensure unauthenticated users cannot edit a post."""
        url = reverse("blog:post_edit", args=[self.post.id])
        response = client.post(url, {"title": "Should Not Update"})
        self.post.refresh_from_db()
        assert response.status_code == 302  # Should redirect to login
        assert self.post.title == "Test Post"  # Post should remain unchanged

    def test_post_delete_authenticated(self, client):
        """Ensure an authenticated user can delete a post."""
        client.login(username="testuser", password="password123")
        url = reverse("blog:post_delete", args=[self.post.id])
        response = client.post(url)
        assert response.status_code == 302  # Redirect after deletion
        assert not Post.objects.filter(id=self.post.id).exists()

    def test_post_delete_invalid_post(self, client):
        """Test deleting a non-existent post."""
        client.login(username="testuser", password="password123")
        url = reverse("blog:post_delete", args=[999])  # Invalid post ID
        response = client.post(url)
        assert response.status_code == 302  # Redirect should occur
        assert Post.objects.filter(id=self.post.id).exists()  # Original post still exists

    def test_post_delete_unauthenticated(self, client):
        """Ensure unauthenticated users cannot delete a post."""
        url = reverse("blog:post_delete", args=[self.post.id])
        response = client.post(url)
        assert response.status_code == 302  # Should redirect to login
        assert Post.objects.filter(id=self.post.id).exists()  # Post should remain
