from .files_country_state_city.read_country import search_countries_by_character, get_country_id_from_name
from .files_country_state_city.read_city import read_state_file
from django.shortcuts import render, HttpResponse, redirect
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from .files_country_state_city.country import country_all
from django.views.decorators.csrf import csrf_exempt
from .files_country_state_city.states import  states_all  # Import the states data

from django.contrib import messages
from django.shortcuts import render, redirect
from subscription_app.models import Erp_Information, SubscriptionInformation
from cryptography.fernet import Fernet
from . files_country_state_city.timezone.timezone import *

from . models import CompanyRegistrationInformation
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

@csrf_exempt
def country_list_from_ajax(request):

    search_query = request.GET.get('q', '')
    matching_countries = search_countries_by_character(search_query)
    return JsonResponse({'results': matching_countries})

@csrf_exempt
def get_states_for_update_ajax(request):
    print("plp")

    country_name = request.GET.get('country_id', '')
    print("ok")
    print(country_name)
    print("ok")
    search_query = ''
    country_id = get_country_id_from_name(country_name)


    matching_states = [{'id': state.get('id'), 'text': state.get('name')}
                       for state in states_all
                       if str(state.get('country_id')) == str(country_id)]

    return JsonResponse(matching_states, safe=False)


    return JsonResponse({'results': matching_countries})


@csrf_exempt
def get_cities_for_update_ajax(request):
    state_id = request.GET.get('state_id', '')
    print('state_id')
    print(state_id)
    print('state_id')
    print('sohel')

    # Filter cities based on the selected state ID
    city_names = read_state_file(state_id)

    if city_names is None:
        return JsonResponse([], safe=False)

    # Format city data as JSON response
    matching_cities = [{'id': index, 'text': city_name} for index, city_name in enumerate(city_names)]
    print('matching_cities')
    print(matching_cities)
    print('matching_cities')

    return JsonResponse(matching_cities, safe=False)


@csrf_exempt
def states_list_from_ajax(request):
    print("state")
    country_id = request.GET.get('country_id')

    matching_states = [{'id': state.get('id'), 'text': state.get('name')}
                       for state in states_all
                       if str(state.get('country_id')) == str(country_id)]


    return JsonResponse(matching_states, safe=False)

@csrf_exempt
def cities_list_from_ajax(request):

    state_id = request.GET.get('state_id')

    matching_states = read_state_file(state_id)
    print("test")
    print(matching_states)
    print("test")


    return JsonResponse(matching_states, safe=False)

def testtu(request):
    country_info = request.POST.get('country_info')
    state_info = request.POST.get('state_info')
    city_info = request.POST.get('city_info')

    response_data = f"Country: {country_info}, State: {state_info}, City: {city_info}"

    # Return the concatenated information as an HTTP response
    return HttpResponse(response_data)


@csrf_exempt
def validate_email(request):
    if request.method == 'POST' and 'email' in request.POST:
        email = request.POST.get('email')
        print('email')
        print(email)
        # Check if the email already exists in the User model
        if User.objects.filter(email=email).exists():

            valid = 'exist'
        else:
            valid = 'not exist'
        print('valid')
        print(valid)
        # Return the validation result as JSON
        return JsonResponse({'valid': valid})

    # Handle invalid requests
    return JsonResponse({'error': 'Invalid request'})



# Encryption key - Replace this with your own key
key = b'mC7xZUvqfWgHRcNpJYvWljMzmo7crFjrHbQqVX2fY4E='
cipher_suite = Fernet(key)

def encrypt_data(data):
    return cipher_suite.encrypt(data.encode()).decode()

