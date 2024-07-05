from django.shortcuts import render, redirect, HttpResponse
from User_Registration_App.models import CompanyRegistrationInformation
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import OdooDomainSetup
from subscription_app.models import SubscriptionInformation
import boto3
import os
import psycopg2
from django.contrib import messages
import time
import uuid
import paramiko
from paramiko import SSHClient, AutoAddPolicy
from django.conf import settings
import subprocess
import paramiko
from scp import SCPClient
import io
import tempfile
import stat
from django.shortcuts import get_object_or_404, redirect
from psycopg2 import sql  # Import the sql module from psycopg2
from io import StringIO
from account.models import User
from django.db import transaction


@login_required
def addMyDomain(request, pk):
    if request.user.is_authenticated:
        company_info = CompanyRegistrationInformation.objects.get(id=pk)
        context={'company_info':company_info, "user_info":request.user}
        return render(request, "Automatic_Deployment/addMyDomain.html", context)
    else:
        return redirect('login_info')



@login_required
def get_static_ip_view(request):
    if request.method == 'POST':
        domain = request.POST.get('domain')
        company_info_id = request.POST.get('company_info_id')

        domain_name = domain.replace(".", "_")

        subcription = SubscriptionInformation.objects.filter(company_info=company_info_id).last()
        erp_users = int(subcription.number_of_expected_users_of_the_platform)

        try:
            print('Verifying aws client ...')
            # Allocate static IP
            client = boto3.client(
                'lightsail',
                region_name=os.getenv('AWS_REGION'),
                aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY')
            )
            print('Successfully got the aws client!')
        except Exception as e:
            print(f"Failed to get the aws client according aws credentials : {e}")
            messages.error(request, f"Failed to get the aws client according aws credentials : {e}")
            return redirect('addMyDomain', company_info_id)

        try:
            print('Trying Allocate static IP ...')
            # Allocate static IP
            staticIpName = "Odoo-" + str(domain_name) + str("-StaticIp")
            static_ip_response = client.allocate_static_ip(staticIpName=staticIpName)
            static_ip_name = static_ip_response['operations'][0]['resourceName']
            print('Successfully Allocate static IP !')
        except Exception as e:
            print(f'Failed to Allocate static IP : {e}')
            messages.error(request, f'Failed to Allocate static IP : {e}')
            return redirect('addMyDomain', company_info_id)

        try:
            print('Trying Retrieve the allocated IP to get the address ...')
            # Retrieve the allocated IP to get the address
            static_ip_details = client.get_static_ip(staticIpName=static_ip_name)
            static_ip_address = static_ip_details['staticIp']['ipAddress']
            print(f'Successfully Retrieve the allocated IP{static_ip_address} to get the address !')
        except Exception as e:
            static_ip_address = '0.0.0.0'
            print(f'Failed to Retrieve the allocated IP to get the address : {e}')


        setup = OdooDomainSetup(
            user=request.user,
            domain=domain,
            erp_users=erp_users,
            static_ip_name=static_ip_name,
            static_ip=static_ip_address,
            blueprint_id='ubuntu_22_04',  # Replace with your desired blueprint ID
        )
        setup.save()
        setup_id = setup.id
        return redirect('confirm_ip', company_info_id, setup_id)


@login_required
def confirm_ip_view(request, company_info_id, setup_id):
    setup = OdooDomainSetup.objects.get(id=setup_id)
    if request.method == 'POST':
        setup.confirmed = True
        setup.save()
        print('Confirmed ip and pointed to domain ...')
        setup_id = setup.id
        return redirect('create_instance', company_info_id, setup_id)

    company_info = CompanyRegistrationInformation.objects.get(id=company_info_id)
    print('Waiting for confirming ip and point to domain ...')
    return render(request, 'Automatic_Deployment/confirm_ip.html', {'setup': setup, 'company_info': company_info, "user_info": request.user})


