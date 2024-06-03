from django.db import models
from datetime import datetime
# Create your models here.
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
# Create your models here.
from User_Registration_App.models import CompanyRegistrationInformation


from cryptography.fernet import Fernet


class SubscriptionInformation(models.Model):
    class Meta:
        verbose_name_plural = 'Subscription Information'

    company_info = models.ForeignKey(CompanyRegistrationInformation, on_delete=models.CASCADE, blank=True, null=True)

    demandscaled = models.BooleanField(blank=True, null=True)
    acquirescaled = models.BooleanField(blank=True, null=True)
    product_recommendations = models.BooleanField(blank=True, null=True)
    campaignscaled = models.BooleanField(blank=True, null=True)

    number_of_month_to_access = models.CharField(max_length=225, blank=True, null=True)
    number_of_times_ERP = models.CharField(max_length=225,blank=True, null=True)
    number_of_expected_users_of_the_platform = models.CharField(max_length=225,blank=True, null=True)

    number_of_training_per_month = models.CharField(max_length=225,blank=True, null=True)
    number_of_support_hours_per_month = models.CharField(max_length=225,blank=True, null=True)

    platform_total_payment = models.CharField(max_length=225,blank=True, null=True)
    paid_payment = models.CharField(max_length=225,blank=True, null=True)

    services_plan_cost= models.CharField(max_length=225,blank=True, null=True)
    services_plan_cost_and_platform_total_payment= models.CharField(max_length=225,blank=True, null=True)

    payment_status = models.BooleanField(default=False)



    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated On')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Added On')


    def __str__(self):
        return str(self.id)

class BillingQuestion(models.Model):
    class Meta:
        verbose_name_plural = 'Billing Question'

    company_info = models.ForeignKey(CompanyRegistrationInformation, on_delete=models.CASCADE, blank=True, null=True)

    subjects = models.CharField(max_length=225, blank=True, null=True)
    massage = models.TextField(blank=True, null=True)


    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated On')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Added On')


    def __str__(self):
        return str(self.id)



class SubscriptionPlan(models.Model):
    class Meta:
        verbose_name_plural = 'Subscription Plan'


    heading = models.CharField(max_length=225, blank=True, null=True)
    discription = RichTextField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)


    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated On')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Added On')


    def __str__(self):
        return str(self.id)

class Erp_Information(models.Model):

    subscription_info = models.ForeignKey(SubscriptionInformation, on_delete=models.CASCADE, blank=True, null=True)
    erp_name = models.CharField(max_length=100, default='')
    erp_site_name = models.CharField(max_length=8, default='')
    erp_admin_user_name = models.CharField(max_length=100, default='')
    erp_admin_pw_encrypted = models.CharField(max_length=300, default='')
    erp_api_key_encrypted = models.CharField(max_length=300, default='')
    erp_api_secret_encrypted = models.CharField(max_length=300, default='')
    erp_page_about_us_content = models.TextField(default='')
    erp_page_contact_us_content = models.TextField(default='')
    erp_pages_root_email = models.EmailField(default='')
    erp_pages_root_email_pw_encrypted = models.CharField(max_length=300, default='')
    erp_country = models.CharField(max_length=100, default='')
    erp_timezone = models.CharField(max_length=100, default='')
    erp_contact_phone = models.CharField(max_length=20, default='')
    erp_contact_email = models.EmailField(default='')
    erp_whatsapp_phone = models.CharField(max_length=20, default='')
    erp_email_account_name = models.CharField(max_length=100, default='')
    erp_email_id = models.EmailField(default='')
    erp_email_account_password_encrypted = models.CharField(max_length=300, default='')
    # domain name
    erp_smtp_server = models.CharField(max_length=100, default='')
    erp_smtp_port = models.PositiveIntegerField(default=0)
    erp_use_tls = models.BooleanField(default=True)
    erp_use_ssl = models.BooleanField(default=True)
    erp_imap_server = models.CharField(max_length=100, default='')
    erp_imap_port = models.PositiveIntegerField(default=0)
    erp_stripe_account_id_encrypted = models.CharField(max_length=300, default='')
    erp_stripe_access_key_encrypted = models.CharField(max_length=300, default='')
    erp_stripe_api_secret_encrypted = models.CharField(max_length=300, default='')
    erp_shipper_name = models.CharField(max_length=100, default='')
    erp_shipper_api_key_encrypted = models.CharField(max_length=300, default='')
    erp_shipper_api_secret_encrypted = models.CharField(max_length=300, default='')
    erp_whatsup_api_url = models.URLField(default='')
    erp_whatsup_api_token_encrypted = models.CharField(max_length=300, default='')
    erp_whatsup_version = models.CharField(max_length=100, default='')
    erp_whatsup_phone_id = models.CharField(max_length=100, default='')
    erp_whatsup_business_id = models.CharField(max_length=100, default='')

    def save(self, *args, **kwargs):
        # Encrypt sensitive information before saving
        cipher_suite = Fernet(Fernet.generate_key())
        self.erp_admin_pw_encrypted = cipher_suite.encrypt(self.erp_admin_pw_encrypted.encode()).decode()
        self.erp_api_key_encrypted = cipher_suite.encrypt(self.erp_api_key_encrypted.encode()).decode()
        self.erp_api_secret_encrypted = cipher_suite.encrypt(self.erp_api_secret_encrypted.encode()).decode()
        self.erp_pages_root_email_pw_encrypted = cipher_suite.encrypt(self.erp_pages_root_email_pw_encrypted.encode()).decode()
        self.erp_email_account_password_encrypted = cipher_suite.encrypt(self.erp_email_account_password_encrypted.encode()).decode()
        self.erp_stripe_account_id_encrypted = cipher_suite.encrypt(self.erp_stripe_account_id_encrypted.encode()).decode()
        self.erp_stripe_access_key_encrypted = cipher_suite.encrypt(self.erp_stripe_access_key_encrypted.encode()).decode()
        self.erp_stripe_api_secret_encrypted = cipher_suite.encrypt(self.erp_stripe_api_secret_encrypted.encode()).decode()
        self.erp_shipper_api_key_encrypted = cipher_suite.encrypt(self.erp_shipper_api_key_encrypted.encode()).decode()
        self.erp_shipper_api_secret_encrypted = cipher_suite.encrypt(self.erp_shipper_api_secret_encrypted.encode()).decode()
        self.erp_whatsup_api_token_encrypted = cipher_suite.encrypt(self.erp_whatsup_api_token_encrypted.encode()).decode()

        super(Erp_Information, self).save(*args, **kwargs)


class ErpActiveCompanyAndWeb(models.Model):

    subscription_info = models.ForeignKey(SubscriptionInformation, on_delete=models.CASCADE, blank=True, null=True)
    Erp_Info = models.ForeignKey(Erp_Information, on_delete=models.CASCADE, blank=True, null=True)
    company_id = models.CharField(max_length=200,blank=True, null=True)
    website_id = models.CharField(max_length=200, blank=True, null=True)
    domain = models.CharField(max_length=200, blank=True, null=True)
    user_count = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated On')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Added On')

    def __str__(self):
        return str(self.id)