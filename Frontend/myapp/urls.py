from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('add/', views.add, name="add"),
    path('listhast/', views.listhast, name="listhast"),
    path('listmension/', views.listmension, name="listmension"),
    path('stats/', views.stats, name="stats"),
    path('palabra/', views.palabra, name="palabra"),
    path('mensaje/', views.mensaje, name="mensaje"),
]