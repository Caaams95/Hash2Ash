#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_instance>"
    exit 1
fi

instance_id=$1
PGPASSWORD='C5yAn39f8Tm7U13z' psql -U userHash2ash -h db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d hash2ash -c "UPDATE public.instances SET status='Terminate' WHERE instance_id='$instance_id';"
