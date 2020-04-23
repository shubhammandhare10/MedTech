from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Patient(models.Model):
    Full_name = models.CharField(max_length=50)
    age = models.CharField(max_length=2)
    Mole_has_Asymmetry_and_Irregular_shape = models.BooleanField(default=False)
    Border_Edge_is_not_smooth_but_Irregular = models.BooleanField(default=False)
    Color_is_Uneven_or_dark = models.BooleanField(default=False)
    Diameter_is_Larger_than_size_of_pencil_eraser = models.BooleanField(default=False)
    Spot_is_changing_in_size_and_shape = models.BooleanField(default=False)
    Skin_image = models.ImageField(upload_to='patient/images/')
    created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    result = models.CharField(max_length=50)

    def __str__(self):
        return self.Full_name
