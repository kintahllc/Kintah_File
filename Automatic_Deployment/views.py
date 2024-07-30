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
from django.shortcuts import get_object_or_404, redirect
from psycopg2 import sql  # Import the sql module from psycopg2
from io import StringIO
import requests
import xmlrpc.client
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

from User_Registration_App.models import PriceMatrixPerCompanyType
from User_Registration_App.utils2 import install_the_modules


@login_required
def addMyDomain(request, pk, sub_id):
    getSubcription = SubscriptionInformation.objects.filter(id=sub_id).last()
    try:
        check_odoo_instance = OdooDomainSetup.objects.filter(subscription_package=getSubcription)
        if check_odoo_instance:
            getOdooDomain = OdooDomainSetup.objects.filter(subscription_package=getSubcription).last()
            if getOdooDomain.domain:
                # already have domain
                if getOdooDomain.confirmed:
                    # ip is confirmed
                    if getOdooDomain.deployed:
                        # deployed
                        if getOdooDomain.setup_company:
                            # setup company
                            if getOdooDomain.installations:
                                return redirect("odoo_landing_page", pk, getOdooDomain.id)
                            else:
                                return redirect("step5_installation", pk, getOdooDomain.id)
                        else:
                            return redirect("step4_setup_company", pk, getOdooDomain.id)
                    else:
                        return redirect('step3_launge_odoo_page', pk, getOdooDomain.id)
                else:
                    return redirect('confirm_ip', pk, getOdooDomain.id)
            else:
                pass
        else:
            pass
    except Exception as e:
        print(f'Failed to check odoo instance : {e}')


    # print(pk, sub_id)
    if request.user.is_authenticated:
        company_info = CompanyRegistrationInformation.objects.get(id=pk)
        Added_Domains = OdooDomainSetup.objects.filter(user=request.user)
        context={'company_info':company_info, "user_info":request.user, 'Added_Domains':Added_Domains, 'sub_id':sub_id}
        return render(request, "Automatic_Deployment/addMyDomain.html", context)
    else:
        return redirect('login_info')


@login_required
def get_static_ip_view(request):
    if request.method == 'POST':
        company_info_id = request.POST.get('company_info_id')
        sub_id = request.POST.get('sub_id')

        domain = request.POST.get('domain')

        if OdooDomainSetup.objects.filter(domain=domain):
            messages.error(request, "Domain already exist!")
            return redirect("addMyDomain", company_info_id, sub_id)


        domain_name = domain.replace(".", "_")

        subcription = SubscriptionInformation.objects.filter(id=sub_id).last()
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
            return redirect('addMyDomain', company_info_id, sub_id)

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
            return redirect('addMyDomain', company_info_id, sub_id)

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
            subscription_package=subcription,
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

    getSubcription = SubscriptionInformation.objects.filter(id=setup.subscription_package.id).last()
    try:
        check_odoo_instance = OdooDomainSetup.objects.filter(subscription_package=getSubcription)
        if check_odoo_instance:
            getOdooDomain = OdooDomainSetup.objects.filter(subscription_package=getSubcription).last()
            if getOdooDomain.domain:
                # already have domain
                if getOdooDomain.confirmed:
                    # ip is confirmed
                    if getOdooDomain.deployed:
                        # deployed
                        if getOdooDomain.setup_company:
                            # setup company
                            if getOdooDomain.installations:
                                return redirect("odoo_landing_page", company_info_id, setup_id)
                            else:
                                return redirect("step5_installation", company_info_id, setup_id)
                        else:
                            return redirect("step4_setup_company", company_info_id, setup_id)
                    else:
                        return redirect('step3_launge_odoo_page', company_info_id, setup_id)
                else:
                    pass
            else:
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
        else:
            return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
    except Exception as e:
        print(f'Failed to check odoo instance : {e}')

    company_info = CompanyRegistrationInformation.objects.get(id=company_info_id)
    print('Waiting for confirming ip and point to domain ...')
    return render(request, 'Automatic_Deployment/confirm_ip.html', {'setup': setup, 'company_info': company_info, "user_info": request.user})


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
            return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
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
            return redirect('addMyDomain', company_info_id, setup.subscription_package.id)

    return redirect('create_instance_second', company_info_id, setup_id, instance_name)


