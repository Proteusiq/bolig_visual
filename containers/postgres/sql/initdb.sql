CREATE DATABASE boligDB;
CREATE USER grafanareader WITH PASSWORD 'grafanareaderpwd';
GRANT USAGE ON SCHEMA schema TO grafanareader;
GRANT SELECT ON schema.table TO grafanareader;