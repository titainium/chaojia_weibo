from django.db import models

# Create your models here.

class InformModel(models.Model):
    wid = models.CharField(max_length=30);
    uid = models.CharField(max_length=30);
    inform_time = models.DateField();
    reason = models.TextField(max_length=100);
    status = models.IntegerField();
