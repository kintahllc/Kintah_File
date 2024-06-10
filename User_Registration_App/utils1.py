import csv
import odoorpc
import os
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings


import xmlrpc.client
from django.conf import settings
from io import TextIOWrapper


import csv
import odoorpc
import os
import boto3
from botocore.exceptions import NoCredentialsError



def upload_contacts_to_odoo(file, company_id, website_id, db, username, password, url):
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        # Check if authentication was successful
        if uid:
            print("Authentication successful. UID:", uid)

            # Connect to the object service
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            # Assuming 'file' is a CSV file uploaded using Django's request.FILES
            # Assuming 'company_id' and 'website_id' are provided

            print("Authentication successful. UID:", uid)

            # Open the CSV file in text mode using TextIOWrapper
            # Open the CSV file in text mode using TextIOWrapper
            csv_file_text = TextIOWrapper(file, encoding='utf-8')

            # Reset the file pointer to the beginning of the file
            csv_file_text.seek(0)

            # Create a CSV reader
            csv_reader = csv.reader(csv_file_text)

            # Read the header row
            header = next(csv_reader)

            # Map header to field names
            field_names = [
                'name', 'company_name', 'parent_id', 'type', 'email', 'phone', 'mobile', 'street', 'street2',
                'city', 'state_id', 'zip', 'country_id', 'title', 'function', 'website', 'comment', 'customer_rank',
                'supplier_rank', 'is_company', 'vat', 'lang', 'active', 'category_id', 'bank_ids'
            ]

            for row in csv_reader:
                # Prepare contact data
                contact_data = dict(zip(field_names, row))
                contact_data['parent_id'] = int(contact_data['parent_id']) if contact_data.get('parent_id') else False
                contact_data['state_id'] = int(contact_data['state_id']) if contact_data.get('state_id') else False
                contact_data['country_id'] = int(contact_data['country_id']) if contact_data.get(
                    'country_id') else False
                contact_data['title'] = int(contact_data['title']) if contact_data.get('title') else False
                contact_data['customer_rank'] = int(contact_data['customer_rank']) if contact_data.get(
                    'customer_rank') else 0
                contact_data['supplier_rank'] = int(contact_data['supplier_rank']) if contact_data.get(
                    'supplier_rank') else 0
                contact_data['is_company'] = contact_data.get('is_company', 'False').lower() in ('true', '1')
                contact_data['active'] = contact_data.get('active', 'True').lower() in ('true', '1')
                contact_data['category_id'] = [
                    (6, 0, [int(cat) for cat in contact_data['category_id'].split(',')])] if contact_data.get(
                    'category_id') else False
                contact_data['bank_ids'] = [(0, 0, {
                    'acc_number': contact_data.get('bank_account'),
                    'bank_id': int(contact_data['bank_id']) if contact_data.get('bank_id') else False,
                })] if contact_data.get('bank_account') else False

                contact_data['company_id'] = company_id
                contact_data['website_id'] = website_id

                # Create or update contact in Odoo
                contact_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [contact_data])
                return 'CSV upload successfully'


    except xmlrpc.client.Fault as fault:
        return fault.faultString


def upload_contacts_to_odoo_here(file, company_id, website_id):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    res = upload_contacts_to_odoo(file, company_id, website_id, db, username, password, url)

    return res





