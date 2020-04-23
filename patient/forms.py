from django.forms import ModelForm
from .models import Patient

class PatientInfoForm(ModelForm):
    class Meta:
        model = Patient
        fields = ['Full_name','age','Mole_has_Asymmetry_and_Irregular_shape','Border_Edge_is_not_smooth_but_Irregular','Color_is_Uneven_or_dark','Diameter_is_Larger_than_size_of_pencil_eraser','Spot_is_changing_in_size_and_shape','Skin_image']
