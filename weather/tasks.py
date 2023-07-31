from weathersite.celery import app
import pygismeteo
from .models import City, Weather


@app.task
def update_weather():
    gm = pygismeteo.Gismeteo()
    cities = City.objects.all()
    for city in cities:
        search_results = gm.search.by_query(city.city)
        if len(search_results) > 0:
            city_id = search_results[0].id
            current = gm.current.by_id(city_id)
            weather_now = Weather.objects.create(temperature=(int(current.temperature.air.c)))
            weather_now.save()
            city.weather_history.add(weather_now)
            city.save()
