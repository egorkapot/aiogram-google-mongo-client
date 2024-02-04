set -e

mongo <<EOF
use admin
db.createUser(
    {
    user: '$MONGO_USERNAME',
    pwd: '$MONGO_PASSWORD',
    roles: [
        {role: "dbOwner", db: "db"}
        ]
    }
);
EOF