from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
# Create your views here.
from . models import CompanyRegistrationInformation, AdministrationkintahSubscriptionPackagePrice, PriceMatrixPerCompanyType, AdditionalCostCalculationFixParameters, TrainingUserEmail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.conf import settings
import random
import string
import stripe
from subscription_app.models import SubscriptionInformation, BillingQuestion, SubscriptionPlan, Erp_Information
from .files_country_state_city.phone_code import  all_phone_code
from .files_country_state_city.read_country import get_country_name
from .files_country_state_city.read_state import get_state_name, get_state_id
from .files_country_state_city.read_city import get_city_name
from .files_country_state_city.country import country_all
from . files_country_state_city.timezone.timezone import *
from subscription_app.service import create_stripe_product_and_price, create_stripe_customer, create_subscription, create_payment_intent

import stripe
from . utils import odooo_company_and_website_create
from subscription_app.models import ErpActiveCompanyAndWeb
from .utils import create_user_manager_role
from .utils import user_list_of_a_company
from .utils import disable_user_with_user_id

from django.core.files.storage import FileSystemStorage
import csv
import os
import xmlrpc.client
import base64
from .utils import get_or_create_category




def generate_otp(length=6):
    """Generate a random OTP of the specified length."""
    otp = ''.join(random.choices(string.digits, k=length))
    return otp


def home_info(request):
    if request.user.is_authenticated:
        user_info= request.user
        if user_info.first_name == '':
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        else:
            company_info = CompanyRegistrationInformation.objects.get(id=user_info.first_name)

        contex = {
            'user_info':user_info,
            'company_info':company_info,
        }
        return render(request, 'home.html', contex)
    else:
        return redirect('login_info')



def billing_history(request, pk):
    if request.user.is_authenticated:
        user_info= request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
        contex = {
            'user_info':user_info,
            'company_info':company_info,
            'subcription':subcription,
            'subcription_one':subcription_one,
            'erp':erp,
            'erp_active':erp_active,
        }
        return render(request, 'billing_history.html', contex)
    else:
        return redirect('login_info')



def ask_billing_question(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            sub_info = CompanyRegistrationInformation.objects.get(id=pk)
            billqtn = BillingQuestion(
                company_info = sub_info,
                subjects = subject,
                massage = message,
            )
            billqtn.save()

        user_info= request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
        contex = {
            'user_info':user_info,
            'company_info':company_info,
            'subcription':subcription,
            'subcription_one': subcription_one,
            'erp': erp,
            'erp_active': erp_active,

        }
        return render(request, 'ask_billing_question.html', contex)
    else:
        return redirect('login_info')




def update_company_info(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            com_id = request.POST.get('com_id')

            file_number = request.POST.get('file_number')
            client_source = request.POST.get('client_source')
            fee_amount = request.POST.get('fee_amount') or 0
            Partner_client_company_name = request.POST.get('Partner_client_company_name')
            partner_client_contact_full_name = request.POST.get('partner_client_contact_full_name')
            client_email_address = request.POST.get('client_email_address')
            client_phone_number = request.POST.get('client_phone_number')
            client_phone_code = request.POST.get('countryCode')
            partner_client_company_address = request.POST.get('partner_client_company_address')
            partner_client_company_country = request.POST.get('partner_client_company_country')
            partner_client_company_state_or_province = request.POST.get('partner_client_company_state_or_province')
            partner_client_company_city = request.POST.get('partner_client_company_city')


            partner_client_company_state_or_province1 = get_state_name(partner_client_company_state_or_province)
            if partner_client_company_state_or_province1 == None:
                pass
                state_id_in = get_state_id(partner_client_company_state_or_province)
            else:
                state_id_in = partner_client_company_state_or_province
                partner_client_company_state_or_province = partner_client_company_state_or_province1



            city_nam = get_city_name(partner_client_company_city, state_id_in)

            partner_client_company_zip_or_postal_code = request.POST.get('partner_client_company_zip_or_postal_code')

            cri = CompanyRegistrationInformation.objects.get(id=com_id)


            cri.file_number=file_number
            cri.client_source=client_source
            cri.fee_amount=float(fee_amount)
            cri.Partner_client_company_name=Partner_client_company_name
            cri.partner_client_contact_full_name=partner_client_contact_full_name
            cri.client_email_address=client_email_address
            cri.client_phone_number=client_phone_number
            cri.client_phone_code=client_phone_code
            cri.partner_client_company_address=partner_client_company_address
            cri.partner_client_company_country=partner_client_company_country
            if cri.partner_client_company_state_or_province != partner_client_company_state_or_province:
                cri.partner_client_company_state_or_province=partner_client_company_state_or_province
            if cri.partner_client_company_city != partner_client_company_city:
                cri.partner_client_company_city=partner_client_company_city
            cri.partner_client_company_zip_or_postal_code=partner_client_company_zip_or_postal_code

            cri.save()
            messages.success(request, "Updated Successfully! ")

        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        country_names = [country['name'] for country in country_all]
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
            'country_names': country_names,
            'phone_codes': all_phone_code,
            'subcription_one': subcription_one,
            'erp': erp,
            'erp_active': erp_active,

        }
        return render(request, 'update_company_info3.html', contex)
    else:
        return redirect('login_info')



def change_password(request, pk):
    if request.user.is_authenticated:

        if request.method == 'POST':
            new_password = request.POST.get('new_password')

            u = request.user
            u.set_password(new_password)
            u.save()


            messages.success(request, "Updated Password Successfully! ")


        user_info = request.user
        if user_info.first_name == '':
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        else:
            company_info = CompanyRegistrationInformation.objects.get(id=user_info.first_name)

        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
            'subcription_one': subcription_one,
            'erp': erp,
            'erp_active': erp_active,

        }
        return render(request, 'change_password.html', contex)
    else:
        return redirect('login_info')



def subscription_history(request, pk):
    if request.user.is_authenticated:

        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
            'subcription_one': subcription_one,
            'erp': erp,
            'erp_active': erp_active,

        }
        return render(request, 'subscription_history.html', contex)
    else:
        return redirect('login_info')


def add_company_users(request, pk):
    if request.user.is_authenticated:


        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
        contex = {
            'subcription_one': subcription_one,
            'erp': erp,
            'erp_active': erp_active,
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
        }
        return render(request, 'add_company_users.html', contex)
    else:
        return redirect('login_info')


def add_expected_users(request, pk):
    if request.user.is_authenticated:

        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        myusr_vari = User.objects.create_user(email, email, password)
        myusr_vari.first_name = pk
        myusr_vari.last_name = role
        myusr_vari.is_active = True
        myusr_vari.save()

        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
            'subcription_one': subcription_one,
            'erp': erp,
            'erp_active': erp_active,
        }
        return render(request, 'add_company_users.html', contex)
    else:
        return redirect('login_info')


def upgrade_subscription(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            from_back = request.POST.get('from_back')
            demandscaled = request.POST.get('demandscaled')
            acquirescaled = request.POST.get('acquirescaled')
            Product_recommendations = request.POST.get('Product_recommendations')
            campaignscaled = request.POST.get('campaignscaled')
            CompanyRegistrationInformationId = request.POST.get('CompanyRegistrationInformationId')
            sub_id = request.POST.get('sub_id')
            check = request.POST.get('check')
            plane_price = request.POST.get('plane_price') or 0

            if from_back == "coming_back":
                subcription_pk = SubscriptionInformation.objects.get(id=sub_id)
                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                         payment_status=True).last()
                erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
                erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one,
                                                                   Erp_Info=erp).last()
                contex = {
                    'demandscaled': demandscaled,
                    'acquirescaled': acquirescaled,
                    'Product_recommendations': Product_recommendations,
                    'campaignscaled': campaignscaled,
                    'CompanyRegistrationInformationId': CompanyRegistrationInformationId,
                    'user_info': user_info,
                    'company_info': company_info,
                    'subcription': subcription,
                    'sub_id': sub_id,
                    'subcription_pk': subcription_pk,
                    'plane_price': plane_price,
                    'subcription_one': subcription_one,
                    'erp': erp,
                    'erp_active': erp_active,
                }

                return render(request, 'upgrade_sub.html', contex)
            elif check == "yes":
                # sp = SubscriptionPlan.objects.all()
                # user_info = request.user
                # company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                # subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                # subcription_pk = SubscriptionInformation.objects.get(id=sub_id)
                # contex = {
                #     'user_info': user_info,
                #     'company_info': company_info,
                #     'subcription': subcription,
                #     'sp': sp,
                #     'subcription_pk': subcription_pk,
                #
                # }
                #
                # return render(request, 'upgrade_new_subscription_plan.html', contex)
                subcription_pk = SubscriptionInformation.objects.get(id=sub_id)

                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                contex = {
                    'user_info': user_info,
                    'company_info': company_info,
                    'subcription': subcription,
                    'subcription_pk': subcription_pk,
                    'sub_id': sub_id,
                    'plane_price': plane_price,
                }
                return render(request, 'upgrade_sub.html', contex)




            else:


                subcription_pk = SubscriptionInformation.objects.get(id=sub_id)


                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                contex = {
                    'user_info': user_info,
                    'company_info': company_info,
                    'subcription': subcription,
                    'subcription_pk': subcription_pk,
                    'sub_id': sub_id,
                    'plane_price': plane_price,
                }
                return render(request, 'upgrade_sub.html', contex)

        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
        }
        return render(request, 'upgrade_subscription1.html', contex)

    else:
        return redirect('login_info')












def upgrade_new_subscription_plan(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':

            campaignscaled = request.POST.get('campaignscaled')
            plane_price = request.POST.get('plane_price')

            file_number = request.POST.get('file_number')
            client_source = request.POST.get('client_source')
            fee_amount = request.POST.get('fee_amount')
            Partner_client_company_name = request.POST.get('Partner_client_company_name')
            partner_client_contact_full_name = request.POST.get('partner_client_contact_full_name')
            client_email_address = request.POST.get('client_email_address')
            client_phone_number = request.POST.get('client_phone_number')
            countryCode = request.POST.get('countryCode')
            partner_client_company_address = request.POST.get('partner_client_company_address')
            partner_client_company_country = request.POST.get('partner_client_company_country')

            partner_client_company_state_or_province = request.POST.get('partner_client_company_state_or_province')
            partner_client_company_city = request.POST.get('partner_client_company_city')
            partner_client_company_zip_or_postal_code = request.POST.get('partner_client_company_zip_or_postal_code')
            password = request.POST.get('password')

            myusr_vari = User.objects.create_user(client_email_address, client_email_address, password)
            myusr_vari.first_name = ''
            myusr_vari.last_name = ''
            myusr_vari.is_active = True
            myusr_vari.save()

            user = authenticate(request, username=client_email_address, password=password)
            if user is not None:
                login(request, user)
                request.session['user_id'] = user.id
                request.session['username'] = user.username

            partner_client_company_country = get_country_name(partner_client_company_country)
            partner_client_company_state_or_province = get_state_name(partner_client_company_state_or_province)

            cri = CompanyRegistrationInformation(
                user_info=myusr_vari,
                file_number=file_number,
                client_source=client_source,
                fee_amount=fee_amount,
                Partner_client_company_name=Partner_client_company_name,
                partner_client_contact_full_name=partner_client_contact_full_name,
                client_email_address=client_email_address,
                client_phone_number=client_phone_number,
                client_phone_code=countryCode,
                partner_client_company_address=partner_client_company_address,
                partner_client_company_country=partner_client_company_country,
                partner_client_company_state_or_province=partner_client_company_state_or_province,
                partner_client_company_city=partner_client_company_city,
                partner_client_company_zip_or_postal_code=partner_client_company_zip_or_postal_code,
            )
            cri.save()

            sp = SubscriptionPlan.objects.all()
            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subcription = SubscriptionInformation.objects.filter(company_info=company_info)
            contex = {
                'user_info': user_info,
                'company_info': company_info,
                'subcription': subcription,
                'CompanyRegistrationInformationId': cri.id,
                'sp': sp,
                'campaignscaled': campaignscaled,
                'plane_price': plane_price,
            }


            return render(request, 'new_subscriptions.html', contex)


        sp = SubscriptionPlan.objects.all()
        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,

            'sp': sp,

        }

        return render(request, 'new_subscription_plan.html', contex)
    else:
        return redirect('login_info')














