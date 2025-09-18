from django.db import models



class ResoursesModel(models.Model):

    name = models.CharField('Название ресурса', max_length=100)
    description = models.TextField('Описание ресурса', null=True, blank=True)