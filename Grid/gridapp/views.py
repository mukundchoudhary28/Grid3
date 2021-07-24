from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.core.files import File
from gridapp.models import Response, Creds
from datetime import datetime

import json
import subprocess
import sys


def user(request):
    return render(request, 'gridapp/user.html')


def gridadmin(request):
    return render(request, 'gridapp/gridadmin.html')


def ipscreen(request):
    return render(request, 'gridapp/ipscreen.html')


def singlescan(request):
    return render(request, 'gridapp/singlescan.html')


def add_asset(request):
    return render(request, 'gridapp/add_asset.html')


def delete_asset(request):
    return render(request, 'gridapp/delete_asset.html')


def run_item(password, username, server, port):
    command = f'sshpass -p {password} ssh {username}@{server} -p {port} python3 < ip.py'
    process = subprocess.Popen(
        f'{command}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate()
    d = {}
    if process.returncode == 0:
        sout = out.decode("utf-8")
        d = json.loads(sout)
    return d
    #d = {"IP":["IP","Hostname","Mac","OS","Status"]}


@method_decorator(csrf_exempt, name='dispatch')
class Scan(View):
    def get(self, request):
        creds = Creds.objects.all()
        page = 'gridapp/user.html'
        if(request.user.is_authenticated):
            page = 'gridapp/gridadmin.html'
        if(len(creds) == 0):
            return render(request, page, context={'emptyCred': True, 'scanCall': True})
        creds = creds[0]
        username = creds.Username
        password = creds.Password
        server = creds.Server
        port = creds.Port
        d = run_item(password, username, server, port)

        if(len(d) == 0):
            return render(request, page, context={'emptyCred': False, 'scanCall': True, 'emptyDB': True})

        print(d)
        for key in d:
            value = d[key]
            #print(key)
            now = datetime.now()
            try:
                obj = Response.objects.get(IP=key)
                obj.Hostname = value["Hostname"]
                obj.MAC = value["MAC"]
                obj.OS = value["OS"]
                obj.Status = value["Status"]
                obj.LastSeenAlive = now
                obj.LastUpdated = now
                obj.Workgroup = value["Workgroup"]
                obj.ADDomain = value["ADDomain"]
                obj.save(update_fields=[
                    "Hostname", "OS", "MAC", "Status", "LastSeenAlive", "LastUpdated", "Workgroup", "ADDomain"])
            except:
                Response.objects.create(IP=value["IP"],Hostname=value["Hostname"], MAC=value["MAC"],
                                       Status=value["Status"], OS=value["OS"], LastSeenAlive=now, LastUpdated=now, ADDomain=value["ADDomain"],Workgroup=value["Workgroup"])
                
        all_items = Response.objects.all()
        for x in all_items:
            if x.IP not in d:
                obj.Status = "Down"
                obj.LastUpdated = now
                obj.save(update_fields=["Status", "LastUpdated"])
        return render(request, page, context={'emptyCred': False, 'scanCall': True, 'emptyDB': False})


@method_decorator(csrf_exempt, name='dispatch')
class AddServer(View):
    def post(self, request):
        page = 'gridapp/user.html'
        if(request.user.is_authenticated):
            page = 'gridapp/gridadmin.html'
        server = request.POST.get("server")
        port = request.POST.get("port")
        if port == '':
            port = 22
        try:
            port = int(port)
        except:
            return render(request, 'gridapp/add_asset.html', context={'portNAN': True})
        username = request.POST.get("username")
        password = request.POST.get("password")
        Creds.objects.all().delete()
        Response.objects.all().delete()
        Creds.objects.create(Server=server, Port=port,
                             Username=username, Password=password)
        return render(request, page, context={'updateCall': True})


@method_decorator(csrf_exempt, name='dispatch')
class SearchDB(View):
    def get(self, request):
        item = Response.objects.all()
        dict = {}
        i = 1
        for x in item:
            properties = [x.IP, x.Hostname, x.MAC, x.OS, x.Status, x.Workgroup, x.ADDomain, str(
                x.LastSeenAlive), str(x.LastUpdated)]
            dict[i] = properties
            i += 1
        return render(request, 'gridapp/ipscreen.html', {'existsDB': bool(len(dict)), 'data': dict})

    def post(self, request):
        # Search based on input parameter
        try:
            parameter = request.POST.get('parameter')
            value = request.POST.get('filter')
            page = 'gridapp/user.html'
            if(request.user.is_authenticated):
                page = 'gridapp/gridadmin.html'

            if(parameter == 'os'):
                items = Response.objects.filter(OS__iexact=value)
            elif parameter == 'workgroup':
                items = Response.objects.filter(Workgroup__iexact=value)
            else:
                items = Response.objects.filter(ADDomain__iexact=value)
            dict = {}
            i = 1
            for x in items:
                properties = [x.IP, x.Hostname, x.MAC, x.OS, x.Status, x.Workgroup, x.ADDomain, str(
                    x.LastSeenAlive), str(x.LastUpdated)]
                dict[i] = properties
                i += 1
            print(len(dict))
            return render(request, page, {'searchResults': bool(len(dict)), 'data': dict, 'searchCall': True})
        except Exception as e:
            print(e)
            return HttpResponse("Yelluru pilega")
