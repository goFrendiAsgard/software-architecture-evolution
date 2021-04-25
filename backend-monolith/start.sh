if [ -z "${BACKEND MONOLITH_HTTP_PORT}" ]
then
    BACKEND MONOLITH_HTTP_PORT=3010
fi
pipenv run uvicorn main:app --host=0.0.0.0 --port=${BACKEND MONOLITH_HTTP_PORT}