# def create_instance_second(request, company_info_id, setup_id, instance_name):
#     setup = OdooDomainSetup.objects.get(id=setup_id)
#
#     # Connect to Lightsail
#     client = boto3.client(
#         'lightsail',
#         region_name=os.getenv('AWS_REGION'),
#         aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
#         aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY')
#     )
#
#     # Wait for the instance to be in "running" state
#     instance_state = ""
#     while instance_state != "running":
#         try:
#             instance_details = client.get_instance(instanceName=setup.instance_name)
#             instance_state = instance_details['instance']['state']['name']
#             print(f"Instance state: {instance_state}")
#             if instance_state == "running":
#                 break
#             else:
#                 time.sleep(10)  # Wait for 10 seconds before checking again
#         except Exception as e:
#             print(f"Error retrieving instance state: {e}")
#             time.sleep(10)  # Retry after 10 seconds if there's an error
#
#
#     # return redirect('step3_launge_odoo_page', company_info_id, setup_id)
#     return redirect('create_instance_third', company_info_id, setup_id, instance_name)


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_instance_second(request, company_info_id, setup_id, instance_name):
    setup = OdooDomainSetup.objects.get(id=setup_id)

    # Connect to Lightsail
    client = boto3.client(
        'lightsail',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY')
    )

    # Wait for the instance to be in "running" state
    instance_state = ""
    retries = 0
    max_retries = 30  # Retry up to 30 times (5 minutes)
    sleep_time = 10  # Wait for 10 seconds before checking again

    while instance_state != "running" and retries < max_retries:
        try:
            instance_details = client.get_instance(instanceName=setup.instance_name)
            instance_state = instance_details['instance']['state']['name']
            logger.info(f"Instance state: {instance_state}")
            if instance_state == "running":
                break
            else:
                time.sleep(sleep_time)
                retries += 1
        except Exception as e:
            logger.error(f"Error retrieving instance state: {e}")
            time.sleep(sleep_time)
            retries += 1

    if instance_state != "running":
        logger.error(f"Instance did not reach 'running' state within {max_retries * sleep_time} seconds.")
        # Handle the error case appropriately (e.g., redirect to an error page, return an error response, etc.)
        return redirect('error_page')  # Replace 'error_page' with your actual error page/view

    # Instance is running, proceed to the next step
    return redirect('create_instance_third', company_info_id, setup_id, instance_name)



def create_instance_third(request, company_info_id, setup_id, instance_name):
    setup = OdooDomainSetup.objects.get(id=setup_id)

    # Connect to Lightsail
    client = boto3.client(
        'lightsail',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY')
    )

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

    # Add firewall rules for ports 22, 80-81, 443, and 8069
    try:
        print("Trying to add firewall rules for ports 22, 80-81, 443, and 8069 ...")
        client.put_instance_public_ports(
            portInfos=[
                {
                    'fromPort': 22,
                    'toPort': 22,
                    'protocol': 'TCP'
                },
                {
                    'fromPort': 80,
                    'toPort': 81,
                    'protocol': 'TCP'
                },
                {
                    'fromPort': 443,
                    'toPort': 443,
                    'protocol': 'TCP'
                },
                {
                    'fromPort': 8069,
                    'toPort': 8069,
                    'protocol': 'TCP'
                },
            ],
            instanceName=instance_name
        )
        print("Successfully added firewall rules for ports 22, 80-81, 443, and 8069.")
    except Exception as e:
        print(f"Failed to add firewall rules: {e}")

    return redirect('step3_launge_odoo_page', company_info_id, setup_id)


@login_required
def step3_launge_odoo_page(request, company_info_id, setup_id):
    setup = OdooDomainSetup.objects.get(id=setup_id)
    getSubcription = SubscriptionInformation.objects.filter(id=setup.subscription_package.id).last()
    try:
        check_odoo_instance = OdooDomainSetup.objects.filter(subscription_package=getSubcription)
        if check_odoo_instance:
            getOdooDomain = OdooDomainSetup.objects.filter(subscription_package=getSubcription).last()
            if getOdooDomain.domain:
                # already have domain
                if getOdooDomain.confirmed:
                    # ip is confirmed
                    if getOdooDomain.deployed:
                        # deployed
                        if getOdooDomain.setup_company:
                            # setup company
                            if getOdooDomain.installations:
                                return redirect("odoo_landing_page", company_info_id, setup_id)
                            else:
                                return redirect("step5_installation", company_info_id, setup_id)
                        else:
                            return redirect("step4_setup_company", company_info_id, setup_id)
                    else:
                        pass
                else:
                    return redirect('confirm_ip', company_info_id, setup_id)
            else:
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
        else:
            return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
    except Exception as e:
        print(f'Failed to check odoo instance : {e}')
    setup = OdooDomainSetup.objects.get(id=setup_id)
    company_info = CompanyRegistrationInformation.objects.get(id=company_info_id)
    return render(request, 'Automatic_Deployment/instance_created.html',
                  {'setup': setup, "company_info": company_info, "user_info": request.user})