def upload_employees_to_odoo(file, company_id, website_id, db, username, password, url):
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        if uid:
            print("Authentication successful. UID:", uid)

            # Connect to the object service
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

            # Open the CSV file in text mode using TextIOWrapper
            csv_file_text = TextIOWrapper(file, encoding='utf-8')
            csv_file_text.seek(0)  # Reset the file pointer to the beginning of the file

            # Create a CSV reader
            csv_reader = csv.reader(csv_file_text)
            header = next(csv_reader)

            # Define field names
            field_names = [
                'name', 'work_email', 'work_phone', 'mobile_phone', 'work_location', 'job_id', 'department_id',
                'manager_id', 'address_home_id', 'country_id', 'identification_id', 'passport_id', 'gender',
                'marital', 'birthday', 'place_of_birth', 'children', 'notes', 'work_address_id', 'barcode', 'pin',
                'active', 'visa_no', 'permit_no', 'visa_expire', 'certificate', 'study_field', 'study_school',
                'emergency_contact', 'emergency_phone'
            ]

            # Read and process each row in the CSV file
            for row in csv_reader:
                employee_data = dict(zip(field_names, row))
                employee_data['job_id'] = int(employee_data['job_id']) if employee_data['job_id'] else False
                employee_data['department_id'] = int(employee_data['department_id']) if employee_data['department_id'] else False
                employee_data['manager_id'] = int(employee_data['manager_id']) if employee_data['manager_id'] else False
                employee_data['address_home_id'] = int(employee_data['address_home_id']) if employee_data['address_home_id'] else False
                employee_data['country_id'] = int(employee_data['country_id']) if employee_data['country_id'] else False
                employee_data['children'] = int(employee_data['children']) if employee_data['children'] else 0
                employee_data['work_address_id'] = int(employee_data['work_address_id']) if employee_data['work_address_id'] else False
                employee_data['active'] = employee_data['active'].lower() in ('true', '1')
                employee_data['company_id'] = company_id
                employee_data['website_id'] = website_id

                # Create or update employee in Odoo
                employee_id = models.execute_kw(db, uid, password, 'hr.employee', 'create', [employee_data])
            return 'CSV upload successfully'

    except xmlrpc.client.Fault as fault:
        return fault.faultString

def upload_employees_to_odoo_here(file, company_id, website_id):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    res = upload_employees_to_odoo(file, company_id, website_id, db, username, password, url)
    return res



def upload_suppliers_to_odoo(file, company_id, website_id, db, username, password, url):
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        if uid:
            print("Authentication successful. UID:", uid)

            # Connect to the object service
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

            # Open the CSV file in text mode using TextIOWrapper
            csv_file_text = TextIOWrapper(file, encoding='utf-8')
            csv_file_text.seek(0)  # Reset the file pointer to the beginning of the file

            # Create a CSV reader
            csv_reader = csv.reader(csv_file_text)
            header = next(csv_reader)

            # Map header to field names (adjust fields as needed for suppliers)
            field_names = [
                'name', 'company_name', 'parent_id', 'type', 'email', 'phone', 'mobile', 'street', 'street2',
                'city', 'state_id', 'zip', 'country_id', 'title', 'function', 'website', 'comment', 'supplier_rank',
                'is_company', 'vat', 'lang', 'active', 'category_id', 'bank_ids'
            ]

            # List of valid language codes (this is a sample, you may need to adjust based on your needs)
            valid_languages = ['en_US', 'fr_FR', 'es_ES', 'de_DE']

            for row in csv_reader:
                supplier_data = dict(zip(field_names, row))
                supplier_data['parent_id'] = int(supplier_data['parent_id']) if supplier_data.get('parent_id') else False
                supplier_data['state_id'] = int(supplier_data['state_id']) if supplier_data.get('state_id') else False
                supplier_data['country_id'] = int(supplier_data['country_id']) if supplier_data.get('country_id') else False
                supplier_data['title'] = int(supplier_data['title']) if supplier_data.get('title') else False
                supplier_data['supplier_rank'] = int(supplier_data['supplier_rank']) if supplier_data.get('supplier_rank') else 0
                supplier_data['is_company'] = supplier_data.get('is_company', 'False').lower() in ('true', '1')
                supplier_data['active'] = supplier_data.get('active', 'True').lower() in ('true', '1')
                supplier_data['category_id'] = [
                    (6, 0, [int(cat) for cat in supplier_data['category_id'].split(',') if cat.isdigit()])] if supplier_data.get('category_id') else False
                supplier_data['bank_ids'] = [(0, 0, {
                    'acc_number': supplier_data.get('bank_account'),
                    'bank_id': int(supplier_data['bank_id']) if supplier_data.get('bank_id') else False,
                })] if supplier_data.get('bank_account') else False

                # Validate language code
                supplier_data['lang'] = supplier_data['lang'] if supplier_data['lang'] in valid_languages else 'en_US'

                supplier_data['company_id'] = company_id
                supplier_data['website_id'] = website_id

                # Create or update supplier in Odoo
                supplier_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [supplier_data])
            return 'CSV upload successfully'

    except xmlrpc.client.Fault as fault:
        return fault.faultString