def erp_info_check(request):
    if request.method == 'POST':
        try:
            sub_id = request.POST['sub_id']
            from_home = request.POST.get('from_home')

            erp_name = request.POST['erp_name']
            erp_site_name = request.POST['erp_site_name']
            erp_admin_user_name = request.POST['erp_admin_user_name']
            erp_admin_pw_encrypted = encrypt_data(request.POST['erp_admin_pw_encrypted'])
            erp_api_key = encrypt_data(request.POST['erp_api_key'])
            erp_api_secret = encrypt_data(request.POST['erp_api_secret'])
            erp_page_about_us_content = request.POST['erp_page_about_us_content']
            erp_page_contact_us_content = request.POST['erp_page_contact_us_content']
            erp_pages_root_email = request.POST['erp_pages_root_email']
            erp_pages_root_email_pw = encrypt_data(request.POST['erp_pages_root_email_pw'])
            erp_country = request.POST['erp_country']
            erp_timezone = request.POST.get('erp_timezone')
            erp_contact_phone = request.POST['erp_contact_phone']
            erp_contact_email = request.POST['erp_contact_email']
            erp_whatsapp_phone = request.POST['erp_whatsapp_phone']
            erp_email_account_name = request.POST['erp_email_account_name']
            erp_email_id = request.POST['erp_email_id']
            erp_email_account_password = request.POST['erp_email_account_password']
            erp_smtp_server = request.POST['erp_smtp_server']
            erp_smtp_port = request.POST['erp_smtp_port']
            erp_use_tls = request.POST['erp_use_tls']
            if erp_use_tls == 'on':
                erp_use_tls = True
            else:
                erp_use_tls = False
            erp_use_ssl = request.POST.get('erp_use_ssl')
            if erp_use_ssl == 'on':
                erp_use_ssl = True
            else:
                erp_use_ssl = False
            erp_imap_server = request.POST['erp_imap_server']
            erp_imap_port = request.POST['erp_imap_port']
            erp_stripe_account_id = encrypt_data(request.POST['erp_stripe_account_id'])
            erp_stripe_access_key = encrypt_data(request.POST['erp_stripe_access_key'])
            erp_stripe_api_secret = encrypt_data(request.POST['erp_stripe_api_secret'])
            erp_shipper_name = request.POST['erp_shipper_name']
            erp_shipper_api_key = encrypt_data(request.POST['erp_shipper_api_key'])
            erp_shipper_api_secret = encrypt_data(request.POST['erp_shipper_api_secret'])
            erp_whatsup_api_url = request.POST['erp_whatsup_api_url']
            erp_whatsup_api_token = encrypt_data(request.POST['erp_whatsup_api_token'])
            erp_whatsup_version = request.POST['erp_whatsup_version']
            erp_whatsup_phone_id = request.POST['erp_whatsup_phone_id']
            erp_whatsup_business_id = request.POST['erp_whatsup_business_id']


            s_in = SubscriptionInformation.objects.get(id = sub_id)
            # Save data to the database

            erp_smtp_server = settings.ODOO_URL+'/'+erp_site_name

            ei = Erp_Information(
                subscription_info = s_in,
                erp_name=erp_name,
                erp_site_name=erp_site_name,
                erp_admin_user_name=erp_admin_user_name,
                erp_admin_pw_encrypted=erp_admin_pw_encrypted,
                erp_api_key_encrypted=erp_api_key,
                erp_api_secret_encrypted=erp_api_secret,
                erp_page_about_us_content=erp_page_about_us_content,
                erp_page_contact_us_content=erp_page_contact_us_content,
                erp_pages_root_email=erp_pages_root_email,
                erp_pages_root_email_pw_encrypted=erp_pages_root_email_pw,
                erp_country=erp_country,
                erp_timezone=erp_timezone,
                erp_contact_phone=erp_contact_phone,
                erp_contact_email=erp_contact_email,
                erp_whatsapp_phone=erp_whatsapp_phone,
                erp_email_account_name=erp_email_account_name,
                erp_email_id=erp_email_id,
                erp_email_account_password_encrypted=erp_email_account_password,
                erp_smtp_server=erp_smtp_server,
                erp_smtp_port=erp_smtp_port,
                erp_use_tls=erp_use_tls,
                erp_use_ssl=erp_use_ssl,
                erp_imap_server=erp_imap_server,
                erp_imap_port=erp_imap_port,
                erp_stripe_account_id_encrypted=erp_stripe_account_id,
                erp_stripe_access_key_encrypted=erp_stripe_access_key,
                erp_stripe_api_secret_encrypted=erp_stripe_api_secret,
                erp_shipper_name=erp_shipper_name,
                erp_shipper_api_key_encrypted=erp_shipper_api_key,
                erp_shipper_api_secret_encrypted=erp_shipper_api_secret,
                erp_whatsup_api_url=erp_whatsup_api_url,
                erp_whatsup_api_token_encrypted=erp_whatsup_api_token,
                erp_whatsup_version=erp_whatsup_version,
                erp_whatsup_phone_id=erp_whatsup_phone_id,
                erp_whatsup_business_id=erp_whatsup_business_id,
            )
            ei.save()

            return redirect('home_info')  # Redirect to success page
        except Exception as e:
            if from_home:
                messages.success(request, str(e))
                user_info = request.user
                company_info = CompanyRegistrationInformation.objects.filter(user_info=user_info).last()
                subcription = SubscriptionInformation.objects.filter(company_info=company_info)
                contex = {
                    'user_info': user_info,
                    'company_info': company_info,
                    'subcription': subcription,
                    'sub_id': sub_id,
                }
                return render(request, 'erp_info_for_home.html', contex)
            else:
                messages.success(request, str(e))
                contex = {
                    'sub_id': sub_id,
                    'timezone_all': timezone_all
                }
                return render(request, 'erp_info.html', contex)

    return render(request, 'erp_info_form.html')




@csrf_exempt
def check_unique_erp_name(request):
    print('popopopopop')
    erp_name = request.GET.get('erp_name', None)

    data = {
        'is_taken': Erp_Information.objects.filter(erp_name=erp_name).exists()
    }
    return JsonResponse(data)

