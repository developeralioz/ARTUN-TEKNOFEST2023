import time
from pyrebase import pyrebase

config = {
  "apiKey": "*******************",
  "authDomain": "**********.firebaseapp.com",
  "databaseURL": "https://************-rtdb.europe-west1.firebasedatabase.app",
  "storageBucket": "**********.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()