def upgrade_calculate_subscriptions(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            demandscaled = request.POST.get('demandscaled')
            acquirescaled = request.POST.get('acquirescaled')
            Product_recommendations = request.POST.get('Product_recommendations')
            campaignscaled = request.POST.get('campaignscaled')
            CompanyRegistrationInformationId = request.POST.get('CompanyRegistrationInformationId')
            sub_id = request.POST.get('sub_id')
            plane_price = request.POST.get('plane_price') or 0

            try:
                package_price_demandscaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(
                    app="demandscaled").last()
                package_price_acquirescaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(
                    app="acquirescaled").last()
                package_price_recommendscaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(
                    app="recommendscaled").last()

                prescriptive_ai = AdministrationkintahSubscriptionPackagePrice.objects.filter(
                    app="(prescriptive_ai").last()
                metricscaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="metricscaled").last()
                driven_erp = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="driven_erp").last()
                driven_edriven_e_commerce = AdministrationkintahSubscriptionPackagePrice.objects.filter(
                    app="driven_edriven_e_commerce").last()

                if package_price_demandscaled:
                    package_price_demandscaled_monthly_base_cost = package_price_demandscaled.monthly_base_cost
                    package_price_demandscaled_monthly_coef = package_price_demandscaled.monthly_coef
                    package_price_demandscaled_monthly_activity_free = package_price_demandscaled.monthly_activity_free

                    package_price_demandscaled_base_price = package_price_demandscaled.base_price
                    package_price_demandscaled_base_number_of_subscription_months = package_price_demandscaled.base_number_of_subscription_months
                    package_price_demandscaled_base_number_of_users = package_price_demandscaled.base_number_of_users
                    package_price_demandscaled_base_number_data_reloads = package_price_demandscaled.base_number_data_reloads
                    package_price_demandscaled_saturation_coef = package_price_demandscaled.saturation_coef
                else:
                    package_price_demandscaled_monthly_base_cost = 495
                    package_price_demandscaled_monthly_coef = 0.025
                    package_price_demandscaled_monthly_activity_free = 12

                    package_price_demandscaled_base_price = 2
                    package_price_demandscaled_base_number_of_subscription_months = 4.9
                    package_price_demandscaled_base_number_of_users = 6
                    package_price_demandscaled_base_number_data_reloads = 6
                    package_price_demandscaled_saturation_coef = 8

                if package_price_acquirescaled:
                    package_price_acquirescaled_monthly_base_cost = package_price_acquirescaled.monthly_base_cost
                    package_price_acquirescaled_monthly_coef = package_price_acquirescaled.monthly_coef
                    package_price_acquirescaled_monthly_activity_free = package_price_acquirescaled.monthly_activity_free

                    package_price_acquirescaled_base_price = package_price_acquirescaled.base_price
                    package_price_acquirescaled_base_number_of_subscription_months = package_price_acquirescaled.base_number_of_subscription_months
                    package_price_acquirescaled_base_number_of_users = package_price_acquirescaled.base_number_of_users
                    package_price_acquirescaled_base_number_data_reloads = package_price_acquirescaled.base_number_data_reloads
                    package_price_acquirescaled_saturation_coef = package_price_acquirescaled.saturation_coef
                else:
                    package_price_acquirescaled_monthly_base_cost = 495
                    package_price_acquirescaled_monthly_coef = 0.025
                    package_price_acquirescaled_monthly_activity_free = 12

                    package_price_acquirescaled_base_price = 22
                    package_price_acquirescaled_base_number_of_subscription_months = 2.9
                    package_price_acquirescaled_base_number_of_users = 3
                    package_price_acquirescaled_base_number_data_reloads = 2.7
                    package_price_acquirescaled_saturation_coef = 2.3


                if package_price_recommendscaled:
                    package_price_recommendscaled_monthly_base_cost = package_price_recommendscaled.monthly_base_cost
                    package_price_recommendscaled_monthly_coef = package_price_recommendscaled.monthly_coef
                    package_price_recommendscaled_monthly_activity_free = package_price_recommendscaled.monthly_activity_free

                    package_price_recommendscaled_base_price = package_price_recommendscaled.base_price
                    package_price_recommendscaled_base_number_of_subscription_months = package_price_recommendscaled.base_number_of_subscription_months
                    package_price_recommendscaled_base_number_of_users = package_price_recommendscaled.base_number_of_users
                    package_price_recommendscaled_base_number_data_reloads = package_price_recommendscaled.base_number_data_reloads
                    package_price_recommendscaled_saturation_coef = package_price_recommendscaled.saturation_coef

                else:
                    package_price_recommendscaled_monthly_base_cost = 495.99
                    package_price_recommendscaled_monthly_coef = 0.025
                    package_price_recommendscaled_monthly_activity_free = 12

                    package_price_recommendscaled_base_price = 2
                    package_price_recommendscaled_base_number_of_subscription_months = 2.9
                    package_price_recommendscaled_base_number_of_users = 2
                    package_price_recommendscaled_base_number_data_reloads = 2
                    package_price_recommendscaled_saturation_coef = 5.9


                if prescriptive_ai:
                    prescriptive_ai_monthly_base_cost = prescriptive_ai.monthly_base_cost
                    prescriptive_ai_monthly_coef = prescriptive_ai.monthly_coef
                    prescriptive_ai_monthly_activity_free = prescriptive_ai.monthly_activity_free

                    prescriptive_ai_monthly_base_price = prescriptive_ai.base_price
                    prescriptive_ai_monthly_base_number_of_subscription_months = prescriptive_ai.base_number_of_subscription_months
                    prescriptive_ai_monthly_base_number_of_users = prescriptive_ai.base_number_of_users
                    prescriptive_ai_monthly_base_number_data_reloads = prescriptive_ai.base_number_data_reloads
                    prescriptive_ai_monthly_saturation_coef = prescriptive_ai.saturation_coef


                else:
                    prescriptive_ai_monthly_base_cost = 995
                    prescriptive_ai_monthly_coef = 0.025
                    prescriptive_ai_monthly_activity_free = 12

                    prescriptive_ai_monthly_base_price = 11
                    prescriptive_ai_monthly_base_number_of_subscription_months = 1.1
                    prescriptive_ai_monthly_base_number_of_users = 11
                    prescriptive_ai_monthly_base_number_data_reloads = 12
                    prescriptive_ai_monthly_saturation_coef = 3

                if metricscaled:
                    metricscaled_monthly_base_cost = metricscaled.monthly_base_cost
                    metricscaled_monthly_coef = metricscaled.monthly_coef
                    metricscaled_monthly_activity_free = metricscaled.monthly_activity_free

                    metricscaled_monthly_base_price = metricscaled.base_price
                    metricscaled_monthly_base_number_of_subscription_months = metricscaled.base_number_of_subscription_months
                    metricscaled_monthly_base_number_of_users = metricscaled.base_number_of_users
                    metricscaled_monthly_base_number_data_reloads = metricscaled.base_number_data_reloads
                    metricscaled_monthly_saturation_coef = metricscaled.saturation_coef
                else:
                    metricscaled_monthly_base_cost = 995
                    metricscaled_monthly_coef = 0.025
                    metricscaled_monthly_activity_free = 12

                    metricscaled_monthly_base_price = 3
                    metricscaled_monthly_base_number_of_subscription_months = 22
                    metricscaled_monthly_base_number_of_users = 43
                    metricscaled_monthly_base_number_data_reloads = 45
                    metricscaled_monthly_saturation_coef = 34

                if driven_erp:
                    driven_erp_monthly_base_cost = driven_erp.monthly_base_cost
                    driven_erp_monthly_coef = driven_erp.monthly_coef
                    driven_erp_monthly_activity_free = driven_erp.monthly_activity_free

                    driven_erp_monthly_base_price = driven_erp.base_price
                    driven_erp_monthly_base_number_of_subscription_months = driven_erp.base_number_of_subscription_months
                    driven_erp_monthly_base_number_of_users = driven_erp.base_number_of_users
                    driven_erp_monthly_base_number_data_reloads = driven_erp.base_number_data_reloads
                    driven_erp_monthly_saturation_coef = driven_erp.saturation_coef
                else:
                    driven_erp_monthly_base_cost = 995
                    driven_erp_monthly_coef = 0.025
                    driven_erp_monthly_activity_free = 12

                    driven_erp_monthly_base_price = 33
                    driven_erp_monthly_base_number_of_subscription_months = 2
                    driven_erp_monthly_base_number_of_users = 9
                    driven_erp_monthly_base_number_data_reloads = 89
                    driven_erp_monthly_saturation_coef = 8

                if driven_edriven_e_commerce:
                    driven_edriven_e_commerce_monthly_base_cost = driven_edriven_e_commerce.monthly_base_cost
                    driven_edriven_e_commerce_monthly_coef = driven_edriven_e_commerce.monthly_coef
                    driven_edriven_e_commerce_monthly_coef_monthly_activity_free = driven_edriven_e_commerce.monthly_activity_free

                    driven_edriven_e_commerce_monthly_base_price = driven_edriven_e_commerce.base_price
                    driven_edriven_e_commerce_monthly_base_number_of_subscription_months = driven_edriven_e_commerce.base_number_of_subscription_months
                    driven_edriven_e_commerce_monthly_base_number_of_users = driven_edriven_e_commerce.base_number_of_users
                    driven_edriven_e_commerce_monthly_base_number_data_reloads = driven_edriven_e_commerce.base_number_data_reloads
                    driven_edriven_e_commerce_monthly_saturation_coef = driven_edriven_e_commerce.saturation_coef

                else:
                    driven_edriven_e_commerce_monthly_base_cost = 995
                    driven_edriven_e_commerce_monthly_coef = 0.025
                    driven_edriven_e_commerce_monthly_coef_monthly_activity_free = 12

                    driven_edriven_e_commerce_monthly_base_price = 6
                    driven_edriven_e_commerce_monthly_base_number_of_subscription_months = 9
                    driven_edriven_e_commerce_monthly_base_number_of_users = 5
                    driven_edriven_e_commerce_monthly_base_number_data_reloads = 56
                    driven_edriven_e_commerce_monthly_saturation_coef = 5

                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                the_subcription = SubscriptionInformation.objects.get(id=sub_id)
                subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                         payment_status=True).last()
                erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
                erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one,
                                                                   Erp_Info=erp).last()

                all_company_types = PriceMatrixPerCompanyType.objects.all()
                parameters = AdditionalCostCalculationFixParameters.objects.filter().last()
                if parameters:
                    sup_cost = parameters.sup_cost
                    Train_cost = parameters.train_cost
                else:
                    sup_cost = 25
                    Train_cost = 500
                contex = {
                    'all_company_types': all_company_types,
                    'sup_cost': sup_cost,
                    'Train_cost': Train_cost,


                    'subcription_one': subcription_one,
                    'erp': erp,
                    'erp_active': erp_active,
                    'campaignscaled': campaignscaled,
                    'plane_price': plane_price,
                    'demandscaled': demandscaled,
                    'demandscaled_monthly_base_cost': package_price_demandscaled_monthly_base_cost,
                    'demandscaled_monthly_coef': package_price_demandscaled_monthly_coef,
                    'demandscaled_monthly_activity_free': package_price_demandscaled_monthly_activity_free,

                    'acquirescaled': acquirescaled,
                    'acquirescaled_monthly_base_cost': package_price_acquirescaled_monthly_base_cost,
                    'acquirescaled_monthly_coef': package_price_acquirescaled_monthly_coef,
                    'acquirescaled_monthly_activity_free': package_price_acquirescaled_monthly_activity_free,

                    'Product_recommendations': Product_recommendations,
                    'Product_recommendations_monthly_base_cost': package_price_recommendscaled_monthly_base_cost,
                    'Product_recommendations_monthly_coef': package_price_recommendscaled_monthly_coef,
                    'Product_recommendations_monthly_activity_free': package_price_recommendscaled_monthly_activity_free,

                    'prescriptive_ai_monthly_base_cost': prescriptive_ai_monthly_base_cost,
                    'prescriptive_ai_monthly_coef': prescriptive_ai_monthly_coef,
                    'prescriptive_ai_monthly_activity_free': prescriptive_ai_monthly_activity_free,

                    'metricscaled_monthly_base_cost': metricscaled_monthly_base_cost,
                    'metricscaled_monthly_coef': metricscaled_monthly_coef,
                    'metricscaled_monthly_activity_free': metricscaled_monthly_activity_free,

                    'driven_erp_monthly_base_cost': driven_erp_monthly_base_cost,
                    'driven_erp_monthly_coef': driven_erp_monthly_coef,
                    'driven_erp_monthly_activity_free': driven_erp_monthly_activity_free,

                    'driven_edriven_e_commerce_monthly_base_cost': driven_edriven_e_commerce_monthly_base_cost,
                    'driven_edriven_e_commerce_monthly_coef': driven_edriven_e_commerce_monthly_coef,
                    'driven_edriven_e_commerce_monthly_coef_monthly_activity_free': driven_edriven_e_commerce_monthly_coef_monthly_activity_free,

                    'CompanyRegistrationInformationId': company_info.id,
                    'user_info': user_info,
                    'company_info': company_info,
                    'subcription': subcription,
                    'the_subcription': the_subcription,
                    'sub_id': sub_id,


                    'package_price_demandscaled_base_price': package_price_demandscaled_base_price,
                    'package_price_demandscaled_base_number_of_subscription_months': package_price_demandscaled_base_number_of_subscription_months,
                    'package_price_demandscaled_base_number_of_users': package_price_demandscaled_base_number_of_users,
                    'package_price_demandscaled_base_number_data_reloads': package_price_demandscaled_base_number_data_reloads,
                    'package_price_demandscaled_saturation_coef': package_price_demandscaled_saturation_coef,
                    'package_price_acquirescaled_base_price': package_price_acquirescaled_base_price,
                    'package_price_acquirescaled_base_number_of_subscription_months': package_price_acquirescaled_base_number_of_subscription_months,
                    'package_price_acquirescaled_base_number_of_users': package_price_acquirescaled_base_number_of_users,
                    'package_price_acquirescaled_base_number_data_reloads': package_price_acquirescaled_base_number_data_reloads,
                    'package_price_acquirescaled_saturation_coef': package_price_acquirescaled_saturation_coef,
                    'package_price_recommendscaled_base_price': package_price_recommendscaled_base_price,
                    'package_price_recommendscaled_base_number_of_subscription_months': package_price_recommendscaled_base_number_of_subscription_months,
                    'package_price_recommendscaled_base_number_of_users': package_price_recommendscaled_base_number_of_users,
                    'package_price_recommendscaled_base_number_data_reloads': package_price_recommendscaled_base_number_data_reloads,
                    'package_price_recommendscaled_saturation_coef': package_price_recommendscaled_saturation_coef,
                    'prescriptive_ai_monthly_base_price': prescriptive_ai_monthly_base_price,
                    'prescriptive_ai_monthly_base_number_of_subscription_months': prescriptive_ai_monthly_base_number_of_subscription_months,
                    'prescriptive_ai_monthly_base_number_of_users': prescriptive_ai_monthly_base_number_of_users,
                    'prescriptive_ai_monthly_base_number_data_reloads': prescriptive_ai_monthly_base_number_data_reloads,
                    'prescriptive_ai_monthly_saturation_coef': prescriptive_ai_monthly_saturation_coef,
                    'metricscaled_monthly_base_price': metricscaled_monthly_base_price,
                    'metricscaled_monthly_base_number_of_subscription_months': metricscaled_monthly_base_number_of_subscription_months,
                    'metricscaled_monthly_base_number_of_users': metricscaled_monthly_base_number_of_users,
                    'metricscaled_monthly_base_number_data_reloads': metricscaled_monthly_base_number_data_reloads,
                    'metricscaled_monthly_saturation_coef': metricscaled_monthly_saturation_coef,
                    'driven_erp_monthly_base_price': driven_erp_monthly_base_price,
                    'driven_erp_monthly_base_number_of_subscription_months': driven_erp_monthly_base_number_of_subscription_months,
                    'driven_erp_monthly_base_number_of_users': driven_erp_monthly_base_number_of_users,
                    'driven_erp_monthly_base_number_data_reloads': driven_erp_monthly_base_number_data_reloads,
                    'driven_erp_monthly_saturation_coef': driven_erp_monthly_saturation_coef,
                    'driven_edriven_e_commerce_monthly_base_price': driven_edriven_e_commerce_monthly_base_price,
                    'driven_edriven_e_commerce_monthly_base_number_of_subscription_months': driven_edriven_e_commerce_monthly_base_number_of_subscription_months,
                    'driven_edriven_e_commerce_monthly_base_number_of_users': driven_edriven_e_commerce_monthly_base_number_of_users,
                    'driven_edriven_e_commerce_monthly_base_number_data_reloads': driven_edriven_e_commerce_monthly_base_number_data_reloads,
                    'driven_edriven_e_commerce_monthly_saturation_coef': driven_edriven_e_commerce_monthly_saturation_coef,


                }
                jk=0
                return render(request, "upgrade_calculate_subscriptions.html", contex)
            except Exception as e:
                d = str(e)
                messages.warning(request, str(e))

                return render(request, "upgrade_calculate_subscriptions.html")
    else:
        return redirect('login_info')





def upgrade_submit_subscription_inside_home(request, pk):
    if request.user.is_authenticated:
        try:
            CompanyRegistrationInformationId = request.POST.get('CompanyRegistrationInformationId')
            sub_id = request.POST.get('sub_id')
            demandscaled = request.POST.get('demandscaled')
            if demandscaled == 'on':
                demandscaled = True
            else:

                demandscaled = False
            acquirescaled = request.POST.get('acquirescaled')
            if acquirescaled == 'on':
                acquirescaled = True
            else:
                acquirescaled = False
            Product_recommendations = request.POST.get('Product_recommendations')
            if Product_recommendations == 'on':
                Product_recommendations = True
            else:
                Product_recommendations = False
            campaignscaled = request.POST.get('campaignscaled')
            if campaignscaled == 'on':
                campaignscaled = True
            else:
                campaignscaled = False

            plane_price = request.POST.get('plane_price')
            month_to_access = request.POST.get('month_to_access')
            number_of_times = request.POST.get('number_of_times')
            expected_users = request.POST.get('expected_users')

            training_hours = request.POST.get('training_hours')
            support_hours = request.POST.get('support_hours')

            payment_type_get = request.POST.get('payment_type_get')
            total_amount = request.POST.get('total_amount')

            installment_amount = request.POST.get('installment_amount')
            all_amount_sum = request.POST.get('all_amount_sum')
            installmentsCount = request.POST.get('installmentsCount')
            if payment_type_get == "installments":
                total = float(installmentsCount)
            else:
                total = float(installmentsCount)

            com_id = CompanyRegistrationInformation.objects.get(id=CompanyRegistrationInformationId)


            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subcription = SubscriptionInformation.objects.filter(company_info=company_info)
            subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()

            publishable_key = settings.STRIPE_PUBLIC_KEY

            context = {
                'training_hours': training_hours,
                'support_hours': support_hours,

                'subcription_one': subcription_one,
                'erp': erp,
                'erp_active': erp_active,
                'demandscaled': demandscaled,
                'acquirescaled': acquirescaled,
                'Product_recommendations': Product_recommendations,
                'campaignscaled': campaignscaled,
                'plane_price': plane_price,
                'month_to_access': month_to_access,
                'number_of_times': number_of_times,
                'expected_users': expected_users,


                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total,
                'user_info': user_info,
                'company_info': company_info,
                'subcription': subcription,

                'services_plan_cost_and_platform_total_payment': all_amount_sum,
                'installment_amount': installment_amount,
                'now_pay': total,

            }
            return render(request, 'payment_home_for_home_for_upgrade.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')
    else:
        return redirect('login_info')



