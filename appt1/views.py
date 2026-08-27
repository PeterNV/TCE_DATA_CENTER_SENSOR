from django.shortcuts import render
from .models import   RGraficos
import pymongo
from django.shortcuts import render
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import paho.mqtt.client as mqtt
import json
import threading
from datetime import datetime
import pytz
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def retorna_dados(request):
    global ULTIMOS_DADOS

    if request.method == "POST":
        data = json.loads(request.body)

        ULTIMOS_DADOS = {
            "t": data.get("Temperatura"),
            "p": data.get("Ponto_de_orvalho"),
            "u": data.get("Umidade")
        }
        myclient = pymongo.MongoClient("mongodb+srv://pedrovilanova34:sacul0499@cluster0.ksgparj.mongodb.net/")
        mydb = myclient["Dados"]
        mycol = mydb["Sensor"]
        mydict = {"Data": data.get("Data"),"Hora": data.get("Hora"), "Temperatura": data.get("Temperatura"), "Umidade": data.get("Umidade"), "Ponto_de_orvalho": data.get("Ponto_de_orvalho")}

        x = mycol.insert_one(mydict)
        return JsonResponse({"status": "ok"})
def get_dados(request):
    return JsonResponse(ULTIMOS_DADOS)

@csrf_exempt
def retorna_dados_dois(request):
    global ULTIMOS_DADOS_DOIS

    if request.method == "POST":
        data = json.loads(request.body)

        ULTIMOS_DADOS_DOIS = {
            "t": data.get("Temperatura"),
            "p": data.get("Ponto_de_orvalho"),
            "u": data.get("Umidade")
        }
        myclient = pymongo.MongoClient("mongodb+srv://pedrovilanova34:sacul0499@cluster0.ksgparj.mongodb.net/")
        mydb = myclient["Dados"]
        mycol = mydb["SensorRl"]
        mydict = {"Data": data.get("Data"),"Hora": data.get("Hora"), "Temperatura": data.get("Temperatura"), "Umidade": data.get("Umidade"), "Ponto_de_orvalho": data.get("Ponto_de_orvalho")}

        x = mycol.insert_one(mydict)
        return JsonResponse({"status": "ok"})
def get_dados_dois(request):
    return JsonResponse(ULTIMOS_DADOS_DOIS)
def cria_grafico(x, y, cor):
    plt.figure(figsize=(5,3))
    plt.plot(x, y, color=cor)
    plt.ylim((min(y)-2, max(y)+2))
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    return img

def cria_gauge(data, min, max, cor_inicio, cor_meio, cor_fim, unidade):
    go_temp = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = data[-1],
        number = {'suffix': unidade, 'font': {'size': 64, 'color': '#444', 'family': 'sans-serif'}},
        gauge = {
            'axis':{'range': [min, max], 'tickwidth': 1, 'tickcolor': '#000'},
            'bar': {'color': '#444'},
            'borderwidth' : 2,
            'bordercolor': 'black',
            'steps': [
                {'range': [min,min + (max-min)/3], 'color': cor_inicio},
                {'range': [min + (max-min)/3,min + 2*(max-min)/3], 'color': cor_meio},
                {'range': [min + 2*(max-min)/3,max], 'color': cor_fim}
            ]

        }
    ))

    go_temp.update_layout(font=dict(size=36))

    img = go_temp.to_image(format='png')
    img_b64 = "data:image/png;base64," + base64.b64encode(img).decode()
    return img_b64

