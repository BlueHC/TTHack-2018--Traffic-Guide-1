import urllib.request
import urllib.parse
import json

def currentWeatherData():
    url = 'https://api.openweathermap.org/data/2.5/weather?q=Hamburg&APPID=b5b4fb75e69eaf5754f4412ca9700d1b'
    f = urllib.request.urlopen(url)
    payload = f.read().decode('utf-8')
    payloadjson = json.loads(payload)

    result = {'TemperatureInKelvin': payloadjson['main']['temp'],
              'WeatherTypeID': payloadjson['weather'][0]['id'],
              'WeatherMain': payloadjson['weather'][0]['main'],
              'WeatherDescription': payloadjson['weather'][0]['description']}

    return result
