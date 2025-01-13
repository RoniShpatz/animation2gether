from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
import requests
import random
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
            
            # Prepare context for template
            context = {
                'artwork': {
                    'title': artwork.get('title'),
                    'artist': artwork.get('artist_title'),
                    'date': artwork.get('date_display'),
                    'medium': artwork.get('medium_display'),
                    'image_url': image_url,
                    'description': artwork.get('description'),
                    'credit_line': artwork.get('credit_line'),
                    'dimensions': artwork.get('dimensions'),
                }
            }
            return render(request, 'index.html', context)
        
        else:
            context = {'error': 'No artwork found'}
            return render(request, 'index.html', context)
            
    except requests.RequestException as e:
        context = {'error': f'Error fetching artwork: {str(e)}'}
        return render(request, 'index.html', context)

