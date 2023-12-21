echo "Starting deploy.sh script..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing Docker..."
    apt-get update -y
    apt-get install -y docker.io
    echo "Docker installation complete."
else
    echo "Docker is already installed."
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.6.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installation complete."
else
    echo "Docker Compose is already installed."
fi

echo "Creating .env file..."
cat << EOF > .env
PRODUCTION_BOT_TOKEN=$PRODUCTION_BOT_TOKEN
DEVELOPMENT_BOT_TOKEN=$DEVELOPMENT_BOT_TOKEN
AUTHOR_CHAT_ID=$AUTHOR_CHAT_ID
GUIDE_LINK=$GUIDE_LINK
WEB_CONTENT_TABLE_LINK=$WEB_CONTENT_TABLE_LINK
WEB_AI_CONTENT_TABLE_LINK=$WEB_AI_CONTENT_TABLE_LINK
SEO_CONTENT_TABLE_LINK=$SEO_CONTENT_TABLE_LINK
BACKUP_TABLE_LINK=$BACKUP_TABLE_LINK
DUPLICHEKER_TOKEN=$DUPLICHEKER_TOKEN
WEB_CONTENT_CHAT_ID=$WEB_CONTENT_CHAT_ID
EOF

echo "Printing environment variable values for debugging..."
echo "PRODUCTION_BOT_TOKEN: $PRODUCTION_BOT_TOKEN"
echo "DEVELOPMENT_BOT_TOKEN: $DEVELOPMENT_BOT_TOKEN"
echo "AUTHOR_CHAT_ID: $AUTHOR_CHAT_ID"
echo "GUIDE_LINK: $GUIDE_LINK"
echo "WEB_CONTENT_TABLE_LINK: $WEB_CONTENT_TABLE_LINK"
echo "WEB_AI_CONTENT_TABLE_LINK: $WEB_AI_CONTENT_TABLE_LINK"
echo "SEO_CONTENT_TABLE_LINK: $SEO_CONTENT_TABLE_LINK"
echo "BACKUP_TABLE_LINK: $BACKUP_TABLE_LINK"
echo "DUPLICHEKER_TOKEN: $DUPLICHEKER_TOKEN"
echo "WEB_CONTENT_CHAT_ID: $WEB_CONTENT_CHAT_ID"

TIER=$1 #pass the tier as the first argument while running script
if [ "$TIER" = "production" ] || [ "$TIER" = "development" ]; then
    export $TIER
  else
    echo "Invalid environment specified"
    exit 1
fi

docker-compose up --build -d