@csrf_exempt
def erp_name_ajax(request):
    if request.method == 'POST' and 'erp_name' in request.POST:
        erp_name = request.POST.get('erp_name')
        print('erp_name')
        print(erp_name)
        # Check if the email already exists in the User model

        if Erp_Information.objects.filter(erp_name=erp_name).exists():
            valid = 'exist'
        else:
            valid = 'not exist'
        print('valid')
        print(valid)
        # Return the validation result as JSON
        return JsonResponse({'valid': valid})

    # Handle invalid requests
    return JsonResponse({'error': 'Invalid request'})

@csrf_exempt
def erp_site_name_ajax(request):
    if request.method == 'POST' and 'erp_site_name' in request.POST:
        erp_site_name = request.POST.get('erp_site_name')
        print('erp_site_name')
        print(erp_site_name)
        # Check if the email already exists in the User model

        if Erp_Information.objects.filter(erp_site_name=erp_site_name).exists():
            valid = 'exist'
        else:
            valid = 'not exist'
        print('valid')
        print(valid)
        # Return the validation result as JSON
        return JsonResponse({'valid': valid})

    # Handle invalid requests
    return JsonResponse({'error': 'Invalid request'})


@csrf_exempt
def check_unique_erp_site_name(request):
    erp_site_name = request.GET.get('erp_site_name', None)
    data = {
        'is_taken': Erp_Information.objects.filter(erp_site_name=erp_site_name).exists()
    }
    return JsonResponse(data)





def erp_info_check_for_upgrade(request):
    if request.method == 'POST':
        # sub_id = request.POST['sub_id']
        #
        # erp_name = request.POST['erp_name']
        # erp_site_name = request.POST['erp_site_name']
        # erp_admin_user_name = request.POST['erp_admin_user_name']
        # erp_admin_pw_encrypted = encrypt_data(request.POST['erp_admin_pw_encrypted'])
        # erp_api_key = encrypt_data(request.POST['erp_api_key'])
        # erp_api_secret = encrypt_data(request.POST['erp_api_secret'])
        # erp_page_about_us_content = request.POST['erp_page_about_us_content']
        # erp_page_contact_us_content = request.POST['erp_page_contact_us_content']
        # erp_pages_root_email = request.POST['erp_pages_root_email']
        # erp_pages_root_email_pw = encrypt_data(request.POST['erp_pages_root_email_pw'])
        # erp_country = request.POST['erp_country']
        # erp_timezone = request.POST['erp_timezone']
        # erp_contact_phone = request.POST['erp_contact_phone']
        # erp_contact_email = request.POST['erp_contact_email']
        # erp_whatsapp_phone = request.POST['erp_whatsapp_phone']
        # erp_email_account_name = request.POST['erp_email_account_name']
        # erp_email_id = request.POST['erp_email_id']
        # erp_email_account_password = request.POST['erp_email_account_password']
        # erp_smtp_server = request.POST['erp_smtp_server']
        # erp_smtp_port = request.POST['erp_smtp_port']
        # erp_use_tls = request.POST['erp_use_tls']
        # if erp_use_tls == 'on':
        #     erp_use_tls = True
        # else:
        #     erp_use_tls = False
        # erp_use_ssl = request.POST.get('erp_use_ssl')
        # if erp_use_ssl == 'on':
        #     erp_use_ssl = True
        # else:
        #     erp_use_ssl = False
        # erp_imap_server = request.POST['erp_imap_server']
        # erp_imap_port = request.POST['erp_imap_port']
        # erp_stripe_account_id = encrypt_data(request.POST['erp_stripe_account_id'])
        # erp_stripe_access_key = encrypt_data(request.POST['erp_stripe_access_key'])
        # erp_stripe_api_secret = encrypt_data(request.POST['erp_stripe_api_secret'])
        # erp_shipper_name = request.POST['erp_shipper_name']
        # erp_shipper_api_key = encrypt_data(request.POST['erp_shipper_api_key'])
        # erp_shipper_api_secret = encrypt_data(request.POST['erp_shipper_api_secret'])
        # erp_whatsup_api_url = request.POST['erp_whatsup_api_url']
        # erp_whatsup_api_token = encrypt_data(request.POST['erp_whatsup_api_token'])
        # erp_whatsup_version = request.POST['erp_whatsup_version']
        # erp_whatsup_phone_id = request.POST['erp_whatsup_phone_id']
        # erp_whatsup_business_id = request.POST['erp_whatsup_business_id']
        #
        #
        # s_in = SubscriptionInformation.objects.get(id = sub_id)
        # # Save data to the database
        # ei = Erp_Information(
        #     subscription_info = s_in,
        #     erp_name=erp_name,
        #     erp_site_name=erp_site_name,
        #     erp_admin_user_name=erp_admin_user_name,
        #     erp_admin_pw_encrypted="erp_admin_pw",
        #     erp_api_key_encrypted=erp_api_key,
        #     erp_api_secret_encrypted=erp_api_secret,
        #     erp_page_about_us_content=erp_page_about_us_content,
        #     erp_page_contact_us_content=erp_page_contact_us_content,
        #     erp_pages_root_email=erp_pages_root_email,
        #     erp_pages_root_email_pw_encrypted=erp_pages_root_email_pw,
        #     erp_country=erp_country,
        #     erp_timezone=erp_timezone,
        #     erp_contact_phone=erp_contact_phone,
        #     erp_contact_email=erp_contact_email,
        #     erp_whatsapp_phone=erp_whatsapp_phone,
        #     erp_email_account_name=erp_email_account_name,
        #     erp_email_id=erp_email_id,
        #     erp_email_account_password_encrypted=erp_email_account_password,
        #     erp_smtp_server=erp_smtp_server,
        #     erp_smtp_port=erp_smtp_port,
        #     erp_use_tls=erp_use_tls,
        #     erp_use_ssl=erp_use_ssl,
        #     erp_imap_server=erp_imap_server,
        #     erp_imap_port=erp_imap_port,
        #     erp_stripe_account_id_encrypted=erp_stripe_account_id,
        #     erp_stripe_access_key_encrypted=erp_stripe_access_key,
        #     erp_stripe_api_secret_encrypted=erp_stripe_api_secret,
        #     erp_shipper_name=erp_shipper_name,
        #     erp_shipper_api_key_encrypted=erp_shipper_api_key,
        #     erp_shipper_api_secret_encrypted=erp_shipper_api_secret,
        #     erp_whatsup_api_url=erp_whatsup_api_url,
        #     erp_whatsup_api_token_encrypted=erp_whatsup_api_token,
        #     erp_whatsup_version=erp_whatsup_version,
        #     erp_whatsup_phone_id=erp_whatsup_phone_id,
        #     erp_whatsup_business_id=erp_whatsup_business_id,
        # )
        # ei.save()

        return redirect('home_info')  # Redirect to success page

    return render(request, 'erp_info_form.html')



