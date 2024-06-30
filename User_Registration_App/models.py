from django.db import models
from datetime import datetime
# Create your models here.

# from django.contrib.auth.models import User
from account.models import User
# Create your models here.

class CompanyRegistrationInformation(models.Model):
    class Meta:
        verbose_name_plural = 'Company Registration Information'

    user_info = models.ForeignKey(User, on_delete=models.CASCADE)
    file_number = models.CharField(max_length=256, blank=True, null=True)
    client_source = models.CharField(max_length=256, blank=True, null=True)
    fee_amount = models.FloatField(blank=True, null=True)
    Partner_client_company_name = models.CharField(max_length=256, blank=True, null=True)
    partner_client_contact_full_name = models.CharField(max_length=256, blank=True, null=True)
    client_email_address = models.CharField(max_length=256, blank=True, null=True)
    client_phone_code = models.CharField(max_length=256, blank=True, null=True)
    client_phone_number = models.CharField(max_length=256, blank=True, null=True)
    partner_client_company_address = models.CharField(max_length=256, blank=True, null=True)
    partner_client_company_country = models.CharField(max_length=256, blank=True, null=True)
    partner_client_company_state_or_province = models.CharField(max_length=256, blank=True, null=True)
    partner_client_company_city = models.CharField(max_length=256, blank=True, null=True)
    partner_client_company_zip_or_postal_code = models.CharField(max_length=256, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated On')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Added On')


    def __str__(self):
        return f"Company Registration: {self.id} - {self.Partner_client_company_name}"

    def save(self, *args, **kwargs):
        if not self.id:
            max_id = CompanyRegistrationInformation.objects.aggregate(max_id=models.Max('id'))['max_id']
            if max_id is None or max_id < 100000:
                self.id = 100000
            else:
                self.id = max_id + 1
        super().save(*args, **kwargs)




class AdministrationkintahSubscriptionPackagePrice(models.Model):
    class Meta:
        verbose_name_plural = 'Subscription Package Price'

    package_category = models.CharField(max_length=255, blank=True, null=True)
    app = models.CharField(max_length=255, blank=True, null=True)
    event_type = models.CharField(max_length=255, blank=True, null=True)
    monthly_base_cost = models.FloatField(blank=True, null=True)
    monthly_coef = models.FloatField(blank=True, null=True)
    monthly_activity_free = models.FloatField(blank=True, null=True)
    max_purchase_value = models.FloatField(blank=True, null=True)

    usage_cycle = models.CharField(max_length=255, blank=True, null=True)

    base_price = models.FloatField(blank=True, null=True)
    base_number_of_subscription_months = models.FloatField(blank=True, null=True)
    base_number_of_users = models.FloatField(blank=True, null=True)
    base_number_data_reloads = models.FloatField(blank=True, null=True)
    saturation_coef = models.FloatField(blank=True, null=True)


    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)



class PriceMatrixPerCompanyType(models.Model):
    class Meta:
        verbose_name_plural = 'Price Matrix Per Company Type'

    company_type_or_industry = models.CharField(max_length=255, blank=True, null=True)
    fix_cost = models.FloatField(blank=True, null=True)
    company_type_cost = models.FloatField(blank=True, null=True)

    subcategory = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    module = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class AdditionalCostCalculationFixParameters(models.Model):
    class Meta:
        verbose_name_plural = 'Additional Cost Calculation Fix Parameters'


    sup_cost = models.FloatField(blank=True, null=True)
    train_cost = models.FloatField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class TrainingUserEmail(models.Model):
    class Meta:
        verbose_name_plural = 'Training User Email'


    email = models.CharField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID: {self.id}"

