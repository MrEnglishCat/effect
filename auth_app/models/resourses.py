from django.db import models

class ResoursesModel(models.Model):

    name = models.CharField('Название ресурса', max_length=100, unique=True)
    description = models.TextField('Описание ресурса', null=True, blank=True)

    class Meta:
        verbose_name = 'Ресурс'
        verbose_name_plural = 'Ресурсы'


    def __str__(self):
        return self.name