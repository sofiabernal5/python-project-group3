from django.db import models


#Create your models here

class Classification(models.Model):
    city = models.CharField(max_length=100)
    time = models.DateTimeField()
    temperature_c = models.FloatField()
    apparent_temperature_c = models.FloatField()
    humidity_pct = models.FloatField()
    windspeed_kmh = models.FloatField()
    precipitation_mm = models.FloatField()
    cloudcover_pct = models.FloatField()
    
    @property
    def is_cloudy(self):
        return self.cloudcover_pct >= 50

#a view decides what happens when you access a URL (page logic)
#core is an app