def upload_suppliers_to_odoo_here(file, company_id, website_id):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    res = upload_suppliers_to_odoo(file, company_id, website_id, db, username, password, url)
    return res



def upload_fleet_assets_to_odoo(file, company_id, website_id, db, username, password, url):
    try:
        # Connect to the common login service
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        if uid:
            print("Authentication successful. UID:", uid)

            # Connect to the object service
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

            # Open the CSV file in text mode using TextIOWrapper
            csv_file_text = TextIOWrapper(file, encoding='utf-8')
            csv_file_text.seek(0)  # Reset the file pointer to the beginning of the file

            # Create a CSV reader
            csv_reader = csv.reader(csv_file_text)
            header = next(csv_reader)

            # Map header to field names
            field_names = [
                'name', 'license_plate', 'vin_sn', 'driver_id', 'model_id', 'odometer', 'odometer_unit',
                'acquisition_date', 'car_value', 'state_id', 'location', 'color', 'seats', 'doors',
                'transmission', 'fuel_type', 'horsepower', 'horsepower_tax', 'power', 'co2', 'notes', 'active'
            ]

            # Read and process each row in the CSV file
            for row in csv_reader:
                fleet_asset_data = dict(zip(field_names, row))
                fleet_asset_data['driver_id'] = int(fleet_asset_data['driver_id']) if fleet_asset_data['driver_id'].isdigit() else False
                fleet_asset_data['model_id'] = int(fleet_asset_data['model_id']) if fleet_asset_data['model_id'].isdigit() else False
                fleet_asset_data['odometer'] = float(fleet_asset_data['odometer']) if fleet_asset_data['odometer'].replace('.', '', 1).isdigit() else 0.0
                fleet_asset_data['car_value'] = float(fleet_asset_data['car_value']) if fleet_asset_data['car_value'].replace('.', '', 1).isdigit() else 0.0
                fleet_asset_data['state_id'] = int(fleet_asset_data['state_id']) if fleet_asset_data['state_id'].isdigit() else False
                fleet_asset_data['seats'] = int(fleet_asset_data['seats']) if fleet_asset_data['seats'].isdigit() else 0
                fleet_asset_data['doors'] = int(fleet_asset_data['doors']) if fleet_asset_data['doors'].isdigit() else 0
                fleet_asset_data['horsepower'] = int(fleet_asset_data['horsepower']) if fleet_asset_data['horsepower'].isdigit() else 0
                fleet_asset_data['horsepower_tax'] = float(fleet_asset_data['horsepower_tax']) if fleet_asset_data['horsepower_tax'].replace('.', '', 1).isdigit() else 0.0
                fleet_asset_data['power'] = float(fleet_asset_data['power']) if fleet_asset_data['power'].replace('.', '', 1).isdigit() else 0.0
                fleet_asset_data['co2'] = float(fleet_asset_data['co2']) if fleet_asset_data['co2'].replace('.', '', 1).isdigit() else 0.0
                fleet_asset_data['active'] = fleet_asset_data.get('active', 'True').lower() in ('true', '1')
                fleet_asset_data['company_id'] = company_id
                fleet_asset_data['website_id'] = website_id

                # Create or update fleet asset in Odoo
                fleet_asset_id = models.execute_kw(db, uid, password, 'fleet.vehicle', 'create', [fleet_asset_data])
            return 'CSV upload successfully'

    except xmlrpc.client.Fault as fault:
        return fault.faultString


def upload_fleet_assets_to_odoo_here(file, company_id, website_id):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    res = upload_fleet_assets_to_odoo(file, company_id, website_id, db, username, password, url)
    return res


