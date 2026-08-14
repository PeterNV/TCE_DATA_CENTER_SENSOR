from django.urls import path
from appt1 import views
urlpatterns = [
    # rota, view responsavel, nome de referencia
    path('',views.home,name='home'),
    path('dados/',views.retorna_dados,name='retorna_dados'),
    path('get_dados/',views.get_dados,name='get_dados'),

    path('dados_dois/',views.retorna_dados_dois,name='retorna_dados_dois'),
    path('get_dados_dois/',views.get_dados_dois,name='get_dados_dois'),

    path('rg/',views.retornaGraficos,name='dados_estacao'),
    path('rgd/',views.retornaGraficosDois,name='dados_estacao_dois'),
]
