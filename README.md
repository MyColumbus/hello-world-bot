# HelloWorld-Bot
HelloWorld Bot backend implementation for Telegram. It also contains all the data for deployment.  

# Data Naming convention
Till date there is single version of collected data and the naming convention is as `Destination_v<major.minor>`. Where `major` defines addition of new columns and drastic change in the number of rows and `minor` signifies slight change in the data content.

Data can be found in `data` directory with their respective version number. 

# Production Deployment
1. Create digital ocean droplet (with standalone login access), login with root access and create user:
```
adduser <user>
usermod -aG sudo <user>
```
2. Install nginx:
```
sudo apt update
sudo apt install nginx
```
Check web server status using: 
```
systemctl status nginx
```

3. Add domain name to the droplet, in our case its 'thecolumbus.xyz'.

4. Install python dependencies: 
```
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools libsm6 libxext6 libxrender1
```

5. Create Python Virtual environment: 
```
sudo apt install python3-venv
mkdir mycolumbus
cd mycolumbus
python3.6 -m venv mycolumbus
source mycolumbus/bin/activate
```

6. Install Gunicorn and Flask
```
pip install wheel
pip install gunicorn

## For Telegram ##
pip install python-telegram-bot --upgrade

```

7. Time to clone mycolumbus-ml project and install all the project requirements: 
```
git clone https://github.com/milinddeore/columbus-ml.git
mv columbus-ml/columbus-ml-app/* .
pip install --requirement requirements.txt
mkdir model
wget https://www.dropbox.com/s/e5fpw8szsxz4849/modelearth_v2.1.cpkl -P ./model
rm -rf columbus-ml
```

8. Test it once if the server is reachable by running following command: 
```
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

9. open URL in browser 'http://thecolumbus.xyz:5000'

10. Deactivate and come out of virtual environment
```
deactivate
```

11. Create mycolumbus as system service: 
```
sudo vim /etc/systemd/system/mycolumbus.service

# add following lines to the file
[Unit]
Description=Gunicorn instance to serve mycolumbus
After=network.target

[Service]
User=mdeore
Group=www-data
WorkingDirectory=/home/mdeore/mycolumbus
Environment="PATH=/home/mdeore/mycolumbus/mycolumbus/bin"
ExecStart=/home/mdeore/mycolumbus/mycolumbus/bin/gunicorn --workers 3 --bind unix:mycolumbus.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```
Make the necessary changed if required. 

12. Start and enable service: 
```
sudo systemctl start mycolumbus
sudo systemctl enable mycolumbus
```

13. Check the status of the service: 
```
sudo systemctl status mycolumbus
```

14. Configure Nginx to proxy request to Gunicorn.

14.1 but first create new server configuration for our project:
```
sudo vim /etc/nginx/sites-available/mycolumbus

# Add following line to the configuration file: 
server {
    listen 80;
    server_name thecolumbus.xyz;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/mdeore/mycolumbus/mycolumbus.sock;
    }
}
```

14.2 Enable nginx server with this new configuration: 
```
sudo ln -s /etc/nginx/sites-available/mycolumbus /etc/nginx/sites-enabled
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
sudo certbot --nginx -d thecolumbus.xyz
```
Follow the instructions. 

16. Now, access URl https://thecolumbus.xyz

If this return data, which means its time to day HIP HIP HURRAY !!!



Following detailed instructions from [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)


# Postgress Requirements
Install python binding

```
sudo apt-get install libpq-dev
pip install psycopg2
```

