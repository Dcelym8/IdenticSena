from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario

class RegistroForm(UserCreationForm):

    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['email','tipoDocumento','numeroDocumento','nombre','apellido','edad','telefono']

    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.username = self.cleaned_data['email']

        usuario.set_password(self.cleaned_data['password1'])
        
        if commit:
            usuario.save()
        return usuario

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']    

class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control'}))