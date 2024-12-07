from django.contrib import admin
from .models import Beneficiary, Donation

# Register your models here.

admin.site.register(Beneficiary)
admin.site.register(Donation)