# @login_required(login_url="users:login")
def Payment_Submit_for_upgrade(request):
    if request.user.is_authenticated:
        # Getting post requests values
        stripeToken = request.POST.get('stripeToken')
        payment_amount = request.POST.get('payment_amount')
        total_amount = request.POST.get('total_amount')
        sub_id = request.POST.get('analytics_services_info_id')
        training_hours = request.POST.get('training_hours')
        support_hours = request.POST.get('support_hours')

        installment_amount = request.POST.get('installment_amount')

        services_plan_cost_and_platform_total_payment = request.POST.get('services_plan_cost_and_platform_total_payment')
        now_pay = request.POST.get('now_pay')



        demandscaled = request.POST.get('demandscaled')
        acquirescaled = request.POST.get('acquirescaled')
        Product_recommendations = request.POST.get('Product_recommendations')
        campaignscaled = request.POST.get('campaignscaled')
        plane_price = request.POST.get('plane_price')

        month_to_access = request.POST.get('month_to_access')
        number_of_times = request.POST.get('number_of_times')
        expected_users = request.POST.get('expected_users')

        secret_key = settings.STRIPE_SECRET_KEY
        stripe.api_key = secret_key
        try:
            product_name = 'Custom Analytics Service'
            unit_price = float(services_plan_cost_and_platform_total_payment) or 300.00
            upfront_payment = float(now_pay) or 200.0  # Amount to be paid upfront/now
            installment_amount = float(installment_amount) or 50.0  # Amount of each installment
            currency = 'usd'
            interval = 'month'  # Monthly billing
            user_info = request.user
            email = user_info.email
            name = user_info.first_name

            payment_method = request.POST.get('payment_method')
            stripe_token = request.POST.get('stripeToken')

            # Create product and price
            product_id, price_id = create_stripe_product_and_price(product_name, unit_price, currency, interval)

            if product_id and price_id:
                # Create customer
                customer_id = create_stripe_customer(email, name)

                if customer_id:
                    # Create subscription with incomplete payment
                    subscription = create_subscription(customer_id, price_id)

                    payment_method = stripe.PaymentMethod.create(
                        type='card',
                        card={'token': stripe_token}
                    )
                    pid = payment_method.id
                    # Create PaymentIntent to collect upfront payment
                    payment_intent = create_payment_intent(customer_id, upfront_payment, currency, payment_method)

                    if payment_intent and payment_intent.status == 'succeeded':
                        messages.success(request, 'Payment was Successfull !!')

                        analitics_info = SubscriptionInformation.objects.filter(id=sub_id).last()
                        if analitics_info:
                            analitics_info.payment_status = True
                            analitics_info.paid_payment = total_amount

                            analitics_info.demandscaled = demandscaled
                            analitics_info.acquirescaled = acquirescaled
                            analitics_info.product_recommendations = Product_recommendations
                            analitics_info.campaignscaled = campaignscaled
                            analitics_info.services_plan_cost = plane_price

                            analitics_info.number_of_month_to_access = month_to_access
                            analitics_info.number_of_times_ERP = number_of_times
                            analitics_info.number_of_expected_users_of_the_platform = expected_users
                            analitics_info.number_of_support_hours_per_month = support_hours
                            analitics_info.number_of_training_per_month = training_hours
                            analitics_info.platform_total_payment = total_amount

                            analitics_info.save()

                        print(f"Product ID: {product_id}, Price ID: {price_id}, Customer: {customer_id}, Subscription: {subscription.id}")

                        user_info = request.user
                        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                        sub_id_info = SubscriptionInformation.objects.filter(id=sub_id).last()
                        erp_info = Erp_Information.objects.filter(subscription_info = sub_id_info).last()
                        contex = {
                            'user_info': user_info,
                            'company_info': company_info,
                            'subcription': subcription,
                            'sub_id': sub_id,
                            'sub_id_info': sub_id_info,
                            'timezone_all': timezone_all,
                            'erp_info': erp_info,
                        }
                        return render(request, 'erp_info_for_home_for_upgrade.html', contex)


                        # return redirect('home_info')

                    else:
                        return HttpResponse("Failed to collect upfront payment.")
                else:
                    return HttpResponse("Failed to create customer.")
            else:
                return HttpResponse("Failed to create Product and Price.")

        except stripe.error.CardError as e:
            messages.info(request, f"{e.error.message}")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)

        except stripe.error.RateLimitError as e:
            messages.info(request, f"{e.error.message}")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        except stripe.error.InvalidRequestError as e:
            messages.info(request, "Invalid Request !")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        except stripe.error.AuthenticationError as e:
            messages.info(request, "Authentication Error !!")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        except stripe.error.APIConnectionError as e:
            messages.info(request, "Check Your Connection !")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        except stripe.error.StripeError as e:
            messages.info(request, "There was an error please try again !")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        except Exception as e:
            messages.info(request, "A serious error occured we were notified !")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        return redirect('shop_dashboard', analytics_services_info_id)
    else:
        return redirect('login_info')


def cancel_subscription(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            sub_id = request.POST.get('sub_id')
            subcription = SubscriptionInformation.objects.get(id=sub_id)
            subcription.delete()



            messages.success(request, "Cancel Subscription Successfully! ")

        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
            'subcription_one': subcription_one,
            'erp': erp,
            'erp_active': erp_active,
        }
        return render(request, 'cancel_subscription.html', contex)
    else:
        return redirect('login_info')

import re
def activate_my_erp(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                erp_id = request.POST.get('erp_id')
                user_count = request.POST.get('user_count')
                erp_info = Erp_Information.objects.get(id=erp_id)
                c_name = erp_info.erp_name
                w_name = erp_info.erp_site_name
                domain = erp_info.erp_smtp_server
                res = odooo_company_and_website_create(c_name, w_name, domain)
                if res == None:
                    messages.warning(request, 'Please make sure the erp name and erp site name is uniq and erp smtp server is a domain and try again !')

                else:
                    company_id = res[0]
                    website_id = res[1]
                    try:
                        user_count = int(user_count)
                    except:
                        user_count = 0
                    Eerp_active = ErpActiveCompanyAndWeb(
                        subscription_info=erp_info.subscription_info,
                        Erp_Info = erp_info,
                        company_id = company_id,
                        website_id = website_id,
                        domain = domain,
                        user_count = user_count,
                    )
                    Eerp_active.save()
                    messages.success(request, "Successfully install cmpany and website")
            except Exception as e:
                error_message = str(e)
                print('ins')

                # Compile the regular expression pattern
                pattern = re.compile(r'database "kintah-db" does not exist')
                # Search for the pattern in the error message
                if pattern.search(error_message):
                    print('yes')  # This will confirm the pattern was found
                    messages.warning(request, 'FATAL: database "kintah-db" does not exist')
                else:
                    messages.warning(request, str(e))


        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info = erp).last()
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
            'erp': erp,
            'subcription_one': subcription_one,
            'erp_active': erp_active,
        }
        return render(request, 'activate_my_erp.html', contex)
    else:
        return redirect('login_info')




def activate_my_erp_info(request, pk):
    if request.user.is_authenticated:

        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info = erp).last()
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
            'erp': erp,
            'subcription_one': subcription_one,
            'erp_active': erp_active,
        }
        return render(request, 'activate_my_erp_info.html', contex)
    else:
        return redirect('login_info')




def add_user_with_manager_role(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                erp_active_id = request.POST.get('erp_active_id')
                user_name = request.POST.get('user_name')
                user_login = request.POST.get('user_login')
                user_email = request.POST.get('user_email')
                new_password = request.POST.get('new_password')

                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                if erp_active_info.user_count > 0 :
                    remain = erp_active_info.user_count
                    erp_active_info.user_count = remain-1
                    company_id = erp_active_info.company_id
                    website_id = erp_active_info.website_id

                    erp_active_info.save()
                    GROUP_NAME = 'Manager'

                    res = create_user_manager_role(user_name, user_login, user_email, new_password, company_id, website_id, GROUP_NAME)

                    if res == None:
                        remain = erp_active_info.user_count
                        erp_active_info.user_count = remain + 1
                        erp_active_info.save()
                        messages.warning(request,'Manager is  not created ! change your email and login and try again !')

                    else:
                        messages.warning(request,'Manager is created !')
                else:
                    messages.warning(request,'your user create limit is over !')
            except Exception as e:
                messages.warning(request, str(e))




        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info = erp).last()
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
            'erp': erp,
            'subcription_one': subcription_one,
            'erp_active': erp_active,
        }
        return render(request, 'add_user_with_manager_role.html', contex)
    else:
        return redirect('login_info')



def add_user_without_manager_role(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                erp_active_id = request.POST.get('erp_active_id')
                user_name = request.POST.get('user_name')
                user_login = request.POST.get('user_login')
                user_email = request.POST.get('user_email')
                new_password = request.POST.get('new_password')

                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                if erp_active_info.user_count > 0 :
                    remain = erp_active_info.user_count
                    erp_active_info.user_count = remain-1
                    company_id = erp_active_info.company_id
                    website_id = erp_active_info.website_id

                    erp_active_info.save()
                    GROUP_NAME = 'User'

                    res = create_user_manager_role(user_name, user_login, user_email, new_password, company_id, website_id, GROUP_NAME)

                    if res == None:
                        remain = erp_active_info.user_count
                        erp_active_info.user_count = remain + 1
                        erp_active_info.save()
                        messages.warning(request,'User is  not created ! change your email and login and try again !')

                    else:
                        messages.warning(request,'User is created !')
                else:
                    messages.warning(request,'your user create limit is over !')
            except Exception as e:
                messages.warning(request, str(e))



        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info = erp).last()
        contex = {
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,
            'erp': erp,
            'subcription_one': subcription_one,
            'erp_active': erp_active,
        }
        return render(request, 'add_user_without_manager_role.html', contex)
    else:
        return redirect('login_info')



def remove_user(request, pk):
    if request.user.is_authenticated:
        try:
            if request.method == 'POST':
                try:
                    erp_active_id = request.POST.get('erp_active_id')
                    user_id = int(request.POST.get('user_id'))


                    erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                    website_id = int(erp_active_info.website_id)
                    company_id = int(erp_active_info.company_id)
                    res = disable_user_with_user_id(user_id, company_id, website_id)
                    if res=="DONE":
                        messages.success(request,'user is disabled !')

                    else:
                        messages.warning(request,'try again !')
                except Exception as e:
                    messages.warning(request, str(e))


            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subcription = SubscriptionInformation.objects.filter(company_info=company_info)
            subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info = erp).last()
            u_list = user_list_of_a_company(int(erp_active.company_id), int(erp_active.website_id))
            contex = {
                'user_info': user_info,
                'company_info': company_info,
                'subcription': subcription,
                'erp': erp,
                'subcription_one': subcription_one,
                'erp_active': erp_active,
                'u_list': u_list,
            }
            return render(request, 'remove_user.html', contex)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')
    else:
        return redirect('login_info')




from .utils import get_users_with_roles_from_company_id, get_all_user_roles, get_user_roles, update_user_roles
def update_user_role(request, pk):
    if request.user.is_authenticated:
        try:

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subcription = SubscriptionInformation.objects.filter(company_info=company_info)
            subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info = erp).last()
            u_list = get_users_with_roles_from_company_id(int(erp_active.company_id), int(erp_active.website_id))
            contex = {
                'user_info': user_info,
                'company_info': company_info,
                'subcription': subcription,
                'erp': erp,
                'subcription_one': subcription_one,
                'erp_active': erp_active,
                'u_list': u_list,
            }
            return render(request, 'update_user_role.html', contex)
        except:
            messages.warning(request, 'Active your ERP first and then a company will create after that you can try this!')

            return redirect('home')
    else:
        return redirect('login_info')


def update_user_roles_view(request):
    if request.user.is_authenticated:
        try:
            if request.method == 'POST':
                first_page = request.POST.get('first_page')
                if first_page =="first_page":
                    user_info = request.user
                    company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                    subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                    subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                             payment_status=True).last()
                    erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
                    erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one,
                                                                       Erp_Info=erp).last()
                    u_list = get_users_with_roles_from_company_id(int(erp_active.company_id), int(erp_active.website_id))


                    user_id = request.POST.get('user_id')

                    if user_id:
                        user_id = int(user_id)
                        roles = get_all_user_roles()
                        user_roles = get_user_roles(user_id)



                        contex = {
                            'user_info': user_info,
                            'company_info': company_info,
                            'subcription': subcription,
                            'erp': erp,
                            'subcription_one': subcription_one,
                            'erp_active': erp_active,
                            'u_list': u_list,
                            'user_id': user_id,
                            'roles': roles,
                            'user_roles': user_roles
                        }

                        return render(request, 'update_user_roles.html', contex)
                    else:
                        messages.warning(request, 'user id is not present !')
                        return redirect('update_user_role', pk=1)
                else:

                    user_id = int(request.POST.get('user_id'))
                    group_ids = request.POST.getlist('group_ids')
                    group_ids = list(map(int, group_ids))

                    result = update_user_roles(user_id, group_ids)
                    if result:
                        messages.success(request, 'User roles updated successfully !')
                        return redirect('update_user_role', pk=1)
                    else:
                        messages.warning(request, 'Failed to update user roles !')
                        return redirect('update_user_role', pk=1)
        except:
            messages.warning(request, str(e))
            return redirect('home')


    else:
        return redirect('login_info')



def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

#
# def export_product_and_image(request, pk):
#     if request.user.is_authenticated:
#         if request.method == 'POST':
#             try:
#                 # Handle file uploads
#                 csv_file = request.FILES['csv_file']
#                 image_folder = request.FILES.getlist('image_folder')
#
#                 # Save files to media folder
#                 fs = FileSystemStorage()
#                 csv_file_path = fs.save(csv_file.name, csv_file)
#                 csv_file_path = fs.url(csv_file_path)
#
#                 image_folder_path = os.path.join(fs.location, 'images')
#                 if not os.path.exists(image_folder_path):
#                     os.makedirs(image_folder_path)
#
#                 for image in image_folder:
#                     fs.save(os.path.join('images', image.name), image)
#
#                 # Process CSV file
#                 csv_file_full_path = os.path.join(fs.location, csv_file.name)
#                 with open(csv_file_full_path, newline='', encoding='utf-8') as csvfile:
#                     csv_reader = csv.DictReader(csvfile)
#                     products = [row for row in csv_reader]
#
#                 # Odoo server information
#                 # url = 'http://127.0.0.1:8069'
#                 # db = 'odoo'
#                 # username = 'admin@gmail.com'
#                 # password = 'admin'
#
#                 url = settings.ODOO_URL
#                 db = settings.DB_NAME
#                 username = settings.ADMIN_USERNAME
#                 password = settings.ADMIN_PASSWORD
#
#                 # Authenticate
#                 common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
#                 uid = common.authenticate(db, username, password, {})
#
#                 # Object proxy
#                 models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
#
#                 # Get the company and website info from the authenticated user
#                 user_info = request.user
#                 company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
#                 subscription = SubscriptionInformation.objects.filter(company_info=company_info).last()
#                 erp = Erp_Information.objects.filter(subscription_info=subscription).last()
#                 erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription, Erp_Info=erp).last()
#
#                 # Get valid fields for product.template model
#                 valid_fields = models.execute_kw(db, uid, password, 'product.template', 'fields_get', [{}]).keys()
#
#                 # Create products in Odoo
#                 for product in products:
#                     category_name = product['Product Category']
#                     category_id = get_or_create_category(models, db, uid, password, category_name)
#
#                     # Check for price fields and convert to float if valid, else set to 0.0
#                     list_price = float(product['Price in Dollars']) if product['Price in Dollars'] else 0.0
#                     standard_price = float(product['Price in Local Currency']) if product[
#                         'Price in Local Currency'] else 0.0
#
#                     product_data = {
#                         'name': product['Product Name'],
#                         # 'detailed_type': 'product',  # Ensure this field is set to a valid value
#                         'list_price': list_price,
#                         'standard_price': standard_price,
#                         'categ_id': category_id,
#                         'company_id': erp_active.company_id,
#                         'description_sale': product.get('Sales Description', ''),
#                         'active': product.get('Active', 'True') == 'True',
#                         'default_code': product['SKU'],
#                     }
#                     if 'website_published' in valid_fields:
#                         product_data['website_published'] = True  # Publish product on website
#
#                     if 'website_id' in valid_fields and erp_active.website_id:
#                         product_data['website_id'] = erp_active.website_id
#
#
#                         # Additional fields
#                     additional_fields = [
#                         'UPC', 'Product Description', 'Length', 'Width', 'Height', 'Weight', 'Color',
#                         'Breakable', 'Market Name', 'Inventory Store Name', 'Product Item Name', 'Dateval',
#                         'Stock Units', 'Supplier Type', 'Supplier Id', 'Sell Category', 'Display Weight',
#                         'Display Height', 'Display Length', 'Display Width', 'E-Mall Category', 'Size',
#                         'Area Scale Unit', 'Mass Scale Unit', 'Display Size', 'Display SKU', 'Local currency code'
#                     ]
#                     for field in additional_fields:
#                         if field in product:
#                             odoo_field_name = field.lower().replace(' ', '_')
#                             if odoo_field_name in valid_fields:
#                                 product_data[odoo_field_name] = product[field]
#
#                     product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [product_data])
#
#                     # If image exists for the product, upload it
#                     image_fields = ['image1_local_path', 'image2_local_path', 'image3_local_path', 'image4_local_path',
#                                     'image5_local_path']
#                     for image_field in image_fields:
#                         image_name = product.get(image_field, '')
#                         if image_name:
#                             image_path = os.path.join(image_folder_path, image_name)
#                             if os.path.exists(image_path):
#                                 image_data = encode_image_to_base64(image_path)
#                                 models.execute_kw(db, uid, password, 'ir.attachment', 'create', [{
#                                     'name': image_name,
#                                     'res_model': 'product.template',
#                                     'res_id': product_id,
#                                     'type': 'binary',
#                                     'datas': image_data,
#                                     'store_fname': image_name,
#                                     'mimetype': 'image/jpeg',
#                                 }])
#
#                 messages.success(request, 'Products uploaded successfully.')
#                 return redirect('export_product_and_image', pk=1)
#             except Exception as e:
#                 return  HttpResponse(str(e))
#         else:
#             user_info = request.user
#             company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
#             subcription = SubscriptionInformation.objects.filter(company_info=company_info)
#             subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
#                                                                      payment_status=True).last()
#             erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
#             erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
#             u_list = get_users_with_roles_from_company_id(int(erp_active.company_id), int(erp_active.website_id))
#             contex = {
#                 'user_info': user_info,
#                 'company_info': company_info,
#                 'subcription': subcription,
#                 'erp': erp,
#                 'subcription_one': subcription_one,
#                 'erp_active': erp_active,
#                 'u_list': u_list,
#             }
#
#             return render(request, 'upload_products.html', contex)
#     else:
#         return redirect('login_info')
#

