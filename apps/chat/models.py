from django.db import models

class Chat(models.Model):
    lesson_id = models.IntegerField(verbose_name="Lesson ID")
    seq = models.IntegerField(verbose_name="Sequência")
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

    def __str__(self):
        return f"Lesson {self.lesson_id} | Seq {self.seq}"

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        db_table = "chats"