from subscription_app.service import create_stripe_product_and_price, create_stripe_customer, create_subscription, create_payment_intent

import stripe
def s_c(request):
    product_name = 'Custom Analytics Service'
    unit_price = 300.0  # Total price of the product
    upfront_payment = 200.0  # Amount to be paid upfront/now
    installment_amount = 50.0  # Amount of each installment
    currency = 'usd'
    interval = 'month'  # Monthly billing

    email = "m@gmail.com"
    name = "M"
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
                return HttpResponse(
                    f"Product ID: {product_id}, Price ID: {price_id}, Customer: {customer_id}, Subscription: {subscription.id}")
            else:
                return HttpResponse("Failed to collect upfront payment.")
        else:
            return HttpResponse("Failed to create customer.")
    else:
        return HttpResponse("Failed to create Product and Price.")


import xmlrpc.client


def create_company_and_website(url, db, username, password, company_data, website_data):
    """
    Connects to the Odoo server and creates a new company and a website for that company.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username for authentication.
        password (str): Password for authentication.
        company_data (dict): A dictionary containing the company data.
        website_data (dict): A dictionary containing the website data linked to the new company.

    Returns:
        dict: IDs of the created company and website.
    """
    # Authenticate
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})

    # Object proxy
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Create a new company
    try:
        company_id = models.execute_kw(db, uid, password, 'res.company', 'create', [company_data])
        print("New company created with ID:", company_id)
    except Exception as e:
        ee = str(e)
        return ee

    # Create a website for the new company
    website_data['company_id'] = company_id
    website_data['domain'] = "http://127.0.0.1:8069/oo1"
    try:
        website_id = models.execute_kw(db, uid, password, 'website', 'create', [website_data])
        print("New website created for the company with ID:", website_id)
    except Exception as e:
        ee = str(e)
        return ee

    return (company_id,  website_id)

def odooo_company_and_website_create(request) :
    # Odoo server information for local use
    url = 'http://127.0.0.1:8069'  # Default Odoo XML-RPC port is 8069
    db = 'odoo'
    username = 'admin@gmail.com'
    password = 'admin'

    # Data for the new company
    company_data = {
        'name': 'abdur company 122333po11',
        'street': '123 Local Street',
        'city': 'Local City',
        'zip': '12345',
        'country_id': 110,  # Assuming the country ID is known and correct
        'phone': '+1234567890',
        'email': 'info@newlocalcompany.com',
        # 'website': 'http://www.newlocalcompany.com'
        'website': 'http://127.0.0.1:8069/122333po11'
    }

    # Data for the new website
    website_data = {
        'name': 'abdur website 122333po11 web',
        # 'url': 'http://www.newlocalcompany.com'
        # 'url': 'http://127.0.0.1:8069'
    }

    # Create the company and the website
    result = create_company_and_website(url, db, username, password, company_data, website_data)
    print("Created entries:", result)
    return HttpResponse(result)





def get_security_groups(url, db, username, password):
    """
    Retrieves all security groups from Odoo.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username for authentication.
        password (str): Password for authentication.

    Returns:
        list: A list of dictionaries, each representing a security group.
    """
    # Authenticate
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})

    # Object proxy
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Search and read security groups
    group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [[]])
    groups = models.execute_kw(db, uid, password, 'res.groups', 'read',
                               [group_ids, ['name', 'display_name', 'comment']])

    return groups

