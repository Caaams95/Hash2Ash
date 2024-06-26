sudo mariadb
show databases;
use test;
show tables;
select * from Hashes;

-- Update la BDD
sudo mariadb test -e "UPDATE Hashes SET result='Hash234' WHERE id_hash=4;"


PGPASSWORD='A72gm143kldF47GI' psql -U userHash2ash -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d initial_db -f commande.sql
initial_db=> select * from information_schema.hashes;

File: commande.sql
-- commands.sql
UPDATE information_schema.hashes SET result='ssssqqh234' WHERE id_hash=1;
-- Ajoutez d'autres commandes SQL ici





echo " SELECT MAX(id_hash) FROM information_schema.hashes;" > /tmp/commande.sql
        PGPASSWORD='A72gm143kldF47GI' psql -U userHash2ash -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d initial_db -f /tmp/commande.sql




while true
        clear
        PGPASSWORD='A72gm143kldF47GI' psql -U userHash2ash -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d initial_db -c "select * from information_schema.hashes;"
        sleep 1 
end


while true
        clear
        PGPASSWORD='A72gm143kldF47GI' psql -U userHash2ash -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d initial_db -c "select * from information_schema.instance;"
        sleep 1 
end


PGPASSWORD='A72gm143kldF47GI' psql -U userHash2ash -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d initial_db -c "select * from information_schema.hashes;"

-- "UPDATE information_schema.hashes SET result='XXX' WHERE id_hash=2;"
PGPASSWORD='A72gm143kldF47GI' psql -U userHash2ash -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d initial_db -c "UPDATE information_schema.hashes SET result='XXX' WHERE id_hash=2;"

-- "UPDATE information_schema.hash SET status='0' WHERE id=1;"
PGPASSWORD='A72gm143kldF47GI' psql -U userHash2ash -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d initial_db -c "UPDATE information_schema.instance SET status='0' WHERE id=1;"
