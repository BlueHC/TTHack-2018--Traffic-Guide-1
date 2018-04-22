import urllib.request
import urllib.parse
import json

def amountStadtRadAvailable():
    # The function returns a list of 3-Tuples. Latitude, Longitude of a StadtRAD station. Number of bikes available at station.
    url = 'https://stadtrad.hamburg.de/kundenbuchung/hal2ajax_process.php?zoom=10&lng1=&lat1=&lng2=&lat2=&stadtCache=&mapstation_id=&mapstadt_id=75&verwaltungfirma=&centerLng=9.986872299999959&centerLat=53.56661530000001&searchmode=default&with_staedte=N&buchungsanfrage=N&bereich=2&stoinput=&before=&after=&ajxmod=hal2map&callee=getMarker&requester=bikesuche&key=&webfirma_id=510'

    f = urllib.request.urlopen(url)
    payload = f.read().decode('utf-8')
    payloadjson = json.loads(payload)

    resultMap = {}

    numberStations = len(payloadjson['marker'])
    amountBikesTotal = 0
    for i in range(0, numberStations):
        resultLat = float(payloadjson['marker'][i]['lat'])
        resultLng = float(payloadjson['marker'][i]['lng'])
        resultAmount = len(payloadjson['marker'][i]['hal2option']['bikelist'])
        resultMap[(resultLat, resultLng)] = resultAmount
        amountBikesTotal += resultAmount

    # Number of stations and bikes in total
    # print('Number of stations: ' + str(numberStations))
    # print('Number of bikes: ' + str(amountBikesTotal))
        
    return resultMap

def amountStadtRadAvailableJSON():
    url = 'https://stadtrad.hamburg.de/kundenbuchung/hal2ajax_process.php?zoom=10&lng1=&lat1=&lng2=&lat2=&stadtCache=&mapstation_id=&mapstadt_id=75&verwaltungfirma=&centerLng=9.986872299999959&centerLat=53.56661530000001&searchmode=default&with_staedte=N&buchungsanfrage=N&bereich=2&stoinput=&before=&after=&ajxmod=hal2map&callee=getMarker&requester=bikesuche&key=&webfirma_id=510'

    f = urllib.request.urlopen(url)
    payload = f.read().decode('utf-8')
    payloadjson = json.loads(payload)

    resultList = []
    numberStations = len(payloadjson['marker'])
    
    for i in range(0, numberStations):
        resultLat = payloadjson['marker'][i]['lat']
        resultLng = payloadjson['marker'][i]['lng']
        resultAmount = len(payloadjson['marker'][i]['hal2option']['bikelist'])
        resultDictElement = {'Latitude': resultLat,
                             'Longitude': resultLng,
                             'AmountBikes': resultAmount}
        resultList.append(resultDictElement)
        
    resultToJson = {'items': resultList}
    resultJson = json.dumps(resultToJson)

    return resultJson

