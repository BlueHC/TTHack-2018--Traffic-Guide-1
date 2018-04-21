import torch
from torch import nn
from torch.optim import Adam
from torch.autograd import Variable
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
plt.switch_backend('agg')
import numpy as np

class HVVNet(nn.Module):
    def __init__(self, input_size, output_size):
        super(HVVNet, self).__init__()
        self.f = nn.Sequential(
            nn.Linear(input_size, 12), nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(12, 12), nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(12, output_size), nn.Sigmoid())
    
    def forward(self, x):
        return self.f(x)

class HVVData(Dataset):
    def __init__(self, data_pairs):
        self.data_pairs = data_pairs
    
    def __len__(self):
        return len(self.data_pairs)
    
    def __getitem__(self, idx):
        d = self.data_pairs[idx]
        return torch.from_numpy(d[0]), torch.from_numpy(d[1])
    
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
        
if __name__ == "__main__":
    data = build_dummy_dummy_data()
    split = int(len(data) * 0.9)
    split = 3
    training_data = HVVData(data[:split])
    validation_data = HVVData(data[split:])
    
    input_size = len(data[0][0])
    output_size = len(data[0][1])
    
    model = HVVNet(input_size, output_size)
    batch_size = 2
    epochs = 20
    wd = 0.00001
    lr = 0.001
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
