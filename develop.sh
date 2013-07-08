# Start the API server, and serve it and the frontend through a reverse proxy.

FRONTEND_PORT=8080
BACKEND_PORT=8081
DB_FILE=test.db

echo "starting backend server on $FRONTEND_PORT ..."
python backend/server.py $DB_FILE $BACKEND_PORT &

echo "starting frontend server on $BACKEND_PORT ..."
tape --root frontend \
     --proxy /api=http://localhost:$BACKEND_PORT/api \
     --port $FRONTEND_PORT &

# when script exits, kill the two servers
trap 'kill $(jobs -p)' EXIT

wait