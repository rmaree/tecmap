# GTFS-Realtime cache server

Lightweight server in node.js to put GTFS-Realtime data from remote source (with limited-access API key) into cache
and serve JSON/raw data to multiple clients

## Goal

This server acts like a proxy/cache between the GTFS-Realtime API from your public transport provider and front-end application.
It allows to reduce calls to API (only the server does, not the clients) and simplify data to deliver smaller data to the clients.

## Internals

```
┌──────────────────────────┐
│  GTFS RealTime API Source     │ ← Request every 10 seconds
│  (Protobuf)              │
└────────┬─────────────────┘
         │
         ▼
┌─────────────────┐
│  Cache Serve    │
│  - Decoding     │
│  - JSON convert │
│  - Store        │
└────────┬────────┘
         │
         ├──→ Client 1 (JSON)
         ├──→ Client 2 (JSON)
         ├──→ Client 3 (JSON)
         └──→ Client ... (JSON)
```

## Technologies

- **Node.js** - Runtime JavaScript
- **Express** - minimalist web framework
- **gtfs-realtime-bindings** - decode protobuf GTFS-RT
- **CORS** - handle cross-origin requests

## Installation

On your Linux-based system (tested on Ubuntu). This doc should be improved but we provide it as is for now.

```
sudo apt update
sudo apt upgrade -y

# Install last node.js version
Follows https://nodejs.org/en/download
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"
# Download and install Node.js:
nvm install 24
# Verify the Node.js version:
node -v # Should print "v24.13.1".
# Verify npm version:
npm -v # Should print "11.8.0".

# Installation directory
sudo mkdir -p /opt/gtfs-cache-server
sudo chown $USER:$USER /opt/gtfs-cache-server
cd /opt/gtfs-cache-server

#copy all files to your server
scp server.js ...@...:/opt/gtfs-cache-server/
scp package.json 
scp .env #contains keys,urls to be configured...
scp gtfs-cache.service 
scp nginx-gtfs-cache
scp setup-https.sh
...

#to host html and data on the server:
#create public and data directory on your server, configure nginx accordingly (see below)
scp tecmap.html ...@...:/opt/gtfs-cache-server/public/
scp data/stop_*.js ...@...:/opt/gtfs-cache-server/public/data/
scp data/routes.js ...@...:/opt/gtfs-cache-server/public/data/
scp data/stops_with_coords.js ...@...:/opt/gtfs-cache-server/public/data/


#config nginx
sudo cp /opt/gtfs-cache-server/gtfs-cache.service /etc/systemd/system/
sudo cp /opt/gtfs-cache-server/nginx-gtfs-cache /etc/nginx/sites-available/gtfs-cache
sudo ln -s /etc/nginx/sites-available/gtfs-cache /etc/nginx/sites-enabled/

#edit server_name in your /etc/nginx/sites-available/gtfs-cache

#start service
sudo systemctl restart nginx
sudo systemctl restart gtfs-cache

#for ssl https
cd /opt/gtfs-cache-server/
chmod u+x setup-https.sh
#get certificate:
sudo certbot --nginx -d XXX_Your_servername
#run setup:
sudo ./setup-https.sh XXX_your_servername your.email@address
#this modifies: /etc/nginx/sites-available/gtfs-cache
systemctl reload nginx
```

### Test server

```bash
cd /opt/gtfs-cache-server
npm install
nano .env  # Configurer vos URLs

# Test
npm start
```

### API endpoints

```
https://your_server_name/api/vehicles
https://your_server_name/api/alerts
https://your_server_name/api/alerts/raw #protobuf
https://your_server_name/api/delays
https://your_server_name/status
```

## Logs & various commands

```bash
# Logs en temps réel
sudo journalctl -u gtfs-cache -f

# restart server
sudo systemctl restart gtfs-cache
```