def odoo_models(request):
    # Odoo server information
    url = 'http://127.0.0.1:8069'  # Default Odoo XML-RPC port is 8069
    db = 'odoo'
    username = 'admin@gmail.com'
    password = 'admin'

    # Retrieve and print all security groups
    security_groups = get_security_groups(url, db, username, password)
    for group in security_groups:
        print(
            f"Name: {group['name']}, Display Name: {group['display_name']}, Description: {group.get('comment', 'No description provided')}")

    return HttpResponse('DONE')


import xmlrpc.client
import base64


def update_company_logo(url, db, username, password, image_path):
    """
    Update the company's logo in Odoo via XML-RPC.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username of the admin user.
        password (str): Password of the admin user.
        image_path (str): Path to the new logo image file.
    """
    # Connect to the common login service
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    # Connect to the object service
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    try:
        # Read image and encode to base64
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Get company id, usually the first company (id=1)
        company_ids = models.execute_kw(db, uid, password, 'res.company', 'search', [[]])
        if not company_ids:
            print("No company found.")
            return

        # Update the company's logo
        if models.execute_kw(db, uid, password, 'res.company', 'write', [company_ids, {'logo': image_base64}]):
            print("Company logo updated successfully.")
            return ('Company logo updated successfully.')
        else:
            print("Failed to update company logo.")
            return ('Failed to update company logo.')
    except Exception as e:
        dd = str(e)


import os
from django.conf import settings
def odoo_company_image_upload(request):

    ODOO_URL = 'http://localhost:8069'
    DB_NAME = 'odoo'
    ADMIN_USERNAME = 'admin@gmail.com'
    ADMIN_PASSWORD = 'admin'
    IMAGE_PATH2 ='img/logo.png'  # Path to the logo image file
    IMAGE_PATH = os.path.join(settings.BASE_DIR, 'static/img/logo.png')

    # FULL_IMAGE_PATH = '/home/sohel/Desktop/kintah/static/img/logo.png'


    # Update the logo
    res = update_company_logo(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, IMAGE_PATH)

    return HttpResponse(res)


import xmlrpc.client


def create_odoo_user(url, db, username, password, user_data):
    """
    Create a new user in Odoo via XML-RPC.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username of the admin user.
        password (str): Password of the admin user.
        user_data (dict): A dictionary containing the new user's data.
    """
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Create a new user
        user_id = models.execute_kw(db, uid, password, 'res.users', 'create', [user_data])

        # Retrieve information about the created user
        user_info = models.execute_kw(db, uid, password, 'res.users', 'read', [[user_id]])

        if user_id:
            print(f"User created successfully with ID: {user_id}")
            return ('User created')
        else:
            print("Failed to create user.")
            return ('User is not created')
    except Exception as e:
        return str(e)


def create_new_odoo_user(request):
    # Configuration
    ODOO_URL = 'http://localhost:8069'
    DB_NAME = 'odoo'
    ADMIN_USERNAME = 'admin@gmail.com'
    ADMIN_PASSWORD = 'admin'

    # New user information
    new_user_data = {
        'name': 'John Doe 3',  # Full name of the user
        'login': 'john.doe3',  # Login username
        'email': 'john3@example.com',  # Email address
        'password': 'user_password2',  # Password (consider using a strong password)
        'groups_id': [(6, 0, [12])]  # Optional: Assign groups, replace 12 with actual group ID
    }

    # Create a new user
    res = create_odoo_user(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, new_user_data)

    return HttpResponse(res)


import xmlrpc.client


def assign_role_to_user(url, db, username, password, user_login, group_external_id):
    """
    Assign a role (group) to an existing user in Odoo via XML-RPC.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username of the admin user.
        password (str): Password of the admin user.
        user_login (str): The login of the user to whom the role will be assigned.
        group_external_id (str): The external ID of the group (role).
    """
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Find the group using its external ID
        group_ids = models.execute_kw(db, uid, password, 'ir.model.data', 'search',
                                      [[['module', '=', 'base'], ['name', '=', group_external_id]]])
        if not group_ids:
            print(f"No group found with external ID '{group_external_id}'.")
            return

        # Get the actual group ID from the ir.model.data record
        group = models.execute_kw(db, uid, password, 'ir.model.data', 'read', [group_ids, ['res_id']])
        if not group:
            print("Failed to read group details.")
            return
        group_id = group[0]['res_id']

        # Find the user by their login
        user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[['login', '=', user_login]]])
        if not user_ids:
            print(f"User with login '{user_login}' not found.")
            return

        # Assign the group to the user
        if models.execute_kw(db, uid, password, 'res.users', 'write', [user_ids, {'groups_id': [(4, group_id)]}]):
            print(f"User '{user_login}' has been added to the group '{group_external_id}'.")
            return ('role added')
        else:
            print("Failed to assign the group to the user.")
            return ('Failed to add role')
    except Exception as e:
        return str(e)


