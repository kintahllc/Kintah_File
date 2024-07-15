from django.urls import path
from . import views

urlpatterns = [
    # step-1
    path('addMyDomain/<int:pk>/<str:sub_id>', views.addMyDomain, name='addMyDomain'),
    path('get_static_ip_view/', views.get_static_ip_view, name='get_static_ip_view'),
    path('confirm_ip/<int:company_info_id>/<int:setup_id>/', views.confirm_ip_view, name='confirm_ip'),

    #step-2
    path('create_instance/<int:company_info_id>/<int:setup_id>/', views.create_instance_view, name='create_instance'),
    path('create_instance_second/<int:company_info_id>/<int:setup_id>/<str:instance_name>', views.create_instance_second, name='create_instance_second'),
    path('step3_launge_odoo_page/<int:company_info_id>/<int:setup_id>/', views.step3_launge_odoo_page, name='step3_launge_odoo_page'),

    #step-3
    path('setup-odoo-docker/<int:setup_id>/<int:company_info_id>/', views.setup_odoo_docker_view, name='setup_odoo_docker'),
    path('step4_finish_odoo_page/<int:company_info_id>/<int:setup_id>/', views.step4_finish_odoo_page, name='step4_finish_odoo_page'),

    #step-4
    path('finish-odoo-deploy/<int:company_info_id>/<int:setup_id>/', views.finish_odoo_deploy, name='finish_odoo_deploy'),
    path('finish-odoo-deploy-view/<int:company_info_id>/<int:setup_id>/', views.finish_odoo_deploy_view, name='finish_odoo_deploy_view'),

    # path('deploy_odoo/<int:setup_id>/', views.deploy_odoo, name='deploy_odoo'),
    # path('setup_postgresql_schema/<str:domain>/', views.setup_postgresql_schema, name='setup_postgresql_schema'),
]