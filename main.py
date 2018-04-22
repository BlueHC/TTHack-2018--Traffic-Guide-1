import numpy as np
from data_generator import DataGenerator


class Main:

    def __init__(self):
        self.generator = DataGenerator()

    def add_disruption(self, begin, end, time=12):
        features_printed=False
        weather = self.generator.generate_weather()
        affected_routes = self.generator.filter_disrupted_routes(begin, end)
        walkers = 0
        bikers = 0
        car_drivers = 0
        pt_users = 0
        routes = self.generator.routes["stations"][affected_routes]
        norm_fact = 2 * len(routes)
        for index, route in enumerate(routes):
            got_first_stop = False
            for i, stop in enumerate(route):
                if stop == begin or stop == end:
                    if got_first_stop:
                        station_prob_mapping = self.generator.generate_prob_mapping(stop, route[-1], affected_routes[index])
                        stations_to_target = route[i+1:]
                        for station in stations_to_target:
                            features, (walking_prob, bike_prob, car_prob, pt_prob) = self.generator.generate_features_for_dest(stop, station, time, weather=weather)
                            walkers += walking_prob * station_prob_mapping[station]
                            bikers += bike_prob * station_prob_mapping[station]
                            car_drivers += car_prob * station_prob_mapping[station]
                            pt_users += pt_prob * station_prob_mapping[station]
                    else:
                        station_prob_mapping = self.generator.generate_prob_mapping(stop, route[0], affected_routes[index])
                        stations_to_target = reversed(route[:i])
                        for station in stations_to_target:
                            features, (walking_prob, bike_prob, car_prob, pt_prob) = self.generator.generate_features_for_dest(stop, station, time, weather=weather)
                            if not features_printed:
                                print("Features: %s" % features)
                                features_printed = True
                            walkers += walking_prob * station_prob_mapping[station]
                            bikers += bike_prob * station_prob_mapping[station]
                            car_drivers += car_prob * station_prob_mapping[station]
                            pt_users += pt_prob * station_prob_mapping[station]
                        got_first_stop = True
        return (features, np.array([walkers / norm_fact, bikers / norm_fact, car_drivers / norm_fact, pt_users / norm_fact]))

    def return_json(self, json_text):
        begin = ""
        end = ""
        (features, labels) = self.add_disruption(begin, end)
        stranded_capacity = self.generator.get_used_capacity()
        walkers = labels[0] * stranded_capacity
        bikers = labels[1] * stranded_capacity
        car_drivers = labels[2] * stranded_capacity
        pt_users = labels[3] * stranded_capacity
        lat, lon = self.generator.mapper.stop_to_coordinates(begin)
        bike_capacity = self.generator.mapper.get_bike_capacity(lat, lon)
        car_capacity = self.generator.mapper.get_car_capacity(lat, lon)
        pt_capacity = self.generator.mapper.get_opvn_capacity(lat, lon)
        return stranded_capacity, walkers, pt_users, min(pt_users, pt_capacity), bikers, min(bikers, bike_capacity),\
               car_drivers, min(car_drivers, car_capacity)

if __name__ == "__main__":
    main = Main()
    print(main.add_disruption("Hamburg Hbf", "Jungfernstieg"))