#
# @login_required
# def create_instance_view(request, company_info_id, setup_id):
#     print('Processing for create instance ...')
#     setup = OdooDomainSetup.objects.get(id=setup_id)
#     if not setup.confirmed:
#         return redirect('confirm_ip', setup_id=setup.id)
#
#     # Determine Lightsail instance size based on erp_users
#     if setup.erp_users <= 10:
#         bundle_id = 'small_1_0'
#     elif setup.erp_users <= 25:
#         bundle_id = 'medium_1_0'
#     else:
#         bundle_id = 'large_1_0'
#
#     # Connect to Lightsail
#     client = boto3.client(
#         'lightsail',
#         region_name=os.getenv('AWS_REGION'),
#         aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
#         aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY')
#     )
#
#     try:
#         print('Trying to create new key pair ...')
#         domain_name = setup.domain.replace(".", "_")
#         unique_suffix = str(uuid.uuid4()).split('-')[0]  # Shorten the UUID for length constraints
#         key_pair_name = f"Odoo-{domain_name[:20]}-{unique_suffix}-keypair"  # Ensure name is within length limits
#
#         # Create key pair
#         key_pair_response = client.create_key_pair(
#             keyPairName=key_pair_name
#         )
#         # private_key = key_pair_response['keyPair']['privateKey']
#         private_key = key_pair_response['privateKeyBase64']
#
#         # Save the private key in the database
#         setup.private_key = private_key
#         setup.key_pair_name = key_pair_name
#         setup.save()
#
#         # Save private key to a .pem file in /media_files/pem_files/
#         # pem_file_path = os.path.join(settings.MEDIA_ROOT, 'key_pair_files', f'{key_pair_name}.pem')
#         # os.makedirs(os.path.dirname(pem_file_path), exist_ok=True)
#         # with open(pem_file_path, 'w') as pem_file:
#         #     pem_file.write(private_key)
#         #
#         # # Save the file path to the model field
#         # setup.key_pair_file.name = os.path.relpath(pem_file_path, settings.MEDIA_ROOT)
#         # setup.key_pair_name = key_pair_name
#         # setup.save()
#         print(f"Key pair '{key_pair_name}' created and saved name and private key to the database ")
#
#     except Exception as e:
#         print(f"Failed to create key pair: {e}")
#         messages.error(request, "Failed to create key pair.")
#         return redirect('addMyDomain', company_info_id)
#
#     try:
#         print('Trying to create new instance ...')
#         instance_name = f"Odoo-{domain_name}-instanceName"
#
#         # Create instance
#         instance_response = client.create_instances(
#             instanceNames=[instance_name],
#             availabilityZone=f'{os.getenv("AWS_REGION")}a',
#             blueprintId='ubuntu_22_04',  # Replace with your desired blueprint ID
#             bundleId=bundle_id,
#             keyPairName=key_pair_name
#         )
#         print('Successfully created new instance ...')
#     except Exception as e:
#         print(f'Failed to create instance: {e}')
#         messages.error(request, "Failed to create instance !")
#         return redirect('addMyDomain', company_info_id)
#
#     instance_id = instance_response['operations'][0]['resourceName']
#     setup.instance_name = instance_name
#     setup.instance_id = instance_id
#     setup.bundle_id = bundle_id
#     setup.save()
#
#     # Wait for the instance to be in "running" state
#     instance_state = ""
#     while instance_state != "running":
#         time.sleep(10)  # Wait for 10 seconds before checking again
#         instance_details = client.get_instance(instanceName=instance_name)
#         instance_state = instance_details['instance']['state']['name']
#         print(f"Instance state: {instance_state}")
#
#     try:
#         print(f"Trying to Attach static IP with Instance ({setup.static_ip_name} + {setup.instance_name})...")
#         # Attach static IP
#         client.attach_static_ip(
#             staticIpName=setup.static_ip_name,
#             instanceName=setup.instance_name
#         )
#         print(f"Successfully Attached static IP with Instance ! ({setup.static_ip_name} + {setup.instance_name})")
#     except Exception as e:
#         print(f"Failed to Attach static IP with Instance: {e}")
#
#     # Get the public IP address of the instance
#     instance_details = client.get_instance(instanceName=instance_name)
#     instance_public_ip = instance_details['instance']['publicIpAddress']
#     print(f"Instance Public IP : {instance_public_ip}")
#     setup.instance_public_ip = instance_public_ip
#     setup.save()
#
#     print('Creating DB ...')
#     # Create a PostgreSQL database for the Odoo instance
#     db_name = f"{setup.domain.replace('.', '_')}-{unique_suffix}-db"
#     db_user = f"{setup.domain.replace('.', '_')}-{unique_suffix}"
#     db_password = f"{setup.domain.replace('.', '_')}-{unique_suffix}"
#     # db_user = f"odoo_{company_info_id}"
#     # db_password = os.getenv('ODOO_DB_PASSWORD')  # Use a secure way to manage passwords
#     # db_password = f"odoo_{company_info_id}" # Use a secure way to manage passwords
#
#     if create_postgresql_db(db_name, db_user, db_password):
#         setup.db_name = db_name
#         setup.db_user = db_user
#         setup.db_password = db_password
#         setup.save()
#         print(f"Database {db_name} created and user {db_user} added.")
#     else:
#         print(f"Failed to create database {db_name} and user {db_user}.")
#         # messages.error(request, "Failed to create database.")
#         # return redirect('addMyDomain', company_info_id)
#     company_info = CompanyRegistrationInformation.objects.get(id=company_info_id)
#     return render(request, 'Automatic_Deployment/instance_created.html', {'setup': setup, "company_info":company_info, "user_info": request.user})


def verify_instance_key_pair(instance_name, expected_key_pair_name):
    try:
        client = boto3.client(
            'lightsail',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY')
        )
        response = client.get_instance(instanceName=instance_name)
        instance_key_pair_name = response['instance']['sshKeyName']

        if instance_key_pair_name == expected_key_pair_name:
            print(f"Instance '{instance_name}' is associated with key pair '{expected_key_pair_name}'.")
            return True
        else:
            print(f"Instance '{instance_name}' is associated with key pair '{instance_key_pair_name}', not '{expected_key_pair_name}'.")
            return False
    except Exception as e:
        print(f"Error verifying instance key pair: {e}")
        return False


@login_required
def create_instance_view(request, company_info_id, setup_id):
    print('Processing for create instance ...')
    setup = OdooDomainSetup.objects.get(id=setup_id)
    if not setup.confirmed:
        return redirect('confirm_ip', setup_id=setup.id)

    domain_name = setup.domain.replace(".", "_")
    unique_suffix = str(uuid.uuid4()).split('-')[0]  # Shorten the UUID for length constraints

    # Determine Lightsail instance size based on erp_users
    if setup.erp_users <= 10:
        bundle_id = 'small_1_0'
    elif setup.erp_users <= 25:
        bundle_id = 'medium_1_0'
    else:
        bundle_id = 'large_1_0'

    # Connect to Lightsail
    client = boto3.client(
        'lightsail',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY')
    )
    if setup.key_pair_name:
        print('Already Have KeyPair for this domain')
    else:
        try:
            key_pair_name = f"Odoo-{domain_name[:20]}-{unique_suffix}-keypair"
            print('Trying to create new key pair ...')
            # Create key pair
            key_pair_response = client.create_key_pair(
                keyPairName=key_pair_name
            )
            private_key = key_pair_response['privateKeyBase64']

            # Save the private key in the database
            setup.private_key = private_key
            setup.key_pair_name = key_pair_name
            setup.save()

            print(f"Key pair '{key_pair_name}' created and saved name and private key to the database.")

        except Exception as e:
            print(f"Failed to create key pair: {e}")
            messages.error(request, "Failed to create key pair.")
            return redirect('addMyDomain', company_info_id)
    if setup.instance_name:
        print("Instance Already Created for this domain")
    else:
        try:
            print('Trying to create new instance ...')
            instance_name = f"Odoo-{domain_name}-instanceName"
            # Create instance
            instance_response = client.create_instances(
                instanceNames=[instance_name],
                availabilityZone=f'{os.getenv("AWS_REGION")}a',
                blueprintId='ubuntu_22_04',  # Replace with your desired blueprint ID
                bundleId=bundle_id,
                keyPairName=key_pair_name
            )
            print(f'Successfully created new instance {instance_name}...')

            # Extract instance ID
            instance_id = instance_response['operations'][0]['resourceName']
            setup.instance_name = instance_name
            setup.instance_id = instance_id
            setup.bundle_id = bundle_id
            setup.save()

        except Exception as e:
            print(f'Failed to create instance: {e}')
            messages.error(request, "Failed to create instance !")
            return redirect('addMyDomain', company_info_id)


    # Wait for the instance to be in "running" state
    instance_state = ""
    while instance_state != "running":
        try:
            instance_details = client.get_instance(instanceName=setup.instance_name)
            instance_state = instance_details['instance']['state']['name']
            print(f"Instance state: {instance_state}")
            if instance_state == "running":
                break
            else:
                time.sleep(10)  # Wait for 10 seconds before checking again
        except Exception as e:
            print(f"Error retrieving instance state: {e}")
            time.sleep(10)  # Retry after 10 seconds if there's an error

    try:
        print(f"Trying to Attach static IP with Instance ({setup.static_ip_name} + {setup.instance_name})...")
        # Attach static IP
        client.attach_static_ip(
            staticIpName=setup.static_ip_name,
            instanceName=setup.instance_name
        )
        print(f"Successfully Attached static IP with Instance ! ({setup.static_ip_name} + {setup.instance_name})")
    except Exception as e:
        print(f"Failed to Attach static IP with Instance: {e}")

    # Get the public IP address of the instance
    try:
        instance_details = client.get_instance(instanceName=instance_name)
        instance_public_ip = instance_details['instance']['publicIpAddress']
        print(f"Instance Public IP : {instance_public_ip}")
        setup.instance_public_ip = instance_public_ip
        setup.save()
    except Exception as e:
        print(f"Failed to retrieve instance public IP: {e}")

    # print('Creating DB ...')
    # # Create a PostgreSQL database for the Odoo instance
    # unique_suffix = str(uuid.uuid4()).split('-')[0]
    # db_name = f"{setup.domain.replace('.', '_')}-{unique_suffix}-db"
    # db_user = f"{setup.domain.replace('.', '_')}-{unique_suffix}"
    # db_password = f"{setup.domain.replace('.', '_')}-{unique_suffix}"
    # setup.db_name = db_name
    # setup.db_user = db_user
    # setup.db_password = db_password
    # setup.save()



    # if create_postgresql_db(db_name, db_user, db_password):
    #     setup.db_name = db_name
    #     setup.db_user = db_user
    #     setup.db_password = db_password
    #     setup.save()
    #     print(f"Database {db_name} created and user {db_user} added.")
    # else:
    #     print(f"Failed to create database {db_name} and user {db_user}.")

    company_info = CompanyRegistrationInformation.objects.get(id=company_info_id)
    return render(request, 'Automatic_Deployment/instance_created.html', {'setup': setup, "company_info": company_info, "user_info": request.user})






