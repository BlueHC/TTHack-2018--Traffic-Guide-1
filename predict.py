import numpy as np
import torch
from neural_net import HVVNet

class Predictor():
    def __init__(self, insize, outsize, model_path):
        self.model = HVVNet(insize, outsize)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
    
    def predict(self, scenarios, weights):
        distribution = np.array([0]*self.model.output_size)
        for scenario in zip(scenarios, weights):
            output = self.model(scenario).numpy()
            output /= sum(output)
            distribution += output * weights
        
        return distribution
        
            