def ssh_transfer_file(instance_ip, username, private_key_string, local_file_name, file_content, remote_file_path):
    try:
        private_key_file = StringIO(private_key_string)
        ssh_key = paramiko.RSAKey.from_private_key(private_key_file)

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(instance_ip, username=username, pkey=ssh_key)
        print("SSH Connected")

        sftp_client = ssh_client.open_sftp()
        temp_remote_file_path = f"/tmp/{local_file_name}"
        with sftp_client.file(temp_remote_file_path, 'w') as remote_file:
            remote_file.write(file_content.encode())
            remote_file.chmod(0o644)

        # Move the file to the desired location using sudo
        move_command = f"sudo mv {temp_remote_file_path} {remote_file_path}"
        ssh_execute_command(instance_ip, username, private_key_string, [move_command])

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


@login_required
def setup_odoo_docker_view(request, setup_id, company_info_id):
    try:
        setup = OdooDomainSetup.objects.get(id=setup_id)

        master_password = request.POST.get('master_password')
        Database_Name = request.POST.get('Database_Name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        language = request.POST.get('language')
        country_code = request.POST.get('country_code')
        demo_data = request.POST.get('demo_data')

        if OdooDomainSetup.objects.filter(Database_Name=Database_Name):
            messages.error(request, "Database Name already exist!")
            return redirect(step3_launge_odoo_page, setup_id, company_info_id)


        setup.Master_Password = master_password
        setup.Database_Name = Database_Name
        setup.email = email
        setup.password = password
        setup.phone_number = phone_number
        setup.language = language
        setup.country_code = country_code
        if demo_data is None:
            print("demo data None")
            setup.demo_data = False
        else:
            setup.demo_data = True



        unique_suffix = str(uuid.uuid4()).split('-')[0]
        # db_name = f"{setup.domain.replace('.', '_')}_{unique_suffix}_db"
        db_user = f"{setup.domain.replace('.', '_')}_{unique_suffix}"
        db_password = f"{setup.domain.replace('.', '_')}_{unique_suffix}"
        # setup.db_name = db_name
        setup.db_user = db_user
        setup.db_password = db_password
        setup.save()


        instance_public_ip = setup.instance_public_ip

        # Debug statements to check setup values
        print(f"Instance Public IP: {instance_public_ip}")
        print(f"DB User: {setup.db_user}")
        # print(f"DB Password: {setup.db_password}")

        # Create PostgreSQL user
        if not create_postgresql_user(setup.db_user, setup.db_password):
            messages.error(request, "Failed to create PostgreSQL user.")
            return redirect('addMyDomain', company_info_id, setup.subscription_package.id)


        # Clone Odoo repository
        clone_odoo_repo_commands = [
            'git clone https://github.com/odoo/odoo.git -b 17.0 --depth 1 /home/ubuntu/odoo'
        ]
        if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, clone_odoo_repo_commands):
            messages.error(request, "Failed to clone Odoo repository.")
            return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
        return HttpResponse("gate -4")



        # Docker Compose and Nginx configuration content
        docker_compose_content = f"""
version: '3.9'
services:
    odoo:
        image: odoo:17.0
        restart: always
        tty: true
        command: -c /etc/odoo/odoo.conf
        volumes:
            - ./custom_addons:/mnt/extra-addons
            - ./config:/etc/odoo
            - /home/ubuntu/odoo:/mnt/odoo
            - odoo_data:/var/lib/odoo
        ports:
            - "8069:8069"
            - "8072:8072"  # Expose Odoo longpolling port
        networks:
            - odoo-network
networks:
  odoo-network:
volumes:
  odoo_data:
"""



#         docker_compose_content = f"""
# version: '3.9'
# services:
#     odoo:
#         image: odoo:17.0
#         restart: always
#         tty: true
#         command: -c /etc/odoo/odoo.conf
#         volumes:
#             - ./custom_addons:/mnt/extra-addons
#             - ./config:/etc/odoo
#             - /home/ubuntu/odoo:/mnt/odoo
#             - odoo_data:/var/lib/odoo
#         ports:
#             - "8069:8069"
#             - "8072:8072"  # Expose Odoo longpolling port
#         networks:
#             - odoo-network
#     db:
#         image: postgres:latest
#         environment:
#             POSTGRES_DB: {db_name}
#             POSTGRES_USER: {db_user}
#             POSTGRES_PASSWORD: {db_password}
#         volumes:
#             - db_data:/var/lib/postgresql/data
#         networks:
#             - odoo-network
# networks:
#   odoo-network:
# volumes:
#   odoo_data:
#   db_data:
# """


        # Docker Compose and Nginx configuration content