@login_required
def setup_odoo_docker_view(request, setup_id, company_info_id):
    try:
        setup = OdooDomainSetup.objects.get(id=setup_id)
        unique_suffix = str(uuid.uuid4()).split('-')[0]
        db_name = f"{setup.domain.replace('.', '_')}_{unique_suffix}_db"
        db_user = f"{setup.domain.replace('.', '_')}_{unique_suffix}"
        db_password = f"{setup.domain.replace('.', '_')}_{unique_suffix}"
        setup.db_name = db_name
        setup.db_user = db_user
        setup.db_password = db_password
        setup.save()

        instance_public_ip = setup.instance_public_ip

        # Debug statements to check setup values
        print(f"Instance Public IP: {instance_public_ip}")
        print(f"DB User: {setup.db_user}")
        print(f"DB Password: {setup.db_password}")

        # Create PostgreSQL user
        if not create_postgresql_user(setup.db_user, setup.db_password):
            messages.error(request, "Failed to create PostgreSQL user.")
            return redirect('addMyDomain', company_info_id)

        # Docker Compose and Nginx configuration content
        docker_compose_content = f"""
version: '3.9'
services:
    odoo:
        image: odoo:17.0
        restart: always
        tty: true
        volumes:
            - ./custom_addons:/mnt/extra-addons
            - ./config:/etc/odoo
            - odoo_data:/var/lib/odoo
        ports:
            - "8069:8069"
            - "8072:8072"  # Expose Odoo longpolling port
        networks:
            - odoo-network
    db:
        image: postgres:latest
        environment:
            POSTGRES_DB: {db_name}
            POSTGRES_USER: {db_user}
            POSTGRES_PASSWORD: {db_password}
        volumes:
            - db_data:/var/lib/postgresql/data
        networks:
            - odoo-network
networks:
  odoo-network:
volumes:
  odoo_data:
  db_data:
"""

        odoo_conf_content = f"""
[options]
db_host = {os.getenv('MS_DB_HOST')}
db_user = {setup.db_user}
db_password = {setup.db_password}
"""

        nginx_conf_content = f"""
upstream odoo {{
 server 127.0.0.1:8069;
}}

upstream odoochat {{
 server 127.0.0.1:8072;
}}

server {{
    listen 80;
    server_name {setup.domain};  # Replace with actual domain

    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    # Proxy headers
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # log files
    access_log /var/log/nginx/odoo.access.log;
    error_log /var/log/nginx/odoo.error.log;

    # Handle longpoll requests
    location /longpolling {{
        proxy_pass http://odoochat;
    }}

    # Handle / requests
    location / {{
       proxy_redirect off;
       proxy_pass http://odoo;
    }}

    # Cache static files
    location ~* /web/static/ {{
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }}

    # Gzip
    gzip_types text/css text/less text/plain text/xml application/xml application/json application/javascript;
    gzip on;
}}
"""

        # Commands to be executed on the remote server
        commands = [
            'sudo apt update',
            'sudo apt install -y docker.io docker-compose nginx python3-certbot-nginx',
            'sudo systemctl start docker',
            'sudo systemctl enable docker',
            'sudo docker rm -f db odoo || true',
            'sudo docker network create odoo-network || true',
            'mkdir -p odoo1/config odoo1/custom_addons',
        ]

        if ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, commands):
            # Create and transfer Docker Compose file
            if not ssh_transfer_file(instance_public_ip, 'ubuntu', setup.private_key, 'docker-compose.yml', docker_compose_content, 'odoo1/docker-compose.yml'):
                messages.error(request, "Failed to transfer Docker Compose file.")
                return redirect('addMyDomain', company_info_id)

            # Create and transfer Odoo config file
            if not ssh_transfer_file(instance_public_ip, 'ubuntu', setup.private_key, 'odoo.conf', odoo_conf_content, 'odoo1/config/odoo.conf'):
                messages.error(request, "Failed to transfer Odoo config file.")
                return redirect('addMyDomain', company_info_id)

            # Run Docker Compose
            run_docker_cmd = 'cd odoo1 && sudo docker-compose up -d'
            if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, [run_docker_cmd]):
                messages.error(request, "Failed to start Docker containers.")
                return redirect('addMyDomain', company_info_id)

            # Remove default Nginx config
            remove_nginx_default_cmd = 'sudo rm /etc/nginx/sites-enabled/default || true'
            if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, [remove_nginx_default_cmd]):
                messages.error(request, "Failed to remove default Nginx config.")
                return redirect('addMyDomain', company_info_id)

            # Create and transfer Nginx config file
            if not ssh_transfer_file(instance_public_ip, 'ubuntu', setup.private_key, 'odoo.conf', nginx_conf_content, '/tmp/odoo.conf'):
                messages.error(request, "Failed to transfer Nginx config file.")
                return redirect('addMyDomain', company_info_id)

            # Move the Nginx config file to the appropriate directory and create symlink
            nginx_commands = [
                'sudo mv /tmp/odoo.conf /etc/nginx/sites-available/odoo.conf',
                'sudo ln -s /etc/nginx/sites-available/odoo.conf /etc/nginx/sites-enabled/',
                'sudo nginx -t',
                'sudo systemctl restart nginx.service',
                f'sudo certbot --nginx -d {setup.domain} --register-unsafely-without-email --agree-tos --no-eff-email'
            ]
            if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, nginx_commands):
                messages.error(request, "Failed to configure Nginx.")
                return redirect('addMyDomain', company_info_id)

            # Check if Docker containers are running
            check_docker_cmd = 'sudo docker ps --format "{{.Names}}"'
            container_names = ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, [check_docker_cmd], get_output=True)
            if 'odoo' in container_names and 'db' in container_names:
                print('Odoo deployment successful.')
                setup.deployed = True
                setup.save()
                messages.success(request, "Odoo deployment successful.")
            else:
                print('Docker containers not running as expected.')
                messages.error(request, "Docker containers not running as expected.")
                return redirect('addMyDomain', company_info_id)
        else:
            print('Odoo deployment failed.')
            messages.error(request, "Odoo deployment failed.")
            return redirect('addMyDomain', company_info_id)

    except OdooDomainSetup.DoesNotExist:
        messages.error(request, "Setup not found.")
        return redirect('addMyDomain', company_info_id)
    except Exception as e:
        print(f"Error during deployment: {e}")
        messages.error(request, "Error during deployment.")
        return redirect('addMyDomain', company_info_id)

    company_info = CompanyRegistrationInformation.objects.get(id=company_info_id)
    return render(request, 'Automatic_Deployment/instance_created.html',
                  {'setup': setup, 'company_info': company_info, 'user_info': request.user})


