#!/bin/bash

echo "$(date '+%Y-%m-%d %H:%M:%S') ... sourcing Environment Settings"
source development.env
echo "$(date '+%Y-%m-%d %H:%M:%S') ... sourcing Environment Settings is DONE"

echo "$(date '+%Y-%m-%d %H:%M:%S') ... installing web-app requirements"
pip install -r ${FASTAPI_USERS_REQUIREMENTS_FOLDER}${FASTAPI_USERS_REQUIREMENTS}
echo "$(date '+%Y-%m-%d %H:%M:%S') ... web-app requirements installed"

if [ "${AERICH_MIGRATIONS}" = True ] ; then
    doing_what="Applying migrations"
    echo "$(date '+%Y-%m-%d %H:%M:%S') ... ${doing_what}"
    aerich init -t app.main.TORTOISE_ORM
    aerich init-db
    aerich upgrade
    echo "$(date '+%Y-%m-%d %H:%M:%S') ... ${doing_what} is DONE"
fi

if [ "${FASTAPI_USERS_ADD_INIT_DATA}" = True ] ; then
    doing_what="Load initial data"
    echo "$(date '+%Y-%m-%d %H:%M:%S') ... ${doing_what}"
    python -m app.loaddata
    echo "$(date '+%Y-%m-%d %H:%M:%S') ... ${doing_what} is DONE"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') ... Running the Server"
uvicorn app.main:app --host=0.0.0.0 --port=8000
