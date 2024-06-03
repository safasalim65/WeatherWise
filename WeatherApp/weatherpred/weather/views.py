from django.shortcuts import render, redirect
import requests
from .models import City
from .forms import CityForm
import datetime
from django.http import HttpResponse
from django.contrib import messages

# Create your views here.
def index(request):
    url_current = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=9fad68433852b22d95a328bde4dac857&units=metric'
    url_forecast = 'http://api.openweathermap.org/data/2.5/forecast?q={}&appid=9fad68433852b22d95a328bde4dac857&units=metric'

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data['name']
            existing_city_count = City.objects.filter(name=new_city).count()
            if existing_city_count == 0:
                r = requests.get(url_current.format(new_city)).json()
                if r['cod'] == 200:
                    form.save()
                else:
                    messages.error(request, 'City does not exist!')
            else:
                messages.error(request, 'City already exists!')

    form = CityForm()
    cities = City.objects.all()
    weather_data = []

    for city in cities:
        # Fetch current weather data
        r_current = requests.get(url_current.format(city.name)).json()
        if r_current['cod'] == 200:
            current_weather = {
                'city': city.name,
                'temperature': r_current['main']['temp'],
                'description': r_current['weather'][0]['description'],
                'icon': r_current['weather'][0]['icon'],
                'humidity': r_current['main']['humidity'],
                'wind_speed': r_current['wind']['speed'],
                'sunrise': datetime.datetime.fromtimestamp(r_current['sys']['sunrise']),
                'sunset': datetime.datetime.fromtimestamp(r_current['sys']['sunset']),
            }
        else:
            current_weather = None

        # Fetch weather forecast data
        r_forecast = requests.get(url_forecast.format(city.name)).json()
        if r_forecast['cod'] == '200':
            forecast_data = []
            for forecast in r_forecast['list']:
                forecast_entry = {
                    'date': datetime.datetime.fromtimestamp(forecast['dt']),
                    'temperature': forecast['main']['temp'],
                    'description': forecast['weather'][0]['description']
                }
                forecast_data.append(forecast_entry)
        else:
            forecast_data = None

        weather_data.append({'current_weather': current_weather, 'forecast_data': forecast_data})

    context = {
        'weather_data': weather_data,
        'form': form,
        'messages': messages.get_messages(request)
    }
    return render(request, 'weather/weather.html', context)

def delete_city(requests, city_name):
    City.objects.get(name=city_name).delete()
    return redirect('home')