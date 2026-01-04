from django import forms
from .models import Chat

class ChatAdminForm(forms.ModelForm):

    TEMPLATE_CHOICES = [
        ("1", "Frase com abreviação e sem abreviação."),
        ("2", "Frase sem abreviação."),
        ("3", "Frase em português para traduzir para o inglês."),
        ("4", "Frase sem abreviação e informal"),
        ("5", "Frase com 2 traducões. Ex: He's home. or He's at home."),
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
        if qs.count() >= 2:
            raise forms.ValidationError(
                "Já existem dois registros com esse expected_en. Não é permitido cadastrar um terceiro."
            )

        return expected

    class Meta:
        model = Chat
        fields = "__all__"