def change_user_rol(request):
    # Configuration
    ODOO_URL = 'http://localhost:8069'
    DB_NAME = 'odoo'
    ADMIN_USERNAME = 'admin@gmail.com'
    ADMIN_PASSWORD = 'admin'
    USER_LOGIN = 'john.doe'  # User login to whom the role will be assigned
    GROUP_EXTERNAL_ID = 'Editor and Designer'  # External ID of the group

    # Assign the role
    res = assign_role_to_user(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, USER_LOGIN, GROUP_EXTERNAL_ID)

    return HttpResponse(res)


import xmlrpc.client


def get_all_groups(url, db, username, password):
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Search for all groups and retrieve their IDs and names
        group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [[]])
        groups_data = models.execute_kw(db, uid, password, 'res.groups', 'read', [group_ids],
                                        {'fields': ['id', 'name']})

        # Print or return the groups data
        return groups_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)

def all_group(request):
    # Usage example
    ODOO_URL = 'http://localhost:8069'
    DB_NAME = 'odoo'
    ADMIN_USERNAME = 'admin@gmail.com'
    ADMIN_PASSWORD = 'admin'

    groups_data = get_all_groups(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD)
    if groups_data:
        for group in groups_data:
            print(f"Group ID: {group['id']}, Group Name: {group['name']}")
    else:
        print("Failed to retrieve group data.")
    return HttpResponse(groups_data)


import xmlrpc.client


def disable_odoo_user(url, db, username, password, user_login):
    """
    Disable an existing user in Odoo via XML-RPC by setting 'active' to False.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username of the admin user.
        password (str): Password of the admin user.
        user_login (str): The login of the user to be disabled.
    """
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Search for the user
        user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', [[['login', '=', user_login]]])

        # Disable the user if found
        if user_ids:
            models.execute_kw(db, uid, password, 'res.users', 'write', [user_ids, {'active': False}])
            print(f"User '{user_login}' has been disabled.")
            return ('user disable')
        else:
            print("User not found.")
            return ("User not found.")
    except Exception as e:
        return str(e)


def disable_odoo_user_info(request):
    # Configuration
    ODOO_URL = 'http://localhost:8069'
    DB_NAME = 'odoo'
    ADMIN_USERNAME = 'admin@gmail.com'
    ADMIN_PASSWORD = 'admin'
    USER_LOGIN = 'john.doe'  # User login to be disabled

    # Disable the user
    res = disable_odoo_user(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, USER_LOGIN)

    return HttpResponse(res)


#create product
import csv
import xmlrpc.client
import base64


def connect_to_odoo(url, db, username, password):
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return uid, models


def create_product(models, db, uid, password, product_data):
    product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [product_data])
    return product_id


def upload_product_images(models, db, uid, password, product_id, image_paths):
    for image_path in image_paths:
        f=5
        # image_path = "/home/sohel/Desktop/kintah/static/product_info/images/RAW_ABK-NVA-COS-SEL-41008_1.jpg"
        # image_path = '/home/sohel/Desktop/kintah/static/product_info/images/RAW_ABK-NVA-COS-SEL-41008_1.jpg'

        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            image_encoded = base64.b64encode(image_data).decode('utf-8')
            models.execute_kw(db, uid, password, 'product.image', 'create', [{
                'name': f'Image for product {product_id}',
                'image_1920': image_encoded,
                'product_tmpl_id': product_id
            }])


def create_product_categories_from_csv(url, db, username, password, csv_path):
    uid, models = connect_to_odoo(url, db, username, password)
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            category_data = {
                'name': row['Category Description'],
                'id': int(row['Category ID'])
            }
            try:
                category_id = models.execute_kw(db, uid, password, 'product.category', 'create', [category_data])
                print(f"Created category {row['Category Description']} with ID {category_id}.")
            except Exception as e:
                print(f"Failed to create category {row['Category Description']}: {str(e)}")


def populate_products_from_csv(url, db, username, password, csv_path, image_directory):
    uid, models = connect_to_odoo(url, db, username, password)
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_data = {
                'name': row['Product Name'],
                'default_code': row['SKU'],
                # 'type': row['Type'],
                'list_price': float(row['Price in Dollars']),
                # 'standard_price': float(row['Cost Price']),
                'standard_price': float(row['Price in Local Currency']),
                'categ_id': int(row['Category ID']),
                'description_sale': row['Sales Description'],
                'description': row['Product Description'],
                'weight': float(row.get('Weight', 0)),
                # 'volume': float(row.get('Volume', 0)),
                'active': row.get('Active', 'True').lower() in ('true', '1', 't')
            }
            product_id = create_product(models, db, uid, password, product_data)
            image_paths = [f"{image_directory}/images/{row['SKU']}_{i}.jpg" for i in range(1, 6)]
            try:
                upload_product_images(models, db, uid, password, product_id, image_paths)
            except Exception as e:
                ff= str(e)
            print(f"Product {row['Name']} with images has been created and associated.")


