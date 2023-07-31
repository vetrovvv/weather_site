from django.urls import path
from .views import *


urlpatterns = [

    path('cities/', CityListView.as_view(), name='cities'),
    path('cities/<int:pk>/', redirect_current_date, name='city'),
    path('cities/create/', CityCreateView.as_view(), name='city_create'),
    path('cities/<int:pk>/<slug:slug>/delete/', CityDeleteView.as_view(), name='city_delete'),
    path('cities/<int:pk>/<slug:slug>/update/', CityUpdateView.as_view(), name='city_update'),
    path('cities/<int:pk>/<slug:slug>/', CityDateWeatherView.as_view(), name='city_by_date'),
    path('cities/<int:pk>/<slug:slug>/<int:weather_pk>/', WeatherDetailView.as_view(), name='weather'),
    path('cities/<int:pk>/<slug:slug>/<int:weather_pk>/update/', WeatherUpdateView.as_view(), name='weather_update'),
    path('cities/<int:pk>/<slug:slug>/<int:weather_pk>/delete/', WeatherDeleteView.as_view(), name='weather_delete'),
    path('cities/<int:pk>/<slug:slug>/weather_create/', WeatherCreateView.as_view(), name='weather_create'),
]