def ssh_transfer_file(instance_ip, username, private_key_string, local_file_name, file_content, remote_file_path):
    try:
        private_key_file = StringIO(private_key_string)
        ssh_key = paramiko.RSAKey.from_private_key(private_key_file)

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(instance_ip, username=username, pkey=ssh_key)
        print("SSH Connected")

        sftp_client = ssh_client.open_sftp()
        with sftp_client.file(remote_file_path, 'w') as remote_file:
            remote_file.set_pipelined()
            remote_file.write(file_content)
            remote_file.chmod(0o644)

        sftp_client.close()
        ssh_client.close()
        print(f"File {local_file_name} transferred successfully to {remote_file_path}.")
        return True
    except Exception as e:
        print(f"File transfer failed: {e}")
        return False


def create_postgresql_user(db_user, db_password):
    try:
        connection = psycopg2.connect(
            host=os.getenv('MS_DB_HOST'),
            port=os.getenv('MS_DB_PORT'),
            user=os.getenv('MS_DB_USER'),
            password=os.getenv('MS_DB_PASSWORD')
        )
        connection.autocommit = True
        cursor = connection.cursor()

        cursor.execute(sql.SQL("SELECT 1 FROM pg_roles WHERE rolname=%s"), [db_user])
        user_exists = cursor.fetchone()

        if not user_exists:
            cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s;").format(
                sql.Identifier(db_user)
            ), [db_password])

        cursor.execute(sql.SQL("ALTER USER {} CREATEDB;").format(
            sql.Identifier(db_user)
        ))

        cursor.close()
        connection.close()
        print(f"User {db_user} created or verified successfully.")
        return True

    except Exception as e:
        print(f"Error creating or verifying user: {e}")
        return False


def ssh_execute_command(instance_ip, username, private_key_string, commands, get_output=False):
    try:
        private_key_file = StringIO(private_key_string)
        ssh_key = paramiko.RSAKey.from_private_key(private_key_file)

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(instance_ip, username=username, pkey=ssh_key)
        print("SSH Connected")

        output = ""
        for command in commands:
            print(f"Executing command: {command}")
            stdin, stdout, stderr = ssh_client.exec_command(command)
            command_output = stdout.read().decode()
            command_error = stderr.read().decode()
            print(command_output)
            print(command_error)
            if get_output:
                output += command_output

        ssh_client.close()
        return output if get_output else True
    except Exception as e:
        print(f"SSH connection or command execution failed: {e}")
        return False





# def create_postgresql_db(db_name, db_user, db_password):
#     try:
#         rds_host = os.getenv('MS_DB_HOST')
#         rds_port = os.getenv('MS_DB_PORT', 5432)
#         rds_master_user = os.getenv('MS_DB_USER')
#         rds_master_password = os.getenv('MS_DB_PASSWORD')
#         rds_master_name = os.getenv('MS_DB_NAME')
#
#         connection = psycopg2.connect(
#             host=rds_host,
#             port=rds_port,
#             user=rds_master_user,
#             password=rds_master_password,
#             dbname=rds_master_name
#         )
#         connection.autocommit = True
#         cursor = connection.cursor()
#
#         cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
#         db_exists = cursor.fetchone()
#
#         if not db_exists:
#             cursor.execute(sql.SQL('CREATE DATABASE {} OWNER {};').format(
#                 sql.Identifier(db_name),
#                 sql.Identifier(rds_master_user)
#             ))
#
#         cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{db_user}';")
#         user_exists = cursor.fetchone()
#
#         if not user_exists:
#             cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s;").format(
#                 sql.Identifier(db_user)
#             ), [db_password])
#
#         cursor.execute(sql.SQL("ALTER USER {} CREATEDB;").format(
#             sql.Identifier(db_user)
#         ))
#         cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {};").format(
#             sql.Identifier(db_name),
#             sql.Identifier(db_user)
#         ))
#
#         cursor.close()
#         connection.close()
#         print(f"Database {db_name} and user {db_user} created or verified successfully.")
#         return True
#
#     except Exception as e:
#         print(f"Error creating or verifying database or user: {e}")
#         return False
#
#
# def ssh_execute_command(instance_ip, username, private_key_string, commands):
#     try:
#         private_key_file = StringIO(private_key_string)
#         ssh_key = paramiko.RSAKey.from_private_key(private_key_file)
#
#         ssh_client = paramiko.SSHClient()
#         ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh_client.connect(instance_ip, username=username, pkey=ssh_key)
#         print("SSH Connected")
#
#         for command in commands:
#             stdin, stdout, stderr = ssh_client.exec_command(command)
#             print(stdout.read().decode())
#             print(stderr.read().decode())
#
#         ssh_client.close()
#         return True
#
#     except Exception as e:
#         print(f"SSH connection or command execution failed: {e}")
#         return False
#
#
# @login_required
# def setup_odoo_docker_view(request, setup_id, company_info_id):
#     setup = OdooDomainSetup.objects.get(id=setup_id)
#     instance_public_ip = setup.instance_public_ip
#
#     try:
#         with transaction.atomic():
#             if not create_postgresql_db(setup.db_name, setup.db_user, setup.db_password):
#                 raise Exception("Failed to create PostgreSQL database and user.")
#
#         print('Deploying Odoo ...')
#
#
#         commands = [
#             'sudo apt update',
#             'sudo apt install -y docker.io',
#             'sudo groupadd docker || true',  # Create the Docker group if it doesn't exist
#             'sudo usermod -aG docker $USER',
#             'sudo systemctl start docker',
#             'sudo systemctl enable docker',
#             'sudo docker network create odoo-network || true',
#             f'sudo docker run -d --name db --network odoo-network -e POSTGRES_DB={setup.db_name} '
#             f'-e POSTGRES_USER={setup.db_user} -e POSTGRES_PASSWORD={setup.db_password} postgres:latest',
#             f'sudo docker run -d --name odoo --network odoo-network -p 8069:8069 '
#             f"-e DB_HOST={os.getenv('MS_DB_HOST')} -e DB_PORT={os.getenv('MS_DB_PORT', 5432)} -e DB_NAME={os.getenv('MS_DB_NAME')}"
#             f"-e DB_USER={os.getenv('MS_DB_USER')} -e DB_PASSWORD={os.getenv('MS_DB_PASSWORD')} odoo:latest"
#         ]
#
#
#         if ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, commands):
#             print('Odoo deployment successful.')
#             setup.deployed = True
#             setup.save()
#             messages.success(request, "Odoo deployment successful.")
#         else:
#             print('Odoo deployment failed.')
#             messages.error(request, "Odoo deployment failed.")
#             return redirect('addMyDomain', company_info_id)
#
#     except Exception as e:
#         print(f"Setup failed: {e}")
#         messages.error(request, f"Setup failed: {e}")
#         return redirect('addMyDomain', company_info_id)
#
#     company_info = CompanyRegistrationInformation.objects.get(id=company_info_id)
#     return render(request, 'Automatic_Deployment/instance_created.html',
#                   {'setup': setup, "company_info": company_info, "user_info": request.user})