def get_bucket_name_for_product(company_id, type):
    return f'{type}/company_{company_id}/'

def encode_image_to_base64_for_product(image_data):
    return base64.b64encode(image_data).decode('utf-8')


import xmlrpc.client
from django.core.files.storage import FileSystemStorage

import logging

# Set up logging
logger = logging.getLogger(__name__)

def export_product_and_image(request, pk):
    if request.user.is_authenticated:
        try:
            if request.method == 'POST':
                erp_active_id = request.POST.get('erp_active_id')
                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)

                # Handle file uploads
                csv_file = request.FILES['csv_file']
                image_folder = request.FILES.getlist('image_folder')

                # Save CSV file locally first
                fs = FileSystemStorage()
                csv_filename = fs.save(csv_file.name, csv_file)
                csv_local_file_path = fs.path(csv_filename)

                # Save image files locally first
                image_folder_path = os.path.join('/tmp', 'images')
                if not os.path.exists(image_folder_path):
                    os.makedirs(image_folder_path)

                image_file_paths = []
                for image in image_folder:
                    image_path = os.path.join(image_folder_path, image.name)
                    with open(image_path, 'wb+') as temp_image:
                        for chunk in image.chunks():
                            temp_image.write(chunk)
                    image_file_paths.append(image_path)

                # AWS S3 credentials from settings
                AWS_ACCESS_KEY_ID = settings.S3_ACCESS_KEY_ID
                AWS_SECRET_ACCESS_KEY = settings.S3_SECRET_ACCESS_KEY
                AWS_REGION = settings.AWS_REGION

                BUCKET_NAME = 'companyid' + str(company_id)
                type = "product"
                S3_FILE_KEY = get_bucket_name_for_product(company_id, type) + csv_file.name

                # Initialize S3 client
                s3 = boto3.client('s3',
                                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                  region_name=AWS_REGION)

                try:
                    # Check if the bucket exists, create it if it doesn't
                    buckets = s3.list_buckets()
                    bucket_exists = any(bucket['Name'] == BUCKET_NAME for bucket in buckets['Buckets'])

                    if not bucket_exists:
                        s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': AWS_REGION})

                    # Upload CSV file to S3
                    s3.upload_file(csv_local_file_path, BUCKET_NAME, S3_FILE_KEY)

                    # Upload image files to S3
                    for image_path in image_file_paths:
                        image_name = os.path.basename(image_path)
                        S3_FILE_KEY_IMAGE = get_bucket_name_for_product(company_id, type) + os.path.join('images', image_name)
                        s3.upload_file(image_path, BUCKET_NAME, S3_FILE_KEY_IMAGE)

                    # Optionally, delete the local files after processing
                    os.remove(csv_local_file_path)
                    for image_path in image_file_paths:
                        os.remove(image_path)

                    messages.success(request, 'Files uploaded successfully.')
                except Exception as e:
                    messages.error(request, str(e))
                    # return redirect('export_product_and_image', pk=pk)

                # Process CSV file from S3
                csv_s3_key = S3_FILE_KEY
                csv_obj = s3.get_object(Bucket=BUCKET_NAME, Key=csv_s3_key)
                csv_content = csv_obj['Body'].read().decode('utf-8').splitlines()
                csv_reader = csv.DictReader(csv_content)
                products = [row for row in csv_reader]

                # Odoo server information
                url = settings.ODOO_URL
                db = settings.DB_NAME
                username = settings.ADMIN_USERNAME
                password = settings.ADMIN_PASSWORD

                # Authenticate
                common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
                uid = common.authenticate(db, username, password, {})

                # Object proxy
                models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

                # Get the company and website info from the authenticated user
                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subscription = SubscriptionInformation.objects.filter(company_info=company_info).last()
                erp = Erp_Information.objects.filter(subscription_info=subscription).last()
                erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription, Erp_Info=erp).last()

                # Get valid fields for product.template model
                valid_fields = models.execute_kw(db, uid, password, 'product.template', 'fields_get', [{}]).keys()

                total_product = 0
                upload_total = 0
                try:
                    # Create products in Odoo
                    for product in products:
                        total_product = total_product+1
                        category_name = product['Product Category']
                        category_id = get_or_create_category(models, db, uid, password, category_name)

                        # Check for price fields and convert to float if valid, else set to 0.0
                        list_price = float(product['Price in Dollars']) if product['Price in Dollars'] else 0.0
                        standard_price = float(product['Price in Local Currency']) if product['Price in Local Currency'] else 0.0

                        product_data = {
                            'name': product['Product Name'],
                            'list_price': list_price,
                            'standard_price': standard_price,
                            'categ_id': category_id,
                            'company_id': erp_active.company_id,
                            'description_sale': product.get('Sales Description', ''),
                            'active': product.get('Active', 'True') == 'True',
                            'default_code': product['SKU'],
                        }
                        if 'website_published' in valid_fields:
                            product_data['website_published'] = True  # Publish product on website

                        if 'website_id' in valid_fields and erp_active.website_id:
                            product_data['website_id'] = erp_active.website_id

                        # Additional fields
                        additional_fields = [
                            'UPC', 'Product Description', 'Length', 'Width', 'Height', 'Weight', 'Color',
                            'Breakable', 'Market Name', 'Inventory Store Name', 'Product Item Name', 'Dateval',
                            'Stock Units', 'Supplier Type', 'Supplier Id', 'Sell Category', 'Display Weight',
                            'Display Height', 'Display Length', 'Display Width', 'E-Mall Category', 'Size',
                            'Area Scale Unit', 'Mass Scale Unit', 'Display Size', 'Display SKU', 'Local currency code'
                        ]
                        try:
                            for field in additional_fields:
                                if field in product:
                                    odoo_field_name = field.lower().replace(' ', '_')
                                    if odoo_field_name in valid_fields:
                                        product_data[odoo_field_name] = product[field]
                        except:
                            pass

                        # product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [product_data])
                        try:
                            product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [product_data])
                        except xmlrpc.client.Fault as fault:
                            logger.error("Error creating product in Odoo: %s", str(fault))
                            messages.error(request, f"Error creating product {product['Product Name']}: {fault}")
                            continue
                        # If image exists for the product, upload it
                        image_fields = ['image1_local_path', 'image2_local_path', 'image3_local_path', 'image4_local_path', 'image5_local_path']
                        for image_field in image_fields:
                            image_name = product.get(image_field, '')
                            if image_name:
                                image_s3_key = get_bucket_name_for_product(company_id, type) + os.path.join('images', image_name)
                                image_obj = s3.get_object(Bucket=BUCKET_NAME, Key=image_s3_key)

                                image_data = image_obj['Body'].read()
                                image_base64 = encode_image_to_base64_for_product(image_data)

                                models.execute_kw(db, uid, password, 'ir.attachment', 'create', [{
                                    'name': image_name,
                                    'res_model': 'product.template',
                                    'res_id': product_id,
                                    'type': 'binary',
                                    'datas': image_base64,
                                    'store_fname': image_name,
                                    'mimetype': 'image/jpeg',
                                }])
                        upload_total = upload_total+1

                    messages.success(request, 'Products uploaded successfully.')
                    # return redirect('export_product_and_image', pk=pk)
                except Exception as e:
                    messages.success(request, f'in place of {total_product} product upload {upload_total}')

            else:
                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subscription = SubscriptionInformation.objects.filter(company_info=company_info)
                subscription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
                erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
                erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()
                u_list = get_users_with_roles_from_company_id(int(erp_active.company_id), int(erp_active.website_id))
                context = {
                    'user_info': user_info,
                    'company_info': company_info,
                    'subscription': subscription,
                    'erp': erp,
                    'subscription_one': subscription_one,
                    'erp_active': erp_active,
                    'u_list': u_list,
                }

                return render(request, 'upload_products.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')
    else:
        return redirect('login_info')




def dashboard(request, pk):
    if request.user.is_authenticated:
        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)
        subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
        erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
        erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
        contex = {
            'subcription_one': subcription_one,
            'erp': erp,
            'erp_active': erp_active,
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,

        }


        return render(request, 'dashboard.html', contex)
    else:
        return redirect('login_info')



def new_subscription_plan(request, pk):
    if request.user.is_authenticated:
        try:
            if request.method == 'POST':


                campaignscaled = request.POST.get('campaignscaled')
                plane_price = request.POST.get('plane_price')
                file_number = request.POST.get('file_number')
                client_source = request.POST.get('client_source')
                fee_amount = request.POST.get('fee_amount')
                Partner_client_company_name = request.POST.get('Partner_client_company_name')
                partner_client_contact_full_name = request.POST.get('partner_client_contact_full_name')
                client_email_address = request.POST.get('client_email_address')
                client_phone_number = request.POST.get('client_phone_number')
                countryCode = request.POST.get('countryCode')
                partner_client_company_address = request.POST.get('partner_client_company_address')
                partner_client_company_country = request.POST.get('partner_client_company_country')
                partner_client_company_state_or_province = request.POST.get('partner_client_company_state_or_province')
                partner_client_company_city = request.POST.get('partner_client_company_city')
                partner_client_company_zip_or_postal_code = request.POST.get('partner_client_company_zip_or_postal_code')
                password = request.POST.get('password')

                myusr_vari = User.objects.create_user(client_email_address, client_email_address, password)
                myusr_vari.first_name = ''
                myusr_vari.last_name = ''
                myusr_vari.is_active = True
                myusr_vari.save()

                user = authenticate(request, username=client_email_address, password=password)
                if user is not None:
                    login(request, user)
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username

                partner_client_company_country = get_country_name(partner_client_company_country)
                partner_client_company_state_or_province = get_state_name(partner_client_company_state_or_province)

                cri = CompanyRegistrationInformation(
                    user_info=myusr_vari,
                    file_number=file_number,
                    client_source=client_source,
                    fee_amount=fee_amount,
                    Partner_client_company_name=Partner_client_company_name,
                    partner_client_contact_full_name=partner_client_contact_full_name,
                    client_email_address=client_email_address,
                    client_phone_number=client_phone_number,
                    client_phone_code=countryCode,
                    partner_client_company_address=partner_client_company_address,
                    partner_client_company_country=partner_client_company_country,
                    partner_client_company_state_or_province=partner_client_company_state_or_province,
                    partner_client_company_city=partner_client_company_city,
                    partner_client_company_zip_or_postal_code=partner_client_company_zip_or_postal_code,
                )
                cri.save()

                sp = SubscriptionPlan.objects.all()
                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                         payment_status=True).last()
                erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
                erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
                contex = {
                    'subcription_one': subcription_one,
                    'erp': erp,
                    'erp_active': erp_active,
                    'user_info': user_info,
                    'company_info': company_info,
                    'subcription': subcription,
                    'CompanyRegistrationInformationId': cri.id,
                    'sp': sp,
                    'campaignscaled': campaignscaled,
                    'plane_price': plane_price,
                }
                return render(request, 'new_subscriptions.html', contex)

            sp = SubscriptionPlan.objects.all()
            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subcription = SubscriptionInformation.objects.filter(company_info=company_info)
            subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()
            contex = {
                'subcription_one': subcription_one,
                'erp': erp,
                'erp_active': erp_active,

                'user_info': user_info,
                'company_info': company_info,
                'subcription': subcription,

                'sp': sp,

            }

            return render(request, 'new_subscription_plan.html', contex)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')
    else:
        return redirect('login_info')




