import pyrebase

# Firebase initialization
config = { "apiKey": "AIzaSyCkHqJQIMS2BecgGYNPHmPcTcxDaoUtri0",
"authDomain": "oblu-iot-ab1cd.firebaseapp.com",
"databaseURL": "https://oblu-iot-ab1cd.firebaseio.com",
"storageBucket": "oblu-iot.appspot.com",
"serviceAccount": "oblu-iot-ab1cd-firebase-adminsdk-j3wwh-1b00bea853.json" }

app = pyrebase.initialize_app(config)

# Get a reference to the database service
db = app.database()

# data to save
data = { "name": "Mortimer 'Morty' Smith"}

# Post data to firebase database
results = db.child("users").push(data)

print("Succesfully posted data to firebase :", results)