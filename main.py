import numpy as np
import json
import io
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
        try:
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
        except Exception as e:
            print(e)
            print("Error for connection {} to {}".format(begin, end))
            return [], []

    def generate_plotly_features(self, begin, end, time=12):
        (features, labels) = self.add_disruption(begin, end)
        for index, route_with_id in self.generator.routes.iterrows():
            route = route_with_id["stations"]
            route_id = route_with_id["id"]
            lat1, lon1 = self.generator.mapper.stop_to_coordinates(begin)
            #lat2, lon2 = self.generator.mapper.stop_to_coordinates(end)
            for i, station1 in enumerate(route):
                if station1 == begin:
                    # simplification for the sake of progress
                    stranded_capacity = self.generator.get_used_capacity(route_id, station1, time) * 250
        walkers = labels[0] * stranded_capacity
        bikers = labels[1] * stranded_capacity
        car_drivers = labels[2] * stranded_capacity
        pt_users = labels[3] * stranded_capacity
        lat, lon = self.generator.mapper.stop_to_coordinates(begin)
        bike_capacity = self.generator.mapper.get_bike_capacity(lat1, lon1)
        car_capacity = self.generator.mapper.get_car_capacity(lat1, lon1)
        pt_capacity = self.generator.mapper.get_opvn_capacity(lat1, lon1, stranded_capacity)
        return stranded_capacity, walkers, pt_users, min(pt_users, pt_capacity), bikers, min(bikers, bike_capacity),\
               car_drivers, min(car_drivers, car_capacity)

def pack_to_dict(strand, walk, pt, pt_use, bike, bike_use, car, car_use):
    dict = {}
    dict["stranded_passengers"] = strand
    dict["walking"] = walk
    dict["want_to_use_public_transport"] = pt
    dict["actually_use_public_transport"] = pt_use
    dict["want_to_ride_bike"] = bike
    dict["actually_ride_bike"] = bike_use
    dict["want_to_drive_car"] = car
    dict["actually_drive_car"] = car_use
    print(dict)
    return dict


if __name__ == "__main__":
    main = Main()
    #print(main.add_disruption("Hamburg Hbf", "Jungfernstieg"))
    features = {}
    strand, walk, pt, pt_use, bike, bike_use, car, car_use = main.generate_plotly_features("Lübecker Straße", "Lohmühlenstraße")
    features["Lohmühlenstraße"] = pack_to_dict(strand, walk, pt, pt_use, bike, bike_use, car, car_use)
    strand, walk, pt, pt_use, bike, bike_use, car, car_use = main.generate_plotly_features("Hamburg Hbf", "Jungfernstieg")
    features["Jungfernstieg"] = pack_to_dict(strand, walk, pt, pt_use, bike, bike_use, car, car_use)
    strand, walk, pt, pt_use, bike, bike_use, car, car_use = main.generate_plotly_features("Kellinghusenstraße", "Klosterstern")
    features["Klosterstern"] = pack_to_dict(strand, walk, pt, pt_use, bike, bike_use, car, car_use)
    strand, walk, pt, pt_use, bike, bike_use, car, car_use = main.generate_plotly_features("Steinfurther Allee", "Mümmelmannsberg")
    features["Mümmelmannsberg"] = pack_to_dict(strand, walk, pt, pt_use, bike, bike_use, car, car_use)
    strand, walk, pt, pt_use, bike, bike_use, car, car_use = main.generate_plotly_features("Poppenbüttel", "Wellingsbüttel")
    features["Wellingbüttel"] = pack_to_dict(strand, walk, pt, pt_use, bike, bike_use, car, car_use)
    strand, walk, pt, pt_use, bike, bike_use, car, car_use = main.generate_plotly_features("Diebsteich", "Holstenstraße")
    features["Holstenstraße"] = pack_to_dict(strand, walk, pt, pt_use, bike, bike_use, car, car_use)
    print(features)
    with io.open('data/plots.json', 'w', encoding='utf-8') as f:
        json.dump(features, f)
