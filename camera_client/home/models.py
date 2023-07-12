from django.db import models

# Create your models here.
class photos(models.Model):
	plate = models.ImageField(upload_to='images/')
