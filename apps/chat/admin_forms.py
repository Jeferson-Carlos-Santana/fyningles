from django import forms
from .models import Chat

class ChatAdminForm(forms.ModelForm):

    TEMPLATE_CHOICES = [
        ("1", "Frase com abreviação e sem abreviação."),
        ("2", "Frase sem abreviação."),
        ("3", "Frase em português para traduzir para o inglês."),
        ("4", "Frase sem abreviação e informal"),
        ("5", "Não definido ainda!"),
    ]

    template_choice = forms.ChoiceField(
        choices=TEMPLATE_CHOICES,
        required=False,
        label="Template de conteúdo"
    )

    class Meta:
        model = Chat
        fields = "__all__"
