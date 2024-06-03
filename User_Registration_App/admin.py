from django.contrib import admin

# Register your models here.
from .models import CompanyRegistrationInformation, AdministrationkintahSubscriptionPackagePrice, PriceMatrixPerCompanyType, AdditionalCostCalculationFixParameters, TrainingUserEmail

admin.site.register(CompanyRegistrationInformation),
admin.site.register(AdministrationkintahSubscriptionPackagePrice),
admin.site.register(PriceMatrixPerCompanyType),
admin.site.register(AdditionalCostCalculationFixParameters),
admin.site.register(TrainingUserEmail),