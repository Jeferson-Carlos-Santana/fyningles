from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterUserForm(UserCreationForm):
       
    username = forms.CharField(
        label="Usuário",
        min_length=5,
        max_length=20,
        error_messages={
            "min_length": "O usuário deve ter no mínimo 5 caracteres.",
            "max_length": "O usuário deve ter no máximo 20 caracteres.",
            "required": "Informe um nome de usuário.",
        },
    )
    
    email = forms.EmailField(
        required=True,
        label="E-mail",
        error_messages={
            "required": "Informe um e-mail.",
            "invalid": "Informe um e-mail válido.",
        },
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email
    
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        min_length=6,
        error_messages={
            "min_length": "A senha deve ter no mínimo 6 caracteres.",
            "required": "Informe uma senha.",
        },
    )
    
    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        if password and password.isdigit():
            raise forms.ValidationError("A senha não pode conter apenas números.")

        return password


    password2 = forms.CharField(
        label="Confirme a senha",
        widget=forms.PasswordInput,
        error_messages={
            "required": "Confirme a senha.",
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error("password2", "As senhas não coincidem.")
            
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