def new_subscriptions(request, pk):
    if request.user.is_authenticated:
        # if request.method == 'POST':
        try:
            campaignscaled = request.POST.get('campaignscaled')
            plane_price = request.POST.get('plane_price') or 1

            from_back = request.POST.get('from_back')
            demandscaled = request.POST.get('demandscaled')
            acquirescaled = request.POST.get('acquirescaled')
            Product_recommendations = request.POST.get('Product_recommendations')
            CompanyRegistrationInformationId = request.POST.get('CompanyRegistrationInformationId')
            own = request.POST.get('own')

            if from_back == "coming_back":

                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                         payment_status=True).last()
                erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
                erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one,
                                                                   Erp_Info=erp).last()
                contex = {
                    'subcription_one': subcription_one,
                    'erp': erp,
                    'erp_active': erp_active,
                    'demandscaled': demandscaled,
                    'acquirescaled': acquirescaled,
                    'Product_recommendations': Product_recommendations,
                    'CompanyRegistrationInformationId': CompanyRegistrationInformationId,
                    'user_info': user_info,
                    'company_info': company_info,
                    'subcription': subcription,
                    'campaignscaled': campaignscaled,
                    'plane_price': plane_price,
                }

                return render(request, 'new_subscriptions.html', contex)
            elif own == "own":


                try:
                    package_price_demandscaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(
                        app="demandscaled").last()
                    package_price_acquirescaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(
                        app="acquirescaled").last()
                    package_price_recommendscaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(
                        app="recommendscaled").last()

                    prescriptive_ai = AdministrationkintahSubscriptionPackagePrice.objects.filter(
                        app="(prescriptive_ai").last()
                    metricscaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="metricscaled").last()
                    driven_erp = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="driven_erp").last()
                    driven_edriven_e_commerce = AdministrationkintahSubscriptionPackagePrice.objects.filter(
                        app="driven_edriven_e_commerce").last()

                    if package_price_demandscaled:
                        package_price_demandscaled_monthly_base_cost = package_price_demandscaled.monthly_base_cost
                        package_price_demandscaled_monthly_coef = package_price_demandscaled.monthly_coef
                        package_price_demandscaled_monthly_activity_free = package_price_demandscaled.monthly_activity_free

                        package_price_demandscaled_base_price = package_price_demandscaled.base_price
                        package_price_demandscaled_base_number_of_subscription_months = package_price_demandscaled.base_number_of_subscription_months
                        package_price_demandscaled_base_number_of_users = package_price_demandscaled.base_number_of_users
                        package_price_demandscaled_base_number_data_reloads = package_price_demandscaled.base_number_data_reloads
                        package_price_demandscaled_saturation_coef = package_price_demandscaled.saturation_coef

                    else:
                        package_price_demandscaled_monthly_base_cost = 495
                        package_price_demandscaled_monthly_coef = 0.025
                        package_price_demandscaled_monthly_activity_free = 12

                        package_price_demandscaled_base_price = 2
                        package_price_demandscaled_base_number_of_subscription_months = 4.9
                        package_price_demandscaled_base_number_of_users = 6
                        package_price_demandscaled_base_number_data_reloads = 6
                        package_price_demandscaled_saturation_coef = 8


                    if package_price_acquirescaled:
                        package_price_acquirescaled_monthly_base_cost = package_price_acquirescaled.monthly_base_cost
                        package_price_acquirescaled_monthly_coef = package_price_acquirescaled.monthly_coef
                        package_price_acquirescaled_monthly_activity_free = package_price_acquirescaled.monthly_activity_free

                        package_price_acquirescaled_base_price = package_price_acquirescaled.base_price
                        package_price_acquirescaled_base_number_of_subscription_months = package_price_acquirescaled.base_number_of_subscription_months
                        package_price_acquirescaled_base_number_of_users = package_price_acquirescaled.base_number_of_users
                        package_price_acquirescaled_base_number_data_reloads = package_price_acquirescaled.base_number_data_reloads
                        package_price_acquirescaled_saturation_coef = package_price_acquirescaled.saturation_coef

                    else:
                        package_price_acquirescaled_monthly_base_cost = 495
                        package_price_acquirescaled_monthly_coef = 0.025
                        package_price_acquirescaled_monthly_activity_free = 12

                        package_price_acquirescaled_base_price = 22
                        package_price_acquirescaled_base_number_of_subscription_months = 2.9
                        package_price_acquirescaled_base_number_of_users = 3
                        package_price_acquirescaled_base_number_data_reloads = 2.7
                        package_price_acquirescaled_saturation_coef = 2.3


                    if package_price_recommendscaled:
                        package_price_recommendscaled_monthly_base_cost = package_price_recommendscaled.monthly_base_cost
                        package_price_recommendscaled_monthly_coef = package_price_recommendscaled.monthly_coef
                        package_price_recommendscaled_monthly_activity_free = package_price_recommendscaled.monthly_activity_free

                        package_price_recommendscaled_base_price = package_price_recommendscaled.base_price
                        package_price_recommendscaled_base_number_of_subscription_months = package_price_recommendscaled.base_number_of_subscription_months
                        package_price_recommendscaled_base_number_of_users = package_price_recommendscaled.base_number_of_users
                        package_price_recommendscaled_base_number_data_reloads = package_price_recommendscaled.base_number_data_reloads
                        package_price_recommendscaled_saturation_coef = package_price_recommendscaled.saturation_coef

                    else:
                        package_price_recommendscaled_monthly_base_cost = 495.99
                        package_price_recommendscaled_monthly_coef = 0.025
                        package_price_recommendscaled_monthly_activity_free = 12

                        package_price_recommendscaled_base_price = 2
                        package_price_recommendscaled_base_number_of_subscription_months = 2.9
                        package_price_recommendscaled_base_number_of_users = 2
                        package_price_recommendscaled_base_number_data_reloads = 2
                        package_price_recommendscaled_saturation_coef = 5.9


                    if prescriptive_ai:
                        prescriptive_ai_monthly_base_cost = prescriptive_ai.monthly_base_cost
                        prescriptive_ai_monthly_coef = prescriptive_ai.monthly_coef
                        prescriptive_ai_monthly_activity_free = prescriptive_ai.monthly_activity_free

                        prescriptive_ai_monthly_base_price = prescriptive_ai.base_price
                        prescriptive_ai_monthly_base_number_of_subscription_months = prescriptive_ai.base_number_of_subscription_months
                        prescriptive_ai_monthly_base_number_of_users = prescriptive_ai.base_number_of_users
                        prescriptive_ai_monthly_base_number_data_reloads = prescriptive_ai.base_number_data_reloads
                        prescriptive_ai_monthly_saturation_coef = prescriptive_ai.saturation_coef

                    else:
                        prescriptive_ai_monthly_base_cost = 995
                        prescriptive_ai_monthly_coef = 0.025
                        prescriptive_ai_monthly_activity_free = 12

                        prescriptive_ai_monthly_base_price = 11
                        prescriptive_ai_monthly_base_number_of_subscription_months = 1.1
                        prescriptive_ai_monthly_base_number_of_users = 11
                        prescriptive_ai_monthly_base_number_data_reloads = 12
                        prescriptive_ai_monthly_saturation_coef = 3

                    if metricscaled:
                        metricscaled_monthly_base_cost = metricscaled.monthly_base_cost
                        metricscaled_monthly_coef = metricscaled.monthly_coef
                        metricscaled_monthly_activity_free = metricscaled.monthly_activity_free

                        metricscaled_monthly_base_price = metricscaled.base_price
                        metricscaled_monthly_base_number_of_subscription_months = metricscaled.base_number_of_subscription_months
                        metricscaled_monthly_base_number_of_users = metricscaled.base_number_of_users
                        metricscaled_monthly_base_number_data_reloads = metricscaled.base_number_data_reloads
                        metricscaled_monthly_saturation_coef = metricscaled.saturation_coef

                    else:
                        metricscaled_monthly_base_cost = 995
                        metricscaled_monthly_coef = 0.025
                        metricscaled_monthly_activity_free = 12

                        metricscaled_monthly_base_price = 3
                        metricscaled_monthly_base_number_of_subscription_months = 22
                        metricscaled_monthly_base_number_of_users = 43
                        metricscaled_monthly_base_number_data_reloads = 45
                        metricscaled_monthly_saturation_coef = 34

                    if driven_erp:
                        driven_erp_monthly_base_cost = driven_erp.monthly_base_cost
                        driven_erp_monthly_coef = driven_erp.monthly_coef
                        driven_erp_monthly_activity_free = driven_erp.monthly_activity_free

                        driven_erp_monthly_base_price = driven_erp.base_price
                        driven_erp_monthly_base_number_of_subscription_months = driven_erp.base_number_of_subscription_months
                        driven_erp_monthly_base_number_of_users = driven_erp.base_number_of_users
                        driven_erp_monthly_base_number_data_reloads = driven_erp.base_number_data_reloads
                        driven_erp_monthly_saturation_coef = driven_erp.saturation_coef

                    else:
                        driven_erp_monthly_base_cost = 995
                        driven_erp_monthly_coef = 0.025
                        driven_erp_monthly_activity_free = 12

                        driven_erp_monthly_base_price = 33
                        driven_erp_monthly_base_number_of_subscription_months = 2
                        driven_erp_monthly_base_number_of_users = 9
                        driven_erp_monthly_base_number_data_reloads = 89
                        driven_erp_monthly_saturation_coef = 8


                    if driven_edriven_e_commerce:
                        driven_edriven_e_commerce_monthly_base_cost = driven_edriven_e_commerce.monthly_base_cost
                        driven_edriven_e_commerce_monthly_coef = driven_edriven_e_commerce.monthly_coef
                        driven_edriven_e_commerce_monthly_coef = driven_edriven_e_commerce.monthly_activity_free

                        driven_edriven_e_commerce_monthly_base_price = driven_edriven_e_commerce.base_price
                        driven_edriven_e_commerce_monthly_base_number_of_subscription_months = driven_edriven_e_commerce.base_number_of_subscription_months
                        driven_edriven_e_commerce_monthly_base_number_of_users = driven_edriven_e_commerce.base_number_of_users
                        driven_edriven_e_commerce_monthly_base_number_data_reloads = driven_edriven_e_commerce.base_number_data_reloads
                        driven_edriven_e_commerce_monthly_saturation_coef = driven_edriven_e_commerce.saturation_coef

                    else:
                        driven_edriven_e_commerce_monthly_base_cost = 995
                        driven_edriven_e_commerce_monthly_coef = 0.025
                        driven_edriven_e_commerce_monthly_coef_monthly_activity_free = 12

                        driven_edriven_e_commerce_monthly_base_price = 6
                        driven_edriven_e_commerce_monthly_base_number_of_subscription_months = 9
                        driven_edriven_e_commerce_monthly_base_number_of_users = 5
                        driven_edriven_e_commerce_monthly_base_number_data_reloads = 56
                        driven_edriven_e_commerce_monthly_saturation_coef = 5

                    user_info = request.user
                    company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                    subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                    subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                             payment_status=True).last()
                    erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
                    erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one,
                                                                       Erp_Info=erp).last()

                    all_company_types = PriceMatrixPerCompanyType.objects.all()
                    parameters = AdditionalCostCalculationFixParameters.objects.filter().last()
                    if parameters:
                        sup_cost = parameters.sup_cost
                        Train_cost = parameters.train_cost
                    else:
                        sup_cost = 25
                        Train_cost = 500
                    contex = {
                        'all_company_types': all_company_types,
                        'sup_cost': sup_cost,
                        'Train_cost': Train_cost,


                        'subcription_one': subcription_one,
                        'erp': erp,
                        'erp_active': erp_active,

                        'demandscaled': demandscaled,
                        'demandscaled_monthly_base_cost': package_price_demandscaled_monthly_base_cost,
                        'demandscaled_monthly_coef': package_price_demandscaled_monthly_coef,
                        'demandscaled_monthly_activity_free': package_price_demandscaled_monthly_activity_free,

                        'acquirescaled': acquirescaled,
                        'acquirescaled_monthly_base_cost': package_price_acquirescaled_monthly_base_cost,
                        'acquirescaled_monthly_coef': package_price_acquirescaled_monthly_coef,
                        'acquirescaled_monthly_activity_free': package_price_acquirescaled_monthly_activity_free,

                        'Product_recommendations': Product_recommendations,
                        'Product_recommendations_monthly_base_cost': package_price_recommendscaled_monthly_base_cost,
                        'Product_recommendations_monthly_coef': package_price_recommendscaled_monthly_coef,
                        'Product_recommendations_monthly_activity_free': package_price_recommendscaled_monthly_activity_free,

                        'prescriptive_ai_monthly_base_cost': prescriptive_ai_monthly_base_cost,
                        'prescriptive_ai_monthly_coef': prescriptive_ai_monthly_coef,
                        'prescriptive_ai_monthly_activity_free': prescriptive_ai_monthly_activity_free,

                        'metricscaled_monthly_base_cost': metricscaled_monthly_base_cost,
                        'metricscaled_monthly_coef': metricscaled_monthly_coef,
                        'metricscaled_monthly_activity_free': metricscaled_monthly_activity_free,

                        'driven_erp_monthly_base_cost': driven_erp_monthly_base_cost,
                        'driven_erp_monthly_coef': driven_erp_monthly_coef,
                        'driven_erp_monthly_activity_free': driven_erp_monthly_activity_free,

                        'driven_edriven_e_commerce_monthly_base_cost': driven_edriven_e_commerce_monthly_base_cost,
                        'driven_edriven_e_commerce_monthly_coef': driven_edriven_e_commerce_monthly_coef,
                        'driven_edriven_e_commerce_monthly_coef_monthly_activity_free': driven_edriven_e_commerce_monthly_coef_monthly_activity_free,

                        'CompanyRegistrationInformationId': company_info.id,
                        'user_info': user_info,
                        'company_info': company_info,
                        'subcription': subcription,

                        'package_price_demandscaled_base_price': package_price_demandscaled_base_price,
                        'package_price_demandscaled_base_number_of_subscription_months': package_price_demandscaled_base_number_of_subscription_months,
                        'package_price_demandscaled_base_number_of_users': package_price_demandscaled_base_number_of_users,
                        'package_price_demandscaled_base_number_data_reloads': package_price_demandscaled_base_number_data_reloads,
                        'package_price_demandscaled_saturation_coef': package_price_demandscaled_saturation_coef,
                        'package_price_acquirescaled_base_price': package_price_acquirescaled_base_price,
                        'package_price_acquirescaled_base_number_of_subscription_months': package_price_acquirescaled_base_number_of_subscription_months,
                        'package_price_acquirescaled_base_number_of_users': package_price_acquirescaled_base_number_of_users,
                        'package_price_acquirescaled_base_number_data_reloads': package_price_acquirescaled_base_number_data_reloads,
                        'package_price_acquirescaled_saturation_coef': package_price_acquirescaled_saturation_coef,
                        'package_price_recommendscaled_base_price': package_price_recommendscaled_base_price,
                        'package_price_recommendscaled_base_number_of_subscription_months': package_price_recommendscaled_base_number_of_subscription_months,
                        'package_price_recommendscaled_base_number_of_users': package_price_recommendscaled_base_number_of_users,
                        'package_price_recommendscaled_base_number_data_reloads': package_price_recommendscaled_base_number_data_reloads,
                        'package_price_recommendscaled_saturation_coef': package_price_recommendscaled_saturation_coef,
                        'prescriptive_ai_monthly_base_price': prescriptive_ai_monthly_base_price,
                        'prescriptive_ai_monthly_base_number_of_subscription_months': prescriptive_ai_monthly_base_number_of_subscription_months,
                        'prescriptive_ai_monthly_base_number_of_users': prescriptive_ai_monthly_base_number_of_users,
                        'prescriptive_ai_monthly_base_number_data_reloads': prescriptive_ai_monthly_base_number_data_reloads,
                        'prescriptive_ai_monthly_saturation_coef': prescriptive_ai_monthly_saturation_coef,
                        'metricscaled_monthly_base_price': metricscaled_monthly_base_price,
                        'metricscaled_monthly_base_number_of_subscription_months': metricscaled_monthly_base_number_of_subscription_months,
                        'metricscaled_monthly_base_number_of_users': metricscaled_monthly_base_number_of_users,
                        'metricscaled_monthly_base_number_data_reloads': metricscaled_monthly_base_number_data_reloads,
                        'metricscaled_monthly_saturation_coef': metricscaled_monthly_saturation_coef,
                        'driven_erp_monthly_base_price': driven_erp_monthly_base_price,
                        'driven_erp_monthly_base_number_of_subscription_months': driven_erp_monthly_base_number_of_subscription_months,
                        'driven_erp_monthly_base_number_of_users': driven_erp_monthly_base_number_of_users,
                        'driven_erp_monthly_base_number_data_reloads': driven_erp_monthly_base_number_data_reloads,
                        'driven_erp_monthly_saturation_coef': driven_erp_monthly_saturation_coef,
                        'driven_edriven_e_commerce_monthly_base_price': driven_edriven_e_commerce_monthly_base_price,
                        'driven_edriven_e_commerce_monthly_base_number_of_subscription_months': driven_edriven_e_commerce_monthly_base_number_of_subscription_months,
                        'driven_edriven_e_commerce_monthly_base_number_of_users': driven_edriven_e_commerce_monthly_base_number_of_users,
                        'driven_edriven_e_commerce_monthly_base_number_data_reloads': driven_edriven_e_commerce_monthly_base_number_data_reloads,
                        'driven_edriven_e_commerce_monthly_saturation_coef': driven_edriven_e_commerce_monthly_saturation_coef,

                        'campaignscaled': campaignscaled,
                        'plane_price': plane_price,

                    }
                    return render(request, "calculate_amount_to_pay_inside_home.html", contex)
                except Exception as e:
                    d = str(e)



                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                         payment_status=True).last()
                erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
                erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one,
                                                                   Erp_Info=erp).last()
                contex = {
                    'subcription_one': subcription_one,
                    'erp': erp,
                    'erp_active': erp_active,
                    'demandscaled': demandscaled,
                    'acquirescaled': acquirescaled,
                    'Product_recommendations': Product_recommendations,
                    'CompanyRegistrationInformationId': company_info.id,
                    'user_info': user_info,
                    'company_info': company_info,
                    'subcription': subcription,
                    'campaignscaled': campaignscaled,
                    'plane_price': plane_price,
                }

                return render(request, 'calculate_amount_to_pay_inside_home.html', contex)
            else:
                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                         payment_status=True).last()
                erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
                erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one,
                                                                   Erp_Info=erp).last()
                contex = {
                    'subcription_one': subcription_one,
                    'erp': erp,
                    'erp_active': erp_active,
                    'user_info': user_info,
                    'company_info': company_info,
                    'subcription': subcription,
                    'campaignscaled': campaignscaled,
                    'plane_price': plane_price,
                }
                return render(request, 'new_subscriptions.html', contex)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')
    else:
        return redirect('login_info')


def submit_subscription_inside_home(request):
    if request.user.is_authenticated:
        CompanyRegistrationInformationId = request.POST.get('CompanyRegistrationInformationId')

        demandscaled = request.POST.get('demandscaled')
        if demandscaled == 'on':
            demandscaled = True
        else:

            demandscaled = False
        acquirescaled = request.POST.get('acquirescaled')
        if acquirescaled == 'on':
            acquirescaled = True
        else:
            acquirescaled = False
        Product_recommendations = request.POST.get('Product_recommendations')
        if Product_recommendations == 'on':
            Product_recommendations = True
        else:
            Product_recommendations = False

        plane_price = request.POST.get('plane_price')
        campaignscaled = request.POST.get('campaignscaled')
        if campaignscaled == 'on':
            campaignscaled = True
        else:
            campaignscaled = False

        all_amount_sum = request.POST.get('all_amount_sum')
        installment_amount = request.POST.get('installment_amount')
        now_pay = request.POST.get('installmentsCount')

        month_to_access = request.POST.get('month_to_access')
        number_of_times = request.POST.get('number_of_times')
        expected_users = request.POST.get('expected_users')

        training_hours = request.POST.get('training_hours')
        support_hours = request.POST.get('support_hours')

        payment_type_get = request.POST.get('payment_type_get')
        total_amount = request.POST.get('total_amount')
        installment_amount = request.POST.get('installment_amount')
        print('total_amount')
        print(installment_amount)
        print('total_amount')
        installmentsCount = request.POST.get('installmentsCount')
        if payment_type_get == "installments":
            total = float(installmentsCount)
        else:
            total = float(installmentsCount)



        com_id = CompanyRegistrationInformation.objects.get(id=CompanyRegistrationInformationId)

        sub = SubscriptionInformation(
            company_info=com_id,
            demandscaled=demandscaled,
            acquirescaled=acquirescaled,
            product_recommendations=Product_recommendations,
            campaignscaled=campaignscaled,
            services_plan_cost=plane_price,

            number_of_month_to_access=month_to_access,
            number_of_times_ERP=number_of_times,
            number_of_expected_users_of_the_platform=expected_users,
            number_of_training_per_month=training_hours,
            number_of_support_hours_per_month=support_hours,
            platform_total_payment=total_amount,
            paid_payment=total,
            services_plan_cost_and_platform_total_payment=all_amount_sum,
        )
        sub.save()

        user_info = request.user
        company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
        subcription = SubscriptionInformation.objects.filter(company_info=company_info)

        publishable_key = settings.STRIPE_PUBLIC_KEY

        print('now pay')
        print(total)
        print('services_plan_cost_and_platform_total_payment')
        print(all_amount_sum)
        print('monthly')
        print(installment_amount)
        print('installment_amount')


        context = {
            'analytics_services_info_id': sub.id,
            'publishable_key': publishable_key,
            'total_amount': total,
            'user_info': user_info,
            'company_info': company_info,
            'subcription': subcription,

            'services_plan_cost_and_platform_total_payment': all_amount_sum,
            'installment_amount': installment_amount,
            'now_pay': total,
        }
        return render(request, 'payment_home_for_home.html', context)
    else:
        return redirect('login_info')
    



