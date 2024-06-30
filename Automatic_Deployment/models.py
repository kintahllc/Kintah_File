from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class OdooDomainSetup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=255, help_text='Your domain name.')
    erp_users = models.IntegerField(help_text='Number of ERP users.')
    static_ip_name = models.CharField(max_length=45, blank=True, null=True, help_text='Name of Assigned static IP address.')
    static_ip = models.CharField(max_length=45, blank=True, null=True, help_text='Assigned static IP address.')
    instance_public_ip = models.CharField(max_length=45, blank=True, null=True, help_text='Assigned public_ip address.')
    instance_name = models.CharField(max_length=255, blank=True, null=True, help_text='Name of the Lightsail instance.')
    instance_id = models.CharField(max_length=255, blank=True, null=True, help_text='ID of the Lightsail instance.')
    blueprint_id = models.CharField(max_length=255, help_text='Blueprint ID for the instance.')
    bundle_id = models.CharField(max_length=255, help_text='Bundle ID for the instance.')
    db_name = models.CharField(max_length=255, blank=True, null=True, help_text='Name of the PostgreSQL database.')
    db_user = models.CharField(max_length=255, blank=True, null=True, help_text='Name of the PostgreSQL database.')
    db_password = models.CharField(max_length=255, blank=True, null=True, help_text='Name of the PostgreSQL database.')
    private_key = models.TextField(blank=True, null=True, help_text='Private key for the instance.')  # New field
    key_pair_name = models.CharField(max_length=255, blank=True, null=True, help_text='Name of the Key Pair')
    confirmed = models.BooleanField(default=False, help_text='Has the static IP been confirmed?')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain

