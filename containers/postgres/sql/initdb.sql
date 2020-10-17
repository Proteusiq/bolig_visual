CREATE DATABASE boligDB;
CREATE USER grafanareader WITH PASSWORD 'grafanareaderpwd';
GRANT CONNECT ON DATABASE boligDB TO grafanareader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafanareader;