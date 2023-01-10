from django.db import models

class Detection(models.Model):
    image = models.ImageField(upload_to='uploads/')
    config = models.FileField()
    weights = models.FileField()
    classes = models.FileField(blank=True, null=True)
