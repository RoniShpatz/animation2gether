from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from game.models import ActiveGame, TempFrame, MessageGame
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class GameViewsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.other_user = User.objects.create_user(username='otheruser', password='testpass')
        self.active_game = ActiveGame.objects.create(user=self.user, user_share=self.other_user, is_accepted=False, is_finished=False)

    def test_index_view(self):
        response = self.client.get(reverse('index'))  # Adjust this to your URL pattern name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertIn('artwork', response.context)

    def test_create_game_view(self):
        response = self.client.post(reverse('game:create_game'), {'username': 'otheruser'})
        self.assertEqual(response.status_code, 302)  # Should redirect after creating a game
        self.assertTrue(ActiveGame.objects.filter(user=self.user, user_share=self.other_user).exists())
        self.assertContains(response, "Invitation sent to otheruser!")

    def test_animate_view(self):
        response = self.client.get(reverse('game:animate', kwargs={'game_id': self.active_game.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game.html')
        self.assertEqual(response.context['game_id'], self.active_game.id)

    def test_save_frame_view(self):
        image_file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('game:save_frame'), {
            'intentional_save': 'true',
            'game-id': self.active_game.id,
            'title': 'Test Animation',
            'image': image_file
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after saving frame
        self.assertTrue(TempFrame.objects.filter(animation_title='Test Animation').exists())
        self.assertContains(response, "Frame saved successfully!")

    def test_games_on_view(self):
        response = self.client.get(reverse('game:games_on'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'games-on.html')
        self.assertIn('pending_games', response.context)
        self.assertIn('active_games', response.context)

    def test_accept_game_view(self):
        response = self.client.post(reverse('game:accept_game'), {
            'game_id': self.active_game.id,
            'accept': True
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after accepting a game
        self.active_game.refresh_from_db()
        self.assertTrue(self.active_game.is_accepted)
        self.assertContains(response, "Game accepted successfully!")

    def test_respond_view(self):
        message = MessageGame.objects.create(sender=self.other_user, recipient=self.user, game_id=self.active_game)
        response = self.client.post(reverse('game:respond'), {
            'message_id': message.id,
            'game-id': self.active_game.id
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('game:animate', kwargs={'game_id': self.active_game.id}))

    def test_finish_animation_view(self):
        # Create a frame for the game
        frame = TempFrame.objects.create(user=self.user, animation_title='Test Animation', frame_number=1, game_id=self.active_game)

        response = self.client.post(reverse('game:finish_animation'), {
            'game-id': self.active_game.id,
            'framePerS': 2
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after finishing animation
        self.assertTrue(ActiveGame.objects.filter(id=self.active_game.id, is_finished=True).exists())
        self.assertContains(response, "Animation created and uploaded successfully.")

    def tearDown(self):
        self.user.delete()
        self.other_user.delete()
        self.active_game.delete()

