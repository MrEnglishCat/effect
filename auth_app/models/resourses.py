from django.db import models

class ResourcesModel(models.Model):

    name = models.CharField('Название ресурса', max_length=100, unique=True, help_text='Название ресурса.')
    code_name = models.CharField('Код ресурса', max_length=100, unique=True, help_text='Кодовое название ресурса к которому нужен доступ')
    description = models.TextField('Описание ресурса', null=True, blank=True, help_text='Описание ресурса.')

    class Meta:
        verbose_name = 'Ресурс'
        verbose_name_plural = 'Ресурсы'


    def __str__(self):
        return self.name