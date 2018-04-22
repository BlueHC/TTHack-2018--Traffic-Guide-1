import pandas as pd
import weatherApi
import numpy as np
from route_coordinate_mapping import HVVCoordinateMapper
from routing import load_routes
import json
import io


class DataGenerator:
    def __init__(self):
        self.mapper = HVVCoordinateMapper()
        self.routes = load_routes()
        self.routes_probs = []
        self.sbahn_routes = []
        self.unaffected_routes = []
        # self._load_s_bahn_routes()
        self.generate_dummy_usage()
        self.time_factor = {
            0: 1.1,
            1: 1.0,
            2: 1.0,
            3: 1.0,
            4: 1.0,
            5: 1.0,
            6: 1.4,
            7: 1.7,
            8: 1.7,
            9: 1.6,
            10: 1.5,
            11: 1.3,
            12: 1.3,
            13: 1.3,
            14: 1.3,
            15: 1.3,
            16: 1.6,
            17: 1.7,
            18: 1.7,
            19: 1.4,
            20: 1.3,
            21: 1.2,
            22: 1.1,
            23: 1.0
        }
        self.features = [-1 for i in range(0, 9)]
        pass

    def generate_weather(self):
        weather_id = np.random.choice([
            211,  # thunderstorm
            310,  # light drizzle
            500,  # rain
            602,  # heavy snow
            741,  # fog
            800,  # clear
            953,  # gentle breeze
        ],
            p=[0.05, 0.1, 0.1, 0.05, 0.1, 0.5, 0.1]
        )
        temp = np.random.randint(-2, 37) + 273.15
        return {"WeatherTypeID": weather_id, "TemperatureInKelvin": temp}

    def generate_good_weather(self):
        weather_id = 800
        temp = 22 + 273.15
        return {"WeatherTypeID": weather_id, "TemperatureInKelvin": temp}

    def bike_factor_for_weather(self, weather):
        """
        :param weather: a container for weather data (general, e.g. sunny and temperature)
        :return: a factor corresponding positively with "good" weather
        """
        id = weather["WeatherTypeID"]
        temperature = weather["TemperatureInKelvin"] - 273.15
        self.features[0] = id
        self.features[1] = temperature
        # see https://openweathermap.org/weather-conditions
        if id in [800, 801, 951, 952, 953]:
            bike_factor = 1
        elif id in [802, 803, 804, 954, 955, 701, 741, 600] or 300 <= id <= 311:
            bike_factor = 0.7
        elif 312 <= id <= 321:
            bike_factor = 0.4
        elif id in [500, 501, 601, 615, 616, 721]:
            bike_factor = 0.2
        else:
            bike_factor = 0
        # temperature adjustment
        if temperature < 5 or temperature > 30:
            bike_factor = bike_factor * 0
        elif 15 < temperature < 25:
            bike_factor = bike_factor * 1.2
        return bike_factor

    def get_car_factor(self, weather, distance, num_near_cars):
        """
        :param weather: weather container containing general weather conditions (e.g. cloudy) and temperature
        :param distance: euclidean distance to estimated destination
        :return: A factor for determining the popularity of bikes (higher -> more people ride bikes)
        """
        car_fact = num_near_cars / 5
        car_fact = car_fact * (1 - self.bike_factor_for_weather(weather))  # inverse correlation with good weather
        car_fact = car_fact * (distance / 10)  # proportional correlation with distance (1.0 distance ~= 100 km)
        return car_fact

    def get_bike_factor(self, weather, distance):
        """
        :param weather: weather container containing general weather conditions (e.g. cloudy) and temperature
        :param distance: euclidean distance to estimated destination
        :return: A factor for determining the popularity of bikes (higher -> more people ride bikes)
        """
        base_prob = max(0, 1 - (distance * 15))  # 100 / 15 ~= 6.5 km max. distance
        return base_prob * self.bike_factor_for_weather(weather)

    def get_foot_factor(self, weather, distance):
        """
        :param weather: weather container containing general weather conditions (e.g. cloudy) and temperature
        :param distance: euclidean distance to estimated destination
        :return: A factor for determining the popularity of walking (higher -> more people walk to their destination)
        """
        base_prob = max(0, 1 - (distance * 35))  # 100 / 35 ~= 3 km max. distance
        return base_prob * self.bike_factor_for_weather(weather)

    def get_public_transport_factor(self, lat_strand, lon_strand):
        """
        :param lat_strand: latitude where person is stranded
        :param lon_strand: longitude where person is stranded
        :return: a factor for determining the popularity of taking other public transportation
        """
        pt_fact = 0
        if self.alt_pt != []:
            pt_fact = 0.5
            for alt in self.alt_pt:
                lat_alt, lon_alt = self.mapper.stop_to_coordinates(alt[1])
                distance = self.mapper.get_distance(lat_strand, lon_strand, lat_alt, lon_alt)
                if distance == 0:
                    pt_fact = 0.9
                    break
                elif distance < 0.0035:
                    pt_fact = 0.7
        return pt_fact

    def _load_s_bahn_routes(self):
        """
        Would be used to load actual S-Bahn data to replace the generated dummy data.
        Currently not in use due to insufficient time for merging with the routes gotten from the HVV data
        """
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
        Filters out routes affected by the disruption between station1 and station2
        :param station1: The station 'behind' which the disruption occured
        :param station2: The station 'before' which the disruption occured
        """
        affected_routes = []
        for index, route_with_id in self.routes.iterrows():
            route = route_with_id["stations"]
            for i, station in enumerate(route):
                if station1 == station and len(route) > (i + 1) and station2 == route[i + 1] or \
                                                station2 == station and len(route) > (i + 1) and station1 == route[
                                    i + 1]:
                    affected_routes.append(index)
                    break
        self.unaffected_routes = self.routes.copy().drop(affected_routes)
        return affected_routes

    def generate_features_for_dest(self, start_station, dest_station, time, weather=weatherApi.currentWeatherData()):
        """
        Generates modal probabilities for a person wanting to travel to dest_station
        :param start_station: The station where the person is stranded
        :param dest_station: The station the person wants to travel to
        :return: probabilities for walking, biking, renting a car or taking other public transport
        """
        if start_station == dest_station:
            print("START STATION EQUALS DESTINATION")
        lat1, lon1 = self.mapper.stop_to_coordinates(start_station)
        bike_stations = self.mapper.bike_stations_in_range(lat1, lon1)
        lat2, lon2 = self.mapper.stop_to_coordinates(dest_station)
        dest_distance = self.mapper.get_distance(lat1, lon1, lat2, lon2)
        bike_fact = self.get_bike_factor(weather, dest_distance) if bike_stations != [] else 0
        foot_fact = self.get_foot_factor(weather, dest_distance)
        near_bus_stations = self.mapper.bus_stations_in_range(lat1, lon1)
        possible_dest_stations = self.mapper.bus_stations_in_range(lat2, lon2)
        self.alt_pt = []
        for index, route_with_id in self.unaffected_routes.iterrows():
            route = route_with_id["stations"]
            route_id = route_with_id["id"]
            for i, station1 in enumerate(route):
                if any(station1 == origin[0] for origin in near_bus_stations):
                    for z in range(i, len(route)):
                        if any(route[z] == dest[0] for dest in possible_dest_stations):
                            self.alt_pt.append((route_id, station1, self.get_used_capacity(route_id, station1, time)))
        near_cars = self.mapper.cars_in_range(lat1, lon1)
        car_fact = self.get_car_factor(weather, dest_distance, len(near_cars))
        pt_fact = self.get_public_transport_factor(lat1, lon1)

        ###
        self.generate_features(near_bus_stations, bike_stations, near_cars)
        dicts = {}
        #routes_dict = {}
        #for i, alt_route in enumerate(self.alt_pt):
         #   r_dict = {}
          #  r_dict["Haltestelle"] = alt_route[1]
          #  lat, lon = self.mapper.stop_to_coordinates(alt_route[1])
          #  r_dict["Latitude"] = lat
          #  r_dict["Longitude"] = lon
          #  routes_dict["Verbindung" + str(i)] = r_dict
        #dicts["OPNVAlternativen"] = routes_dict
        dicts["Sperrbeginn"] = start_station
        rad_dict = {}
        rad_dict["AnzahlFahrraeder"] = self.mapper.get_bike_capacity(lat1, lon1)
        dicts["StadtRAD"] = rad_dict
        sm_dict = {}
        sm_dict["AnzahlSharingMobility"] = self.mapper.get_car_capacity(lat1, lon1)
        dicts["SharingMobility"] = sm_dict
        with io.open('data/misc.txt', mode='a', encoding='UTF-8') as f:
            f.seek(0, 2)
            json.dump(dicts, f, ensure_ascii=False, indent=2)

            ###
        self.generate_features(near_bus_stations, bike_stations, near_cars)
        return self.modal_split(foot_fact, bike_fact, car_fact, pt_fact)

    def generate_features(self, near_bus_stations, bike_stations, near_cars):
        self.features[6] = self.get_closest(near_bus_stations, 1)
        self.features[7] = self.get_closest(bike_stations, 2)
        self.features[8] = self.get_closest(near_cars, 2)

    def get_closest(self, locations_with_distances, dist_index):
        if locations_with_distances == []:
            return 5
        minimum = locations_with_distances[0][dist_index]
        for loc in locations_with_distances:
            if loc[1] < minimum:
                minimum = loc[dist_index]
        return minimum

    def modal_split(self, foot_fact, bike_fact, car_fact, pt_fact):
        """
        Returns probabilities for 4 travel modalities based on a static modal split and a given condition-dependent
        collection of factors for each modality
        """
        base_foot = 0.1
        base_bike = 0.25
        base_car = 0.25
        base_pt = 0.4
        self.features[2] = base_foot
        self.features[3] = base_bike
        self.features[4] = base_car
        self.features[5] = base_pt
        foot = base_foot * foot_fact
        bike = base_bike * bike_fact
        car = base_car * car_fact
        pt = base_pt * pt_fact
        normal_factor = foot + bike + car + pt
        if normal_factor > 0:
            return (
            self.features, (foot / normal_factor, bike / normal_factor, car / normal_factor, pt / normal_factor))
        else:
            return (self.features, (0, 0, 0, 0))

    def get_used_capacity(self, route_id, station, time):
        route_capacities = self.routes_probs.loc[self.routes_probs[1] == route_id]
        for stop in route_capacities[0].values[0]:
            if stop[0] == station:
                capacity = (stop[1] * 100) ** 2.32 / 100
                return min(0.95, self.time_factor[time] * capacity)

    def generate_dummy_usage(self):
        for j, route in enumerate(self.routes["stations"]):
            route_prob = []
            total_prob = 0
            for i, stop in enumerate(route):
                prob = 1 - (abs((i / len(route)) - 0.5))  # approximate distribution of popularity of stations
                total_prob += prob
                route_prob.append((stop, prob))
            for i, (stop, prob) in enumerate(route_prob):
                # normalize probability, so that it's actually a probability
                route_prob[i] = (stop, prob / total_prob)
            self.routes_probs.append((route_prob, self.routes["id"][j]))
        self.routes_probs = pd.DataFrame(self.routes_probs)

    def generate_prob_mapping(self, start, end, route_index):
        (route, id) = self.routes_probs.iloc[route_index]
        partial_route = []
        prob_mapping = {}
        for i, (station, prob) in enumerate(route):
            if station == start:
                if end != route[0][0]:
                    print("not reversed")
                    partial_route = route[i + 1:]
                else:
                    print("reversed")
                    partial_route = list(reversed(route[:i]))
        if len(partial_route) == 0:
            print("Partial Route is empty!")
        total_prob = sum([prob for (station, prob) in partial_route])
        for (station, prob) in partial_route:
            prob_mapping[station] = prob / total_prob
        return prob_mapping


def _test_routing():
    gen = DataGenerator()
    gen.filter_disrupted_routes("Hamburg Hbf", "Jungfernstieg")
    gen.generate_features_for_dest("Hamburg Hbf", "Jungfernstieg", 17)


def _test_probable_destination():
    gen = DataGenerator()
    ret = gen.probable_destination("Aumühle", "Elbgaustraße")
    print(ret)


if __name__ == "__main__":
    _test_routing()
    # _test_probable_destination()