import time


def install_module(url, db, username, password, module_name):
    """Install a module and handle dependencies."""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [[('name', '=', module_name)]])
    if not module_ids:
        raise Exception(f"Module {module_name} not found.")

    state = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [module_ids, ['state']])
    if state and state[0]['state'] == 'installed':
        print(f"Module {module_name} is already installed.")
        # return True

    if state[0]['state'] == 'uninstallable':
        print(f"Module {module_name} is uninstallable.")
        # return False

    # Get module dependencies
    dependencies = models.execute_kw(db, uid, password, 'ir.module.module.dependency', 'search_read', [[('module_id', 'in', module_ids)]], {'fields': ['name']})
    for dependency in dependencies:
        p = f"Installing dependency: {dependency['name']}"
        install_module(url, db, username, password, dependency['name'])

    # Install the module
    models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [module_ids])

    # Wait for the module installation to complete
    for _ in range(30):
        state = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [module_ids, ['state']])
        if state and state[0]['state'] == 'installed':
            pp = f"Module {module_name} installed successfully."
            # return True
        time.sleep(1)

    raise Exception(f"Failed to install module {module_name}.")



def enable_full_accounting_features(url, db, username, password, company_id):
    """Enable full accounting features in developer mode."""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Enable developer mode for full accounting features
    config_settings_id = models.execute_kw(db, uid, password, 'res.config.settings', 'create', [{
        'company_id': company_id,
        'module_account': True  # Enable the accounting module
    }])
    models.execute_kw(db, uid, password, 'res.config.settings', 'execute', [config_settings_id])

    # Verify if the accounting features are enabled
    settings = models.execute_kw(db, uid, password, 'res.config.settings', 'read', [config_settings_id])
    if settings and settings[0].get('module_account'):
        print("Accounting features enabled successfully.")
    else:
        print("Failed to enable accounting features.")
        raise Exception("Failed to enable accounting features.")

    return 'Accounting features enabled'


def configure_accounting(
        url, db, username, password, company_id,
        fiscal_year_name, fiscal_year_start, fiscal_year_end, income_tax_name, income_tax_rate,
        bank_name, bank_street, bank_city, bank_state, bank_zip, bank_country, bank_phone,
        bank_account_number, sales_tax_name, sales_tax_rate, chart_template_name
):
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Create a fiscal year
    fiscal_year = models.execute_kw(db, uid, password, 'account.fiscal.year', 'create', [{
        'name': fiscal_year_name,
        'date_from': fiscal_year_start,
        'date_to': fiscal_year_end,
        'company_id': company_id
    }])
    # Verify if the fiscal year is created
    if fiscal_year:
        print("Fiscal year created successfully.")
    else:
        raise Exception("Failed to create fiscal year.")

    # Create an income tax
    income_tax = models.execute_kw(db, uid, password, 'account.tax', 'create', [{
        'name': income_tax_name,
        'amount': income_tax_rate,
        'type_tax_use': 'sale',
        'company_id': company_id
    }])
    # Verify if the income tax is created
    if income_tax:
        print("Income tax created successfully.")
    else:
        raise Exception("Failed to create income tax.")

    # Add a bank account
    bank = models.execute_kw(db, uid, password, 'res.bank', 'create', [{
        'name': bank_name,
        'street': bank_street,
        'city': bank_city,
        'state': bank_state,
        'zip': bank_zip,
        'country': bank_country,
        'phone': bank_phone
    }])
    # Verify if the bank is created
    if bank:
        print("Bank created successfully.")
    else:
        raise Exception("Failed to create bank.")

    bank_account = models.execute_kw(db, uid, password, 'res.partner.bank', 'create', [{
        'acc_number': bank_account_number,
        'partner_id': company_id,
        'bank_id': bank,
        'company_id': company_id
    }])
    # Verify if the bank account is created
    if bank_account:
        print("Bank account created successfully.")
    else:
        raise Exception("Failed to create bank account.")

    # Edit sales tax information
    sales_tax_ids = models.execute_kw(db, uid, password, 'account.tax', 'search', [[('name', '=', sales_tax_name)]])
    if sales_tax_ids:
        models.execute_kw(db, uid, password, 'account.tax', 'write', [sales_tax_ids, {'amount': sales_tax_rate}])
        # Verify if the sales tax is updated
        updated_tax = models.execute_kw(db, uid, password, 'account.tax', 'read', [sales_tax_ids, ['amount']])
        if updated_tax and updated_tax[0]['amount'] == sales_tax_rate:
            print("Sales tax updated successfully.")
        else:
            raise Exception("Failed to update sales tax.")
    else:
        raise Exception(f"Sales tax {sales_tax_name} not found.")

    # Select a chart of accounts
    chart_template_ids = models.execute_kw(db, uid, password, 'account.chart.template', 'search',
                                           [[('name', '=', chart_template_name)]])
    if chart_template_ids:
        models.execute_kw(db, uid, password, 'account.chart.template', 'load_for_current_company',
                          [chart_template_ids[0], company_id])
        # Verify if the chart of accounts is set
        company = models.execute_kw(db, uid, password, 'res.company', 'read', [company_id, ['chart_template_id']])
        if company and company[0]['chart_template_id'][0] == chart_template_ids[0]:
            print("Chart of accounts set successfully.")
        else:
            raise Exception("Failed to set chart of accounts.")
    else:
        raise Exception(f"Chart template {chart_template_name} not found.")

    print("Configuration completed successfully!")
    return 'Configuration completed successfully!'


