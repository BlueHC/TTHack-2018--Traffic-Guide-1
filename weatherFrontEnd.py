import urllib.request
import urllib.parse
import json

def weatherFrontEnd():
    """
    The function returns a json with the weather data, that will be used for the frontend

    TypeIDs: https://openweathermap.org/weather-conditions
             2xx: Thunderstorm
             3xx: Drizzle
             5xx: Rain
             6xx: Snow
             7xx: Atmosphere
             800: Clear
             80x: Clouds
             90x: Extreme
             9xx: Misc
    """
    url = 'https://api.openweathermap.org/data/2.5/weather?q=Hamburg&APPID=b5b4fb75e69eaf5754f4412ca9700d1b'
    f = urllib.request.urlopen(url)
    payload = f.read().decode('utf-8')
    payloadjson = json.loads(payload)

    iconBaseUrl = 'http://openweathermap.org/img/w/'
    iconUrl = iconBaseUrl + str(payloadjson['weather'][0]['icon']) + '.png'

    temperatureInCelsius = int(float(payloadjson['main']['temp']) - 273.15)
    resultToday = {'TemperatureInCelsius': temperatureInCelsius,
              'WeatherTypeID': payloadjson['weather'][0]['id'],
              'WeatherMain': payloadjson['weather'][0]['main'],
              'WeatherDescription': payloadjson['weather'][0]['description'],
              'WeatehrIconUrl': iconUrl}

    resultJson = json.dumps(result)
    
    # outout to file. Not sure if it works correctly.
    # with open('weatherFrontEndJSON.txt', 'w') as outfile:
    #    json.dump(resultJson, outfile)

    return resultJson


def weatherFrontEndForecast():    
    urlForecast = 'https://api.openweathermap.org/data/2.5/weather?q=Hamburg&APPID=b5b4fb75e69eaf5754f4412ca9700d1b'
    g = urllib.request.urlopen(urlForecast)
    payloadForecast = g.read().decode('utf-8')
    payloadForecastJson = json.loads(payloadForecast)



    







