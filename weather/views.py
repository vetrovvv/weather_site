
from django.views.generic import  DetailView, ListView, CreateView, UpdateView, DeleteView
from .filters import *
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pygismeteo
from django.http import HttpResponseRedirect

class CityListView(ListView):

    model = City
    context_object_name = 'cities'
    template_name = 'weather/cities.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = CityFilter(self.request.GET, queryset=self.get_queryset())
        context['filter'] = CityFilter(self.request.GET, queryset=self.get_queryset())
        filter_qs = filter.qs
        paginator = Paginator(filter_qs, 5)
        page = self.request.GET.get('page', 1)
        try:
            cities = paginator.page(page)
        except PageNotAnInteger:
            cities = paginator.page(1)
        except EmptyPage:
            cities = paginator.page(paginator.num_pages)
        context['paginator'] = paginator
        context['cities'] = cities
        return context

    def get_queryset(self):
        queryset = City.objects.all()
        return queryset





class CityCreateView(LoginRequiredMixin, CreateView):
    model = City
    template_name = 'weather/city_create.html'
    form_class = CityForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CityForm()
        return context

    def post(self, request, *args, **kwargs):
        gm = pygismeteo.Gismeteo()
        if request.method == "POST":
            city_from_user = request.POST.get('city')
            search_results = gm.search.by_query(city_from_user)
            if len(search_results) > 0:
                city_from_server = search_results[0].name
                if len(City.objects.filter(city=city_from_server)) != 0:
                    id = City.objects.get(city=city_from_server).id
                    return redirect(f'/weather/cities/{id}/')
                else:
                    city_id = search_results[0].id
                    current = gm.current.by_id(city_id)
                    new_city = City.objects.create(city=city_from_server)
                    new_city.save()
                    weather_now = Weather.objects.create(temperature=(int(current.temperature.air.c)))
                    weather_now.save()
                    new_city.weather_history.add(weather_now)
                    new_city.save()
                    return redirect(f'/weather/cities/{new_city.id}/')

            else:
                error = "Ошибка запроса"
                form = CityForm()
                return render(request, 'weather/city_create.html', {'error': error, 'form': form})


class CityDeleteView(LoginRequiredMixin, DeleteView):
    model = City
    template_name = 'weather/city_delete.html'
    success_url = '/weather/cities/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.kwargs.get('slug')
        city_id = self.kwargs.get('pk')
        city = City.objects.get(id=city_id)
        context['city'] = city
        context['date'] = date
        return context

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        object = City.objects.get(pk=id)
        return object


class CityUpdateView(LoginRequiredMixin, UpdateView):
    model = City
    template_name = 'weather/city_update.html'
    form_class = CityForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.kwargs.get('slug')
        city_id = self.kwargs.get('pk')
        city = City.objects.get(id=city_id)
        context['city'] = city
        context['date'] = date
        return context

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        object = City.objects.get(pk=id)
        return object

    def post(self, request, *args, **kwargs):
        current_date = datetime.now()
        date_formated = current_date.strftime("%Y-%m-%d")
        id = self.kwargs.get('pk')
        city = City.objects.get(id=id)
        gm = pygismeteo.Gismeteo()
        city_from_user = request.POST.get('city')
        search_results = gm.search.by_query(city_from_user)
        if len(search_results) > 0:
            city_from_server = search_results[0].name
            if city_from_server == city:
                return redirect(f'/weather/cities/{self.id}/')
            else:
                city_id = search_results[0].id
                current = gm.current.by_id(city_id)
                Weather.objects.filter(city=city).delete()
                temp = Weather.objects.create(temperature=(int(current.temperature.air.c)))
                temp.save()
                city.city = city_from_server
                city.save()
                city.weather_history.add(temp)
                city.save()
                return redirect(f'/weather/cities/{city.id}/{date_formated}/')
        else:
            form = self.form_class(request.POST)
            error = 'Некорректный запрос'
            return render(request, 'weather/city_update.html', {'error': error, 'form': form})


