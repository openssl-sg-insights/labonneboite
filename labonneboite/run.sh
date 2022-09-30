# /bin/bash

# alembic
poetry run alembic upgrade head 

# run custom sql scripts if any
echo 'Running sql scripts if any'
for i in `/bin/ls -1 /sql/*.sql`; do 
    echo $i
    mysql --user=$DB_USER \
    --password=$DB_PASSWORD \
    --host=$DB_HOST \
    --port=$DB_PORT \
    --database=$DB_DATABASE < $i
done


# create the index in elastic search
poetry run create_index --full

# run the server
poetry run gunicorn --config python:wsgi-conf web.app:app