TIER=$1 #pass the tier as the first argument while running script
if [ "$TIER" = "production" ] || [ "$TIER" = "development" ]; then
    export $TIER
  else
    echo "Invalid environment specified"
    exit 1
fi

docker-compose up --build