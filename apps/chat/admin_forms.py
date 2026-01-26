from django import forms
from .models import Chat

class ChatAdminForm(forms.ModelForm):
    
    role = forms.ChoiceField(
        choices=[
        ("teacher", "Teacher"),
        ("pt-mark", "🟠 Setar traduzir para português"),
        ("single-mark", "🟢 Setar não traduzida para potutuguês"),        
        ]
    )

    TEMPLATE_CHOICES = [
        ("1", "🟢 Frase com abreviação e sem abreviação."),
        ("2", "🟢 Frase sem abreviação."),
        ("3", "🟠 Frase em português."),
        ("4", "🟢 Frase sem abreviação e informal"),
        ("5", "🟢 Frase com 2 traducões. Ex: He's home. or He's at home."),        
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

        
        LIMITES_POR_LESSON = {
            1: 2,
            2: 4,
            3: 4,
            4: 2,
            5: 2,
            6: 2,
            7: 2,
            8: 2,
            9: 2,
            10: 2,
        }

        lesson_id = self.cleaned_data.get("lesson_id")
        limite = LIMITES_POR_LESSON[lesson_id]

        if qs.count() >= limite:
            raise forms.ValidationError(
                f"Limite de {limite} registros para esta lição."
            )

        return expected
    
    class Meta:
        model = Chat
        fields = "__all__"