#         docker_compose_content = f"""
# version: '3.9'
# services:
#     odoo:
#         image: odoo:17.0
#         restart: always
#         tty: true
#         volumes:
#              - ./custom_addons:/mnt/extra-addons
#              - ./config:/etc/odoo
#              - odoo_data:/var/lib/odoo
#         ports:
#              - "8069:8069"
#              - "8072:8072"
# volumes:
#     odoo_data:
# """




        odoo_conf_content = f"""
[options]
admin_passwd = {master_password}
db_host = {os.getenv('MS_DB_HOST')}
db_user = {setup.db_user}
db_password = {setup.db_password}
addons_path = /mnt/extra-addons,/mnt/odoo/addons

data_dir = /var/lib/odoo
proxy_mode = True
dbfilter = .*
http_port = 8069
longpolling_port = 8072
limit_memory_hard = 1677721600
limit_memory_soft = 629145600
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
max_cron_threads = 1
workers = 5

logfile = /var/log/odoo/odoo-server.log
"""

        # odoo_conf_content = f"""
        # [options]
        # ; This is the password that allows database operations:
        # admin_passwd = admin
        # addons_path = /mnt/extra-addons
        # data_dir = /var/lib/odoo
        # db_host = {os.getenv('MS_DB_HOST')}
        # db_port = {os.getenv('MS_DB_PORT')}
        # db_user = {setup.db_user}
        # db_password = {setup.db_password}
        # proxy_mode = True
        # ; dbfilter = .*
        # xmlrpc_port = 8069
        # longpolling_port = 8072
        # ; limit_memory_hard = 1677721600
        # ; limit_memory_soft = 629145600
        # limit_request = 8192
        # limit_time_cpu = 600
        # limit_time_real = 1200
        # max_cron_threads = 1
        # workers = 5
        # """





        nginx_conf_content = f"""
upstream odoo {{
 server 127.0.0.1:8069;
}}

upstream odoochat {{
 server 127.0.0.1:8072;
}}

server {{
    listen 80;
    server_name {setup.domain} www.{setup.domain};  # Replace with actual domain

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
            if not ssh_transfer_file(instance_public_ip, 'ubuntu', setup.private_key, 'docker-compose.yml',
                                     docker_compose_content, 'odoo1/docker-compose.yml'):
                messages.error(request, "Failed to transfer Docker Compose file.")
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)

            # Create and transfer Odoo config file
            if not ssh_transfer_file(instance_public_ip, 'ubuntu', setup.private_key, 'odoo.conf', odoo_conf_content,
                                     'odoo1/config/odoo.conf'):
                messages.error(request, "Failed to transfer Odoo config file.")
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)

            # Run Docker Compose
            run_docker_cmd = 'cd odoo1 && sudo docker-compose up -d'
            if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, [run_docker_cmd]):
                messages.error(request, "Failed to start Docker containers.")
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)

            # Remove default Nginx config
            remove_nginx_default_cmd = 'sudo rm /etc/nginx/sites-enabled/default || true'
            if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, [remove_nginx_default_cmd]):
                messages.error(request, "Failed to remove default Nginx config.")
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)

            # Create and transfer Nginx config file
            if not ssh_transfer_file(instance_public_ip, 'ubuntu', setup.private_key, 'nginx.conf', nginx_conf_content,
                                     '/etc/nginx/sites-available/odoo.conf'):
                messages.error(request, "Failed to transfer Nginx config file.")
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)

            # Create symlink for Nginx config
            nginx_commands = [
                'sudo ln -s /etc/nginx/sites-available/odoo.conf /etc/nginx/sites-enabled/',
                'sudo nginx -t',
                'sudo systemctl restart nginx.service',
                f'sudo certbot --nginx -d {setup.domain} -d www.{setup.domain} --register-unsafely-without-email --agree-tos --no-eff-email'
            ]
            if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, nginx_commands):
                messages.error(request, "Failed to configure Nginx.")
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)

            # Check if Docker containers are running
            check_docker_cmd = 'sudo docker ps --format "{{.Names}}"'
            container_names = ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, [check_docker_cmd],
                                                  get_output=True)
            # if 'odoo' in container_names and 'db' in container_names:
            if 'odoo' in container_names:
                print('Odoo deployment successful.')
                messages.success(request, f"Odoo deployment successful.")
            else:
                print('Docker containers not running as expected.')
                messages.error(request, "Docker containers not running as expected.")
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
        else:
            print('Odoo deployment failed.')
            messages.error(request, "Odoo deployment failed.")
            return redirect('addMyDomain', company_info_id, setup.subscription_package.id)

    except OdooDomainSetup.DoesNotExist:
        messages.error(request, "Setup not found.")
        return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
    except Exception as e:
        print(f"Error during deployment: {e}")
        messages.error(request, "Error during deployment.")
        return redirect('addMyDomain', company_info_id, setup.subscription_package.id)

    # return redirect('step4_setup_company', company_info_id, setup_id)
    return redirect('create_odoo_database', company_info_id, setup_id)



# import boto3
# import time
#
# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
#
# @login_required
# def setup_odoo_docker_view(request, setup_id, company_info_id):
#     if request.method != "POST":
#         messages.error(request, "Invalid request method.")
#         return redirect('step3_launge_odoo_page', setup_id, company_info_id)
#
#     try:
#         setup = OdooDomainSetup.objects.get(id=setup_id)
#
#         # Retrieve POST data
#         master_password = request.POST.get('master_password')
#         Database_Name = request.POST.get('Database_Name')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         phone_number = request.POST.get('phone_number')
#         language = request.POST.get('language')
#         country_code = request.POST.get('country_code')
#         demo_data = request.POST.get('demo_data')
#
#         # Check if Database_Name already exists
#         if OdooDomainSetup.objects.filter(Database_Name=Database_Name).exists():
#             messages.error(request, "Database Name already exists!")
#             return redirect('step3_launge_odoo_page', setup_id, company_info_id)
#
#         # Update setup object
#         setup.Master_Password = master_password
#         setup.Database_Name = Database_Name
#         setup.email = email
#         setup.password = password
#         setup.phone_number = phone_number
#         setup.language = language
#         setup.country_code = country_code
#         setup.demo_data = demo_data is not None
#
#         unique_suffix = str(uuid.uuid4()).split('-')[0]
#         db_user = f"{setup.domain.replace('.', '_')}_{unique_suffix}"
#         db_password = f"{setup.domain.replace('.', '_')}_{unique_suffix}"
#         setup.db_user = db_user
#         setup.db_password = db_password
#         setup.save()
#
#         instance_public_ip = setup.instance_public_ip
#
#         logger.info(f"Instance Public IP: {instance_public_ip}")
#         logger.info(f"DB User: {setup.db_user}")
#
#         # Create PostgreSQL user
#         if not create_postgresql_user(setup.db_user, setup.db_password):
#             messages.error(request, "Failed to create PostgreSQL user.")
#             return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
#
#         # Clone Odoo repository
#         clone_odoo_repo_commands = [
#             'git clone https://github.com/odoo/odoo.git -b 17.0 --depth 1 /home/ubuntu/odoo'
#         ]
#         if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, clone_odoo_repo_commands):
#             messages.error(request, "Failed to clone Odoo repository.")
#             return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
#
#         # Docker Compose and Nginx configuration content
#         docker_compose_content = f"""
# version: '3.9'
# services:
#     odoo:
#         image: odoo:17.0
#         restart: always
#         tty: true
#         command: -c /etc/odoo/odoo.conf
#         volumes:
#             - ./custom_addons:/mnt/extra-addons
#             - ./config:/etc/odoo
#             - /home/ubuntu/odoo:/mnt/odoo
#             - odoo_data:/var/lib/odoo
#         ports:
#             - "8069:8069"
#             - "8072:8072"  # Expose Odoo longpolling port
#         networks:
#             - odoo-network
# networks:
#   odoo-network:
# volumes:
#   odoo_data:
# """
#
#         odoo_conf_content = f"""
# [options]
# admin_passwd = {master_password}
# db_host = {os.getenv('MS_DB_HOST')}
# db_user = {setup.db_user}
# db_password = {setup.db_password}
# addons_path = /mnt/extra-addons,/mnt/odoo/addons
# data_dir = /var/lib/odoo
# proxy_mode = True
# dbfilter = .*
# http_port = 8069
# longpolling_port = 8072
# limit_memory_hard = 1677721600
# limit_memory_soft = 629145600
# limit_request = 8192
# limit_time_cpu = 600
# limit_time_real = 1200
# max_cron_threads = 1
# workers = 5
# logfile = /var/log/odoo/odoo-server.log
# """
#
#         nginx_conf_content = f"""
# upstream odoo {{
#  server 127.0.0.1:8069;
# }}
#
# upstream odoochat {{
#  server 127.0.0.1:8072;
# }}
#
# server {{
#     listen 80;
#     server_name {setup.domain} www.{setup.domain};  # Replace with actual domain
#
#     proxy_read_timeout 720s;
#     proxy_connect_timeout 720s;
#     proxy_send_timeout 720s;
#
#     # Proxy headers
#     proxy_set_header X-Forwarded-Host $host;
#     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#     proxy_set_header X-Forwarded-Proto $scheme;
#     proxy_set_header X-Real-IP $remote_addr;
#
#     # log files
#     access_log /var/log/nginx/odoo.access.log;
#     error_log /var/log/nginx/odoo.error.log;
#
#     # Handle longpoll requests
#     location /longpolling {{
#         proxy_pass http://odoochat;
#     }}
#
#     # Handle / requests
#     location / {{
#        proxy_redirect off;
#        proxy_pass http://odoo;
#     }}
#
#     # Cache static files
#     location ~* /web/static/ {{
#         proxy_cache_valid 200 90m;
#         proxy_buffering on;
#         expires 864000;
#         proxy_pass http://odoo;
#     }}
#
#     # Gzip
#     gzip_types text/css text/less text/plain text/xml application/xml application/json application/javascript;
#     gzip on;
# }}
# """
#
#         # Commands to be executed on the remote server
#         commands = [
#             'sudo apt update',
#             'sudo apt install -y docker.io docker-compose nginx python3-certbot-nginx',
#             'sudo systemctl start docker',
#             'sudo systemctl enable docker',
#             'sudo docker rm -f db odoo || true',
#             'sudo docker network create odoo-network || true',
#             'mkdir -p odoo1/config odoo1/custom_addons',
#         ]
#
#         if ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, commands):
#             # Create and transfer Docker Compose file
#             if not ssh_transfer_file(instance_public_ip, 'ubuntu', setup.private_key, 'docker-compose.yml',
#                                      docker_compose_content, 'odoo1/docker-compose.yml'):
#                 messages.error(request, "Failed to transfer Docker Compose file.")
#                 return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
#
#             # Create and transfer Odoo config file
#             if not ssh_transfer_file(instance_public_ip, 'ubuntu', setup.private_key, 'odoo.conf', odoo_conf_content,
#                                      'odoo1/config/odoo.conf'):
#                 messages.error(request, "Failed to transfer Odoo config file.")
#                 return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
#
#             # Run Docker Compose
#             run_docker_cmd = 'cd odoo1 && sudo docker-compose up -d'
#             if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, [run_docker_cmd]):
#                 messages.error(request, "Failed to start Docker containers.")
#                 return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
#
#             # Remove default Nginx config
#             remove_nginx_default_cmd = 'sudo rm /etc/nginx/sites-enabled/default || true'
#             if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, [remove_nginx_default_cmd]):
#                 messages.error(request, "Failed to remove default Nginx config.")
#                 return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
#
#             # Create and transfer Nginx config file
#             if not ssh_transfer_file(instance_public_ip, 'ubuntu', setup.private_key, 'nginx.conf', nginx_conf_content,
#                                      '/etc/nginx/sites-available/odoo.conf'):
#                 messages.error(request, "Failed to transfer Nginx config file.")
#                 return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
#
#             # Create symlink for Nginx config
#             nginx_commands = [
#                 'sudo ln -s /etc/nginx/sites-available/odoo.conf /etc/nginx/sites-enabled/',
#                 'sudo nginx -t',
#                 'sudo systemctl restart nginx.service',
#                 f'sudo certbot --nginx -d {setup.domain} -d www.{setup.domain} --register-unsafely-without-email --agree-tos --no-eff-email'
#             ]
#             if not ssh_execute_command(instance_public_ip, 'ubuntu', setup.private_key, nginx_commands):
#                 messages.error(request, "Failed to set up Nginx and SSL certificates.")
#                 return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
#
#             messages.success(request, "Odoo setup and Docker containers started successfully!")
#             return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
#         else:
#             messages.error(request, "Failed to execute initial setup commands.")
#             return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
#
#     except OdooDomainSetup.DoesNotExist:
#         messages.error(request, "Setup object not found.")
#         return redirect('step3_launge_odoo_page', setup_id, company_info_id)
#
#     except Exception as e:
#         logger.error(f"Error during Odoo Docker setup: {e}")
#         messages.error(request, f"Error during Odoo Docker setup: {e}")
#         return redirect('addMyDomain', company_info_id, setup.subscription_package.id)





