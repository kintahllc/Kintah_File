
from django.urls import path
from . import views
from . import views2


urlpatterns = [
    
    path('', views.home, name='home'),
    path('registration/', views.index, name='index'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('set_new_password/', views.set_new_password, name='set_new_password'),
    path('home_info/', views.home_info, name='home_info'),
    path('login_info/', views.login_info, name='login_info'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('submit_subscription/', views.submit_subscription, name='submit_subscription'),

    path('Payment_Submit/', views.Payment_Submit, name='Payment_Submit'),
    path('Payment_Submit_for_upgrade/', views.Payment_Submit_for_upgrade, name='Payment_Submit_for_upgrade'),

    path('billing_history/<int:pk>', views.billing_history, name='billing_history'),
    path('ask_billing_question/<int:pk>', views.ask_billing_question, name='ask_billing_question'),
    path('update_company_info/<int:pk>', views.update_company_info, name='update_company_info'),
    path('change_password/<int:pk>', views.change_password, name='change_password'),
    path('subscription_history/<int:pk>', views.subscription_history, name='subscription_history'),
    path('cancel_subscription/<int:pk>', views.cancel_subscription, name='cancel_subscription'),
    path('upgrade_subscription/<int:pk>', views.upgrade_subscription, name='upgrade_subscription'),
    path('upgrade_calculate_subscriptions/<int:pk>', views.upgrade_calculate_subscriptions, name='upgrade_calculate_subscriptions'),
    path('upgrade_submit_subscription_inside_home/<int:pk>', views.upgrade_submit_subscription_inside_home, name='upgrade_submit_subscription_inside_home'),
    path('add_company_users/<int:pk>', views.add_company_users, name='add_company_users'),

    path('add_expected_users/<int:pk>', views.add_expected_users, name='add_expected_users'),

    path('new_subscriptions/<int:pk>', views.new_subscriptions, name='new_subscriptions'),
    path('new_subscription_plan/<int:pk>', views.new_subscription_plan, name='new_subscription_plan'),

    path('dashboard/<int:pk>', views.dashboard, name='dashboard'),

    path('submit_subscription_inside_home/', views.submit_subscription_inside_home, name='submit_subscription_inside_home'),

    path('user_registration/', views.user_registration, name='user_registration'),
    path('calculate_amount_to_pay/', views.calculate_amount_to_pay, name='calculate_amount_to_pay'),

    path('subscription_plan/', views.subscription_plan, name='subscription_plan'),


    path('country_list_from_ajax/', views2.country_list_from_ajax, name='country_list_from_ajax'),
    path('states_list_from_ajax/', views2.states_list_from_ajax, name='states_list_from_ajax'),
    path('cities_list_from_ajax/', views2.cities_list_from_ajax, name='cities_list_from_ajax'),
    path('testtu/', views2.testtu, name='testtu'),
    path('get_states_for_update_ajax/', views2.get_states_for_update_ajax, name='get_states_for_update_ajax'),
    path('get_cities_for_update_ajax/', views2.get_cities_for_update_ajax, name='get_cities_for_update_ajax'),

    path('erp_info_check/', views2.erp_info_check, name='erp_info_check'),


    path('check-erp-site-name/', views2.check_unique_erp_site_name, name='check_unique_erp_site_name'),

    path('erp_info_check_for_upgrade/', views2.erp_info_check_for_upgrade, name='erp_info_check_for_upgrade'),
    path('s_c/', views2.s_c, name='s_c'),
    path('validate_email/', views2.validate_email, name='validate_email'),
    path('erp_name_ajax/', views2.erp_name_ajax, name='erp_name_ajax'),
    path('erp_site_name_ajax/', views2.erp_site_name_ajax, name='erp_site_name_ajax'),

    #odoo_create_new_company.py
    path('odooo_company_and_website_create/', views2.odooo_company_and_website_create, name='odooo_company_and_website_create'),
    #odoo_list_modules.py
    path('odoo_models/', views2.odoo_models, name='odoo_models'),
    #odoo_load_update_company_logo.py
    path('odoo_company_image_upload/', views2.odoo_company_image_upload, name='odoo_company_image_upload'),
    #odoo_add_new_user.py
    path('create_new_odoo_user/', views2.create_new_odoo_user, name='create_new_odoo_user'),
    #odoo_assign_role.py
    path('change_user_rol/', views2.change_user_rol, name='change_user_rol'),

    path('all_group/', views2.all_group, name='all_group'),
    #odoo_disable_user.py
    path('disable_odoo_user_info/', views2.disable_odoo_user_info, name='disable_odoo_user_info'),
    #create_product_to_odoo.py
    path('create_product_to_odoo/', views2.create_product_to_odoo, name='create_product_to_odoo'),

    # use Manager role
    path('create_user_manager_role/', views2.create_user_manager_role, name='create_user_manager_role'),




    path('activate_my_erp/<int:pk>', views.activate_my_erp, name='activate_my_erp'),
    path('activate_my_erp_info/<int:pk>', views.activate_my_erp_info, name='activate_my_erp_info'),
    path('add_user_with_manager_role/<int:pk>', views.add_user_with_manager_role, name='add_user_with_manager_role'),
    path('add_user_without_manager_role/<int:pk>', views.add_user_without_manager_role, name='add_user_without_manager_role'),
    path('remove_user/<int:pk>', views.remove_user, name='remove_user'),
    path('update_user_role/<int:pk>', views.update_user_role, name='update_user_role'),
    path('export_product_and_image/<int:pk>', views.export_product_and_image, name='export_product_and_image'),

    path('update_user_roles_view/', views.update_user_roles_view, name='update_user_roles_view'),
    path('update_user_roles/', views.update_user_roles, name='update_user_roles'),



    path('import_contacts_record/<int:pk>', views.import_contacts_record, name='import_contacts_record'),
    path('import_suppliers_record/<int:pk>', views.import_suppliers_record, name='import_suppliers_record'),
    path('import_employees_record/<int:pk>', views.import_employees_record, name='import_employees_record'),
    path('import_fleet_assets_record/<int:pk>', views.import_fleet_assets_record, name='import_fleet_assets_record'),

    path('odoo_account_accountant/<int:pk>', views.odoo_account_accountant, name='odoo_account_accountant'),
    path('odoo_setup_manual_shipping/<int:pk>', views.odoo_setup_manual_shipping, name='odoo_setup_manual_shipping'),
    path('odoo_configure_mail/<int:pk>', views.odoo_configure_mail, name='odoo_configure_mail'),
    path('odoo_set_website_languages/<int:pk>', views.odoo_set_website_languages, name='odoo_set_website_languages'),
    path('odoo_configure_whatsapp_service/<int:pk>', views.odoo_configure_whatsapp_service, name='odoo_configure_whatsapp_service'),
    path('odoo_twilio_sms_config/<int:pk>', views.odoo_twilio_sms_config, name='odoo_twilio_sms_config'),
    path('odoo_configure_stripe_payment/<int:pk>', views.odoo_configure_stripe_payment, name='odoo_configure_stripe_payment'),
    path('odoo_configure_paypal_payment/<int:pk>', views.odoo_configure_paypal_payment, name='odoo_configure_paypal_payment'),

    path('get_training/<int:pk>', views.get_training, name='get_training'),
    path('learn_erp/<int:pk>', views.learn_erp, name='learn_erp'),




]