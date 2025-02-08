from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.contrib.auth.forms import AuthenticationForm
from PIL import Image, ImageDraw
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import UploadedFile
import io

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Login', css_class='btn btn-primary')
        )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() and self.instance.email != email:
            raise forms.ValidationError("This email is already in use.")
        return email


class UploadForm(forms.ModelForm):
    file = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    class Meta:
        model = UploadedFile
        fields = ['file']

    def clean_file(self):
        # Add extra validation and debugging
        file = self.cleaned_data.get('file')
        
        # # Debug prints
        # print("File received:", file)
        # print("File type:", type(file))
        
        if not file:
            print("No file found in cleaned_data")
            raise forms.ValidationError("No file was uploaded.")
        
        # Additional checks if needed
        if file.size > 5 * 1024 * 1024:  # 5MB limit
            raise forms.ValidationError("File size must be under 5MB.")
        
        return file

    def save(self, commit=True):
        print("Saving form with commit:", commit)
        instance = super().save(commit=False)

        uploaded_file = self.cleaned_data.get('file')
        processed_file = self.resize_and_crop_image(uploaded_file)
        
        instance.file = processed_file

        if commit:
            # print("Attempting to save instance")
            instance.save()
        
        return instance
    #  Resize and crop an uploaded image to a circular shape
    def resize_and_crop_image(self, uploaded_file, target_size=(200, 200)):
        img = Image.open(uploaded_file)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        new_img = Image.new("RGB", target_size, (255, 255, 255))    
        paste_position = ((target_size[0] - img.size[0]) // 2, (target_size[1] - img.size[1]) // 2)
        new_img.paste(img, paste_position)  
        # Save to a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=90)  # Save as JPEG with 90% quality
        buffer.seek(0)


        # Convert to Django InMemoryUploadedFile
        return InMemoryUploadedFile(
            buffer,
            None,
            f'{uploaded_file.name.split(".")[0]}_circular.png',
            'image/png',
            buffer.getbuffer().nbytes,
            None
        )