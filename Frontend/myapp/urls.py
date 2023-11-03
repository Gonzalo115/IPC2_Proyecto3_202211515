from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('help/', views.help, name="help"),
    path('add/', views.add, name="add"),
    path('listhast/', views.listhast, name="listhast"),
    path('listmension/', views.listmension, name="listmension"),
    path('listfeelings/', views.listfeelings, name="listfeelings"),
    path('stats/', views.stats, name="stats"),
    path('palabra/', views.palabra, name="palabra"),
    path('mensaje/', views.mensaje, name="mensaje"),
    path('inicializar/', views.inicializar, name="inicializar"),
]