def home(request):
    myclient = pymongo.MongoClient("mongodb+srv://pedrovilanova34:sacul0499@cluster0.ksgparj.mongodb.net/")
    mydb = myclient["Dados"]
    mycol = mydb["Sensor"]
    mycolDois = mydb["SensorRl"]
    allData = []
    allIndex = 0
    allDataDois = []
    allIndexDois = 0
    saveIndex = []
    saveIndexDois = []
    print(mycol.find_one())
    print(mycolDois.find_one())
    if mycol.find_one() == None and mycolDois.find_one() == None:
          AsDatas ={
                
                'Data' : "Dados não encontrados",  
                'DataDois' : "Dados não encontrados", 
                'Index': "",
                'IndexDois': ""
            }
          return render(request,'estacao/home.html',AsDatas)
    elif mycol.find_one() != None and mycolDois.find_one() == None:
         for y in mycol.distinct("Data"):
                         print(str(y))
                         allIndex += 1
                         print(allIndex)
                         allData.append(str(y))
                         saveIndex.append(allIndex)
                         AsDatas ={
                             
                             'Data' : allData,  
                             'DataDois' : "Dados não encontrados", 
                             'Index': saveIndex,
                             'IndexDois': ""
                         }
    elif mycol.find_one() == None and mycolDois.find_one() != None:
             for y in mycolDois.distinct("Data"):
                             print(str(y))
                             allIndexDois += 1
                             print(allIndexDois)
                             allDataDois.append(str(y))
                             saveIndexDois.append(allIndexDois)
                             AsDatas ={
                                 
                                 'Data' : "Dados não encontrados",  
                                 'DataDois' : allDataDois, 
                                 'Index': "",
                                 'IndexDois': saveIndexDois
                             }
    elif mycol.find_one() != None and mycolDois.find_one() != None:
        for y in mycolDois.distinct("Data"):
            allIndexDois += 1
            allDataDois.append(str(y))
            saveIndexDois.append(allIndexDois)

        for x in mycol.distinct("Data"):
             allIndex += 1
             allData.append(str(x))
             saveIndex.append(allIndex)
        
             AsDatas ={
                        
                        'Data' : allData,  
                        'Index': saveIndex,
                        'DataDois' : allDataDois, 
                        'IndexDois': saveIndexDois
             }
    return render(request,'estacao/home.html',AsDatas)
# Create your views here.

