# HelloWorld-Bot
HelloWorld Bot backend implementation for Telegram. It also contains all the data for deployment.  

# Data Naming convention
Till date there is single version of collected data and the naming convention is as `Destination_<major_minor>`. Where `major` defines addition of new columns and drastic change in the number of rows and `minor` signifies slight change in the data content.

Data can be found in `data` directory with their respective version number. 

Due to large size of the data, developer has to wget it to `data` directory in the repo before use. Data is stored [here](https://www.dropbox.com/sh/kho4jd47842khi3/AACoZXFzjns7WnK8ILs8DMSca). 

# Production Deployment
1. Create digital ocean droplet (with standalone login access), login with root access and create user:
```
adduser <user>
usermod -aG sudo <user>
```
Logout and login back with the new `user` and new `password`.

2. Install nginx:
```
sudo apt update
sudo apt install nginx
```
Check web server status using: 
```
systemctl status nginx
```

3. Add domain name to the droplet, in our case its 'mycolumbus.xyz' (Test domain).

4. Install python dependencies: 
```
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools libsm6 libxext6 libxrender1
```

5. Create Python Virtual environment: 
```
sudo apt install python3-venv
mkdir hwbot
cd hwbot
python3.6 -m venv hwbot
source hwbot/bin/activate
```

6. Install Gunicorn and Flask
```
pip install wheel
pip install gunicorn
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

7. Time to clone hello-world-bot project and install all the project requirements: 
```
cd ~
git clone https://github.com/milinddeore/hello-world-bot.git
cd ~/hwbot
mv ~/hello-world-bot/hello-world-bot-webhook/* .
pip install --requirement requirements.txt
```

8. Test it once if the server is reachable by running following command: 
```
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

9. open URL in browser 'http://mycolumbus.xyz:5000'

10. Deactivate and come out of virtual environment
```
deactivate
```

11. Create hwbot as system service: 
```
sudo vim /etc/systemd/system/hwbot.service

## add following lines to the file
[Unit]
Description=Gunicorn instance to serve Hello World Bot
After=network.target

[Service]
User=mdeore
Group=www-data
WorkingDirectory=/home/mdeore/hwbot
Environment="PATH=/home/mdeore/hwbot/hwbot/bin"
ExecStart=/home/mdeore/hwbot/hwbot/bin/gunicorn --workers 3 --log-level=debug --timeout 60 --bind unix:hwbot.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```
Make the necessary changed if required. 

12. Start and enable service: 
```
sudo systemctl start hwbot
sudo systemctl enable hwbot
```

13. Check the status of the service: 
```
sudo systemctl status hwbot
```

14. Configure Nginx to proxy request to Gunicorn.

14.1 but first create new server configuration for our project:
```
sudo vim /etc/nginx/sites-available/hwbot

# Add following line to the configuration file: 
server {
    listen 80;
    server_name mycolumbus.xyz;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/mdeore/hwbot/hwbot.sock;
    }
}
```

14.2 Enable nginx server with this new configuration: 
```
sudo ln -s /etc/nginx/sites-available/hwbot /etc/nginx/sites-enabled
```

14.3 Check if everything is fine with nginx
```
sudo nginx -t
```

14.4 Restart nginx, so that new configuration should get applied:
```
sudo systemctl restart nginx
```

15. Time to Secure site, by applying SSL certificate.
```
sudo add-apt-repository ppa:certbot/certbot
sudo apt install python-certbot-nginx
sudo certbot --nginx -d mycolumbus.xyz
```
Follow the instructions. 

16. Now, access URl https://mycolumbus.xyz

If this return data, which means its time to day HIP HIP HURRAY !!!



Following detailed instructions from [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)