def update_website_page(models, db, uid, password, page_handle, content):
    """ Update a website page in Odoo via XML-RPC. """
    page_ids = models.execute_kw(db, uid, password, 'website.page', 'search', [[['url', '=', page_handle]]])
    if page_ids:
        models.execute_kw(db, uid, password, 'website.page', 'write', [page_ids, {'arch_base': content}])
        print(f"Updated page '{page_handle}' successfully.")
    else:
        print(f"No page found with URL handle '{page_handle}'. No updates made.")


def populate_ecommerce_pages(url, db, username, password, page_contents):
    """ Populate various ecommerce pages with given content. """
    uid, models = connect_to_odoo(url, db, username, password)
    for page_handle, content in page_contents.items():
        update_website_page(models, db, uid, password, page_handle, content)


def create_product_to_odoo(request):
    try:
        # Configuration
        ODOO_URL = 'http://localhost:8069'
        DB_NAME = 'odoo'
        USERNAME = 'admin@gmail.com'
        PASSWORD = 'admin'
        # IMAGE_PATH = os.path.join(settings.BASE_DIR, 'static/img/logo.png')
        PRODUCT_CSV_PATH = os.path.join(settings.BASE_DIR, 'static/product_info/raw_products.csv')
        # CATEGORY_CSV_PATH = 'path_to_your_category_csv_file.csv'
        CATEGORY_CSV_PATH = os.path.join(settings.BASE_DIR, 'static/product_info/caegory_csv.csv')
        IMAGE_LOCAL_DIR = os.path.join(settings.BASE_DIR, 'static/product_info')
        # Create categories
        try:
            res = create_product_categories_from_csv(ODOO_URL, DB_NAME, USERNAME, PASSWORD, CATEGORY_CSV_PATH)
        except Exception as e:
            d= str(e)
        try:
            # Populate products
            res = populate_products_from_csv(ODOO_URL, DB_NAME, USERNAME, PASSWORD, PRODUCT_CSV_PATH, IMAGE_LOCAL_DIR)
        except Exception as e:
            d= str(e)

        try:
            # Page content definitions
            page_contents = {
                '/about-us': '<p>This is the updated content for the About Us page.</p>',
                '/contact-us': '<p>Contact us at: <br>Phone: 123-456-7890<br>Email: info@example.com</p>',
                '/privacy-policy': '<p>This is the updated Privacy Policy page.</p>',
                '/terms-of-use': '<p>These are the updated Terms of Use.</p>'
            }

            # Update pages
            populate_ecommerce_pages(ODOO_URL, DB_NAME, USERNAME, PASSWORD, page_contents)

        except Exception as e:
            d = str(e)

    except Exception as e:
        d = str(e)
        return HttpResponse(str(e))










# test

import xmlrpc.client


import xmlrpc.client

def create_user_group_new(url, db, username, password, group_name):
    """
    Create a new user group in Odoo via XML-RPC or return the existing group ID if already created.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username of the admin user.
        password (str): Password of the admin user.
        group_name (str): Name of the user group to be created.

    Returns:
        int: ID of the user group (whether newly created or existing).
    """
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Search for the group by name
        group_ids = models.execute_kw(db, uid, password, 'res.groups', 'search', [[['name', '=', group_name]]])

        if group_ids:
            # Group with the same name already exists, return its ID
            group_id = group_ids[0]
            print(f"User group '{group_name}' already exists with ID {group_id}.")
            return group_id
        else:
            # Create the user group
            group_id = models.execute_kw(db, uid, password, 'res.groups', 'create', [{'name': group_name}])
            print(f"User group '{group_name}' created successfully with ID {group_id}.")
            return group_id
    except Exception as e:
        print(f"Failed to create or find user group '{group_name}': {e}")
        return str(e)

def assign_access_rights_to_all(url, db, username, password, group_name):
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service with allow_none enabled
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
        group_exist = models.execute_kw(db, uid, password, 'res.groups', 'search', [[['name', '=', group_name]]])
        if group_exist:
            return group_exist
        # Retrieve all modules using search_read
        all_modules = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read', [[]], {'fields': ['id', 'name']})

        for module in all_modules:
            module_name = module['name']
            module_id = module['id']

            # Retrieve all models in the module
            # model_ids = models.execute_kw(db, uid, password, 'ir.model', 'search', [[('module', '=', module_name)]])
            module_models = models.execute_kw(db, uid, password, 'ir.model', 'read', [module_id])

            for model in module_models:
                model_name = model['model']
                model_id = model['id']

                # Create the user group if it doesn't exist
                group_id = create_user_group_new(url, db, username, password, group_name)

                # Assign access rights to the user group for the model
                access_rights_data = {
                    'name': f"Access rights for {group_name} in model {model_name}",
                    'group_id': group_id,
                    'model_id': model_id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True,
                    # 'implied_ids': [(4, models.execute_kw(db, uid, password, 'res.groups', 'search',
                    #                                       [[('name', '=', 'Base')]])[0])],
                    # 'users': [(4, uid)],
                    # 'users_create': True,
                    # 'users_write': True,
                    # 'users_delete': True,
                }

                models.execute_kw(db, uid, password, 'ir.model.access', 'create', [access_rights_data])
        k=0
        k=0
        k=0
        print(f"Access rights assigned successfully to user group '{group_name}' for all modules and models.")
        return group_id
    except Exception as e:
        print(f"Failed to assign access rights: {e}")
        return str(e)


