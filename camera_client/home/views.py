import contextlib
import io
from django.shortcuts import render
from .forms import *
from math import ceil
import datetime
import pyrebase
import numpy as np
import cv2 as cv
# from home.model.image_segmentation import recognition
import re

from home.model.improved_model import recognition


# Initialising reference to firebase realtime database
config = {
    'apiKey': "AIzaSyAkNBtRdsF2EdpaRwheRaZHtwQK3ujtG1Y",
    'authDomain': "smart-parking-syatem-ff56b.firebaseapp.com",
    'databaseURL': "https://smart-parking-syatem-ff56b-default-rtdb.firebaseio.com",
    'projectId': "smart-parking-syatem-ff56b",
    'storageBucket': "smart-parking-syatem-ff56b.appspot.com",
    'messagingSenderId': "848307937951",
    'appId': "1:848307937951:web:23eb5c59ea7d407a21f8aa",
    'measurementId': "G-REXLL6ERDH",
#    "serviceAccount": ".secrets/sps-firebase-adminsdk.json"
}
#firebase = pyrebase.initialize_app(config)
db = pyrebase.initialize_app(config).database()


def home(request):
    
    saved=None;         direction = None
    isParked = None;    anprSuccessful = None
    fee = 0;         currentBalance = 0 

    if request.method == 'POST':
        saved=None;   direction = None
        isParked = None;    anprSuccessful = None
        vehicleRegistered = None
        form = photosform(request.POST, request.FILES)     

        if form.is_valid():
            
            plateNum = getPlateNum(form.files)
            if plateNum != None:

                anprSuccessful = True
                userIdList = db.child('vehicle').order_by_child('vehiclePlateNo').equal_to(plateNum).get().val()
                if len(userIdList) == 1:

#                    print(list(useridList.values())[0]['userId'])
                    vehicleRegistered = True
                    (isParked, vehicleHistoryKey, inTime) = getInfoForParkedVehicle(plateNum)
                    direction = eval(form.data['direction'])

                    #True for recording entry
                    if direction:
                        if not isParked:
                            db.child("VehicleHistory").push({
                                'vehiclePlateNo': plateNum,
                                'inTime': str(datetime.datetime.now()),
                                'outTime': ''
                            })
                            saved = True                        

                    #For recording exit and making payment
                    else:

                        userId = list(userIdList.values())[0]['userId']
                        user = db.child("User").order_by_child("userId").equal_to(userId).get().val()
                        outTime = datetime.datetime.now()
                        fee = calculateParkingFee(inTime, outTime) if isParked else 20
                        currentBalance = int(list(user.values())[0]['wallet'])

                        if (currentBalance >= fee):
                            userKey = list(user.keys())[0]
                            db.child("User").child(userKey).update({
                                'wallet': currentBalance-fee
                            })

                            transactionId = db.child("Transaction").push({
                                'userId': userId,
                                'dateTime': str(outTime),
                                'credit': False,
                                'amount': fee
                            })
                            if isParked:
                                db.child("VehicleHistory").child(vehicleHistoryKey).update({
                                    'transactionId': transactionId['name'],
                                    'outTime': str(outTime),
                                    'fee': fee
                                })
                            else:
                                db.child("VehicleHistory").push({
                                    'transactionId': transactionId['name'],
                                    "vehiclePlateNo": plateNum,
                                    "inTime": str(outTime),
                                    "outTime": str(outTime),
                                    "fee": fee
                                })
                            saved = True

        return render(request, 'home.html', {
            'form': photosform(),
            'saveAttempted': True,
            'anprSuccesssful': anprSuccessful,
            'plateNum': plateNum,
            'vehicleRegistered': vehicleRegistered,
            'saved': saved,
            'direction': direction,
            'wasParked': isParked,
            'fee': fee,
            'balance': currentBalance-fee if saved else currentBalance
        })

    return render(request, 'home.html', {
         'form': photosform(),
         'saveAttempted': False
    })

def getPlateNum(files):
    try:
        photo = cv.imdecode(np.fromstring(files['plate'].read(), np.uint8), cv.IMREAD_UNCHANGED)
        # with contextlib.redirect_stdout(io.StringIO()):
        #     anprResult = recognition(photo)

        anprResult = recognition(photo)
        anprResultReplace = anprResult.replace(" ", "")


        temp = anprResultReplace[-4:].replace("O", "0").replace("S", "5")

        anprResult = anprResultReplace[:-4] + temp


        isFormatCorrect = re.compile("[A-Z][A-Z][0-9][0-9][A-Z][A-Z][0-9][0-9][0-9][0-9]").match(anprResult.upper())
        plateNum = None if isFormatCorrect is None else anprResult.upper()

    except Exception as e:
        print("Exception : ", e)
        plateNum = None
    # plateNum = "GJ01AA1112"

    print("plate number : ", plateNum)
    return plateNum

def getInfoForParkedVehicle(plateNum):
    parkedVehicles = db.child("VehicleHistory").order_by_child("outTime").equal_to("").get().val()
    parkedVehicleValues = [] if len(parkedVehicles)==0 else list(parkedVehicles.values())
    parkedVehicleKeys = [] if len(parkedVehicles)==0 else list(parkedVehicles.keys())
    isParked = False;    inTime = None;    vehicleHistoryKey = None
    for i in range(len(parkedVehicles)):
        if parkedVehicleValues[i]["vehiclePlateNo"] == plateNum:
            isParked = True
            vehicleHistoryKey = parkedVehicleKeys[i]
            #print("VehicleHistory Key:"+vehicleHistoryKey)
            inTime = parkedVehicleValues[i]["inTime"]
            break
    return (isParked, vehicleHistoryKey, inTime)

def calculateParkingFee(inTime, outTime):
    inTimeStr = str(inTime).split(" ")
    (y,m,d) = inTimeStr[0].split("-")
    (h,minute,s) = inTimeStr[1].split(":")
    (y,m,d,h,minute,s) = (int(y),int(m),int(d),int(h),int(minute),int(s[:2]))
    timeDiff = outTime - datetime.datetime(y,m,d,h,minute,s)
    timeDiff = ceil(timeDiff.total_seconds()/3600)
    fee = 10 * timeDiff
    return fee