# def connect_to_instance(instance_ip, username, private_key):
#     # print(instance_ip, username, private_key)
#     try:
#         ssh_client = paramiko.SSHClient()
#         ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh_key = paramiko.RSAKey.from_private_key(io.StringIO(private_key))
#         ssh_client.connect(instance_ip, username=username, pkey=ssh_key)
#         print("ssh Connected")
#         return ssh_client
#     except Exception as e:
#         print(f"Error connecting to instance: {e}")
#         return False


# def wait_for_apt_lock(ssh_client):
#     command = "sudo lsof /var/lib/dpkg/lock-frontend"
#     while True:
#         stdin, stdout, stderr = ssh_client.exec_command(command)
#         output = stdout.read().decode()
#         if not output:
#             break
#         print(f"Waiting for lock: {output}")
#         time.sleep(10)
#     print("Lock released, proceeding with installation.")

# def install_docker(ssh_client):
#     try:
#         commands = [
#             "sudo apt update && sudo apt upgrade -y",
#             "curl -fsSL https://get.docker.com -o get-docker.sh",
#             "sudo sh get-docker.sh",
#             "sudo usermod -aG docker $USER",
#             "sudo apt install docker-compose -y"
#         ]
#
#         for command in commands:
#             print(f"Executing: {command}")
#             wait_for_apt_lock(ssh_client)  # Ensure the lock is released before running the command
#             stdin, stdout, stderr = ssh_client.exec_command(command)
#             exit_status = stdout.channel.recv_exit_status()
#             output = stdout.read().decode()
#             error = stderr.read().decode()
#             print(f"Output: {output}")
#             if error:
#                 print(f"Error: {error}")
#
#         print("Docker and Docker Compose installed successfully.")
#         return True
#     except Exception as e:
#         print(f"Error installing Docker: {e}")
#         return False

# def create_docker_compose_file(ssh_client):
#     docker_compose_content = """
#     version: '3.1'
#
#     services:
#       web:
#         image: odoo:14
#         depends_on:
#           - db
#         ports:
#           - "8069:8069"
#         environment:
#           - HOST=db
#           - USER=odoo
#           - PASSWORD=odoo
#         volumes:
#           - odoo-web-data:/var/lib/odoo
#           - ./config:/etc/odoo
#
#       db:
#         image: postgres:13
#         environment:
#           - POSTGRES_DB=postgres
#           - POSTGRES_PASSWORD=odoo
#           - POSTGRES_USER=odoo
#         volumes:
#           - odoo-db-data:/var/lib/postgresql/data
#
#     volumes:
#       odoo-web-data:
#       odoo-db-data:
#     """
#
#     command = f'echo "{docker_compose_content}" | sudo tee /home/ubuntu/docker-compose.yml'
#     stdin, stdout, stderr = ssh_client.exec_command(command)
#     output = stdout.read().decode()
#     error = stderr.read().decode()
#     print(f"Output: {output}")
#     if error:
#         print(f"Error: {error}")
#     else:
#         print("Docker Compose file created successfully.")


# def start_docker_containers(ssh_client):
#     try:
#         commands = [
#             "cd /home/ubuntu",
#             "sudo docker-compose up -d"
#         ]
#
#         for command in commands:
#             print(f"Executing: {command}")
#             stdin, stdout, stderr = ssh_client.exec_command(command)
#             output = stdout.read().decode()
#             error = stderr.read().decode()
#             print(f"Output: {output}")
#             if error:
#                 print(f"Error: {error}")
#
#         print("Docker containers started successfully.")
#         return True
#     except Exception as e:
#         print(f"Error starting Docker containers: {e}")
#         return False


# @login_required
# def setup_odoo_docker_view(request, setup_id, company_info_id):
#     print("Odoo Deployment Process Start ...")
#     setup = OdooDomainSetup.objects.get(id=setup_id)
#
    # if not verify_instance_key_pair(setup.instance_name, setup.key_pair_name):
    #     # Handle key pair verification failure
    #     return HttpResponse("Instance key pair association verification failed.")
#
#
#     ssh_client = connect_to_instance(setup.instance_public_ip, 'ubuntu', setup.private_key)
#     # print(ssh_client)
#     if ssh_client:
#         if install_docker(ssh_client):
#             create_docker_compose_file(ssh_client)
#             start_docker_containers(ssh_client)
#         ssh_client.close()
#         print("Successfully Installed Odoo")
#         return HttpResponse("Successfully Installed Odoo")
#     else:
#         print("Failed to connect ssh")
#         return HttpResponse("Failed to connect ssh")