def accounting_here(
        company_id, website_id, fiscal_year_name, fiscal_year_start, fiscal_year_end,
        income_tax_name, income_tax_rate, bank_name, bank_street, bank_city, bank_state,
        bank_zip, bank_country, bank_phone, bank_account_number, sales_tax_name,
        sales_tax_rate, chart_template_name
):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    try:
        # Install necessary modules
        modules_to_install = ['account_accountant']
        for module in modules_to_install:
            install_module(url, db, username, password, module)

        # Enable full accounting features
        enable_full_accounting_features(url, db, username, password, company_id)

        # Configure accounting settings
        configure_accounting(
            url, db, username, password, company_id,
            fiscal_year_name=fiscal_year_name,
            fiscal_year_start=fiscal_year_start,
            fiscal_year_end=fiscal_year_end,
            income_tax_name=income_tax_name,
            income_tax_rate=income_tax_rate,
            bank_name=bank_name,
            bank_street=bank_street,
            bank_city=bank_city,
            bank_state=bank_state,
            bank_zip=bank_zip,
            bank_country=bank_country,
            bank_phone=bank_phone,
            bank_account_number=bank_account_number,
            sales_tax_name=sales_tax_name,
            sales_tax_rate=sales_tax_rate,
            chart_template_name=chart_template_name
        )
        return 'DONE'
    except Exception as e:
        return str(e)

# Example usage:




def configure_manual_shipping(url, db, username, password, company_id, website_id, shipping_name, product_id, fixed_price, margin, sequence=10, delivery_type='fixed'):
    try:
        """Configure manual shipping in Odoo using XML-RPC."""
        # Connect to the Odoo server
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise Exception("Authentication failed")

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        # Check if the delivery method already exists
        delivery_carrier_ids = models.execute_kw(db, uid, password, 'delivery.carrier', 'search', [
            [('name', '=', shipping_name), ('company_id', '=', company_id), ('website_id', '=', website_id)]
        ])

        carrier_vals = {
            'name': shipping_name,
            'product_id': product_id,
            'delivery_type': delivery_type,
            'fixed_price': fixed_price,
            'margin': margin,
            'sequence': sequence,
            'active': True,
            'company_id': company_id,
            'website_id': website_id
        }

        if delivery_carrier_ids:
            models.execute_kw(db, uid, password, 'delivery.carrier', 'write', [delivery_carrier_ids, carrier_vals])
            print(f"{shipping_name} shipping method updated successfully!")
        else:
            models.execute_kw(db, uid, password, 'delivery.carrier', 'create', [carrier_vals])
            return (f"'{shipping_name}' shipping method created successfully!")
    except Exception as e:
        return str(e)

