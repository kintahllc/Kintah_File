from django.contrib import admin

# Register your models here.
from .models import SubscriptionInformation, BillingQuestion, SubscriptionPlan, Erp_Information, ErpActiveCompanyAndWeb

admin.site.register(SubscriptionInformation),
admin.site.register(BillingQuestion),
admin.site.register(SubscriptionPlan),
admin.site.register(Erp_Information),
admin.site.register(ErpActiveCompanyAndWeb),