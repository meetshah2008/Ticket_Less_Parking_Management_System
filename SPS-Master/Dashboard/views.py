from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import pyrebase
from . import configfile


firebase = pyrebase.initialize_app(configfile.config)
auth = firebase.auth()
database = firebase.database()


def index(request):
    template = loader.get_template('index1.html')

    #Gets the number of occupied parking slots
    occupied_parking_spots = 0
    max_parking_capacity = 40
    parked_vehicles = database.child("VehicleHistory").order_by_child("outTime").equal_to("").get()
    for vehicle in parked_vehicles.each():
        occupied_parking_spots += 1

    #Gets the top ten recent vehicles from vehicle history
    recent_vehicles = database.child("VehicleHistory").order_by_child("inTime").limit_to_last(3).get()
    vehicles = []
    for vehicle in recent_vehicles.each():
        vehicles.append(vehicle.val())
    vehicles.reverse()


    #vehicles = database.child("VehicleHistory").order_by_child("vehiclePlateNo").equal_to("GJ05JD9750").get()
    #list_of_parked_vehicles=[]
    #for vehicle in vehicles.each():
    #    if vehicle.val()["outTime"] == "":
    #        list_of_parked_vehicles.append(vehicle.val())
        

    context = {
        'spots': occupied_parking_spots,
        'total': max_parking_capacity,
        'vehicles': vehicles,
    }
#    return HttpResponse(template.render(context,request))
    return render(request,"index.html", context)