def setup_manual_shipping(company_id, website_id, shipping_name, product_id, fixed_price, margin, sequence):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    # Shipping method configuration
    # company_id = 1  # Replace with your actual company ID
    # website_id = 1  # Replace with your actual website ID
    # shipping_name = 'Manual Shipping'
    # product_id = 1  # Replace with your actual shipping product ID
    # fixed_price = 10.0  # Example fixed price
    # margin = 0.0  # Example margin
    # free_if_more_than = 50.0  # Example free shipping threshold
    # sequence = 10  # Example sequence

    res = configure_manual_shipping(url, db, username, password, company_id, website_id, shipping_name, product_id, fixed_price, margin, sequence)
    return res


def set_website_languages_here(url, db, username, password, company_id, website_id, languages):
    # Initialize the connection to the Odoo server
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("Authentication failed")

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Ensure languages is a list
    if isinstance(languages, str):
        languages = languages.split(',')

    # Check if the languages are installed
    installed_langs = models.execute_kw(db, uid, password, 'res.lang', 'search_read',
                                        [[('code', 'in', languages)]], {'fields': ['code']})
    installed_lang_codes = [lang['code'] for lang in installed_langs]

    # Install the languages if they are not already installed
    for lang in languages:
        if lang not in installed_lang_codes:
            models.execute_kw(db, uid, password, 'base.language.install', 'create', [{'lang': lang}])
            installed_lang_codes.append(lang)
            print(f"Language {lang} installed.")

    # Update the website with the installed languages
    lang_ids = models.execute_kw(db, uid, password, 'res.lang', 'search', [[('code', 'in', installed_lang_codes)]])
    website_update_vals = {'language_ids': [(6, 0, lang_ids)]}
    models.execute_kw(db, uid, password, 'website', 'write', [[website_id], website_update_vals])
    return f"Website {website_id} updated with languages: {installed_lang_codes}"



def set_website_languages(company_id, website_id, languages):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    try:
        res = set_website_languages_here(url, db, username, password, company_id, website_id, languages)
        return res
    except Exception as e:
        return str(e)


def configure_whatsapp_service(url, db, username, password, company_id, website_id, twilio_account_sid, twilio_auth_token, twilio_whatsapp_number):
    """Configure the WhatsApp service in Odoo using Twilio for a specific company and website."""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("Authentication failed")

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Create WhatsApp Gateway
    gateway_id = models.execute_kw(db, uid, password, 'sms.gateway', 'create', [{
        'name': 'Twilio WhatsApp Gateway',
        'gateway_url': 'https://api.twilio.com/2010-04-01/Accounts',
        'method': 'http',
        'state': 'test',
        'from_mobile': f'whatsapp:{twilio_whatsapp_number}',
        'company_id': company_id,
        'website_id': website_id
    }])

    # Create WhatsApp Account
    models.execute_kw(db, uid, password, 'sms.account', 'create', [{
        'gateway_id': gateway_id,
        'name': 'Twilio WhatsApp Account',
        'account_sid': twilio_account_sid,
        'auth_token': twilio_auth_token,
        'number': f'whatsapp:{twilio_whatsapp_number}',
        'company_id': company_id,
        'website_id': website_id
    }])

    return "Twilio WhatsApp service configured successfully!"



def set_configure_whatsapp_service(company_id, website_id, twilio_account_sid, twilio_auth_token, twilio_whatsapp_number):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    try:
        res = configure_whatsapp_service(url, db, username, password, company_id, website_id, twilio_account_sid, twilio_auth_token, twilio_whatsapp_number)
        return res
    except xmlrpc.client.Fault as fault:
        return fault.faultString


