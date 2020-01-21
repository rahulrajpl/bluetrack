import pyrebase
# Firebase initialization
config = {"apiKey": "AIzaSyCkHqJQIMS2BecgGYNPHmPcTcxDaoUtri0",
          "authDomain": "oblu-iot-ab1cd.firebaseapp.com",
          "databaseURL": "https://oblu-iot-ab1cd.firebaseio.com",
          "storageBucket": "oblu-iot.appspot.com",
          "serviceAccount": "oblu-iot-ab1cd-firebase-adminsdk-j3wwh-1b00bea853.json"}
app = pyrebase.initialize_app(config)
# Get a reference to the database service
db = app.database()
# Retrieve data from firebase database
users = db.child("users").get()
print("Retreive data from firebase database:", users.val())
