#Hosting Command

1. install python and create virtual env:
    sudo apt-get update
    sudo apt-get install -y python3-venv
    python3 -m venv env

if pillow not installing:
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade Pillow


2. activate virtual env, install req.txt packages
    source env/bin/activate

    pip install django==3.0.2
    pip install -r requirements.txt

3. install nginx:
    sudo apt-get install nginx
   
   change the security group

   install gunicorn:
    pip install gunicorn

4. bind gunicorn with wsgi
    gunicorn --bind 0.0.0.0:8000 project_name.wsgi:application

    allow the host in settings.py
    sudo nano project_name/settings.py

    gunicorn --bind 0.0.0.0:8000 project_name.wsgi:application

   try to run :
    ip:8000


sudo systemctl reload nginx


To make it permanent running state
	sudo apt-get install supervisor


cd /etc/supervisor/conf.d/
	sudo touch gunicorn.conf

sudo nano gunicorn.conf:

[program:gunicorn]
directory=/home/ubuntu/project
command=/home/ubuntu/env/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/project/app.sock project_name.wsgi:application
autostart = true
autorestart=true
stderr_logfile= /var/log/gunicorn/gunicorn.err.log
stdout_logfile= /var/log/gunicorn/gunicorn.out.log

[group:guni]
programs:gunicorn



sudo supervisorctl reread
sudo mkdir /var/log/gunicorn

sudo supervisorctl reread

sudo supervisorctl update

sudo supervisorctl status

sudo systemctl reload nginx



cd /etc/nginx/sites-available/

sudo nano default

## make some line into comments - example : root /var/www/html;, index index.html, uri uri try_files ...

and add in location:
include proxy_params;
proxy_pass http://unix:/home/ubuntu/project/app.sock;

add server name ip_address www.domain.com domain.com;


sudo systemctl reload nginx


show statics:
===============
sudo nano default

location /static/{
	autoindex on;
	alias /home/ubuntu/final_test/static/;
	}


sudo systemctl reload nginx

python manage.py collectstatic


to make HTTPS request:
===========================
1. sudo apt-add-repository -r ppa:certbot/certbot
2. sudo apt-get install python3-certbot-nginx
3. sudo certbot --nginx -d YourDomain.com -d www.yourDomain.com
	- 2
	

# if you changes anything need to stop supervisor and start again
sudo systemctl stop supervisor
sudo systemctl start supervisor

# reload the nginx
sudo systemctl reload nginx



# env needed credentials

# Stripe Access Keys Test
STRIPE_PUBLIC_KEY_TEST=value
STRIPE_SECRET_KEY_TEST=value
STRIPE_WEBHOOK_SECRET_TEST=value

#odoo
ODOO_URL=http://127.0.0.1:8069
DB_NAME=odoo
ADMIN_USERNAME=admin@gmail.com
ADMIN_PASSWORD=admin

#postgres
MS_DB_USER=postgres
MS_DB_PASSWORD=value
MS_DB_HOST=value
MS_DB_PORT=5432
MS_DB_NAME=value

#S3
S3_ACCESS_KEY_ID=value
S3_SECRET_ACCESS_KEY=value
AWS_REGION=value

#for email
DEBUG=False
SECRET_KEY=secrete_key

#email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER_TEST=user@example.com
EMAIL_HOST_PASSWORD_TEST='abcd'

# admin will know user subscription info from this email
ADMIN_EMAIL_TO_GET_MESSAGE='mail@example.com'