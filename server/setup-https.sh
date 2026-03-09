#!/bin/bash

# Script d'installation HTTPS automatique pour le serveur GTFS Cache
# Usage: sudo ./setup-https.sh votre-domaine.com votre@email.com

set -e  # Arrêt en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Vérifier que le script est lancé en root
if [ "$EUID" -ne 0 ]; then 
    error "Ce script doit être lancé avec sudo"
fi

# Vérifier les arguments
if [ $# -lt 2 ]; then
    error "Usage: sudo ./setup-https.sh votre-domaine.com votre@email.com"
fi

DOMAIN=$1
EMAIL=$2

info "Configuration HTTPS pour le domaine: $DOMAIN"
info "Email pour Let's Encrypt: $EMAIL"

# Vérifier que le domaine pointe vers ce serveur
info "Vérification DNS..."
SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

if [ -z "$DOMAIN_IP" ]; then
    error "Le domaine $DOMAIN ne résout vers aucune IP. Vérifiez votre configuration DNS."
fi

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    warning "Le domaine $DOMAIN pointe vers $DOMAIN_IP mais ce serveur a l'IP $SERVER_IP"
    read -p "Voulez-vous continuer quand même ? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Installation de Certbot si nécessaire
if ! command -v certbot &> /dev/null; then
    info "Installation de Certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
else
    info "Certbot est déjà installé"
fi

# Installation de Nginx si nécessaire
if ! command -v nginx &> /dev/null; then
    info "Installation de Nginx..."
    apt install -y nginx
    systemctl start nginx
    systemctl enable nginx
else
    info "Nginx est déjà installé"
fi

# Créer le répertoire de configuration si nécessaire
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# Backup de l'ancienne configuration si elle existe
if [ -f /etc/nginx/sites-available/gtfs-cache ]; then
    info "Sauvegarde de l'ancienne configuration..."
    cp /etc/nginx/sites-available/gtfs-cache /etc/nginx/sites-available/gtfs-cache.backup.$(date +%Y%m%d_%H%M%S)
fi

# Créer la configuration Nginx
info "Création de la configuration Nginx..."
cat > /etc/nginx/sites-available/gtfs-cache << EOF
# Configuration Nginx avec HTTPS
# Généré automatiquement le $(date)

# Redirection HTTP → HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# Configuration HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
    
    if (\$request_method = 'OPTIONS') {
        return 204;
    }

    access_log /var/log/nginx/gtfs-cache-access.log;
    error_log /var/log/nginx/gtfs-cache-error.log;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Activer le site
info "Activation du site..."
ln -sf /etc/nginx/sites-available/gtfs-cache /etc/nginx/sites-enabled/

# Supprimer le site par défaut si présent
if [ -f /etc/nginx/sites-enabled/default ]; then
    info "Désactivation du site par défaut Nginx..."
    rm -f /etc/nginx/sites-enabled/default
fi

# Tester la configuration Nginx
info "Test de la configuration Nginx..."
nginx -t || error "La configuration Nginx est invalide"

# Recharger Nginx
info "Rechargement de Nginx..."
systemctl reload nginx

# Vérifier que le serveur Node.js tourne
if ! systemctl is-active --quiet gtfs-cache; then
    warning "Le service gtfs-cache ne semble pas actif"
    info "Vérifiez avec: sudo systemctl status gtfs-cache"
fi

# Obtenir le certificat SSL
info "Obtention du certificat SSL avec Let's Encrypt..."
info "Cela peut prendre quelques secondes..."

certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --no-eff-email --redirect || error "Échec de l'obtention du certificat SSL"

# Vérifier le renouvellement automatique
info "Configuration du renouvellement automatique..."
systemctl enable certbot.timer
systemctl start certbot.timer

# Test du renouvellement
info "Test du renouvellement automatique..."
certbot renew --dry-run || warning "Le test de renouvellement a échoué, mais le certificat est installé"

# Configuration du pare-feu si UFW est actif
if command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
    info "Configuration du pare-feu UFW..."
    ufw allow 443/tcp comment "HTTPS pour GTFS Cache"
    ufw allow 80/tcp comment "HTTP pour Let's Encrypt"
fi

# Afficher le résumé
echo
info "=========================================="
info "✅ Installation HTTPS terminée avec succès !"
info "=========================================="
echo
info "Votre serveur GTFS est maintenant accessible via:"
info "  🔒 https://$DOMAIN"
echo
info "Certificat SSL:"
info "  - Émis par: Let's Encrypt"
info "  - Valide pour: 90 jours"
info "  - Renouvellement: Automatique"
echo
info "Prochaines étapes:"
info "  1. Testez: curl https://$DOMAIN/health"
info "  2. Mettez à jour votre code client avec la nouvelle URL HTTPS"
info "  3. Vérifiez le renouvellement auto: sudo certbot renew --dry-run"
echo
info "Logs Nginx:"
info "  - Access: /var/log/nginx/gtfs-cache-access.log"
info "  - Errors: /var/log/nginx/gtfs-cache-error.log"
echo
info "Pour vérifier la qualité SSL:"
info "  https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo

exit 0
