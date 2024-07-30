import xmlrpc.client
from django.conf import settings




def install_the_modules(modules_list):
    k=0
    try:
        url = settings.ODOO_URL
        db = settings.DB_NAME
        username = settings.ADMIN_USERNAME
        password = settings.ADMIN_PASSWORD

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        # Function to set configuration parameters
        def set_param(key, value):
            models.execute_kw(db, uid, password, 'ir.config_parameter', 'set_param', [key, value])

        # Function to install modules
        # def install_module(module_name):
        #     models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [
        #         [models.execute_kw(db, uid, password, 'ir.module.module', 'search', [[('name', '=', module_name)]])]
        #     ])
        def install_module(module_name):
            module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
                                           [[('name', '=', module_name)]])
            if module_ids:
                models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [module_ids])
            else:
                print(f"Module {module_name} not found")

        modules = modules_list

        # c = [
        #     'sale_management', 'point_of_sale', 'crm', 'stock', 'purchase', 'website_sale',
        #     'payment', 'website_gift_card', 'sale_coupon', 'fleet', 'mass_mailing', 'sms',
        #     'social', 'hr', 'account_accountant', 'project', 'helpdesk', 'mail', 'barcodes', 'quality'
        # ]

        # Install all modules
        for module in modules:
            install_module(module)

            if module == 'sale_management':
                # Sale Management configuration
                set_param('sale.use_quotations', True)
                set_param('sale.sale_order_template', True)

            if module == 'point_of_sale':
                # Point of Sale configuration
                set_param('pos.iface_tax_included', True)
                set_param('pos.iface_tipproduct', True)

            if module == 'crm':
                # CRM configuration
                set_param('crm.use_leads', True)
                set_param('crm.use_opportunities', True)

            if module == 'stock':
                # Stock configuration
                set_param('stock.use_warehouse', True)
                set_param('stock.use_routing', True)

            if module == 'purchase':
                # Purchase configuration
                set_param('purchase.use_approval', True)
                set_param('purchase.use_three_way_matching', True)

            if module == 'website_sale':
                # Website Sale configuration
                set_param('website_sale.use_website_sale', True)
                set_param('website_sale.display_categories', True)

            if module == 'payment':
                # Payment configuration
                set_param('payment.use_payment_acquirers', True)

            if module == 'website_gift_card':
                # Website Gift Card configuration
                set_param('website_gift_card.use_gift_cards', True)

            if module == 'sale_coupon':
                # Sale Coupon configuration
                set_param('sale_coupon.use_coupons', True)

            if module == 'fleet':
                # Fleet configuration
                set_param('fleet.use_fleet_management', True)

            if module == 'mass_mailing':
                # Mass Mailing configuration
                set_param('mass_mailing.use_mass_mailing', True)

            if module == 'sms':
                # SMS configuration
                set_param('sms.use_sms_marketing', True)

            if module == 'social':
                # Social configuration
                set_param('social.use_social_media', True)

            if module == 'hr':
                # HR configuration
                set_param('hr.use_hr_payroll', True)
                set_param('hr.use_hr_attendance', True)

            if module == 'account_accountant':
                # Account Accountant configuration
                set_param('account_accountant.use_accounting', True)

            if module == 'project':
                # Project configuration
                set_param('project.use_project_management', True)

            if module == 'helpdesk':
                # Helpdesk configuration
                set_param('helpdesk.use_helpdesk', True)

            if module == 'mail':
                # Mail configuration
                set_param('mail.use_mail', True)
            if module == 'barcodes':
                # Barcodes configuration
                set_param('barcodes.use_barcodes', True)

            if module == 'quality':
                # Quality configuration
                set_param('quality.use_quality_checks', True)
        return ('Done')
    except Exception as e:
        print(f"Failed to install modules")
        return str(e)





# for mail cnfiguration

def configure_outgoing_mail_server(models, db, uid, password, email, email_password, email_service, company_id):
    if email_service == 'Google Workspace':
        smtp_host = 'smtp.gmail.com'
        smtp_port = 587
    elif email_service == 'Microsoft Exchange':
        smtp_host = 'smtp.office365.com'
        smtp_port = 587
    else:
        raise ValueError("Unsupported email service. Please use 'Google Workspace' or 'Microsoft Exchange'.")

    mail_server_values = {
        'name': f'{email_service} SMTP {email}',
        'smtp_host': smtp_host,
        'smtp_port': smtp_port,
        'smtp_user': email,
        'smtp_pass': email_password,
        'smtp_encryption': 'starttls',
        'sequence': 1,
        'active': True,
        # 'company_id': company_id,
    }
    # fields = models.execute_kw(db, uid, password, 'ir.mail_server', 'fields_get', [], {'attributes': ['string', 'help', 'type']})

    mail_server_id = models.execute_kw(db, uid, password, 'ir.mail_server', 'create', [mail_server_values])
    print(f"Outgoing Mail Server created with ID: {mail_server_id} for {email}")
    return mail_server_id

def configure_incoming_mail_server(models, db, uid, password, email, email_password, email_service, company_id):
    if email_service == 'Google Workspace':
        imap_host = 'imap.gmail.com'
        imap_port = 993
    elif email_service == 'Microsoft Exchange':
        imap_host = 'outlook.office365.com'
        imap_port = 993
    else:
        raise ValueError("Unsupported email service. Please use 'Google Workspace' or 'Microsoft Exchange'.")

    action_id = models.execute_kw(db, uid, password, 'ir.actions.server', 'search', [[['name', '=', 'Default action']]])

    fetchmail_server_values = {
        'name': f'{email_service} IMAP {email}',
        'server': imap_host,
        'port': imap_port,
        # 'type': 'imap',
        'is_ssl': True,
        'user': email,
        'password': email_password,
        # 'action_id': action_id[0] if action_id else False,
        'active': True,
        # 'company_id': company_id,
    }
    fields = models.execute_kw(db, uid, password, 'fetchmail.server', 'fields_get', [], {'attributes': ['string', 'help', 'type']})
    fetchmail_server_id = models.execute_kw(db, uid, password, 'fetchmail.server', 'create', [fetchmail_server_values])
    print(f"Incoming Mail Server created with ID: {fetchmail_server_id} for {email}")
    return fetchmail_server_id



def configure_mail(email, email_service, email_password, employee_type, company_id):
    url = settings.ODOO_URL
    db = settings.DB_NAME
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD

    try:

        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise Exception("Authentication failed")

        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')


        email_service = email_service
        email_password = email_password
        company_id = company_id
        # email = f'support@{client_domain}'
        email = email

        # Configure email servers in Odoo for the client
        res1 = configure_outgoing_mail_server(models, db, uid, password, email, email_password, email_service, company_id)
        res2 = configure_incoming_mail_server(models, db, uid, password, email, email_password, email_service, company_id)
        return res1, res2
    except xmlrpc.client.Fault as fault:
            return fault.faultString, 'Not Done'