# def setup_odoo_instance(ssh_client, setup):
#     try:
#         commands = [
#             "sudo apt update && sudo apt upgrade -y",
#             "sudo apt install wget git python3-pip build-essential python3-dev libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev libjpeg-dev libpq-dev libjpeg8-dev liblcms2-dev libblas-dev libatlas-base-dev libssl-dev libffi-dev -y",
#             "sudo apt install postgresql -y",
#             f"sudo su - postgres -c \"createuser -s {setup.db_user}\"",
#             f"sudo su - postgres -c \"createdb {setup.db_name} -O {setup.db_user}\"",
#             f"sudo su - postgres -c \"psql -c \\\"ALTER USER {setup.db_user} WITH PASSWORD '{setup.db_password}';\\\"\"",
#             "wget -O- https://nightly.odoo.com/odoo.key | sudo apt-key add -",
#             "echo 'deb http://nightly.odoo.com/15.0/nightly/deb/ ./' | sudo tee /etc/apt/sources.list.d/odoo.list",
#             "sudo apt update && sudo apt install odoo -y",
#             f"sudo sed -i 's/db_host = False/db_host = localhost/g' /etc/odoo/odoo.conf",
#             f"sudo sed -i 's/db_user = odoo/db_user = {setup.db_user}/g' /etc/odoo/odoo.conf",
#             f"sudo sed -i 's/db_password = False/db_password = {setup.db_password}/g' /etc/odoo/odoo.conf",
#             "sudo systemctl enable odoo",
#             "sudo systemctl start odoo"
#         ]
#
#         for command in commands:
#             print(f"Executing: {command}")
#             stdin, stdout, stderr = ssh_client.exec_command(command)
#             stdout.channel.recv_exit_status()  # Wait for the command to finish
#             output = stdout.read().decode()
#             error = stderr.read().decode()
#             print(f"Output: {output}")
#             if error:
#                 print(f"Error: {error}")
#
#         print("Odoo installation and setup completed successfully.")
#         return True
#     except Exception as e:
#         print(f"Error setting up Odoo: {e}")
#         return False




# @login_required
# def setup_odoo_docker_view(request, setup_id, company_info_id):
#     setup = get_object_or_404(OdooDomainSetup, id=setup_id)
#
#     # Assume you have a method to securely retrieve the private key from the database
#     private_key = setup.private_key  # Replace with your actual method
#
#     # Use a temporary file to write the private key
#     with tempfile.NamedTemporaryFile(delete=False) as key_file:
#         key_file.write(private_key.encode('utf-8'))
#         key_file_path = key_file.name
#
#     try:
#         os.chmod(key_file_path, stat.S_IRUSR | stat.S_IWUSR)
#
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#
#         instance_ip = setup.static_ip
#
#         try:
#             ssh.connect(instance_ip, username='ubuntu', key_filename=key_file_path)
#             print("SSH connection successful!")
#             ssh.close()
#         except Exception as e:
#             print(f"Manual SSH connection test failed: {e}")
#             messages.error(request, "Manual SSH connection test failed.")
#             return redirect('addMyDomain', company_info_id)
#
#         if setup_odoo_docker(instance_ip, key_file_path, os.getenv('MS_DB_HOST'), setup.db_user, setup.db_password,
#                              setup.db_name):
#             print("Odoo Docker setup completed successfully.")
#             messages.success(request, "Odoo Docker setup completed successfully.")
#         else:
#             print("Failed to setup Odoo Docker.")
#             messages.error(request, "Failed to setup Odoo Docker.")
#             return redirect('addMyDomain', company_info_id)
#
#     finally:
#         os.remove(key_file_path)
#
#     return redirect('addMyDomain', company_info_id)


# @login_required
# def setup_odoo_docker_view(request, setup_id, company_info_id):
#     setup = get_object_or_404(OdooDomainSetup, id=setup_id)
#     private_key = setup.private_key  # Assuming you store the private key in the database
#
#     # Write the private key to a temporary file
#     with tempfile.NamedTemporaryFile(delete=False) as key_file:
#         key_file.write(private_key.encode('utf-8'))
#         key_file_path = key_file.name
#
#     try:
#         # Set the correct permissions for the private key file
#         os.chmod(key_file_path, stat.S_IRUSR | stat.S_IWUSR)
#
#         ssh = SSHClient()
#         ssh.set_missing_host_key_policy(AutoAddPolicy())
#         instance_ip = setup.static_ip
#
#         # Add debugging prints
#         print(f"Attempting to connect to {instance_ip} with username 'ubuntu' and key file {key_file_path}")
#         print(f"Private key content (first 100 characters): {private_key[:100]}...")
#
#         try:
#             ssh.connect(instance_ip, username='ubuntu', key_filename=key_file_path)
#             print("SSH connection successful!")
#             ssh.close()
#         except paramiko.ssh_exception.AuthenticationException as e:
#             print(f"Manual SSH connection test failed: {e}")
#             messages.error(request, "Manual SSH connection test failed.")
#             return redirect('addMyDomain', company_info_id)
#         except Exception as e:
#             print(f"Error during SSH connection: {e}")
#             messages.error(request, f"Error during SSH connection: {e}")
#             return redirect('addMyDomain', company_info_id)
#
#         # Attempt to set up Odoo Docker
#         if setup_odoo_docker(instance_ip, key_file_path, os.getenv('MS_DB_HOST'), setup.db_user, setup.db_password, setup.db_name):
#             print("Odoo Docker setup completed successfully.")
#             messages.success(request, "Odoo Docker setup completed successfully.")
#         else:
#             print("Failed to setup Odoo Docker.")
#             messages.error(request, "Failed to setup Odoo Docker.")
#             return redirect('addMyDomain', company_info_id)
#     finally:
#         os.remove(key_file_path)
#
#     return redirect('addMyDomain', company_info_id)


