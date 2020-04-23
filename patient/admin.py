from django.contrib import admin
from .models import Patient
# Register your models here.
class PatientAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)

admin.site.register(Patient, PatientAdmin)