def create_odoo_database(request, company_info_id, setup_id):
    setup = OdooDomainSetup.objects.get(id=setup_id)
    logger.info("Creating Odoo Database ...")

    # Retrieve setup details
    master_password = setup.Master_Password
    database_name = setup.Database_Name
    email = setup.email
    password = setup.password
    phone_number = setup.phone_number
    language = setup.language
    country_code = setup.country_code
    demo_data = setup.demo_data == 'true'

    # Odoo server details
    url = f'http://{setup.static_ip}'
    admin_password = master_password

    # Database details
    new_db_name = database_name
    admin_login = email
    admin_pass = password
    admin_lang = language

    # XML-RPC endpoints
    common_url = f'{url}/xmlrpc/2/common'
    object_url = f'{url}/xmlrpc/2/object'
    db_url = f'{url}/xmlrpc/2/db'

    # Create a new database
    try:
        db = xmlrpc.client.ServerProxy(db_url, allow_none=True)
        db.create_database(admin_password, new_db_name, demo_data, admin_lang, admin_pass, admin_login)
        logger.info(f"Database '{new_db_name}' created successfully.")
    except Exception as e:
        logger.error(f"An error occurred while creating the database: {e}")
        return JsonResponse({'status': 'error', 'message': 'Failed to create database', 'details': str(e)})

    # Authenticate and get UID
    try:
        common = xmlrpc.client.ServerProxy(common_url, allow_none=True)
        uid = common.authenticate(new_db_name, admin_login, admin_pass, {})
        logger.info(f"Authenticated with UID: {uid}")
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return JsonResponse({'status': 'error', 'message': 'Authentication failed', 'details': str(e)})

    # Check installed modules
    if 'uid' in locals():
        try:
            models = xmlrpc.client.ServerProxy(object_url, allow_none=True)
            installed_modules = models.execute_kw(new_db_name, uid, admin_pass, 'ir.module.module', 'search_read',
                                                  [[['state', '=', 'installed']]], {'fields': ['name']})
            logger.info(f"Installed modules: {installed_modules}")
        except Exception as e:
            logger.error(f"Error fetching modules: {e}")

    setup.deployed = True
    setup.save()

    return redirect('step4_setup_company', company_info_id, setup_id)