# def setup_odoo_docker(instance_ip, key_file_path, db_host, db_user, db_password, db_name):
#     username = 'ubuntu'  # Default username for Ubuntu instances on Lightsail
#     docker_compose_content = """
#     version: '3.9'
#     services:
#         odoo:
#             image: odoo:17.0
#             restart: always
#             tty: true
#             volumes:
#                 - ./custom_addons:/mnt/extra-addons
#                 - ./config:/etc/odoo
#                 - odoo_data:/var/lib/odoo
#             ports:
#                 - "8069:8069"
#     volumes:
#       odoo_data:
#     """
#     odoo_conf_content = f"""
#     [options]
#     db_host = {db_host}
#     db_user = {db_user}
#     db_password = {db_password}
#     db_name = {db_name}
#     """
#
#     try:
#         # Connect to the Lightsail instance
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh.connect(instance_ip, username=username, key_filename=key_file_path)
#
#         # Create the necessary directories
#         commands = [
#             'mkdir -p ~/odoo1/config',
#             'mkdir -p ~/odoo1/custom_addons'
#         ]
#         for command in commands:
#             ssh.exec_command(command)
#
#         # Create SCP client
#         with SCPClient(ssh.get_transport()) as scp:
#             # Transfer docker-compose.yml
#             scp.putfo(io.StringIO(docker_compose_content), '~/odoo1/docker-compose.yml')
#
#             # Transfer odoo.conf
#             scp.putfo(io.StringIO(odoo_conf_content), '~/odoo1/config/odoo.conf')
#
#         # Run Docker Compose
#         ssh.exec_command('docker-compose -f ~/odoo1/docker-compose.yml up -d')
#
#         ssh.close()
#         print("Odoo setup completed successfully.")
#         return True
#
#     except Exception as e:
#         print(f"Error setting up Odoo: {e}")
#         return False


# def setup_odoo_on_instance(instance_ip, key_file_path, db_name, db_user, db_password, username='ubuntu'):
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(instance_ip, username=username, key_filename=key_file_path)
#
#     commands = [
#         'sudo apt-get update',
#         'sudo apt-get install -y docker.io docker-compose',
#         'sudo mkdir -p /opt/odoo/config /opt/odoo/custom_addons',
#         f'echo "[options]\ndb_host = {os.getenv("MS_DB_HOST")}\ndb_user = {db_user}\ndb_password = {db_password}\ndb_name = {db_name}\n" | sudo tee /opt/odoo/config/odoo.conf',
#         'sudo touch /opt/odoo/docker-compose.yml',
#         'echo "version: \'3.9\'\nservices:\n  odoo:\n    image: odoo:17.0\n    restart: always\n    tty: true\n    volumes:\n      - ./custom_addons:/mnt/extra-addons\n      - ./config:/etc/odoo\n      - odoo_data:/var/lib/odoo\n    ports:\n      - \'8069:8069\'\nvolumes:\n  odoo_data:" | sudo tee /opt/odoo/docker-compose.yml',
#         'cd /opt/odoo && sudo docker-compose up -d'
#     ]
#
#     try:
#         for command in commands:
#             stdin, stdout, stderr = ssh.exec_command(command)
#             stdout.channel.recv_exit_status()
#             time.sleep(5)  # Wait for the command to complete
#         ssh.close()
#         return True
#     except Exception as e:
#         print(f"Error setting up Odoo: {e}")
#         ssh.close()
#         return False

# def create_postgresql_db(db_name):
#     rds_host = os.getenv('MS_DB_HOST')
#     rds_port = os.getenv('MS_DB_PORT', 5432)
#     rds_user = os.getenv('MS_DB_USER')
#     rds_password = os.getenv('MS_DB_PASSWORD')
#     rds_dbname = os.getenv('MS_DB_NAME')  # Connect to the default database to create a new one
#
#     try:
#         connection = psycopg2.connect(
#             host=rds_host,
#             port=rds_port,
#             user=rds_user,
#             password=rds_password,
#             dbname=rds_dbname
#         )
#         connection.autocommit = True
#
#         cursor = connection.cursor()
#         cursor.execute(f'CREATE DATABASE "{db_name}" OWNER {rds_user};')
#         cursor.close()
#         connection.close()
#
#         print(f"Database {db_name} created successfully.")
#         return True
#     except Exception as e:
#         print(f"Error creating database: {e}")
#         return False
#
# # Function to generate SSH key pair
# def generate_ssh_key_pair(username, email, key_path):
#     try:
#         # Generate SSH key pair
#         key = paramiko.RSAKey.generate(bits=4096)
#
#         # Save private key
#         private_key_path = os.path.join(key_path, 'id_rsa')
#         key.write_private_key_file(private_key_path)
#
#         # Save public key
#         public_key_path = os.path.join(key_path, 'id_rsa.pub')
#         with open(public_key_path, 'w') as f:
#             f.write(f'ssh-rsa {key.get_base64()} {username}@{email}\n')
#
#         return private_key_path
#
#     except Exception as e:
#         print(f"Error generating SSH key pair: {e}")
#         return None
#
#
# def deploy_odoo(request, setup_id):
#     # Command to run Docker Compose for Odoo deployment
#     command = [
#         'docker-compose',
#         '-f', f'{settings.BASE_DIR}/docker-compose.yml',  # Replace with your actual Docker Compose file path
#         'up', '-d'
#     ]
#
#     try:
#         # Execute the command
#         subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         return HttpResponse('Odoo deployment initiated successfully.')
#     except subprocess.CalledProcessError as e:
#         return HttpResponse(f'Error deploying Odoo: {e.stderr}', status=500)

# def deploy_odoo(request, setup_id):
#     setup = OdooDomainSetup.objects.get(id=setup_id)
#
#     # Generate SSH key pair (replace with your desired username and email)
#     key_path = f'{settings.BASE_DIR}/'  # Replace with your desired path
#     username = 'root'  # Replace with desired username
#     email = 'root@admin.kintah.com'  # Replace with desired email
#
#     private_key_path = generate_ssh_key_pair(username, email, key_path)
#
#     if private_key_path:
#         try:
#             # Connect to Lightsail instance via SSH using Paramiko
#             instance_public_ip = setup.static_ip  # Assuming static_ip holds the static IP address
#             key = paramiko.RSAKey.from_private_key_file(private_key_path)
#             ssh = paramiko.SSHClient()
#             ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#
#             ssh.connect(hostname=instance_public_ip, username="ubuntu", pkey=key)
#
#             # Odoo setup script
#             setup_script = """
#                 #!/bin/bash
#                 sudo apt-get update
#                 sudo apt-get install -y python3-pip postgresql-client wget git
#                 sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev libpq-dev
#                 sudo adduser --system --home=/opt/odoo --group odoo
#                 sudo git clone https://www.github.com/odoo/odoo --depth 1 --branch 14.0 --single-branch /opt/odoo/odoo
#                 sudo pip3 install -r /opt/odoo/odoo/requirements.txt
#                 sudo cp /opt/odoo/odoo/debian/odoo.conf /etc/odoo.conf
#                 sudo chown odoo: /etc/odoo.conf
#                 sudo chmod 640 /etc/odoo.conf
#                 echo "
#                 [options]
#                 admin_passwd = admin
#                 db_host = {os.getenv('MS_DB_HOST')}
#                 db_port = {os.getenv('MS_DB_PORT')}
#                 db_user = {os.getenv('MS_DB_USER')}
#                 db_password = {os.getenv('MS_DB_PASSWORD')}
#                 addons_path = /opt/odoo/odoo/addons
#                 " | sudo tee /etc/odoo.conf
#                 echo "
#                 [Unit]
#                 Description=Odoo
#                 Documentation=http://www.odoo.com
#                 [Service]
#                 Type=simple
#                 User=odoo
#                 ExecStart=/usr/bin/python3 /opt/odoo/odoo/odoo-bin -c /etc/odoo.conf
#                 [Install]
#                 WantedBy=default.target
#                 " | sudo tee /etc/systemd/system/odoo.service
#                 sudo systemctl daemon-reload
#                 sudo systemctl start odoo
#                 sudo systemctl enable odoo
#                 """
#
#             # Write setup script to a file
#             stdin, stdout, stderr = ssh.exec_command('echo "{}" > setup_odoo.sh'.format(setup_script))
#             stdout.channel.recv_exit_status()
#
#             # Run setup script
#             stdin, stdout, stderr = ssh.exec_command('sudo bash setup_odoo.sh')
#             stdout.channel.recv_exit_status()
#
#             # Close SSH connection
#             ssh.close()
#
#             # Update setup status if deployment is successful
#             setup.odoo_deployed = True
#             setup.save()
#
#             return redirect('instance_detail', setup_id=setup.id)
#
#         except Exception as e:
#             print(f"Error deploying Odoo: {e}")
#             ssh.close()  # Close SSH connection on error
#             return render(request, 'deployment_failed.html')  # Handle failure scenario
#
#     else:
#         print("Failed to generate SSH key pair.")
#         return render(request, 'deployment_failed.html')  # Handle failure scenario