def retornaGraficos(request):
    myclient = pymongo.MongoClient("mongodb+srv://pedrovilanova34:sacul0499@cluster0.ksgparj.mongodb.net/")
    mydb = myclient["Dados"]
    mycol = mydb["Sensor"]
    ExibeGrafico = RGraficos()
    ExibeGrafico.datae = request.GET.get('datadados')
    VerificaTempAlta = 0
    RespostaTempAlta = ""

    VerificaTempBaixa = 0
    RespostaTempBaixa = ""


    VerificaUmidAlta = 0
    RespostaUmidAlta = ""
    
    VerificaUmidBaixa = 0
    RespostaUmidBaixa = ""

        
    print(ExibeGrafico.datae)
 
    datacompleta = ''
    datacompleta = ExibeGrafico.datae
    print(ExibeGrafico.datae)
  
    i = 0
    leitura = []
    
    t, u,  p = [], [], []
    y = mycol.find_one({"Data": datacompleta})
    tmax = []
    tmin = []
    hmax = []
    hmin = []
    pmax = []
    pmin = []
    
    tm = 0.0
    hm = 0.0
    pm = 0.0    
    print(y)
    for x in mycol.find({"Data": datacompleta}):
       
        i+=1
        leitura.append(i)
        tm += float(x.get("Temperatura"))
        hm += float(x.get("Umidade"))
        pm += float(x.get("Ponto_de_orvalho"))
        print("Temp med: ",tm)

        tmax.append(x.get("Temperatura"))
        tmin.append(x.get("Temperatura"))
        hmax.append(x.get("Umidade"))
        hmin.append(x.get("Umidade"))
        pmax.append(x.get("Ponto_de_orvalho"))
        pmin.append(x.get("Ponto_de_orvalho"))
        

        t.append(float(x.get("Temperatura")))
        u.append(float(x.get("Umidade")))
        p.append(float(x.get("Ponto_de_orvalho")))
        if float(x.get("Temperatura")) > 27.00 and float(x.get("Temperatura")) < 32.99:
              VerificaTempAlta += 1
        if float(x.get("Temperatura")) > 15.00 and float(x.get("Temperatura")) < 18.00:
              VerificaTempBaixa += 1
        if float(x.get("Umidade")) > 55.00 and float(x.get("Umidade")) < 60.99:
              VerificaUmidAlta += 1
        if float(x.get("Umidade")) > 20.00 and float(x.get("Umidade")) < 40.00:
              VerificaUmidBaixa += 1
        
        print(x)
    print("{:.2f}".format(float(tm/i)))
    print("{:.2f}".format(float(hm/i)))
    print("{:.2f}".format(float(pm/i)))

    print(max(tmax))
    print(min(tmin))
    print(max(hmax))
    print(min(hmin))
    print(max(pmax))
    print(min(pmin))
   
    print(y)
    if VerificaTempAlta >= 10:
        RespostaTempAlta = "SIM"
    else:
        RespostaTempAlta = "NÃO"

    if VerificaTempBaixa >= 10:
        RespostaTempBaixa = "SIM"
    else:
        RespostaTempBaixa = "NÃO"

    if VerificaUmidAlta >= 10:
        RespostaUmidAlta = "SIM"
    else:
        RespostaUmidAlta = "NÃO"

    if VerificaUmidBaixa >= 10:
        RespostaUmidBaixa = "SIM"
    else:
        RespostaUmidBaixa = "NÃO"
    print(VerificaTempAlta)
    print(VerificaTempBaixa)
    print(VerificaUmidAlta)
    print(VerificaUmidBaixa)
    if y == None:
        AsDatas ={
        
         'DataInvalida': True,
         'DataValida': False
        }
        return render(request,'estacao/DataConfirmada.html',AsDatas)
    else:    
           img_t = cria_grafico(leitura, t, 'red')
           img_u = cria_grafico(leitura, u, 'blue')

           img_p = cria_grafico(leitura, p, 'purple')

          

           context = {
               'temperatura': t[-1], 
               'umidade': u[-1], 
               
               'pressao': p[-1],
               'tempMed':"{:.2f}".format(sum(t) / len(t)),
               'umidMed':"{:.2f}".format(sum(u) / len(u)),
               'pdoMed':"{:.2f}".format(sum(p) / len(p)),
               
               'tempMax':"{:.2f}".format(max(t)),
               'tempMin':"{:.2f}".format(min(t)),
               'humMax':"{:.2f}".format(max(u)),
               'humMin':"{:.2f}".format(min(u)),
               'pdoMax':"{:.2f}".format(max(p)),
               'pdoMin':"{:.2f}".format(min(p)),
            
               'img_t': img_t,
               'img_u': img_u,
               'img_p': img_p,
               'DataInvalida': False,
               'DataValida': True,
               'datacompleta': datacompleta,
               'RespTempAlta': RespostaTempAlta,
               'RespTempBaixa': RespostaTempBaixa,
               'RespUmidAlta': RespostaUmidAlta,
               'RespUmidBaixa':RespostaUmidBaixa,
               'TotalTempAlta': VerificaTempAlta,
               'TotalTempBaixa': VerificaTempBaixa,
               'TotalUmidAlta': VerificaUmidAlta,
               'TotalUmidBaixa': VerificaUmidBaixa,
        }
    return render(request,'estacao/DataConfirmada.html',context)

