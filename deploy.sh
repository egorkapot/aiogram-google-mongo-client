if command -v docker > /dev/null && command -v docker-compose &> /dev/null; then
    echo "Docker environment is already installed"
else
    # Install dependencies and add the Docker repository
    apt-get update -y && apt-get install ca-certificates curl gnupg lsb-release -y
    mkdir -p /etc/apt/keyrings
    curl -fsSL -q https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker and Docker Compose
    apt-get install docker-ce docker-ce-cli containerd.io -y
    curl -L -q "https://github.com/docker/compose/releases/download/v2.6.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "Docker has been installed"
fi


TIER=$1 #pass the tier as the first argument while running script
if [ "$TIER" = "production" ] || [ "$TIER" = "development" ]; then
    export $TIER
  else
    echo "Invalid environment specified"
    exit 1
fi

docker build -t telegram_access_bot:latest
docker-compose up --build