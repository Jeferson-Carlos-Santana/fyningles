from django import forms
from .models import Chat

class ChatAdminForm(forms.ModelForm):
    
    role = forms.ChoiceField(
        choices=[
        ("teacher", "Teacher"),
        ("pt-mark", "Setar traduzir para português"),
        ("single-mark", "Setar não traduzida para potutuguês"),        
        ]
    )

    TEMPLATE_CHOICES = [
        ("1", "Frase com abreviação e sem abreviação."),
        ("2", "Frase sem abreviação."),
        ("3", "Frase em português."),
        ("4", "Frase sem abreviação e informal"),
        ("5", "Frase com 2 traducões. Ex: He's home. or He's at home."),        
        ("6", "🟢 Verbos - Português e inglês."),
        ("7", "🟠 Verbos - Português."),        
    ]

    template_choice = forms.ChoiceField(
        choices=TEMPLATE_CHOICES,
        required=False,
        label="Template de conteúdo"
    )
    
    def clean_expected_en(self):
        expected = self.cleaned_data.get("expected_en", "").strip()

        qs = Chat.objects.filter(expected_en__iexact=expected)

        # ignora o próprio registro ao editar
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        # permite até 2 iguais
        limite = 4 if self.cleaned_data.get("lesson_id") == 2 else 2
        if qs.count() >= limite:
            raise forms.ValidationError(
                "Já existem dois registros com esse expected_en. Não é permitido cadastrar um terceiro."
            )

        return expected

    class Meta:
        model = Chat
        fields = "__all__"
