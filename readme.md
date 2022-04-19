# CloudFlare-Tunnels-Ingress-Rules-GUI
## How To Install 
1. Install CloudFlared download: [here](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)
2. run `cloudflared login` and chose the website you want to manage (the ability to add more than one site is coming)
3. Create an API token for "edit zone dns" [cloudflared doc](https://developers.cloudflare.com/api/tokens/create/) save this somewhere we will need this later(only one zone is supported)
4. install python3 and pip3 on your debain based distro this is developed on ubuntu 21.10
5. clone this repo to where you want it to be run from
6. install the required python packages with ` pip3 install -r requirements.txt`
7. run the python web server with `python3 main.py`
8. head to your servers ip address with the port number 5000 e.g. `192.168.1.50:5000`
9. login with the default login username:FirstSetup password:FirstSetup
10. You will be greeted with the setup page input what it asks for. The cloudflared path this would be something like `/home/user/.cloudflared/` DO NOT FORGET THE END FORWARD SLASH. Username would be something like Admin and Password would be a password. API key is the key you saved before and RootDomain would be something like example.com.
11. Create your first new rule under create tunnel fill out your first rule click submit then restart cloudflared with restart cloudflared button

# DOCS
coming soon