# @login_required  # Ensure user is logged in to access this view
# def create_instance_view(request):
#     if request.method == 'POST':
#         domain = request.POST.get('domain')
#         erp_users = int(request.POST.get('erp_users'))
#         print(domain, erp_users)
#
#         # Determine Lightsail instance size based on erp_users
#         if erp_users <= 10:
#             bundle_id = 'small_1_0'
#         elif erp_users <= 25:
#             bundle_id = 'medium_1_0'
#         else:
#             bundle_id = 'large_1_0'
#
#         print(bundle_id)
#
#         # Connect to Lightsail
#         client = boto3.client(
#             'lightsail',
#             region_name=os.getenv('AWS_REGION'),
#             aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
#             aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY')
#         )
#         print(client)
#
#         # Create instance
#         instance_response = client.create_instances(
#             instanceNames=[domain],
#             availabilityZone=f'{os.getenv("AWS_REGION")}a',
#             blueprintId='ubuntu_20_04',  # Replace with your desired blueprint ID
#             bundleId=bundle_id
#         )
#         print(instance_response)
#         instance_id = instance_response['operations'][0]['resourceName']
#         print(instance_id)
#
#         # Allocate and assign static IP (example)
#         static_ip = StaticIP.objects.filter(is_used=False).first()
#         print(static_ip)
#         if static_ip:
#             static_ip.is_used = True
#             static_ip.save()
#             static_ip_address = static_ip.ip_address
#         else:
#             static_ip_address = None  # Handle case when no static IP is available
#         print(static_ip_address)
#         # Create OdooDomainSetup instance
#         setup = OdooDomainSetup(
#             user=request.user,
#             domain=domain,
#             erp_users=erp_users,
#             static_ip=static_ip_address,
#             instance_name=domain,  # Example: Use domain as instance name
#             instance_id=instance_id,
#             blueprint_id='ubuntu_20_04',  # Replace with your desired blueprint ID
#             bundle_id=bundle_id
#         )
#         setup.save()
#         print(setup)
#
#         return redirect('setup_postgresql_schema', domain=domain)
#
#     return render(request, 'create_instance.html')

# @login_required
# def create_instance_view(request):
#     if request.method == 'POST':
#         domain = request.POST.get('domain')
#         erp_users = int(request.POST.get('erp_users'))
#         print(domain, erp_users)
#
#         setup = OdooDomainSetup(
#             user=request.user,
#             domain=domain,
#             erp_users=erp_users
#         )
#
#         # Determine Lightsail instance size
#         if setup.erp_users <= 10:
#             setup.bundle_id = 'small_1_0'
#         elif setup.erp_users <= 25:
#             setup.bundle_id = 'medium_1_0'
#         else:
#             setup.bundle_id = 'large_1_0'
#
#         print('trying create client')
#         # Connect to Lightsail
#         client = boto3.client(
#             'lightsail',
#             region_name=os.getenv('AWS_REGION'),
#             aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
#             aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY')
#         )
#         print(client)
#
#         # Create static IP
#         static_ip_response = client.allocate_static_ip(staticIpName=setup.domain)
#         setup.static_ip = static_ip_response['operations'][0]['status']
#
#         # Create instance
#         instance_response = client.create_instances(
#             instanceNames=[setup.domain],
#             availabilityZone=f'{os.getenv("AWS_REGION")}a',
#             blueprintId='ubuntu_20_04',
#             bundleId=setup.bundle_id
#         )
#         setup.instance_id = instance_response['operations'][0]['resourceName']
#
#         # Attach static IP
#         client.attach_static_ip(
#             staticIpName=setup.domain,
#             instanceName=setup.instance_id
#         )
#
#         setup.save()
#         return redirect('setup_postgresql_schema', domain=setup.domain)
#
#     return render(request, 'create_instance.html')

# @login_required
# def setup_postgresql_schema(request, domain):
#     setup = OdooDomainSetup.objects.get(domain=domain)
#     subscription_id = f"odoo_{setup.user.id}"
#     db_password = "your_secure_password"  # Generate or get this securely
#
#     # Connect to PostgreSQL RDS
#     conn = psycopg2.connect(
#         dbname='postgres',
#         user=os.getenv('RDS_MASTER_USERNAME'),
#         password=os.getenv('RDS_MASTER_PASSWORD'),
#         host=os.getenv('RDS_ENDPOINT'),
#         port=os.getenv('RDS_PORT')
#     )
#     conn.autocommit = True
#     cur = conn.cursor()
#
#     try:
#         cur.execute(f"CREATE USER {subscription_id} WITH PASSWORD '{db_password}';")
#         cur.execute(f"ALTER USER {subscription_id} CREATEDB;")
#         conn.commit()
#     except Exception as e:
#         return render(request, 'error.html', {'error': str(e)})
#     finally:
#         cur.close()
#         conn.close()
#
#     return render(request, 'success.html', {'domain': domain, 'static_ip': setup.static_ip})
