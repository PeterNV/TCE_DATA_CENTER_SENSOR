from django.db import models


class RGraficos(models.Model):
    datae = models.TextField(max_length=255)
    
class novos_valores(models.Model):
    temp = models.TextField(max_length=255,default='SOME STRING')
    hum = models.TextField(max_length=255,default='SOME STRING')
    luz = models.TextField(max_length=255,default='SOME STRING')
    press = models.TextField(max_length=255,default='SOME STRING')
    gas = models.TextField(max_length=255,default='SOME STRING')
    rpm = models.TextField(max_length=255,default='SOME STRING')
    vento = models.TextField(max_length=255,default='SOME STRING')
    ar = models.TextField(max_length=255,default='SOME STRING')
    