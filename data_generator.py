import pandas as pd
import weatherApi
import numpy as np
import scipy.stats as sp
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
        self.routes_probs = []
        self.sbahn_routes = []
        # self._load_s_bahn_routes()
        pass

    
    def generate_weather(self):
        weather_id = np.random.choice([
                        211, # thunderstorm
                        310, # light drizzle
                        500, # rain
                        602, # heavy snow
                        741, # fog
                        800, # clear
                        953, # gentle breeze
                        ],
                        p = [0.05, 0.1, 0.1, 0.05, 0.1, 0.5, 0.1]
                    )
        
        temp = np.random.randint(-2, 37) + 273.15
        
        return {"WeatherTypeID":weather_id, "TemperatureInKelvin":temp}
        
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
        self.sbahn_routes = np.asarray(self.sbahn_routes)
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
                                stops_to_passengers[station] = stops_to_passengers[station] + int(
                                    float(exit.replace(",", ".")))
                        except KeyError:
                            stops_to_passengers[station] = int(float(exit.replace(",", ".")))
                    elif station == start_station:
                        past_start_station = True
        count_list = [(station, stops_to_passengers[station]) for station in stops_to_passengers.keys()]
        total_count = 0
        for c in count_list:
            total_count += c[1]
        return [(station, count / total_count) for (station, count) in count_list]

    def filter_disrupted_routes(self, station1, station2):
        """
        Filters out routes disrupted by the disruption between station1 and station2
        :param station1: The first station between the disruption occured
        :param station2: The second station between the disruption occured
        """
        affected_routes = []
        for index, route_with_id in self.routes.iterrows():
            route = route_with_id["stations"]
            for i, station in enumerate(route):
                if station1 == station and len(route) > (i+1) and station2 == route[i+1] \
                    or station2 == station and len(route) > (i+1) and station1 == route[i+1]:
                    affected_routes.append(index)
                    break
        self.unaffected_routes = self.routes.copy().drop(affected_routes)                 

    def generate_features_for_dest(self, start_station, dest_station):
        """
        Generates modal probabilities for a person wanting to travel to dest_station
        :param start_station: The station where the person is stranded
        :param dest_station: The station the person wants to travel to
        :return: probabilities for walking, biking, renting a car or taking other public transport
        """
        #weather = weatherApi.currentWeatherData()
        weather = self.generate_weather()
        bike_prob = self.bike_probabilities_for_weather(weather)
        lat1, lon1 = self.mapper.stop_to_coordinates(start_station)
        bike_stations = self.mapper.bike_stations_in_range(lat1, lon1)
        lat2, lon2 = self.mapper.stop_to_coordinates(dest_station)
        dest_distance = self.mapper.get_distance(lat1, lon1, lat2, lon2)
        foot_prob = self.get_foot_prob(weather, dest_distance)
        near_bus_stations = self.mapper.bus_stations_in_range(lat1, lon1)
        possible_dest_stations = self.mapper.bus_stations_in_range(lat2, lon2)
        alt_pt = []
        for route in self.unaffected_routes["stations"].values:
            for i, station1 in enumerate(route):
                if any(station1 == origin[0] for origin in near_bus_stations):
                    for z in range(i, len(route)):
                        if any(route[z] == dest[0] for dest in possible_dest_stations):
                            alt_pt.append(route)
        if alt_pt != []:
            print("Alternative found!")

    def generate_modal_split(self, start, dest):
        following_stations = self.get_stations_on_route(start, dest)
        base_pt = 0.25
        base_bike = 0.2
        base_car = 0.45
        base_foot = 0.1

    def combine_sbahn_into_normal_routes(self):
        pass

    def generate_dummy_usage(self):
        for j, route in enumerate(self.routes["stations"]):
            route_prob = []
            total_prob = 0
            for i, stop in enumerate(route):
                prob = 1 - (abs(i / len(route) - 0.5))  # approximate distribution of popularity of stations
                total_prob += prob
                route_prob.append((stop, prob))
            for i, (stop, prob) in enumerate(route_prob):
                # normalize probability, so that it's actually a probability
                route_prob[i] = (stop, prob / total_prob)
            self.routes_probs.append((route_prob, self.routes["id"][j]))
        self.routes_probs = pd.DataFrame(self.routes_probs)
        print(self.routes_probs)

    def get_probabilities_for_route(self, start, last_stop):
        pass

    def get_stations_on_route(self, start, dest):
        return []

    def dummy_bus_data(self):
        pass

    def dummy_sub_data(self):
        pass


def _test_routing():
    gen = DataGenerator()
    gen.filter_disrupted_routes("Hamburg Hbf", "Jungfernstieg")
    gen.generate_features_for_dest("Hamburg Hbf", "Jungfernstieg")
    gen.combine_sbahn_into_normal_routes()
    # print(gen.routes)
    gen.generate_dummy_usage()


def _test_probable_destination():
    gen = DataGenerator()
    ret = gen.probable_destination("Aumühle", "Elbgaustraße")
    print(ret)


if __name__ == "__main__":
    _test_routing()
    # _test_probable_destination()