def home(request):

    return redirect('home_info')

def index(request):

    # return render(request, 'registration6.html', {'phone_codes': all_phone_code})
    return render(request, 'registration6.html', {'phone_codes': all_phone_code})
    # return render(request, 'erp_info.html')

# def index(request):
#
#     return render(request, 'registration.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        list_mail = []
        get_recipient_list = list_mail.append(email)
        get_subject = "OTP form the Kintah"
        otp = generate_otp()
        print('otp')
        print(otp)
        print("otp")
        get_massage = f"your otp is {otp}"
        res = send_email_info(get_subject, get_massage, get_recipient_list)
        # if res == 'Done':
        if res:
            contex = {
                'otp':otp,
                'email':email,

            }
            return render(request, 'enter_new_password.html', contex)
        else:
            messages.success(request, "please try again later . ")
            return redirect('forgot_password')

    return render(request, 'forgot_password.html')


def set_new_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        u = User.objects.get(username=email)
        u.set_password(password)
        u.save()
        messages.success(request, "Password reset successfully.")
        return redirect('login_info')


    return render(request, 'forgot_password.html')


def login_info(request):
    if request.user.is_authenticated:
        return redirect('home_info')
    if request.method == 'POST':
        get_email = request.POST['email']
        get_password = request.POST['password']


        user = authenticate(request, username=get_email, password=get_password)
        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id
            request.session['username'] = user.username

            if request.POST.get('remember-me'):
                messages.success(request, "You have been successfully logged in.")
                response =  redirect('home_info')
                response.set_cookie('set_email', get_email)
                response.set_cookie('set_password', get_password)
                return response
            else:
                messages.success(request, "You have been successfully logged in.")
                return redirect('home_info')
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
            return redirect('login_info')
    if request.COOKIES.get('set_email'):
        contex = {
            'set_email':request.COOKIES['set_email'],
            'set_password':request.COOKIES['set_password']
        }
        return render(request, 'login.html', contex)
    return render(request, 'login.html')




def user_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login_info')


def subscription_plan(request):

    if request.method == 'POST':
        try:
            file_number = request.POST.get('file_number')
            client_source = request.POST.get('client_source')
            fee_amount = request.POST.get('fee_amount')
            Partner_client_company_name = request.POST.get('Partner_client_company_name')
            partner_client_contact_full_name = request.POST.get('partner_client_contact_full_name')
            client_email_address = request.POST.get('client_email_address')
            client_phone_number = request.POST.get('client_phone_number')
            countryCode = request.POST.get('countryCode')
            partner_client_company_address = request.POST.get('partner_client_company_address')
            partner_client_company_country = request.POST.get('partner_client_company_country')

            partner_client_company_state_or_province = request.POST.get('partner_client_company_state_or_province')
            partner_client_company_city = request.POST.get('partner_client_company_city')
            partner_client_company_zip_or_postal_code = request.POST.get('partner_client_company_zip_or_postal_code')
            password = request.POST.get('password')

            myusr_vari = User.objects.create_user(client_email_address, client_email_address, password)
            myusr_vari.first_name = ''
            myusr_vari.last_name = ''
            myusr_vari.is_active = True
            myusr_vari.save()

            user = authenticate(request, username=client_email_address, password=password)
            if user is not None:
                login(request, user)
                request.session['user_id'] = user.id
                request.session['username'] = user.username

            partner_client_company_country = get_country_name(partner_client_company_country)
            partner_client_company_state_or_province = get_state_name(partner_client_company_state_or_province)

            cri = CompanyRegistrationInformation(
                user_info=myusr_vari,
                file_number=file_number,
                client_source=client_source,
                fee_amount=fee_amount,
                Partner_client_company_name=Partner_client_company_name,
                partner_client_contact_full_name=partner_client_contact_full_name,
                client_email_address=client_email_address,
                client_phone_number=client_phone_number,
                client_phone_code=countryCode,
                partner_client_company_address=partner_client_company_address,
                partner_client_company_country=partner_client_company_country,
                partner_client_company_state_or_province=partner_client_company_state_or_province,
                partner_client_company_city=partner_client_company_city,
                partner_client_company_zip_or_postal_code=partner_client_company_zip_or_postal_code,
            )
            cri.save()

            sp = SubscriptionPlan.objects.all()

            contex = {
                'CompanyRegistrationInformationId': cri.id,
                'sp': sp
            }

            return render(request, 'subscription_plan.html', contex)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('index')
    else:
        return render(request, 'not_allowed.html')






def user_registration(request):
    if request.method == 'POST':
        from_back = request.POST.get('from_back')
        plane_price = request.POST.get('plane_price') or 0

        if from_back =="coming_back":
            CompanyRegistrationInformationId = request.POST.get('CompanyRegistrationInformationId')
            demandscaled = request.POST.get('demandscaled')
            acquirescaled = request.POST.get('acquirescaled')
            Product_recommendations = request.POST.get('Product_recommendations')
            campaignscaled = request.POST.get('campaignscaled')
            contex = {
                'demandscaled': demandscaled,
                'acquirescaled': acquirescaled,
                'Product_recommendations': Product_recommendations,
                'campaignscaled': campaignscaled,
                'CompanyRegistrationInformationId': CompanyRegistrationInformationId,
                'plane_price': plane_price,
            }
            return render(request, 'authorize_the_following_connected_services.html', contex)

        else:
            try:
                file_number = request.POST.get('file_number')
                client_source = request.POST.get('client_source')
                fee_amount = request.POST.get('fee_amount')
                Partner_client_company_name = request.POST.get('Partner_client_company_name')
                partner_client_contact_full_name = request.POST.get('partner_client_contact_full_name')
                client_email_address = request.POST.get('client_email_address')
                client_phone_number = request.POST.get('client_phone_number')
                countryCode = request.POST.get('countryCode')
                partner_client_company_address = request.POST.get('partner_client_company_address')
                partner_client_company_country = request.POST.get('partner_client_company_country')

                partner_client_company_state_or_province = request.POST.get('partner_client_company_state_or_province')
                partner_client_company_city = request.POST.get('partner_client_company_city')
                partner_client_company_zip_or_postal_code = request.POST.get('partner_client_company_zip_or_postal_code')
                password = request.POST.get('password')

                myusr_vari = User.objects.create_user(client_email_address, client_email_address, password)
                myusr_vari.first_name = ''
                myusr_vari.last_name = ''
                myusr_vari.is_active = True
                myusr_vari.save()

                user = authenticate(request, username=client_email_address, password=password)
                if user is not None:
                    login(request, user)
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username

                partner_client_company_country = get_country_name(partner_client_company_country)
                partner_client_company_state_or_province = get_state_name(partner_client_company_state_or_province)

                cri = CompanyRegistrationInformation(
                    user_info=myusr_vari,
                    file_number=file_number,
                    client_source=client_source,
                    fee_amount=fee_amount,
                    Partner_client_company_name=Partner_client_company_name,
                    partner_client_contact_full_name=partner_client_contact_full_name,
                    client_email_address=client_email_address,
                    client_phone_number=client_phone_number,
                    client_phone_code=countryCode,
                    partner_client_company_address=partner_client_company_address,
                    partner_client_company_country=partner_client_company_country,
                    partner_client_company_state_or_province=partner_client_company_state_or_province,
                    partner_client_company_city=partner_client_company_city,
                    partner_client_company_zip_or_postal_code=partner_client_company_zip_or_postal_code,
                )
                cri.save()

                contex = {
                    'CompanyRegistrationInformationId': cri.id,
                    'plane_price': plane_price
                }

                return render(request, 'authorize_the_following_connected_services.html', contex)

            except Exception as e:
                messages.warning(request, str(e))
                return redirect('index')

        return render(request, 'authorize_the_following_connected_services.html')
    else:
        return render(request, 'not_allowed.html')


