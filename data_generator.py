import pandas as pd
import weatherApi
import numpy as np
from route_coordinate_mapping import HVVCoordinateMapper
from routing import load_routes


class DataGenerator:
    """
    Features:
    (static) modal split: Fahrrad, Fuß, Auto?
    Anzahl Fahrradstationen in 1km?
    Anzahl Bus-/Bahnstationen in der Nähe (Richtung?)
    Destination Proximity(je näher -> mehr Fuß/Fahrrad)
    Wetter (Temperatur, Niederschlagswahrscheinlichkeit)
    """

    def __init__(self):
        self.mapper = HVVCoordinateMapper()
        self.routes = load_routes()
        self.sbahn_routes = []
        #self._load_s_bahn_routes()
        pass

    def bike_probabilities_for_weather(self, weather):
        id = weather["WeatherTypeID"]
        temperature = weather["TemperatureInKelvin"] - 273.15
        # see https://openweathermap.org/weather-conditions
        if 200 <= id <= 300:
            bike_probability = 0
        elif id in [800, 801, 951, 952, 953]:
            bike_probability = 0.4
        elif id in [802, 803, 804, 954, 955, 701, 741, 600] or 300 <= id <= 311:
            bike_probability = 0.3
        elif 312 <= id <= 321:
            bike_probability = 0.2
        elif id in [500, 501, 601, 615, 616, 721]:
            bike_probability = 0.1
        else:
            bike_probability = 0
        # temperature adjustment
        if temperature < 5 or temperature > 30:
            bike_probability = bike_probability * 0
        elif 15 < temperature < 25:
            bike_probability = bike_probability * 1.2
        return bike_probability

    def get_foot_prob(self, weather, distance):
        base_prob = 1 - (distance * 200)
        return base_prob * self.bike_probabilities_for_weather(weather)

    def _load_s_bahn_routes(self):
        print('Loading S-Bahn Routes')
        df = pd.read_csv(filepath_or_buffer="data/Hackathon.csv", delimiter=";")
        current_route = [248206]
        for i, row in df.iterrows():
            if row["Zugnr"] == current_route[0]:
                current_route.append((row["Station"], row["Einsteiger"], row["Aussteiger"]))
            else:
                self.sbahn_routes.append(current_route)
                current_route = [row["Zugnr"]]
                current_route.append((row["Station"], row["Einsteiger"], row["Aussteiger"]))
        print('Finished loading S-Bahn Routes')

    def probable_destination(self, start_station, dest_station):
        """
        Generates relative proportions of people wanting to exit on stations between start_station and dest_station
        :return: a list of stations between start_station and dest_station (including dest_station) along with the
                 proportion of people wanting to exit there
        """
        stops_to_passengers = {}
        for r in self.sbahn_routes:
            if len(r) > 1 and r[-1][0] == dest_station:
                past_start_station = False
                for (station, entr, exit) in r[1:]:
                    if past_start_station:
                        try:
                            if stops_to_passengers[station] is None:
                                stops_to_passengers[station] = int(float(exit.replace(",", ".")))
                            else:
                                stops_to_passengers[station] = stops_to_passengers[station] + int(float(exit.replace(",", ".")))
                        except KeyError:
                            stops_to_passengers[station] = int(float(exit.replace(",", ".")))
                    elif station == start_station:
                        past_start_station = True
        return [(station, stops_to_passengers[station]) for station in stops_to_passengers.keys()]

    def generate_features_for_dest(self, start_station, dest_station):
        """
        Generates modal probabilities for a person wanting to travel to dest_station
        :param start_station: The station where the person is stranded
        :param dest_station: The station the person wants to travel to
        :return: probabilities for walking, biking, renting a car or taking other public transport
        """
        weather = weatherApi.currentWeatherData()
        bike_prob = self.bike_probabilities_for_weather(weather)
        lat1, lon1 = self.mapper.stop_to_coordinates(start_station)
        bike_stations = self.mapper.bike_stations_in_range(lat1, lon1)
        lat2, lon2 = self.mapper.stop_to_coordinates(dest_station)
        dest_distance = self.mapper.get_distance(lat1, lon1, lat2, lon2)
        foot_prob = self.get_foot_prob(weather, dest_distance)

        near_bus_stations = self.mapper.bus_stations_in_range(lat1, lon1) #TODO: schauen ob aktuelle position bei near dabei ist
        possible_dest_stations = self.mapper.bus_stations_in_range(lat2, lon2)
        alt_pt = []
        for route in self.routes["stations"].values:
            for i, station1 in enumerate(route):
                if any(station1 == origin[0] for origin in near_bus_stations):
                    for z in range(i, len(route)):
                        if any(route[z] == dest[0] for dest in possible_dest_stations):
                            alt_pt.append(route) 

    def generate_modal_split(self, start, dest):
        following_stations = self.get_stations_on_route(start, dest)
        base_pt=0.25
        base_bike=0.2
        base_car=0.45
        base_foot=0.1


    def get_stations_on_route(self, start, dest):
        return []

    def dummy_bus_data(self):
        pass

    def dummy_sub_data(self):
        pass

def _test_routing():
    gen = DataGenerator()
    gen.generate_features_for_dest("Hamburg Hbf", "Jungfernstieg")

def _test_probable_destination():
    gen = DataGenerator()
    ret = gen.probable_destination("Aumühle", "Elbgaustraße")
    print(ret)

if __name__ == "__main__":
    _test_routing()
    #_test_probable_destination()
