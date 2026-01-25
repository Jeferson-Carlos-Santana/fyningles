from django.db import models, transaction
from django.db.models import Max, F
from django.conf import settings

class Chat(models.Model):
    lesson_id = models.IntegerField(verbose_name="Lesson ID")
    seq = models.IntegerField(null=True, blank=True, verbose_name="Sequência")
    role = models.CharField(max_length=30, verbose_name="Role")
    auto = models.BooleanField(default=False, verbose_name="Auto")
    end = models.BooleanField(default=False, verbose_name="End")
    status = models.BooleanField(default=True, verbose_name="Status")
    status_point = models.BooleanField(default=False, verbose_name="Status Point")
    LANG_CHOICES = [("PT","Português"),("EN","English"),("IT","Italiano"),("FR","Français"),("ES","Español")]
    lang = models.CharField(max_length=2, choices=LANG_CHOICES, default="PT", verbose_name="Linguagem")

    be_ready = models.BooleanField(default=False, verbose_name="Revisado")
    
    content_pt = models.TextField(null=True, blank=True, verbose_name="Conteúdo (PT)")
    content_it = models.TextField(null=True, blank=True, verbose_name="Conteúdo (IT)")
    content_fr = models.TextField(null=True, blank=True, verbose_name="Conteúdo (FR)")
    content_es = models.TextField(null=True, blank=True, verbose_name="Conteúdo (ES)")
    
    expected_en = models.CharField(max_length=255, verbose_name="Expectativa (EN)")

    expected_pt = models.CharField(max_length=255, null=True, blank=True, verbose_name="Expectativa (PT)")
    expected_it = models.CharField(max_length=255, null=True, blank=True, verbose_name="Expectativa (IT)")
    expected_fr = models.CharField(max_length=255, null=True, blank=True, verbose_name="Expectativa (FR)")
    expected_es = models.CharField(max_length=255, null=True, blank=True, verbose_name="Expectativa (ES)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="Modified At")
    

    def save(self, *args, **kwargs):
        with transaction.atomic():

            # INSERT (novo registro)
            
            if self.pk is None:

                # se NÃO informou seq → vai para o final
                if not self.seq:
                    ultimo = (
                        Chat.objects
                        .filter(lesson_id=self.lesson_id)
                        .aggregate(max_seq=Max("seq"))
                        .get("max_seq")
                    )
                    self.seq = (ultimo or 0) + 1

                # se INFORMOU seq → respeita e abre espaço
                else:
                    Chat.objects.filter(
                        lesson_id=self.lesson_id,
                        seq__gte=self.seq
                    ).update(seq=F("seq") + 1)

                super().save(*args, **kwargs)

                # normaliza a lição
                qs = (
                    Chat.objects
                    .filter(lesson_id=self.lesson_id)
                    .order_by("seq", "id")
                )
                for i, obj in enumerate(qs, start=1):
                    if obj.seq != i:
                        Chat.objects.filter(pk=obj.pk).update(seq=i)

                return

            # EDIT (registro existente)            
            antigo = Chat.objects.get(pk=self.pk)

            lesson_antiga = antigo.lesson_id
            lesson_nova = self.lesson_id

            seq_antigo = antigo.seq
            seq_novo = self.seq
            
            # CASO 1: mudou de lição            
            if lesson_antiga != lesson_nova:

                # 1) REMOVE da lição antiga (fecha buracos)
                qs_antiga = (
                    Chat.objects
                    .filter(lesson_id=lesson_antiga)
                    .exclude(pk=self.pk)
                    .order_by("seq")
                )
                for i, obj in enumerate(qs_antiga, start=1):
                    Chat.objects.filter(pk=obj.pk).update(seq=i)

                # 2) ABRE ESPAÇO na lição nova respeitando seq_novo
                Chat.objects.filter(
                    lesson_id=lesson_nova,
                    seq__gte=seq_novo
                ).update(seq=F("seq") + 1)

                # mantém exatamente o seq informado
                self.seq = seq_novo
            
            # CASO 2: mesma lição, mudou seq            
            else:
                if seq_novo != seq_antigo:
                    if seq_novo > seq_antigo:
                        Chat.objects.filter(
                            lesson_id=lesson_nova,
                            seq__gt=seq_antigo,
                            seq__lte=seq_novo
                        ).exclude(pk=self.pk).update(seq=F("seq") - 1)
                    else:
                        Chat.objects.filter(
                            lesson_id=lesson_nova,
                            seq__gte=seq_novo,
                            seq__lt=seq_antigo
                        ).exclude(pk=self.pk).update(seq=F("seq") + 1)

            # salva o próprio registro
            super().save(*args, **kwargs)
  
            # NORMALIZA AMBAS AS LIÇÕES ENVOLVIDAS       
            for lesson_id in {lesson_antiga, lesson_nova}:
                qs = (
                    Chat.objects
                    .filter(lesson_id=lesson_id)
                    .order_by("seq", "id")
                )
                for i, obj in enumerate(qs, start=1):
                    if obj.seq != i:
                        Chat.objects.filter(pk=obj.pk).update(seq=i)

        
    def __str__(self):
        return f"Lesson {self.lesson_id} | Seq {self.seq}"    

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        db_table = "chats"
        ordering = ["lesson_id", "seq"]

# PROGRESS
class Progress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress"
    )

    lesson_id = models.IntegerField()

    chat = models.ForeignKey(
        "Chat",
        on_delete=models.CASCADE,
        related_name="progress"
    )

    points = models.IntegerField()

    status = models.PositiveSmallIntegerField(default=0)
    stage = models.PositiveSmallIntegerField(default=0)
    concluded_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "progress"
        indexes = [
            models.Index(fields=["user", "chat"]),
            models.Index(fields=["lesson_id"]),
        ]

    def __str__(self):
        return f"{self.user_id} | lesson {self.lesson_id} | chat {self.chat_id}"
    
#  TMP_PROGRESS
class ProgressTmp(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    chat = models.ForeignKey(
        "Chat",
        on_delete=models.CASCADE
    )

    points = models.PositiveSmallIntegerField()

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "progress_tmp"
        indexes = [
            models.Index(fields=["user", "chat"]),
            models.Index(fields=["updated_at"]),
        ]
        
# NIVEL USUARIO
class UserNivel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nivel"
    )

    nivel = models.PositiveSmallIntegerField(default=0)  # 0, 1, 2, 3
    
    last_activation_sent_at = models.DateTimeField(null=True, blank=True)
    last_password_reset_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "user_nivel"

    def __str__(self):
        return f"{self.user_id} | nivel {self.nivel}"
