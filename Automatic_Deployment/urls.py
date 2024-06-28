from django.urls import path
from . import views

urlpatterns = [
    path('addMyDomain/<int:pk>', views.addMyDomain, name='addMyDomain'),
    path('get_static_ip_view/', views.get_static_ip_view, name='get_static_ip_view'),
    path('confirm_ip/<int:company_info_id>/<int:setup_id>/', views.confirm_ip_view, name='confirm_ip'),
    path('create_instance/<int:company_info_id>/<int:setup_id>/', views.create_instance_view, name='create_instance'),
    path('setup-odoo-docker/<int:setup_id>/<int:company_info_id>/', views.setup_odoo_docker_view, name='setup_odoo_docker'),
    # path('deploy_odoo/<int:setup_id>/', views.deploy_odoo, name='deploy_odoo'),
    # path('setup_postgresql_schema/<str:domain>/', views.setup_postgresql_schema, name='setup_postgresql_schema'),
]