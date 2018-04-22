import numpy as np
import torch
from torch.autograd import Variable
from neural_net import HVVNet

class Predictor():
    def __init__(self, insize, outsize, model_path):
        self.model = HVVNet(insize, outsize)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
    
    def predict(self, scenarios, weights):
        distribution = np.array([0.0]*4)
        for scenario, weight in zip(scenarios, weights):
            scenario = Variable(torch.from_numpy(scenario).float())
            output = self.model(scenario).data.numpy()
            output /= sum(output)
            distribution += output * weight
        
        return distribution
    
    def predict2(self, disruption):
        disruption = Variable(torch.from_numpy(disruption).float())
        output = self.model(disruption).data.numpy()
        return output /= sum(output)
            
if __name__ == "__main__":
    model_path = "learning-rate=0.001_weight-decay=1e-05.model"
    p = Predictor(4, 4, model_path)
    example = [np.array([3,4,2,1])]
    print(p.predict(example, np.array([1])))
