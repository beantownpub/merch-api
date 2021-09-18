#!/bin/bash
set -e

psql -h localhost -v ON_ERROR_STOP=1 --username "postgres" --password <<-EOSQL
    CREATE USER jalbot WITH PASSWORD 'TG7ujL74svsXUETr7VP2PNqeP79a';
    CREATE DATABASE users;
    CREATE DATABASE food;
    GRANT ALL PRIVILEGES ON DATABASE users TO jalbot;
EOSQL