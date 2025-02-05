from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
import requests
import random
from game.models import TempFrame, ActiveGame, Animations, MessageGame
from django.contrib.auth.models import User
from django.db.models import Max
from django.db.models import Q, Window, F, Max
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import RowNumber
from django.utils import timezone
from django.contrib import messages
from django.utils.timezone import now
from .utils import create_animation
import traceback
from django.core.files.base import File

# Create your views here.

@login_required
def index(request):
    try:
        # First, get the total number of artworks
        base_url = "https://api.artic.edu/api/v1/artworks"
        response = requests.get(f"{base_url}?page=1&limit=1")
        data = response.json()
        total_artworks = data['pagination']['total']
        
        # Generate a random page number
        random_page = random.randint(1, total_artworks)
        
        # Fetch the random artwork
        artwork_response = requests.get(f"{base_url}?page={random_page}&limit=1")
        artwork_data = artwork_response.json()
        
        if artwork_data['data']:
            artwork = artwork_data['data'][0]
            
            # Construct image URL if available
            image_id = artwork.get('image_id')
            image_url = None
            if image_id:
                image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"

            #list of users to invite to a game
            users_to_invite = User.objects.all().exclude(id=request.user.id).order_by('username')
            usernames = [user.username for user in users_to_invite]
            # print(usernames)

            # Prepare context for template
            context = {
                'artwork': {
                    'title': artwork.get('title'),
                    'artist': artwork.get('artist_title'),
                    'image_url': image_url,  
                }, 
                'usernames': usernames,

            }
        else:
            context = {'error': 'No artwork found'}
            return render(request, 'index.html', context)
            
    except requests.RequestException as e:
        context = {'error': f'Error fetching artwork: {str(e)}'}
    return render(request, 'index.html', context)
    
@login_required
def create_game(request):
    if request.method == 'POST':
        selected_username = request.POST.get('username')
        if selected_username:
            try:
                user_share = User.objects.get(username=selected_username)
                user = request.user
                new_game = ActiveGame(user=user, user_share=user_share, is_accepted = False, is_finished = False)
                new_game.save()
                        # send an invitation 
                messages.success(request, f'Invitation sent to {user_share.username}!')
                        # Redirect to the animate view
                return redirect('game:animate', game_id=new_game.id)
            except User.DoesNotExist:
                        messages.error(request, f'User {selected_username} does not exist.')
        else:
            messages.error(request, 'Please select a user to invite.')
    return redirect(animate, game_id=new_game.id)

@login_required
def animate(request, game_id):
    if not request.META.get('HTTP_REFERER'):
        storage = messages.get_messages(request)
        storage.used = True
    storage = messages.get_messages(request)
    storage.used = True
    temp_frame = TempFrame.objects.filter(game_id=game_id).order_by('-frame_number').first()
    animation_title = temp_frame.animation_title if temp_frame else None
    file = None
    if temp_frame:
        if temp_frame.frame_number > 1:
            prev_frame = TempFrame.objects.filter(game_id=game_id, frame_number=temp_frame.frame_number).first()
            file = prev_frame.file
        elif temp_frame.frame_number == 1:
            prev_frame = TempFrame.objects.filter(game_id=game_id, frame_number=1).first()
            file = prev_frame.file
    else: file=None
    
    return render(request, 'game.html', {'game_id': game_id, 
                                         'title':animation_title,
                                           'prev_file': file })


@login_required
def save_frame(request):
    if request.method == 'POST':
        if request.POST.get('intentional_save', 'false') == 'true':
    
            current_game_id = request.POST.get('game-id', "").strip()
            
            active_game = ActiveGame.objects.filter(id=current_game_id).first()

            if not active_game:
                messages.error(request, "Game not found!")
                return redirect('game:games_on')
            first_frame = TempFrame.objects.filter(game_id=current_game_id, frame_number=1).first()
        
            last_frame = TempFrame.objects.filter(game_id=current_game_id).order_by('-frame_number').first()
             
           
            if last_frame:
                next_frame_number = last_frame.frame_number + 1
                animation_title = first_frame.animation_title
                user_sender = last_frame.user_share_with
                user_recipient = last_frame.user
                
            else: 
                next_frame_number = 1
                animation_title = request.POST.get('title', 'Untitled Animation').strip()
                user_sender = active_game.user
                user_recipient = active_game.user_share
                
            current_massage = MessageGame.objects.filter(temp_frame=last_frame).first()
            if current_massage:
                current_massage.is_read = True
                current_massage.save()
            
            new_frame = TempFrame(
                user=request.user,
                animation_title=animation_title,
                frame_number=next_frame_number,
                game_id=active_game,
                user_share_with=user_recipient
                
            )                  
            
            if request.FILES.get('image'):
                image_file = request.FILES['image']
                new_frame.file.save(
                    f"frame_{request.user.id}_{next_frame_number}_{now().strftime('%Y%m%d_%H%M%S')}.jpg", 
                    image_file
                    )
                new_frame.save()
                new_massage = MessageGame(
                                sender=user_sender,
                                recipient=user_recipient,
                                temp_frame=new_frame,
                                game_id=active_game,
                                is_read= False, 
                                )
                new_massage.save()
                
                messages.success(request, 'Frame saved successfully!')
                return redirect('game:games_on')
            else:
                 messages.error(request, 'Failed to save frame. Please check your inputs.')
        
    return redirect('game:games_on') 


