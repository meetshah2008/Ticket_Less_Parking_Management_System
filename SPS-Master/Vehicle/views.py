from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .forms import *
import pyrebase
from . import configfile

firebase = pyrebase.initialize_app(configfile.config)
auth = firebase.auth()
database = firebase.database()

def search(request):
    template = loader.get_template('search.html')

    #this block gets executed when user hits the search button
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_title = request.POST['search_title']

            #Get the searched vehicle information
            res=[]
            vehicle = database.child('VehicleHistory').order_by_child('vehiclePlateNo').equal_to(search_title).get()
            for v in vehicle.each():
                if v.val()['outTime']=="":
                    res.append(v.val())
            #print(len(res))
            
            if len(res) != 0:
                #fetch the userid's of the vehicle owner from the vehicle table using the vehicle plate information
                req_vehicle = database.child('vehicle').order_by_child('vehiclePlateNo').equal_to(search_title).get()
                userid = ""
                for u in req_vehicle.each():
                    userid = u.val()['userId']
                print(req_vehicle.val())

                #fetches the username of the vehicle owner from the user table using the userid obtained above
                if userid != "":
                    req_user = database.child('User').order_by_child('userId').equal_to(userid).get()
                    print(req_user.val())
                    username = ""
                    wallet_balance = 0
                    for u in req_user.each():
                        username = u.val()['name']
                        wallet_balance = u.val()['wallet']
                    print(username)
                    context = {
                        'search_title': search_title, 
                        'search': True, 
                        'form': form,
                        'vehicle': res,
                        'username': username,
                        'wallet_balance': wallet_balance
                    }
            else:
                context = {
                    'search': False, 
                    'form': form,
                }

            return HttpResponse(template.render(context,request))
    
    #this block gets executed when the page is first rendered
    elif request.method == 'GET':
        form = SearchForm()
        context = {'form': form}
        return HttpResponse(template.render(context,request)) 
    