def retornaGraficosDois(request):
    myclient = pymongo.MongoClient("mongodb+srv://pedrovilanova34:sacul0499@cluster0.ksgparj.mongodb.net/")
    mydb = myclient["Dados"]
    mycol = mydb["SensorRl"]
    ExibeGrafico = RGraficos()
    ExibeGrafico.datae = request.GET.get('datadadosDois')
    VerificaTempAlta = 0
    RespostaTempAlta = ""
    
    VerificaTempBaixa = 0
    RespostaTempBaixa = ""
    
    
    VerificaUmidAlta = 0
    RespostaUmidAlta = ""
        
    VerificaUmidBaixa = 0
    RespostaUmidBaixa = ""
    RespostaTempAlta = ""
    print(ExibeGrafico.datae)
 
    datacompleta = ''
    datacompleta = ExibeGrafico.datae
    print(ExibeGrafico.datae)
  
    i = 0
    leitura = []
    
    t, u,  p = [], [], []
    y = mycol.find_one({"Data": datacompleta})
    tmax = []
    tmin = []
    hmax = []
    hmin = []
    pmax = []
    pmin = []
    
    tm = 0.0
    hm = 0.0
    pm = 0.0    
    print(y)
    for x in mycol.find({"Data": datacompleta}):
       
        i+=1
        leitura.append(i)
        tm += float(x.get("Temperatura"))
        hm += float(x.get("Umidade"))
        pm += float(x.get("Ponto_de_orvalho"))
        print("Temp med: ",tm)

        tmax.append(x.get("Temperatura"))
        tmin.append(x.get("Temperatura"))
        hmax.append(x.get("Umidade"))
        hmin.append(x.get("Umidade"))
        pmax.append(x.get("Ponto_de_orvalho"))
        pmin.append(x.get("Ponto_de_orvalho"))
        

        t.append(float(x.get("Temperatura")))
        u.append(float(x.get("Umidade")))
        p.append(float(x.get("Ponto_de_orvalho")))
        if float(x.get("Temperatura")) > 27.00 and float(x.get("Temperatura")) < 32.99:
                      VerificaTempAlta += 1
        if float(x.get("Temperatura")) > 15.00 and float(x.get("Temperatura")) < 18.00:
                      VerificaTempBaixa += 1
        if float(x.get("Umidade")) > 55.00 and float(x.get("Umidade")) < 60.99:
                      VerificaUmidAlta += 1
        if float(x.get("Umidade")) > 20.00 and float(x.get("Umidade")) < 40.00:
                      VerificaUmidBaixa += 1
        print(x)
    print("{:.2f}".format(float(tm/i)))
    print("{:.2f}".format(float(hm/i)))
    print("{:.2f}".format(float(pm/i)))

    print(max(tmax))
    print(min(tmin))
    print(max(hmax))
    print(min(hmin))
    print(max(pmax))
    print(min(pmin))
   
    print(y)
    if VerificaTempAlta >= 10:
            RespostaTempAlta = "SIM"
    else:
            RespostaTempAlta = "NÃO"
    
    if VerificaTempBaixa >= 10:
            RespostaTempBaixa = "SIM"
    else:
            RespostaTempBaixa = "NÃO"
    
    if VerificaUmidAlta >= 10:
            RespostaUmidAlta = "SIM"
    else:
            RespostaUmidAlta = "NÃO"
    
    if VerificaUmidBaixa >= 10:
            RespostaUmidBaixa = "SIM"
    else:
            RespostaUmidBaixa = "NÃO"
    if y == None:
        AsDatas ={
        
         'DataInvalida': True,
         'DataValida': False
        }
        return render(request,'estacao/DataConfirmadaDois.html',AsDatas)
    else:    
           img_t = cria_grafico(leitura, t, 'red')
           img_u = cria_grafico(leitura, u, 'blue')

           img_p = cria_grafico(leitura, p, 'purple')

          

           context = {
               'temperatura': t[-1], 
               'umidade': u[-1], 
               
               'pressao': p[-1],
               'tempMed':"{:.2f}".format(sum(t) / len(t)),
               'umidMed':"{:.2f}".format(sum(u) / len(u)),
               'pdoMed':"{:.2f}".format(sum(p) / len(p)),
               
               'tempMax':"{:.2f}".format(max(t)),
               'tempMin':"{:.2f}".format(min(t)),
               'humMax':"{:.2f}".format(max(u)),
               'humMin':"{:.2f}".format(min(u)),
               'pdoMax':"{:.2f}".format(max(p)),
               'pdoMin':"{:.2f}".format(min(p)),
            
               'img_t': img_t,
               'img_u': img_u,
               'img_p': img_p,
               'DataInvalida': False,
               'DataValida': True,
               'datacompleta': datacompleta,
               'RespTempAlta': RespostaTempAlta,
               'RespTempBaixa': RespostaTempBaixa,
               'RespUmidAlta': RespostaUmidAlta,
               'RespUmidBaixa':RespostaUmidBaixa,
               'TotalTempAlta': VerificaTempAlta,
               'TotalTempBaixa': VerificaTempBaixa,
               'TotalUmidAlta': VerificaUmidAlta,
               'TotalUmidBaixa': VerificaUmidBaixa,
        }
    return render(request,'estacao/DataConfirmadaDois.html',context)
