set -e
#Creates a user in admin database. It means that admin should be use as authSource while authenticating
mongosh admin --host localhost -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" <<EOF
db.createUser(
    {
    user: '$MONGO_USERNAME',
    pwd: '$MONGO_PASSWORD',
    roles: [{
      role: "dbOwner",
      db: "db"
    }]
})
EOF