class CityDateWeatherView(ListView):
    model = Weather
    template_name = 'weather/city_date_weather.html'
    context_object_name = 'date_weather'
    form_class = WeatherInDateForm

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        if request.method == "POST":
                date = request.POST.get('date')
                if datetime.strptime(date, "%d.%m.%Y"):
                    date_formated = datetime.strptime(date, "%d.%m.%Y")
                    dt = date_formated.date()
                    final_date = dt.isoformat()
                    return redirect(f'/weather/cities/{id}/{final_date}/')




    def get(self, request, **kwargs):

        date_value = self.kwargs.get('slug')
        city = City.objects.get(id=self.kwargs.get('pk'))
        date = self.kwargs.get('slug')
        weather = Weather.objects.filter(city=city, in_date=(str(date_value)))
        form = WeatherInDateForm()
        array = []
        array.append(["Время", "Температура", 'Id'])
        values = Weather.objects.filter(city=city, in_date=(str(date_value))).values_list('in_time', 'temperature', 'id')
        for time, temperature, pk in values:
            time_res = time.strftime("%H:%M")
            array.append([str(time_res), int(temperature), int(pk)])

        return render(request, 'weather/city_date_weather.html', {'array': array, 'date': date,
                                                                  'city': city, 'weather': weather, 'form': form})


class WeatherDetailView(LoginRequiredMixin, DetailView):
    model = Weather
    context_object_name = 'weather'
    template_name = 'weather/weather_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.kwargs.get('slug')
        city_id = self.kwargs.get('pk')
        city = City.objects.get(id=city_id)
        context['city'] = city
        context['date'] = date
        return context




    def get_object(self, **kwargs):
        city_id = self.kwargs.get('pk')
        city = City.objects.get(id=city_id)
        id = self.kwargs.get('weather_pk')
        date = self.kwargs.get('slug')
        object = Weather.objects.get(id=id)
        if object not in city.weather_history.all().filter(in_date=date):
            pass
        else:
            return object

class WeatherUpdateView(LoginRequiredMixin, UpdateView):
    model = Weather
    context_object_name = 'weather'
    template_name = 'weather/weather_update.html'
    form_class = WeatherForm

    def get_object(self, **kwargs):
        city_id = self.kwargs.get('pk')
        city = City.objects.get(id=city_id)
        id = self.kwargs.get('weather_pk')
        date = self.kwargs.get('slug')
        object = Weather.objects.get(id=id)
        if object not in city.weather_history.all().filter(in_date=date):
            pass
        else:
            return object

    def get_success_url(self, **kwargs):
        id = self.kwargs.get('weather_pk')
        return reverse_lazy('weather', kwargs={'weather_pk': id})


class WeatherDeleteView(LoginRequiredMixin, DeleteView):
    model = Weather
    context_object_name = 'weather'
    template_name = 'weather/weather_delete.html'

    def get_object(self, **kwargs):
        city_id = self.kwargs.get('pk')
        city = City.objects.get(id=city_id)
        id = self.kwargs.get('weather_pk')
        date = self.kwargs.get('slug')
        object = Weather.objects.get(id=id)
        if object not in city.weather_history.all().filter(in_date=date):
            pass
        else:
            return object

    def get_success_url(self, **kwargs):
        city_id = self.kwargs.get('pk')
        date = self.kwargs.get('slug')
        return reverse_lazy('city_by_date', kwargs={'pk': city_id, 'slug': date})

class WeatherCreateView(LoginRequiredMixin, CreateView):
    model = Weather
    context_object_name = 'weather'
    template_name = 'weather/weather_create.html'
    form_class = WeatherForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_id = self.kwargs.get('pk')
        city = City.objects.get(id=city_id)
        context['city'] = city
        date = self.kwargs.get('slug')
        context['date'] = date
        return context



    def get_object(self, **kwargs):
        id = self.kwargs.get('weather_pk')
        object = Weather.objects.get(id=id)
        return object

    def post(self, request, *args, **kwargs):
        city_id = self.kwargs.get('pk')
        current_date = datetime.now()
        date_formated = current_date.strftime("%Y-%m-%d")
        city = City.objects.get(id=city_id)
        form = WeatherForm(request.POST)
        if form.is_valid():
            new_weather = form.save()
            new_weather.save()
            city.weather_history.add(new_weather)
            city.save()
            return HttpResponseRedirect(reverse_lazy('city_by_date', kwargs={'pk': city_id, 'slug': date_formated}))
        return render(request, 'weather/weather_create.html', {'form': form})


def redirect_current_date(request, **kwargs):
    id = kwargs.get('pk')
    current_date = datetime.now()
    date_formated = current_date.strftime("%Y-%m-%d")
    return redirect(f'http://127.0.0.1:8000/weather/cities/{id}/{date_formated}/')