@login_required
def step4_setup_company(request, company_info_id, setup_id):
    setup = OdooDomainSetup.objects.get(id=setup_id)
    getSubcription = SubscriptionInformation.objects.filter(id=setup.subscription_package.id).last()
    try:
        check_odoo_instance = OdooDomainSetup.objects.filter(subscription_package=getSubcription)
        if check_odoo_instance:
            getOdooDomain = OdooDomainSetup.objects.filter(subscription_package=getSubcription).last()
            if getOdooDomain.domain:
                # already have domain
                if getOdooDomain.confirmed:
                    # ip is confirmed
                    if getOdooDomain.deployed:
                        # deployed
                        if getOdooDomain.setup_company:
                            # setup company
                            if getOdooDomain.installations:
                                return redirect("odoo_landing_page", company_info_id, setup_id)
                            else:
                                return redirect("step5_installation", company_info_id, setup_id)
                        else:
                            pass
                    else:
                        return redirect('step3_launge_odoo_page', company_info_id, setup_id)
                else:
                    return redirect('confirm_ip', company_info_id, setup_id)
            else:
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
        else:
            return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
    except Exception as e:
        print(f'Failed to check odoo instance : {e}')

    setup = OdooDomainSetup.objects.get(id=setup_id)

    company_info = CompanyRegistrationInformation.objects.get(id=company_info_id)
    return render(request, 'Automatic_Deployment/setup_company.html',
                  {'setup': setup, 'company_info': company_info, 'user_info': request.user})