def calculate_amount_to_pay(request):
    if request.method == 'POST':
        demandscaled = request.POST.get('demandscaled')
        acquirescaled = request.POST.get('acquirescaled')
        Product_recommendations = request.POST.get('Product_recommendations')
        campaignscaled = request.POST.get('campaignscaled')
        plane_price = request.POST.get('plane_price')

        CompanyRegistrationInformationId = request.POST.get('CompanyRegistrationInformationId')
        try:
            all_company_types = PriceMatrixPerCompanyType.objects.all()

            package_price_demandscaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="demandscaled").last()
            package_price_acquirescaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="acquirescaled").last()
            package_price_recommendscaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="recommendscaled").last()

            prescriptive_ai = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="(prescriptive_ai").last()
            metricscaled = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="metricscaled").last()
            driven_erp = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="driven_erp").last()
            driven_edriven_e_commerce = AdministrationkintahSubscriptionPackagePrice.objects.filter(app="driven_edriven_e_commerce").last()


            if package_price_demandscaled:
                package_price_demandscaled_monthly_base_cost=package_price_demandscaled.monthly_base_cost
                package_price_demandscaled_monthly_coef = package_price_demandscaled.monthly_coef
                package_price_demandscaled_monthly_activity_free = package_price_demandscaled.monthly_activity_free

                package_price_demandscaled_base_price = package_price_demandscaled.base_price
                package_price_demandscaled_base_number_of_subscription_months = package_price_demandscaled.base_number_of_subscription_months
                package_price_demandscaled_base_number_of_users = package_price_demandscaled.base_number_of_users
                package_price_demandscaled_base_number_data_reloads = package_price_demandscaled.base_number_data_reloads
                package_price_demandscaled_saturation_coef = package_price_demandscaled.saturation_coef

            else:
                package_price_demandscaled_monthly_base_cost = 495
                package_price_demandscaled_monthly_coef = 0.025
                package_price_demandscaled_monthly_activity_free = 12

                package_price_demandscaled_base_price = 2
                package_price_demandscaled_base_number_of_subscription_months = 4.9
                package_price_demandscaled_base_number_of_users = 6
                package_price_demandscaled_base_number_data_reloads = 6
                package_price_demandscaled_saturation_coef = 8


            if package_price_acquirescaled:
                package_price_acquirescaled_monthly_base_cost = package_price_acquirescaled.monthly_base_cost
                package_price_acquirescaled_monthly_coef = package_price_acquirescaled.monthly_coef
                package_price_acquirescaled_monthly_activity_free = package_price_acquirescaled.monthly_activity_free

                package_price_acquirescaled_base_price = package_price_acquirescaled.base_price
                package_price_acquirescaled_base_number_of_subscription_months = package_price_acquirescaled.base_number_of_subscription_months
                package_price_acquirescaled_base_number_of_users = package_price_acquirescaled.base_number_of_users
                package_price_acquirescaled_base_number_data_reloads = package_price_acquirescaled.base_number_data_reloads
                package_price_acquirescaled_saturation_coef = package_price_acquirescaled.saturation_coef

            else:
                package_price_acquirescaled_monthly_base_cost = 495
                package_price_acquirescaled_monthly_coef = 0.025
                package_price_acquirescaled_monthly_activity_free = 12

                package_price_acquirescaled_base_price = 22
                package_price_acquirescaled_base_number_of_subscription_months = 2.9
                package_price_acquirescaled_base_number_of_users = 3
                package_price_acquirescaled_base_number_data_reloads = 2.7
                package_price_acquirescaled_saturation_coef = 2.3

            if package_price_recommendscaled:
                package_price_recommendscaled_monthly_base_cost = package_price_recommendscaled.monthly_base_cost
                package_price_recommendscaled_monthly_coef = package_price_recommendscaled.monthly_coef
                package_price_recommendscaled_monthly_activity_free = package_price_recommendscaled.monthly_activity_free

                package_price_recommendscaled_base_price = package_price_recommendscaled.base_price
                package_price_recommendscaled_base_number_of_subscription_months = package_price_recommendscaled.base_number_of_subscription_months
                package_price_recommendscaled_base_number_of_users = package_price_recommendscaled.base_number_of_users
                package_price_recommendscaled_base_number_data_reloads = package_price_recommendscaled.base_number_data_reloads
                package_price_recommendscaled_saturation_coef = package_price_recommendscaled.saturation_coef

            else:
                package_price_recommendscaled_monthly_base_cost = 495.99
                package_price_recommendscaled_monthly_coef = 0.025
                package_price_recommendscaled_monthly_activity_free = 12

                package_price_recommendscaled_base_price = 2
                package_price_recommendscaled_base_number_of_subscription_months = 2.9
                package_price_recommendscaled_base_number_of_users = 2
                package_price_recommendscaled_base_number_data_reloads = 2
                package_price_recommendscaled_saturation_coef = 5.9


            if prescriptive_ai:
                prescriptive_ai_monthly_base_cost=prescriptive_ai.monthly_base_cost
                prescriptive_ai_monthly_coef = prescriptive_ai.monthly_coef
                prescriptive_ai_monthly_activity_free = prescriptive_ai.monthly_activity_free

                prescriptive_ai_monthly_base_price = prescriptive_ai.base_price
                prescriptive_ai_monthly_base_number_of_subscription_months = prescriptive_ai.base_number_of_subscription_months
                prescriptive_ai_monthly_base_number_of_users = prescriptive_ai.base_number_of_users
                prescriptive_ai_monthly_base_number_data_reloads = prescriptive_ai.base_number_data_reloads
                prescriptive_ai_monthly_saturation_coef = prescriptive_ai.saturation_coef

            else:
                prescriptive_ai_monthly_base_cost = 995
                prescriptive_ai_monthly_coef = 0.025
                prescriptive_ai_monthly_activity_free = 12

                prescriptive_ai_monthly_base_price = 11
                prescriptive_ai_monthly_base_number_of_subscription_months = 1.1
                prescriptive_ai_monthly_base_number_of_users = 11
                prescriptive_ai_monthly_base_number_data_reloads = 12
                prescriptive_ai_monthly_saturation_coef = 3

            if metricscaled:
                metricscaled_monthly_base_cost=metricscaled.monthly_base_cost
                metricscaled_monthly_coef = metricscaled.monthly_coef
                metricscaled_monthly_activity_free = metricscaled.monthly_activity_free

                metricscaled_monthly_base_price = metricscaled.base_price
                metricscaled_monthly_base_number_of_subscription_months = metricscaled.base_number_of_subscription_months
                metricscaled_monthly_base_number_of_users = metricscaled.base_number_of_users
                metricscaled_monthly_base_number_data_reloads = metricscaled.base_number_data_reloads
                metricscaled_monthly_saturation_coef = metricscaled.saturation_coef

            else:
                metricscaled_monthly_base_cost = 995
                metricscaled_monthly_coef = 0.025
                metricscaled_monthly_activity_free = 12

                metricscaled_monthly_base_price = 3
                metricscaled_monthly_base_number_of_subscription_months = 22
                metricscaled_monthly_base_number_of_users = 43
                metricscaled_monthly_base_number_data_reloads = 45
                metricscaled_monthly_saturation_coef = 34

            if driven_erp:
                driven_erp_monthly_base_cost=driven_erp.monthly_base_cost
                driven_erp_monthly_coef = driven_erp.monthly_coef
                driven_erp_monthly_activity_free = driven_erp.monthly_activity_free

                driven_erp_monthly_base_price = driven_erp.base_price
                driven_erp_monthly_base_number_of_subscription_months = driven_erp.base_number_of_subscription_months
                driven_erp_monthly_base_number_of_users = driven_erp.base_number_of_users
                driven_erp_monthly_base_number_data_reloads = driven_erp.base_number_data_reloads
                driven_erp_monthly_saturation_coef = driven_erp.saturation_coef

            else:
                driven_erp_monthly_base_cost = 995
                driven_erp_monthly_coef = 0.025
                driven_erp_monthly_activity_free = 12

                driven_erp_monthly_base_price = 33
                driven_erp_monthly_base_number_of_subscription_months = 2
                driven_erp_monthly_base_number_of_users = 9
                driven_erp_monthly_base_number_data_reloads = 89
                driven_erp_monthly_saturation_coef = 8


            if driven_edriven_e_commerce:
                driven_edriven_e_commerce_monthly_base_cost=driven_edriven_e_commerce.monthly_base_cost
                driven_edriven_e_commerce_monthly_coef = driven_edriven_e_commerce.monthly_coef
                driven_edriven_e_commerce_monthly_coef_monthly_activity_free = driven_edriven_e_commerce.monthly_activity_free

                driven_edriven_e_commerce_monthly_base_price = driven_edriven_e_commerce.base_price
                driven_edriven_e_commerce_monthly_base_number_of_subscription_months = driven_edriven_e_commerce.base_number_of_subscription_months
                driven_edriven_e_commerce_monthly_base_number_of_users = driven_edriven_e_commerce.base_number_of_users
                driven_edriven_e_commerce_monthly_base_number_data_reloads = driven_edriven_e_commerce.base_number_data_reloads
                driven_edriven_e_commerce_monthly_saturation_coef = driven_edriven_e_commerce.saturation_coef

            else:
                driven_edriven_e_commerce_monthly_base_cost = 995
                driven_edriven_e_commerce_monthly_coef = 0.025
                driven_edriven_e_commerce_monthly_coef_monthly_activity_free = 12

                driven_edriven_e_commerce_monthly_base_price = 6
                driven_edriven_e_commerce_monthly_base_number_of_subscription_months = 9
                driven_edriven_e_commerce_monthly_base_number_of_users = 5
                driven_edriven_e_commerce_monthly_base_number_data_reloads = 56
                driven_edriven_e_commerce_monthly_saturation_coef = 5

            parameters = AdditionalCostCalculationFixParameters.objects.filter().last()
            if parameters:
                sup_cost = parameters.sup_cost
                Train_cost = parameters.train_cost
            else:
                sup_cost = 25
                Train_cost = 500

            contex = {
                'all_company_types': all_company_types,
                'sup_cost': sup_cost,
                'Train_cost': Train_cost,

                'campaignscaled': campaignscaled,
                'plane_price': plane_price,

                'demandscaled': demandscaled,
                'demandscaled_monthly_base_cost': package_price_demandscaled_monthly_base_cost,
                'demandscaled_monthly_coef': package_price_demandscaled_monthly_coef,
                'demandscaled_monthly_activity_free': package_price_demandscaled_monthly_activity_free,

                'acquirescaled': acquirescaled,
                'acquirescaled_monthly_base_cost': package_price_acquirescaled_monthly_base_cost,
                'acquirescaled_monthly_coef': package_price_acquirescaled_monthly_coef,
                'acquirescaled_monthly_activity_free': package_price_acquirescaled_monthly_activity_free,

                'Product_recommendations': Product_recommendations,
                'Product_recommendations_monthly_base_cost': package_price_recommendscaled_monthly_base_cost,
                'Product_recommendations_monthly_coef': package_price_recommendscaled_monthly_coef,
                'Product_recommendations_monthly_activity_free': package_price_recommendscaled_monthly_activity_free,


                'prescriptive_ai_monthly_base_cost': prescriptive_ai_monthly_base_cost,
                'prescriptive_ai_monthly_coef': prescriptive_ai_monthly_coef,
                'prescriptive_ai_monthly_activity_free': prescriptive_ai_monthly_activity_free,

                'metricscaled_monthly_base_cost': metricscaled_monthly_base_cost,
                'metricscaled_monthly_coef': metricscaled_monthly_coef,
                'metricscaled_monthly_activity_free': metricscaled_monthly_activity_free,

                'driven_erp_monthly_base_cost': driven_erp_monthly_base_cost,
                'driven_erp_monthly_coef': driven_erp_monthly_coef,
                'driven_erp_monthly_activity_free': driven_erp_monthly_activity_free,

                'driven_edriven_e_commerce_monthly_base_cost': driven_edriven_e_commerce_monthly_base_cost,
                'driven_edriven_e_commerce_monthly_coef': driven_edriven_e_commerce_monthly_coef,
                'driven_edriven_e_commerce_monthly_coef_monthly_activity_free': driven_edriven_e_commerce_monthly_coef_monthly_activity_free,


                'CompanyRegistrationInformationId': CompanyRegistrationInformationId,

                'package_price_demandscaled_base_price': package_price_demandscaled_base_price,
                'package_price_demandscaled_base_number_of_subscription_months': package_price_demandscaled_base_number_of_subscription_months,
                'package_price_demandscaled_base_number_of_users': package_price_demandscaled_base_number_of_users,
                'package_price_demandscaled_base_number_data_reloads': package_price_demandscaled_base_number_data_reloads,
                'package_price_demandscaled_saturation_coef': package_price_demandscaled_saturation_coef,
                'package_price_acquirescaled_base_price': package_price_acquirescaled_base_price,
                'package_price_acquirescaled_base_number_of_subscription_months': package_price_acquirescaled_base_number_of_subscription_months,
                'package_price_acquirescaled_base_number_of_users': package_price_acquirescaled_base_number_of_users,
                'package_price_acquirescaled_base_number_data_reloads': package_price_acquirescaled_base_number_data_reloads,
                'package_price_acquirescaled_saturation_coef': package_price_acquirescaled_saturation_coef,
                'package_price_recommendscaled_base_price': package_price_recommendscaled_base_price,
                'package_price_recommendscaled_base_number_of_subscription_months': package_price_recommendscaled_base_number_of_subscription_months,
                'package_price_recommendscaled_base_number_of_users': package_price_recommendscaled_base_number_of_users,
                'package_price_recommendscaled_base_number_data_reloads': package_price_recommendscaled_base_number_data_reloads,
                'package_price_recommendscaled_saturation_coef': package_price_recommendscaled_saturation_coef,
                'prescriptive_ai_monthly_base_price': prescriptive_ai_monthly_base_price,
                'prescriptive_ai_monthly_base_number_of_subscription_months': prescriptive_ai_monthly_base_number_of_subscription_months,
                'prescriptive_ai_monthly_base_number_of_users': prescriptive_ai_monthly_base_number_of_users,
                'prescriptive_ai_monthly_base_number_data_reloads': prescriptive_ai_monthly_base_number_data_reloads,
                'prescriptive_ai_monthly_saturation_coef': prescriptive_ai_monthly_saturation_coef,
                'metricscaled_monthly_base_price': metricscaled_monthly_base_price,
                'metricscaled_monthly_base_number_of_subscription_months': metricscaled_monthly_base_number_of_subscription_months,
                'metricscaled_monthly_base_number_of_users': metricscaled_monthly_base_number_of_users,
                'metricscaled_monthly_base_number_data_reloads': metricscaled_monthly_base_number_data_reloads,
                'metricscaled_monthly_saturation_coef': metricscaled_monthly_saturation_coef,
                'driven_erp_monthly_base_price': driven_erp_monthly_base_price,
                'driven_erp_monthly_base_number_of_subscription_months': driven_erp_monthly_base_number_of_subscription_months,
                'driven_erp_monthly_base_number_of_users': driven_erp_monthly_base_number_of_users,
                'driven_erp_monthly_base_number_data_reloads': driven_erp_monthly_base_number_data_reloads,
                'driven_erp_monthly_saturation_coef': driven_erp_monthly_saturation_coef,
                'driven_edriven_e_commerce_monthly_base_price': driven_edriven_e_commerce_monthly_base_price,
                'driven_edriven_e_commerce_monthly_base_number_of_subscription_months': driven_edriven_e_commerce_monthly_base_number_of_subscription_months,
                'driven_edriven_e_commerce_monthly_base_number_of_users': driven_edriven_e_commerce_monthly_base_number_of_users,
                'driven_edriven_e_commerce_monthly_base_number_data_reloads': driven_edriven_e_commerce_monthly_base_number_data_reloads,
                'driven_edriven_e_commerce_monthly_saturation_coef': driven_edriven_e_commerce_monthly_saturation_coef,

            }
            return render(request, "calculate_amount_to_pay.html", contex)
        except Exception as e:
            d = str(e)


        return render(request, 'calculate_amount_to_pay.html')
    else:
        return render(request, 'not_allowed.html')

def submit_subscription(request):
    try:
        CompanyRegistrationInformationId = request.POST.get('CompanyRegistrationInformationId')
        plane_price = request.POST.get('plane_price')

        demandscaled = request.POST.get('demandscaled')
        if demandscaled == 'on':
            demandscaled = True
        else:

            demandscaled = False
        acquirescaled = request.POST.get('acquirescaled')
        if acquirescaled == 'on':
            acquirescaled = True
        else:
            acquirescaled = False
        Product_recommendations = request.POST.get('Product_recommendations')
        if Product_recommendations == 'on':
            Product_recommendations = True
        else:
            Product_recommendations = False
        campaignscaled = request.POST.get('campaignscaled')
        if campaignscaled == 'on':
            campaignscaled = True
        else:
            campaignscaled = False

        month_to_access = request.POST.get('month_to_access')
        number_of_times = request.POST.get('number_of_times')
        expected_users = request.POST.get('expected_users')

        training_hours = request.POST.get('training_hours')
        support_hours = request.POST.get('support_hours')

        payment_type_get = request.POST.get('payment_type_get')
        total_amount = request.POST.get('total_amount')

        installment_amount = request.POST.get('installment_amount')

        installmentsCount = request.POST.get('installmentsCount')

        if payment_type_get == "installments":
            total = float(installmentsCount)
        else:
            total = float(installmentsCount)
        services_plan_cost_and_platform_total_payment = float(total_amount)+float(plane_price)
        com_id = CompanyRegistrationInformation.objects.get(id=CompanyRegistrationInformationId)

        sub = SubscriptionInformation(
            company_info = com_id,
            demandscaled = demandscaled,
            acquirescaled = acquirescaled,
            product_recommendations = Product_recommendations,
            campaignscaled = campaignscaled,

            number_of_month_to_access = month_to_access,
            number_of_times_ERP = number_of_times,
            number_of_expected_users_of_the_platform = expected_users,
            number_of_support_hours_per_month = support_hours,
            number_of_training_per_month = training_hours,
            platform_total_payment = total_amount,
            services_plan_cost = plane_price,
            services_plan_cost_and_platform_total_payment = services_plan_cost_and_platform_total_payment,
            paid_payment = total,
        )
        sub.save()



        publishable_key = settings.STRIPE_PUBLIC_KEY
        context = {
            'analytics_services_info_id': sub.id,
            'publishable_key': publishable_key,
            'total_amount': total,

            'services_plan_cost_and_platform_total_payment': services_plan_cost_and_platform_total_payment,
            'installment_amount': installment_amount,

            'now_pay': total,
            'sub_id': sub.id,
        }
        return render(request, 'payment_home.html', context)

    except Exception as e:
        return HttpResponse(str(e))

    # return render(request, 'registration.html')
    # return render(request, 'home.html')


def send_email_info(get_subject, get_massage, get_recipient_list):
    try:
        get_from_email = settings.EMAIL_HOST_USER
        send_mail(
            get_subject,
            get_massage,
            get_from_email,
            get_recipient_list,
            fail_silently=False,
        )
        return 'Done'
    except Exception as E:
        return str(E)




# @login_required(login_url="users:login")
def Payment_Submit(request):
    if request.user.is_authenticated:
        # Getting post requests values
        stripeToken = request.POST.get('stripeToken')
        installment_amount = request.POST.get('installment_amount')
        print('installment_amount')
        print(installment_amount)
        print('installment_amount')
        services_plan_cost_and_platform_total_payment = request.POST.get('services_plan_cost_and_platform_total_payment')
        now_pay = request.POST.get('now_pay')
        print('services_plan_cost_and_platform_total_payment')
        print(services_plan_cost_and_platform_total_payment)
        print('services_plan_cost_and_platform_total_payment')





        payment_amount = request.POST.get('payment_amount')
        total_amount = request.POST.get('total_amount')
        sub_id = request.POST.get('analytics_services_info_id')
        iamhome = request.POST.get('iamhome')

        secret_key = settings.STRIPE_SECRET_KEY
        stripe.api_key = secret_key

        try:
            product_name = 'Custom Analytics Service'
            unit_price = float(services_plan_cost_and_platform_total_payment) or 300.00
            upfront_payment = float(now_pay) or 200.0  # Amount to be paid upfront/now
            installment_amount = float(installment_amount) or 50.0  # Amount of each installment
            currency = 'usd'
            interval = 'month'  # Monthly billing
            user_info = request.user
            email = user_info.email
            name = user_info.first_name
            payment_method = request.POST.get('payment_method')
            stripe_token = request.POST.get('stripeToken')

            # Create product and price
            product_id, price_id = create_stripe_product_and_price(product_name, unit_price, currency, interval)

            if product_id and price_id:
                # Create customer
                customer_id = create_stripe_customer(email, name)

                if customer_id:
                    # Create subscription with incomplete payment
                    subscription = create_subscription(customer_id, price_id)

                    payment_method = stripe.PaymentMethod.create(
                        type='card',
                        card={'token': stripe_token}
                    )
                    pid = payment_method.id
                    # Create PaymentIntent to collect upfront payment
                    payment_intent = create_payment_intent(customer_id, upfront_payment, currency, payment_method)

                    if payment_intent and payment_intent.status == 'succeeded':
                        messages.success(request, 'Payment was Successfull !!')

                        analitics_info = SubscriptionInformation.objects.filter(id=sub_id).last()
                        if analitics_info:
                            analitics_info.payment_status = True
                            analitics_info.save()
                        print(f"Product ID: {product_id}, Price ID: {price_id}, Customer: {customer_id}, Subscription: {subscription.id}")
                        # return redirect('home_info')
                        if iamhome == "iamhome":
                            user_info = request.user
                            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                            subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                            contex = {
                                'user_info': user_info,
                                'company_info': company_info,
                                'subcription': subcription,
                                'sub_id': sub_id,
                                'timezone_all': timezone_all
                            }
                            return render(request, 'erp_info_for_home.html', contex)
                        else:
                            contex = {
                                'sub_id': sub_id,
                                'timezone_all':timezone_all
                            }
                            return render(request, 'erp_info.html', contex)

                        # return HttpResponse(
                        #     f"Product ID: {product_id}, Price ID: {price_id}, Customer: {customer_id}, Subscription: {subscription.id}")
                    else:
                        return HttpResponse("Failed to collect upfront payment.")
                else:
                    return HttpResponse("Failed to create customer.")
            else:
                return HttpResponse("Failed to create Product and Price.")



        except stripe.error.CardError as e:
            messages.info(request, f"{e.error.message}")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)

        except stripe.error.RateLimitError as e:
            messages.info(request, f"{e.error.message}")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        except stripe.error.InvalidRequestError as e:
            messages.info(request, "Invalid Request !")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        except stripe.error.AuthenticationError as e:
            messages.info(request, "Authentication Error !!")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        except stripe.error.APIConnectionError as e:
            messages.info(request, "Check Your Connection !")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        except stripe.error.StripeError as e:
            messages.info(request, "There was an error please try again !")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        except Exception as e:
            messages.info(request, "A serious error occured we were notified !")
            publishable_key = settings.STRIPE_PUBLIC_KEY
            context = {
                'analytics_services_info_id': sub_id,
                'publishable_key': publishable_key,
                'total_amount': total_amount,
                'messages': messages,
            }
            return render(request, 'payment_home.html', context)
        return redirect('shop_dashboard', analytics_services_info_id)
    else:
        return redirect('login_info')







from .utils1 import  upload_contacts_to_odoo_here, upload_employees_to_odoo_here, upload_suppliers_to_odoo_here, upload_fleet_assets_to_odoo_here
import csv
import odoorpc
import os
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import datetime

def get_bucket_name(company_id, type):
    today_date_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    bucket_name = f'{type}/{today_date_time}/'
    return bucket_name


# import re

# def sanitize_bucket_name(bucket_name):
#     # Remove any special characters except periods, hyphens, and underscores
#     bucket_name = re.sub(r'[^\w\.-]', '', bucket_name)
#     # Truncate if the length exceeds 255 characters
#     bucket_name = bucket_name[:255]
#     return bucket_name

