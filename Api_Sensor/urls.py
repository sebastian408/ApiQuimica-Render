from django.contrib import admin
from django.urls import path
from Api_Sensor import views

urlpatterns = [
    path('', views.home, name='home'),
    path('visualizar_datos/', views.visualizar_datos, name='visualizar_datos'),
    
    path('mostrar/<str:tabla>/', views.mostrar_tabla, name='mostrar_tabla'),
    path('descargar/<int:experimento_id>/<str:tabla>/', views.descargar_datos, name='descargar_datos'),
    
    path('upload_sensor/', views.upload_sensor_data, name='upload_sensor_data'),
    path('upload_key_point/', views.upload_key_point_data, name='upload_key_point_data'),
    path('download_csv/', views.download_csv, name='download_csv'),
    path('experimentos/', views.experiment_list, name="experiment_list"),
]