# def create_user_manager_role(request):
#     # Configuration
#     ODOO_URL = 'http://localhost:8069'
#     DB_NAME = 'odoo'
#     ADMIN_USERNAME = 'admin@gmail.com'
#     ADMIN_PASSWORD = 'admin'
#     GROUP_NAME = 'Manager'
#
#     # Assign access rights to all modules and models for the "Manager" user group
#     res = assign_access_rights_to_all(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, GROUP_NAME)


def create_odoo_user_with_manager_role(url, db, username, password, user_data, company_id, website_id, manager_group_id):
    """
    Create a new user for a specific company and website with the manager role in Odoo via XML-RPC.

    Args:
        url (str): URL of the Odoo server.
        db (str): Database name.
        username (str): Username of the admin user.
        password (str): Password of the admin user.
        user_data (dict): Data for creating the new user.
        company_id (int): ID of the company to assign the user.
        website_id (int): ID of the website to assign the user.
        manager_group_id (int): ID of the "Manager" group.
    """
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Create the new user
        # user_id = models.execute_kw(db, uid, password, 'res.users', 'create', [user_data])
        user_id = 45

        allow_company_res = models.execute_kw(db, uid, password, 'res.users', 'write', [[user_id], {
            'company_ids': [(4, company_id)]
        }])
        for i in manager_group_id:
            manager_group_id_without_list = i

        # Assign the user to the "Manager" group
        m_res = models.execute_kw(db, uid, password, 'res.users', 'write', [[user_id], {
            'groups_id': [(4, manager_group_id_without_list)]
        }])

        # Assign the user to the specified company and website
        s_c_w_res = models.execute_kw(db, uid, password, 'res.users', 'write', [[user_id], {
            'company_id': company_id,
            'website_id': website_id
        }])

        print(f"User '{user_data['login']}' created successfully with manager role for company ID {company_id} and website ID {website_id}.")
        return user_data
    except Exception as e:
        print(f"Failed to create user: {e}")
        return str(e)



def create_user_manager_role(request):
    # Configuration
    ODOO_URL = 'http://localhost:8069'
    DB_NAME = 'odoo'
    ADMIN_USERNAME = 'admin@gmail.com'
    ADMIN_PASSWORD = 'admin'
    GROUP_NAME = 'Manager'

    res = assign_access_rights_to_all(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, GROUP_NAME)

    # Group ID of the "Manager" group
    MANAGER_GROUP_ID = res  # Replace with the actual ID of the "Manager" group
    # MANAGER_GROUP_ID = [45]  # Replace with the actual ID of the "Manager" group

    # New user information
    new_user_data = {
        'name': 'John Doe 16',  # Full name of the user
        'login': 'john16.doe',  # Login username
        'email': 'john@example16.com',  # Email address
        'password': 'user_password',  # Password (consider using a strong password)
    }

    # ID of the company to assign the user
    # COMPANY_ID = 32  # Replace with the actual ID of the company
    COMPANY_ID = 35  # Replace with the actual ID of the company

    # ID of the website to assign the user
    # WEBSITE_ID = 13  # Replace with the actual ID of the website
    WEBSITE_ID = 15  # Replace with the actual ID of the website
    # w_res = get_website_info(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, WEBSITE_ID)
    # c_res = get_company_info(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, COMPANY_ID)
    w_u_res = get_website_url(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, WEBSITE_ID)
    # Create a new user with the manager role for the specified company and website
    cres = create_odoo_user_with_manager_role(ODOO_URL, DB_NAME, ADMIN_USERNAME, ADMIN_PASSWORD, new_user_data, COMPANY_ID, WEBSITE_ID, MANAGER_GROUP_ID)

    d=3
    d=3
    d=3
    d=3
    d=3
    # company_id=32, website_id=13
    return HttpResponse(cres)



def get_website_info(url, db, username, password, website_id):
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Retrieve website information by ID
        website_info = models.execute_kw(db, uid, password, 'website', 'read', [[website_id]])
        return website_info
    except Exception as e:
        print(f"Failed to retrieve website info: {e}")
        return None

def get_company_info(url, db, username, password, company_id):
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Retrieve company information by ID
        company_info = models.execute_kw(db, uid, password, 'res.company', 'read', [[company_id]])
        return company_info
    except Exception as e:
        print(f"Failed to retrieve company info: {e}")
        return None
def get_website_url(url, db, username, password, website_id):
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Connect to the object service
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        # Retrieve website information by ID
        website_info = models.execute_kw(db, uid, password, 'website', 'read', [[website_id]], {'fields': ['domain']})
        if website_info:
            return website_info[0]['domain']
        else:
            print("Website information not found.")
            return None
    except Exception as e:
        print(f"Failed to retrieve website URL: {e}")
        return None