def import_contacts_record(request, pk):
    if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')

                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)

                file = request.FILES['file']

                # Save the file locally first
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                local_file_path = fs.path(filename)

                # AWS S3 credentials from environment variables
                AWS_ACCESS_KEY_ID = settings.S3_ACCESS_KEY_ID
                AWS_SECRET_ACCESS_KEY = settings.S3_SECRET_ACCESS_KEY
                AWS_REGION = settings.AWS_REGION
                # BUCKET_NAME = 'buckets'+str(company_id)
                type = 'contact'
                BUCKET_NAME = 'companyid'+str(company_id)
                S3_FILE_KEY = get_bucket_name(company_id, type)+file.name  # Use the uploaded file's name as the key in S3
                # S3_FILE_KEY = file.name  # Use the uploaded file's name as the key in S3

                # Initialize S3 client
                s3 = boto3.client('s3',
                                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                  region_name=AWS_REGION)

                try:
                    # Check if the bucket exists, create it if it doesn't
                    buckets = s3.list_buckets()
                    bucket_exists = any(bucket['Name'] == BUCKET_NAME for bucket in buckets['Buckets'])

                    if not bucket_exists:
                        res = s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': AWS_REGION})

                except Exception as e:
                    messages.warning(request, str(e))

                try:
                    # Upload file to S3
                    res2 = s3.upload_file(local_file_path, BUCKET_NAME, S3_FILE_KEY)
                    print(f"File {file.name} uploaded to S3 bucket {BUCKET_NAME} successfully!")
                    file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{S3_FILE_KEY}"


                except Exception as e:
                    messages.warning(request, str(e))

                # Odoo credentials from environment variables

                try:
                    res3 = upload_contacts_to_odoo_here(file, company_id, website_id)

                    messages.success(request, res3)
                except Exception as e:
                    messages.warning(request, str(e))
                finally:
                    # Optionally, delete the local file after processing
                    os.remove(local_file_path)




            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subcription = SubscriptionInformation.objects.filter(company_info=company_info)
            subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                     payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()

            contex = {
                'user_info': user_info,
                'company_info': company_info,
                'subcription': subcription,
                'erp': erp,
                'subcription_one': subcription_one,
                'erp_active': erp_active,

            }
            return render(request, 'import_contacts_record.html', contex)
        except Exception as e:

            messages.warning(request, str(e))
            return redirect('home')

    else:
        return redirect('login_info')


def import_suppliers_record(request, pk):
    if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')

                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)

                file = request.FILES['file']

                # Save the file locally first
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                local_file_path = fs.path(filename)

                # AWS S3 credentials from environment variables
                AWS_ACCESS_KEY_ID = settings.S3_ACCESS_KEY_ID
                AWS_SECRET_ACCESS_KEY = settings.S3_SECRET_ACCESS_KEY
                AWS_REGION = settings.AWS_REGION
                type = 'supplier'
                # BUCKET_NAME = get_bucket_name(company_id, type)
                # S3_FILE_KEY = file.name  # Use the uploaded file's name as the key in S3

                BUCKET_NAME = 'companyid' + str(company_id)
                S3_FILE_KEY = get_bucket_name(company_id, type) + file.name


                # Initialize S3 client
                s3 = boto3.client('s3',
                                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                  region_name=AWS_REGION)

                try:
                    # Check if the bucket exists, create it if it doesn't
                    buckets = s3.list_buckets()
                    bucket_exists = any(bucket['Name'] == BUCKET_NAME for bucket in buckets['Buckets'])

                    if not bucket_exists:
                        res = s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': AWS_REGION})

                except Exception as e:
                    messages.warning(request, str(e))

                try:
                    # Upload file to S3
                    res2 = s3.upload_file(local_file_path, BUCKET_NAME, S3_FILE_KEY)
                    print(f"File {file.name} uploaded to S3 bucket {BUCKET_NAME} successfully!")
                    file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file.name}"

                except Exception as e:
                    messages.warning(request, str(e))

                # Odoo credentials from environment variables

                try:
                    res3 = upload_suppliers_to_odoo_here(file, company_id, website_id)

                    messages.success(request, res3)
                except Exception as e:
                    messages.warning(request, str(e))
                finally:
                    # Optionally, delete the local file after processing
                    os.remove(local_file_path)

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subcription = SubscriptionInformation.objects.filter(company_info=company_info)
            subcription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                     payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subcription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one, Erp_Info=erp).last()

            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subcription': subcription,
                'erp': erp,
                'subcription_one': subcription_one,
                'erp_active': erp_active,

            }
            return render(request, 'import_suppliers_record.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')

    else:
        return redirect('login_info')

def import_employees_record(request, pk):
    if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')

                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)

                file = request.FILES['file']

                # Save the file locally first
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                local_file_path = fs.path(filename)

                # AWS S3 credentials from environment variables
                AWS_ACCESS_KEY_ID = settings.S3_ACCESS_KEY_ID
                AWS_SECRET_ACCESS_KEY = settings.S3_SECRET_ACCESS_KEY
                AWS_REGION = settings.AWS_REGION
                type = 'employee'
                # BUCKET_NAME = get_bucket_name(company_id, type)
                # S3_FILE_KEY = file.name  # Use the uploaded file's name as the key in S3

                BUCKET_NAME = 'companyid' + str(company_id)
                S3_FILE_KEY = get_bucket_name(company_id, type) + file.name

                # Initialize S3 client
                s3 = boto3.client('s3',
                                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                  region_name=AWS_REGION)

                try:
                    # Check if the bucket exists, create it if it doesn't
                    buckets = s3.list_buckets()
                    bucket_exists = any(bucket['Name'] == BUCKET_NAME for bucket in buckets['Buckets'])

                    if not bucket_exists:
                        res = s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': AWS_REGION})

                except Exception as e:
                    messages.warning(request, str(e))

                try:
                    # Upload file to S3
                    res2 = s3.upload_file(local_file_path, BUCKET_NAME, S3_FILE_KEY)
                    print(f"File {file.name} uploaded to S3 bucket {BUCKET_NAME} successfully!")
                    file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file.name}"

                except Exception as e:
                    messages.warning(request, str(e))

                # Odoo credentials from environment variables

                try:
                    res3 = upload_employees_to_odoo_here(file, company_id, website_id)

                    messages.success(request, res3)
                except Exception as e:
                    messages.warning(request, str(e))
                finally:
                    # Optionally, delete the local file after processing
                    os.remove(local_file_path)

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()

            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
            }
            return render(request, 'import_employees_record.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')
    else:
        return redirect('login_info')
def import_fleet_assets_record(request, pk):
    if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')

                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)

                file = request.FILES['file']

                # Save the file locally first
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                local_file_path = fs.path(filename)

                # AWS S3 credentials from environment variables
                AWS_ACCESS_KEY_ID = settings.S3_ACCESS_KEY_ID
                AWS_SECRET_ACCESS_KEY = settings.S3_SECRET_ACCESS_KEY
                AWS_REGION = settings.AWS_REGION
                type = 'fleet_asset'
                # BUCKET_NAME = get_bucket_name(company_id, type)
                # S3_FILE_KEY = file.name  # Use the uploaded file's name as the key in S3

                BUCKET_NAME = 'companyid' + str(company_id)
                S3_FILE_KEY = get_bucket_name(company_id, type) + file.name

                # Initialize S3 client
                s3 = boto3.client('s3',
                                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                  region_name=AWS_REGION)

                try:
                    # Check if the bucket exists, create it if it doesn't
                    buckets = s3.list_buckets()
                    bucket_exists = any(bucket['Name'] == BUCKET_NAME for bucket in buckets['Buckets'])

                    if not bucket_exists:
                        res = s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': AWS_REGION})

                except Exception as e:
                    messages.warning(request, str(e))

                try:
                    # Upload file to S3
                    res2 = s3.upload_file(local_file_path, BUCKET_NAME, S3_FILE_KEY)
                    print(f"File {file.name} uploaded to S3 bucket {BUCKET_NAME} successfully!")
                    file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file.name}"

                except Exception as e:
                    messages.warning(request, str(e))

                # Odoo credentials from environment variables

                try:
                    res3 = upload_fleet_assets_to_odoo_here(file, company_id, website_id)

                    messages.success(request, res3)
                except Exception as e:
                    messages.warning(request, str(e))
                finally:
                    # Optionally, delete the local file after processing
                    os.remove(local_file_path)

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()

            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
            }
            return render(request, 'import_fleet_assets_record.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')

    else:
        return redirect('login_info')


from . utils1 import accounting_here
def odoo_account_accountant(request, pk):
      if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')
                fiscal_year_name = request.POST.get('fiscal_year_name')
                fiscal_year_start = request.POST.get('fiscal_year_start')
                fiscal_year_end = request.POST.get('fiscal_year_end')
                income_tax_name = request.POST.get('income_tax_name')
                income_tax_rate = request.POST.get('income_tax_rate')
                bank_name = request.POST.get('bank_name')
                bank_street = request.POST.get('bank_street')
                bank_city = request.POST.get('bank_city')
                bank_state = request.POST.get('bank_state')
                bank_zip = request.POST.get('bank_zip')
                bank_country = request.POST.get('bank_country')
                bank_phone = request.POST.get('bank_phone')
                bank_account_number = request.POST.get('bank_account_number')
                sales_tax_name = request.POST.get('sales_tax_name')
                sales_tax_rate = request.POST.get('sales_tax_rate')
                chart_template_name = request.POST.get('chart_template_name')

                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)
                try:
                    result = accounting_here(
                        company_id=company_id, website_id=website_id,
                        fiscal_year_name=fiscal_year_name, fiscal_year_start=fiscal_year_start, fiscal_year_end=fiscal_year_end,
                        income_tax_name=income_tax_name, income_tax_rate=income_tax_rate, bank_name=bank_name,
                        bank_street=bank_street,
                        bank_city=bank_city, bank_state=bank_state, bank_zip=bank_zip, bank_country=bank_country,
                        bank_phone=bank_phone,
                        bank_account_number=bank_account_number, sales_tax_name=sales_tax_name, sales_tax_rate=sales_tax_rate,
                        chart_template_name=chart_template_name
                    )
                    messages.warning(request, str(result))
                    # result = accounting_here(
                    #     company_id=company_id, website_id=website_id,
                    #     fiscal_year_name='2024', fiscal_year_start='2024-01-01', fiscal_year_end='2024-12-31',
                    #     income_tax_name='Income Tax', income_tax_rate=15.0, bank_name='My Bank',
                    #     bank_street='123 Bank Street',
                    #     bank_city='Bank City', bank_state='Bank State', bank_zip='12345', bank_country='Country',
                    #     bank_phone='123456789',
                    #     bank_account_number='1234567890123456', sales_tax_name='Sales Tax', sales_tax_rate=7.5,
                    #     chart_template_name='Standard Chart of Accounts'
                    # )
                except Exception as e:
                    messages.warning(request, str(e))

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()
            website_id = int(erp_active.website_id)
            company_id = int(erp_active.company_id)
            years = list(range(2020, 2061))
            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
                'years': years,
            }
            return render(request, 'odoo_account_accountant.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')

      else:
        return redirect('login_info')



from . utils1 import setup_manual_shipping
def odoo_setup_manual_shipping(request, pk):
      if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')

                shipping_name = request.POST.get('shipping_name')
                product_id = int(request.POST.get('product_id'))
                fixed_price = float(request.POST.get('fixed_price'))
                margin = float(request.POST.get('margin'))
                sequence = int(request.POST.get('sequence'))

                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)
                try:

                    result = setup_manual_shipping(company_id, website_id, shipping_name, product_id, fixed_price, margin, sequence)
                    messages.warning(request, str(result))

                except Exception as e:
                    messages.warning(request, str(e))

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()
            website_id = int(erp_active.website_id)
            company_id = int(erp_active.company_id)
            years = list(range(2020, 2061))
            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
                'years': years,
            }
            return render(request, 'odoo_setup_manual_shipping.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')

      else:
        return redirect('login_info')

from . utils1 import set_website_languages

def odoo_set_website_languages(request, pk):
      if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')

                languages = request.POST.get('languages')


                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)
                try:

                    result = set_website_languages(company_id, website_id, languages)
                    messages.warning(request, str(result))

                except Exception as e:
                    messages.warning(request, str(e))

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()

            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
            }
            return render(request, 'odoo_set_website_languages.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')

      else:
        return redirect('login_info')





from .utils1 import set_configure_whatsapp_service
def odoo_configure_whatsapp_service(request, pk):
      if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')

                twilio_account_sid = request.POST.get('twilio_account_sid')
                twilio_auth_token = request.POST.get('twilio_auth_token')
                twilio_whatsapp_number = request.POST.get('twilio_whatsapp_number')


                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)
                try:

                    result = set_configure_whatsapp_service(company_id, website_id, twilio_account_sid, twilio_auth_token, twilio_whatsapp_number)
                    messages.warning(request, str(result))

                except Exception as e:
                    messages.warning(request, str(e))

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()

            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
            }
            return render(request, 'configure_whatsapp_service.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')
      else:
        return redirect('login_info')



from .utils1 import set_twilio_sms_config
def odoo_twilio_sms_config(request, pk):
      if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')

                twilio_account_sid = request.POST.get('twilio_account_sid')
                twilio_auth_token = request.POST.get('twilio_auth_token')
                twilio_sender_number = request.POST.get('twilio_sender_number')


                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)
                try:

                    result = set_twilio_sms_config(company_id, website_id, twilio_account_sid, twilio_auth_token, twilio_sender_number)
                    messages.warning(request, str(result))

                except Exception as e:
                    messages.warning(request, str(e))

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()

            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
            }
            return render(request, 'twilio_sms_config.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')

      else:
        return redirect('login_info')




from .utils1 import configure_stripe_payment
def odoo_configure_stripe_payment(request, pk):
      if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')

                stripe_secret_key = request.POST.get('stripe_secret_key')
                stripe_publishable_key = request.POST.get('stripe_publishable_key')

                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)
                try:

                    result = configure_stripe_payment(company_id, website_id, stripe_secret_key, stripe_publishable_key)
                    messages.warning(request, str(result))

                except Exception as e:
                    messages.warning(request, str(e))

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()

            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
            }
            return render(request, 'odoo_configure_stripe_payment.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')

      else:
        return redirect('login_info')




from .utils1 import configure_paypal_payment
def odoo_configure_paypal_payment(request, pk):
      if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')

                paypal_email = request.POST.get('paypal_email')
                paypal_seller_account = request.POST.get('paypal_seller_account')

                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)
                try:

                    result = configure_paypal_payment(company_id, website_id, paypal_email, paypal_seller_account)
                    messages.warning(request, str(result))

                except Exception as e:
                    messages.warning(request, str(e))

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()

            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
            }
            return render(request, 'odoo_configure_paypal_payment.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')

      else:
        return redirect('login_info')




def get_training(request, pk):
      if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')
                email = request.POST.get('email')
                print('email')
                print(email)



                # erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                # website_id = int(erp_active_info.website_id)
                # company_id = int(erp_active_info.company_id)
                try:

                    result = TrainingUserEmail(
                        email=email
                    )
                    result.save()
                    print('000')
                    messages.success(request, "Saved Successfully")

                except Exception as e:
                    messages.warning(request, str(e))


            user_info = request.user
            print('1')
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            print('2')
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()

            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
            }
            return render(request, 'get_training.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')

      else:
        return redirect('login_info')


def learn_erp(request, pk):
      if request.user.is_authenticated:
        try:
            if request.method == 'POST':

                erp_active_id = request.POST.get('erp_active_id')



                erp_active_info = ErpActiveCompanyAndWeb.objects.get(id=erp_active_id)
                website_id = int(erp_active_info.website_id)
                company_id = int(erp_active_info.company_id)
                try:

                    result = configure_paypal_payment(company_id, website_id, paypal_email, paypal_seller_account)
                    messages.warning(request, str(result))

                except Exception as e:
                    messages.warning(request, str(e))

            user_info = request.user
            company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
            subscription = SubscriptionInformation.objects.filter(company_info=company_info)
            subscription_one = SubscriptionInformation.objects.filter(company_info=company_info,
                                                                      payment_status=True).last()
            erp = Erp_Information.objects.filter(subscription_info=subscription_one).last()
            erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subscription_one, Erp_Info=erp).last()

            context = {
                'user_info': user_info,
                'company_info': company_info,
                'subscription': subscription,
                'erp': erp,
                'subscription_one': subscription_one,
                'erp_active': erp_active,
            }
            return render(request, 'learn_erp.html', context)
        except Exception as e:
            messages.warning(request, str(e))
            return redirect('home')

      else:
        return redirect('login_info')
