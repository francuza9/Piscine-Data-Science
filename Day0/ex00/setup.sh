#!/bin/bash

set -e

echo "Updating packages..."
sudo apt update -y

echo "Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

echo "Starting PostgreSQL service..."
sudo service postgresql start

echo "Creating database and user..."

sudo -i -u postgres psql <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'gtskitis') THEN
      CREATE ROLE gtskitis LOGIN PASSWORD 'mysecretpassword';
   END IF;
END
\$do\$;

CREATE DATABASE piscineds OWNER gtskitis;
GRANT ALL PRIVILEGES ON DATABASE piscineds TO gtskitis;
EOF

echo "✅ PostgreSQL setup complete!"
echo "You can now connect using:"
echo "psql -U gtskitis -d piscineds -h localhost -W"
