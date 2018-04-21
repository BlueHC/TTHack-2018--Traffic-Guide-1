from route_coordinate_mapping import HVVCoordinateMapper
from data_generator import DataGenerator


class Main:

    def __init__(self):
        self.generator = DataGenerator()

    def add_disruption(self, begin, end, time=12):
        print(len(self.generator.routes))
        affected_routes = self.generator.filter_disrupted_routes(begin, end)
        print(len(self.generator.routes))
        walkers = 0
        bikers = 0
        car_drivers = 0
        pt_users = 0
        for route in self.generator.routes["stations"][affected_routes]:
            got_first_stop = False
            for i, stop in enumerate(route):
                if stop == begin or stop == end:
                    if got_first_stop:
                        walking_prob, bike_prob, car_prob, pt_prob = self.generator.generate_features_for_dest(stop, route[-1])
                        #walkers += walking_prob * TODO: wait for capacity
                    else:
                        walking_prob, bike_prob, car_prob, pt_prob = self.generator.generate_features_for_dest(stop, route[0])

if __name__ == "__main__":
    main = Main()
    main.add_disruption("Hamburg Hbf", "Jungfernstieg")