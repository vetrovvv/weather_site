from django.forms import ModelForm, Form, DateField,TextInput
from .models import *


class WeatherInDateForm(Form):
    date = DateField(input_formats=['dd.mm.yyyy'])


class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ['city']


class WeatherForm(ModelForm):
    class Meta:
        model = Weather
        fields = ['temperature']
        widgets = {
            'temperature': TextInput(),
        }