def twilio_sms_config(url, db, username, password, company_id, website_id, twilio_account_sid, twilio_auth_token, twilio_sender_number):
    """Configure the SMS service in Odoo using Twilio for a specific company and website."""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("Authentication failed")

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Create SMS Gateway
    gateway_id = models.execute_kw(db, uid, password, 'sms.gateway', 'create', [{
        'name': 'Twilio SMS Gateway',
        'gateway_url': 'https://api.twilio.com/2010-04-01/Accounts',
        'method': 'http',
        'state': 'test',
        'from_mobile': twilio_sender_number,
        'company_id': company_id,
        'website_id': website_id
    }])

    # Create SMS Account
    models.execute_kw(db, uid, password, 'sms.account', 'create', [{
        'gateway_id': gateway_id,
        'name': 'Twilio SMS Account',
        'account_sid': twilio_account_sid,
        'auth_token': twilio_auth_token,
        'number': twilio_sender_number,
        'company_id': company_id,
        'website_id': website_id
    }])

    return "Twilio SMS service configured successfully!"

def set_twilio_sms_config(company_id, website_id, twilio_account_sid, twilio_auth_token, twilio_sender_number):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    try:
        res = twilio_sms_config(url, db, username, password, company_id, website_id, twilio_account_sid, twilio_auth_token, twilio_sender_number)
        return res
    except xmlrpc.client.Fault as fault:
        return fault.faultString


def configure_stripe_payment_provider(url, db, username, password, company_id, website_id, stripe_secret_key, stripe_publishable_key):
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("Authentication failed")

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Check if Stripe payment provider already exists for the company
    stripe_provider_id = models.execute_kw(db, uid, password, 'payment.acquirer', 'search',
                                           [[('provider', '=', 'stripe'), ('company_id', '=', company_id)]])

    if stripe_provider_id:
        # Update existing Stripe provider
        models.execute_kw(db, uid, password, 'payment.acquirer', 'write',
                          [[stripe_provider_id], {'stripe_secret_key': stripe_secret_key,
                                                  'stripe_publishable_key': stripe_publishable_key}])
    else:
        # Create new Stripe provider
        models.execute_kw(db, uid, password, 'payment.acquirer', 'create',
                          [{'name': 'Stripe',
                            'provider': 'stripe',
                            'state': 'enabled',
                            'company_id': company_id,
                            'website_id': website_id,
                            'stripe_secret_key': stripe_secret_key,
                            'stripe_publishable_key': stripe_publishable_key}])

    return "Stripe payment provider configured successfully!"



def configure_stripe_payment(company_id, website_id, stripe_secret_key, stripe_publishable_key):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    try:
        res = configure_stripe_payment_provider(url, db, username, password, company_id, website_id, stripe_secret_key, stripe_publishable_key)
        return res
    except xmlrpc.client.Fault as fault:
        return fault.faultString





def configure_paypal_payment_provider(url, db, username, password, company_id, website_id, paypal_email, paypal_seller_account):
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("Authentication failed")

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Check if PayPal payment provider already exists for the company
    paypal_provider_id = models.execute_kw(db, uid, password, 'payment.acquirer', 'search',
                                            [[('provider', '=', 'paypal'), ('company_id', '=', company_id)]])
    paypal_vals = {
        'name': 'PayPal',
        'provider': 'paypal',
        'state': 'enabled',
        'company_id': company_id,
        'website_id': website_id,
        'paypal_email_account': paypal_email,
        'paypal_seller_account': paypal_seller_account,
    }
    if paypal_provider_id:
        # Update existing PayPal provider
        models.execute_kw(db, uid, password, 'payment.acquirer', 'write', [paypal_provider_id, paypal_vals])
    else:
        # Create new PayPal provider
        models.execute_kw(db, uid, password, 'payment.acquirer', 'create', [paypal_vals])

    return "PayPal payment provider configured successfully!"


def configure_paypal_payment(company_id, website_id, paypal_email, paypal_seller_account):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    try:
        res = configure_paypal_payment_provider(url, db, username, password, company_id, website_id, paypal_email, paypal_seller_account)
        return res
    except xmlrpc.client.Fault as fault:
        return fault.faultString