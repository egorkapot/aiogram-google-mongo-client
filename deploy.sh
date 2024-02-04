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

#Create a tier based on the first argument while running script
TIER=$1
if [ "$TIER" = "production" ] || [ "$TIER" = "development" ]; then
    export $TIER
  else
    echo "Invalid environment specified"
    exit 1
fi


echo "Creating .env file..."
cat << EOF > .env
TIER=$TIER
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
MONGO_ROOT_USER=$MONGO_ROOT_USER
MONGO_ROOT_PASS=$MONGO_ROOT_PASS
MONGO_USERNAME=$MONGO_USERNAME
MONGO_PASSWORD=$MONGO_PASSWORD
EOF

docker-compose up --build -d