@login_required
def games_on(request):
    storage = messages.get_messages(request)
    storage.used = True 
    pending_games= ActiveGame.objects.filter(
        user_share=request.user,
        is_accepted=False
    )
    active_games = ActiveGame.objects.filter(
        user_share=request.user,
        is_accepted=True,
        is_finished=False
    )
    # Games waiting for the user's response
    messages_for_me = (
        MessageGame.objects.filter(
            is_read=False,
            recipient=request.user,
            game_id__in=ActiveGame.objects.filter(
                (Q(user=request.user) | Q(user_share=request.user)) & 
                Q(is_accepted=True)  & 
                Q(is_finished=False)
            ).values('id')
        )
        .annotate(
            last_frame_number=Max('temp_frame__frame_number'),
            row_num=Window(
                expression=RowNumber(),
                partition_by=[F('game_id')],
                order_by=F('temp_frame__frame_number').desc()
            ),
            sender_username=F('sender__username'),
            recipient_username=F('recipient__username')
        )
        .filter(row_num=1)
        .values('id', 'game_id', 'sender_id', 'recipient_id', 'temp_frame_id', 'last_frame_number', 'sender_username', 'recipient_username')
    )

    massages_wait = (
        MessageGame.objects.filter(
            is_read=False,
            sender = request.user,
            game_id__in=ActiveGame.objects.filter(
                (Q(user=request.user) | Q(user_share=request.user)) & 
                Q(is_accepted=True) & 
                Q(is_finished=False)
            ).values('id')
        )
        .annotate(
            last_frame_number=Max('temp_frame__frame_number'),
            row_num=Window(
                expression=RowNumber(),
                partition_by=[F('game_id')],
                order_by=F('temp_frame__frame_number').desc()
            ),
            sender_username=F('sender__username'),
            recipient_username=F('recipient__username')
        )
        .filter(row_num=1)
        .values('id', 'game_id', 'sender_id', 'recipient_id', 'temp_frame_id', 'last_frame_number', 'sender_username', 'recipient_username')
    )
      
    context = {
        'pending_games': pending_games,
        'active_games': active_games,
        'animation_waiting_respone': messages_for_me,
        'wait_for_respone' : massages_wait,
    }

    return render(request, 'games-on.html', context)   

@login_required
def accept_game(request):
    if request.method == 'POST':
        # Retrieve and validate the game_id
        game_id = request.POST.get("game_id", "").strip()
        if not game_id:
            messages.error(request, "Invalid game ID.")
            return redirect('game:games_on')

        # Find the current game for the user
        current_game = ActiveGame.objects.filter(id=game_id, user_share=request.user).first()
        current_massage= MessageGame.objects.filter(game_id=game_id).first()
        if current_game:
            if 'accept' in request.POST:
                current_game.is_accepted = True
                current_game.save()
                if current_massage:
                    current_massage.is_read = True
                    current_massage.save()
                messages.success(request, "Game accepted successfully!")
                return redirect('game:animate', game_id=game_id)
            elif 'decline' in request.POST:
                current_game.delete()
                messages.success(request, "Game declined and removed successfully!")
                return redirect('game:games_on')
        else:
            messages.error(request, "Game not found or you're not authorized to access it.")
            return redirect('game:games_on')

    # Default redirect if the method is not POST
    return redirect('game:games_on')



@login_required
def respond(request):
    if request.method == 'POST':
        massage_id = request.POST.get("message_id").strip()
        game_id = request.POST.get("game-id").strip()
        current_massage = MessageGame.objects.filter(id=massage_id).first()
     
        if not current_massage:
            messages.error(request, "No massage found.")
            return redirect('game:games_on')
        # current_massage.is_read = True
        # current_massage.save()
        return redirect('game:animate', game_id=game_id)
    
    return redirect('game:games_on')

@login_required
def finish_animation(request):
    if request.method == 'POST':
        try:
            game_id = request.POST.get('game-id')
            frame_per_s = int(request.POST.get('framePerS', 2))
            print(f"Processing game ID: {game_id} with {frame_per_s} FPS")
            
            current_game = ActiveGame.objects.filter(id=game_id).first()
            
            if current_game:
                frames = TempFrame.objects.filter(game_id=game_id).order_by('frame_number')
                animation_name = TempFrame.objects.filter(game_id=game_id).first()
                # print(f"Found {frames.count()} frames")
                
                if not frames.exists():
                    # print("No frames found for this game.")
                    messages.error(request, "No frames found for this game.")
                    return redirect('users:profile')
                
                try:
                    animation = create_animation(frames, 5) 

                    new_animation = Animations(
                        user=current_game.user,
                        shared_with=current_game.user_share,
                        animation_name = animation_name.animation_title
                    )
                    new_animation.animation_file.save("animation.gif", animation)
                    new_animation.save()
                    current_game.is_finished = True
                    current_game.save()                   
                    messages.success(request, "Animation created and uploaded successfully.")
                    
                except Exception as e:
                    print(f"Error creating animation:")
                    print(traceback.format_exc())
                    messages.error(request, f"Error creating animation: {str(e)}")
                    
            else:
                print("No game found")
                messages.error(request, "No game found. Animation is not created")
            
        except Exception as e:
            print("Error in finish_animation view:")
            print(traceback.format_exc())
            messages.error(request, f"Error processing request: {str(e)}")
            
        return redirect('users:profile')
    
    return redirect('users:profile')