from User_Registration_App.utils import odooo_company_and_website_create
from subscription_app.models import ErpActiveCompanyAndWeb
def finish_setup_company(request, company_info_id, setup_id):
    setup = OdooDomainSetup.objects.get(id=setup_id)

    subcription = SubscriptionInformation.objects.filter(id=setup.subscription_package.id).last()


    c_name = subcription.company_info.file_number+"1233"
    w_name = subcription.company_info.file_number+"1233"
    # domain = setup.static_ip
    domain = f'http://{setup.static_ip}'

    url = f'http://{setup.static_ip}'
    db = setup.Database_Name
    username = setup.email
    password = setup.password

    res = odooo_company_and_website_create(url, db, username, password, c_name, w_name, domain)
    if res == None:
        messages.warning(request,
                         'Please make sure the erp name and erp site name is uniq and erp smtp server is a domain and try again !')
        return redirect('step4_setup_company', company_info_id, setup_id)
    else:
        company_id = res[0]
        website_id = res[1]
        try:
            user_count = int(setup.subscription_package.number_of_expected_users_of_the_platform)
        except:
            user_count = 0


        Eerp_active = ErpActiveCompanyAndWeb(
            subscription_info=subcription,
            # Erp_Info=erp_info,
            company_id=company_id,
            website_id=website_id,
            domain=domain,
            user_count=user_count,
        )
        Eerp_active.save()
        messages.success(request, "Successfully install cmpany and website")

        setup.setup_company = True
        setup.save()
        return redirect('step5_installation', company_info_id, setup_id)


