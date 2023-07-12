from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import pyrebase
from . import configfile

firebase = pyrebase.initialize_app(configfile.config)
auth = firebase.auth()
database = firebase.database()

def history(request):
    template = loader.get_template('history.html')

    #Gets all the transaction history sorted by date
    res = database.child("Transaction").order_by_child('credit').equal_to(False).get()
    transaction_by_date = database.sort(res,"dateTime")
    
    transactons = []

    for transaction in transaction_by_date:
        t = transaction.val()
        t['transactionId'] = transaction.key()
        transactons.append(t)

    transactons.reverse()

    #prints each transactions fetched for testing purposes
    for transaction in transactons:
        print(transaction)

    #fetches the licence plate number associated with each transaction
    for transaction in transactons:
        vehicle_no = database.child("VehicleHistory").order_by_child('transactionId').equal_to(transaction['transactionId']).get()
        print(vehicle_no.val())
        for key,val in vehicle_no.val().items():
            transaction['vehiclePlateNo'] =val["vehiclePlateNo"]
        
    context = {'transactions':transactons}
    return HttpResponse(template.render(context,request))
    
 