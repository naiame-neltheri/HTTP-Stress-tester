{
 
  "scripts": {
 
    "start": "gunicorn -b unix:/mnt/home/app.sock --worker-class socketio.sgunicorn.GeventSocketIOWorker server:app"
 
  }
 
}