@login_required
def step5_installation(request, company_info_id, setup_id):
    setup = OdooDomainSetup.objects.get(id=setup_id)
    getSubcription = SubscriptionInformation.objects.filter(id=setup.subscription_package.id).last()
    try:
        check_odoo_instance = OdooDomainSetup.objects.filter(subscription_package=getSubcription)
        if check_odoo_instance:
            getOdooDomain = OdooDomainSetup.objects.filter(subscription_package=getSubcription).last()
            if getOdooDomain.domain:
                # already have domain
                if getOdooDomain.confirmed:
                    # ip is confirmed
                    if getOdooDomain.deployed:
                        # deployed
                        if getOdooDomain.setup_company:
                            # setup company
                            if getOdooDomain.installations:
                                return redirect("odoo_landing_page", company_info_id, setup_id)
                            else:
                                pass
                        else:
                            return redirect("step4_setup_company", company_info_id, setup_id)
                    else:
                        return redirect('step3_launge_odoo_page', company_info_id, setup_id)
                else:
                    return redirect('confirm_ip', company_info_id, setup_id)
            else:
                return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
        else:
            return redirect('addMyDomain', company_info_id, setup.subscription_package.id)
    except Exception as e:
        print(f'Failed to check odoo instance : {e}')

    setup = OdooDomainSetup.objects.get(id=setup_id)

    company_info = CompanyRegistrationInformation.objects.get(id=company_info_id)
    return render(request, 'Automatic_Deployment/installations.html',
                  {'setup': setup, 'company_info': company_info, 'user_info': request.user})



def finish_installation(request, company_info_id, setup_id):
    setup = OdooDomainSetup.objects.get(id=setup_id)

    subcription = SubscriptionInformation.objects.filter(id=setup.subscription_package.id).last()
    type = subcription.select_erp_business_type
    pmpt = PriceMatrixPerCompanyType.objects.filter(company_type_or_industry=type).last()

    modules_string = pmpt.module
    modules_list = [module.strip().strip("'") for module in modules_string.split(',')]

    url = f'http://{setup.static_ip}'
    db = setup.Database_Name
    username = setup.email
    password = setup.password

    res = install_the_modules(url, db, username, password, modules_list)
    ko=9
    if res == 'Done':
        setup.installations = True
        setup.save()
        return redirect('odoo_landing_page', company_info_id, setup_id)
    else:
        messages.warning('Please try again !')
        return redirect("step5_installation", company_info_id, setup_id)


@login_required
def odoo_landing_page(request, company_info_id, setup_id):
    setup = OdooDomainSetup.objects.get(id=setup_id)
    company_info = CompanyRegistrationInformation.objects.get(id=company_info_id)

    subcription_one = SubscriptionInformation.objects.filter(company_info=company_info, payment_status=True).last()
    erp_active = ErpActiveCompanyAndWeb.objects.filter(subscription_info=subcription_one).last()
    try:
        erp_active_id = erp_active.id
    except:
        erp_active_id = None
    return render(request, "Automatic_Deployment/successpage.html", {'setup': setup, 'company_info': company_info, 'user_info': request.user, 'subcription_one':subcription_one, 'erp_active':erp_active, 'erp_active_id':erp_active_id})


