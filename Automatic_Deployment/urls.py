from django.urls import path
from . import views

urlpatterns = [
    # step-1
    path('addMyDomain/<int:pk>/<str:sub_id>', views.addMyDomain, name='addMyDomain'),
    path('get_static_ip_view/', views.get_static_ip_view, name='get_static_ip_view'),

    #step-2
    path('confirm_ip/<int:company_info_id>/<int:setup_id>/', views.confirm_ip_view, name='confirm_ip'),
    path('create_instance/<int:company_info_id>/<int:setup_id>/', views.create_instance_view, name='create_instance'),
    path('create_instance_second/<int:company_info_id>/<int:setup_id>/<str:instance_name>', views.create_instance_second, name='create_instance_second'),
    path('create_instance_third/<int:company_info_id>/<int:setup_id>/<str:instance_name>', views.create_instance_third, name='create_instance_third'),

    #step-3
    path('step3_launge_odoo_page/<int:company_info_id>/<int:setup_id>/', views.step3_launge_odoo_page, name='step3_launge_odoo_page'),
    path('setup-odoo-docker/<int:setup_id>/<int:company_info_id>/', views.setup_odoo_docker_view, name='setup_odoo_docker'),
    path('create_odoo_database/<int:company_info_id>/<int:setup_id>/', views.create_odoo_database, name='create_odoo_database'),

    #step-4
    path('step4-setup-company/<int:company_info_id>/<int:setup_id>/', views.step4_setup_company, name='step4_setup_company'),
    path('finish-setup-company/<int:company_info_id>/<int:setup_id>/', views.finish_setup_company, name='finish_setup_company'),

    #step-5
    path('step5-installation/<int:company_info_id>/<int:setup_id>/', views.step5_installation, name='step5_installation'),
    path('finish-installation/<int:company_info_id>/<int:setup_id>/', views.finish_installation, name='finish_installation'),

    path('odoo-landing-page/<int:company_info_id>/<int:setup_id>/', views.odoo_landing_page, name='odoo_landing_page'),
]