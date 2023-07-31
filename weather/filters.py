from django_filters import FilterSet
from .models import Weather,City



class CityFilter(FilterSet):
    class Meta:
        model = City
        fields = {
            'city': ['icontains'],
        }



class CityDateWeatherFilter(FilterSet):

    class Meta:
        model = Weather

        fields = {'in_time':['exact'],
                 }
