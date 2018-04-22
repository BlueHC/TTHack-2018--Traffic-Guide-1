import torch
from torch import nn
from torch.optim import Adam
from torch.autograd import Variable
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
plt.switch_backend('agg')
import numpy as np
import pandas as pd
import random
from main import Main

class HVVNet(nn.Module):
    def __init__(self, input_size, output_size):
        super(HVVNet, self).__init__()
        self.f = nn.Sequential(
            nn.Linear(input_size, 8), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(8, 8), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(8, output_size), nn.ReLU())
    
    def forward(self, x):
        return self.f(x)

class HVVData(Dataset):
    def __init__(self, data_pairs):
        self.data_pairs = data_pairs
    
    def __len__(self):
        return len(self.data_pairs[0])
    
    def __getitem__(self, idx):
        return torch.from_numpy(self.data_pairs[0][idx]), torch.from_numpy(self.data_pairs[1][idx])
    
def train(model, train_loader, optimizer, criterion):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.cpu().float(), target.cpu().float()
        data, target = Variable(data), Variable(target)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
    return loss.data[0]
    
def validate(model, test_loader, criterion):
    model.eval()
    for batch_idx, (data, target) in enumerate(test_loader):
        data, target = data.cpu().float(), target.cpu().float()
        data, target = Variable(data), Variable(target)
        output = model(data)
        loss = criterion(output, target)
    return loss.data[0]


def build_dummy_dummy_data():
    inputs = np.array([
        np.array([4, 1, 4, 2]),
        np.array([5, 2, 3, 5]),
        np.array([9, 2, 4, 1]),
        np.array([4, 2, 3, 7])])
    
    outputs = np.array([
        np.array([0.5, 0.3, 0.1, 0.1]),
        np.array([0.7, 0.05, 0.05, 0.2]),
        np.array([0.4, 0.2, 0.1, 0.3]),
        np.array([0.2, 0.5, 0.25, 0.05])])
    
    return np.array([np.array([inputs[i], outputs[i]]) for i in range(len(outputs))])
        
def generate_stop_pairs(n_disturbances):
    valid_pairs = []
    good_ids = pd.read_csv("../good_trips.csv").values.reshape(-1)
    stops = pd.read_csv("data/stops.txt", usecols=["stop_id", "stop_name"], 
                        dtype={"stop_id":"str"})
    stop_times = pd.read_csv("data/stop_times.txt", usecols=["stop_id", "trip_id", "stop_sequence"], dtype={"stop_id":"str"})
    merged = stop_times.merge(stops, on="stop_id").sort_values(by=["trip_id", "stop_sequence"]).drop(["stop_id"], axis=1)
    merged["next_stop"] = merged["stop_name"].shift(-1)
    merged["next_trip_id"] = merged["trip_id"].shift(-1)
    merged = merged.iloc[:-1]
    merged["next_stop"] = merged["next_stop"].astype("str")
    merged["next_trip_id"] = merged["next_trip_id"].astype(int)
    merged = merged.drop(["stop_sequence"], axis=1)
    merged = merged.loc[[idee in good_ids for idee in merged["trip_id"]]]
    merged = merged.drop_duplicates(subset=["stop_name", "next_stop"])
    
    for i, row in enumerate(merged.iterrows()):
        r = row[1]
        if r.trip_id == r.next_trip_id:
            valid_pairs.append([(r.stop_name, r.next_stop)])
    
    samples = random.sample(valid_pairs, n_disturbances)
    
    return samples

def binarize_weather_id(samples):
    idx = 0
    possible_labels = np.array([211, 310, 500, 602, 741, 800, 953])
    binaries = []
    for sample in samples:
        binaries.append((possible_labels == sample[idx]).astype(int))
    
    return np.concatenate((np.delete(samples, idx, axis=1), np.array(binaries)), axis=1)
    
if __name__ == "__main__":
    m = Main()
    pairs = generate_stop_pairs(2)
    
    ins = []
    outs = []
    for pair in pairs:
        feat, out = m.add_disruption(*pair[0], time=random.randint(0, 23))
        if feat == []:
            continue
        ins.append(feat)
        outs.append(out)
    
    ins = np.array(ins)
    outs = np.array(outs)
    print("ins before", ins)
    ins = binarize_weather_id(ins)
    print("ins after", ins)
    
    print("outs", outs)
    
    data = (ins, outs)
    print("data", data)
    split = int(len(data) * 0.8)
    split = 1

    training_data = HVVData((data[0][:split], data[1][:split]))
    validation_data = HVVData((data[0][split:], data[1][split:]))
    
    input_size = len(data[0][0])
    output_size = len(data[1][0])
    
    model = HVVNet(input_size, output_size)
    batch_size = 1
    epochs = 100
    wd = 0.00001
    lr = 0.0001
    criterion = nn.MSELoss()
    optimizer = Adam(model.parameters(), lr=lr, weight_decay=wd)
    
    train_loader = DataLoader(training_data, shuffle=True, batch_size=batch_size)
    test_loader = DataLoader(validation_data, batch_size=len(validation_data))
    
    training_losses = []
    validation_losses = []
    for epoch in range(1, epochs):
        print('--- Epoch', epoch, "---")
        
        training_loss = train(model, train_loader, optimizer, criterion)
        training_losses.append(training_loss)
        print('Training Loss: {:.6f}'.format(training_loss))
                                                
        validation_loss = validate(model, test_loader, criterion)
        validation_losses.append(validation_loss)
        print('Validation Loss: {:.6f}'.format(validation_loss))
    
    filename = "learning-rate=" + str(lr) + "_weight-decay=" + str(wd)
    
    plt.figure(figsize=(20,15))
    font = {'family' : 'DejaVu Sans',
            'weight' : 'normal',
            'size'   : 24}

    plt.rc('font', **font)
    plt.title("Learning Rate {} | Weight Decay {}".format(lr, wd))
    plt.plot(training_losses, "b", marker="o", linestyle="dashed")
    plt.plot(validation_losses, "r", marker="o", linestyle="dashed")
        
    plt.legend(["Training Loss", "Validation Loss"])
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")
    plt.savefig(filename + ".png")
    
    torch.save(model.state_dict(), filename + ".model")
