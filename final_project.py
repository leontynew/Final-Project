# -*- coding: utf-8 -*-
"""Final Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10FiQfdDBgnL9HGnVVFRff3W7i8ytvMXN

Final Project-Luyang Wang 65788904

## First task-Implementation of LSB
"""

from google.colab import drive
drive.mount('/content/drive')
import sys
sys.path.insert(0,'/content/drive/My Drive/110bprojects')

import numpy as np
from PIL import Image
import os
import cv2
from google.colab.patches import cv2_imshow
path = os.getcwd()
img1 = Image.open(path + "/drive/MyDrive/110bprojects/finalproject/coast/arnat59.jpg").convert("RGB")
img1

path = os.getcwd()
img2 = Image.open(path + "/drive/MyDrive/110bprojects/finalproject/forest/bost98.jpg").convert("RGB")
img2

def LSB(img1, img2):
    assert img1.size == img2.size
    #reshape array of size 196608 into shape (256,256,3)
    image_size = tuple(list(img1.size)+[3])
    array1 = np.array(img1.getdata()).reshape(image_size)
    array2 = np.array(img2.getdata()).reshape(image_size)
    #binary tuple
    bin_vec = np.vectorize(lambda _int: f"{_int:08b}")
    merge_vec = np.vectorize(lambda _bin1, _bin2: _bin1[:4]+_bin2[4:])
    #integer tuple with the two RGB values merged. 
    merge = merge_vec(bin_vec(array1), bin_vec(array2))
    #integer tuple
    int_vec = np.vectorize(lambda _bin: int(_bin, 2))
    merge_array = int_vec(merge)
    merge_image = Image.fromarray(np.uint8(merge_array), "RGB")
    return merge_image

"""Reference: https://github.com/kelvins/steganography/blob/main/steganography.py"""

lsb = LSB(img1, img2)
lsb

"""## Second task-Neural Network

Reference: https://github.com/fpingham/DeepSteg/blob/master/DeepSteganography.ipynb
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import random_split
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.autograd import Variable
import matplotlib.pyplot as plt

gamma = 1
learning_rate = .0001
num_epochs = 3
train_ratio = .8

images = []
for folder in os.listdir(path + "/drive/MyDrive/110bprojects/finalproject"):
    if not folder.startswith("."):
        for file in os.listdir(os.path.join(path + "/drive/MyDrive/110bprojects/finalproject", folder)):
            if file.endswith(".jpg"):
                image = Image.open(os.path.join(
                    path + "/drive/MyDrive/110bprojects/finalproject", folder, file)).convert("RGB")
                image_size = tuple(list(image.size)+[3])
                images.append(np.array(image.getdata()).reshape(image_size))

lengths = [int(train_ratio*len(images)), len(images) -
           int(train_ratio*len(images))]
X_train, X_test = random_split(images, lengths, generator=torch.Generator().manual_seed(42))
X_train = np.array(X_train) / 255
X_test = np.array(X_test) / 255

# Creates training set
train_loader = DataLoader(X_train, batch_size=2, pin_memory=True, shuffle=True)
# Creates test set
test_loader = DataLoader(X_test, batch_size=2, pin_memory=True, shuffle=True)

# Preparation Network (2 conv layers)
class PrepNetwork(nn.Module):
    def __init__(self):
        super(PrepNetwork, self).__init__()
        # preparation network
        self.initial_p3 = nn.Sequential(nn.Conv2d(3, 50, kernel_size=3, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=3, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=3, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=3, padding=1), nn.ReLU())
        self.initial_p4 = nn.Sequential(nn.Conv2d(3, 50, kernel_size=4, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=4, padding=2), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=4, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=4, padding=2), nn.ReLU())
        self.initial_p5 = nn.Sequential(nn.Conv2d(3, 50, kernel_size=5, padding=2), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=5, padding=2), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=5, padding=2), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=5, padding=2), nn.ReLU())
        self.final_p3 = nn.Sequential(nn.Conv2d(150, 50, kernel_size=3, padding=1), nn.ReLU())
        self.final_p4 = nn.Sequential(nn.Conv2d(150, 50, kernel_size=4, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=4, padding=2), nn.ReLU())
        self.final_p5 = nn.Sequential(nn.Conv2d(150, 50, kernel_size=5, padding=2), nn.ReLU())

    def forward(self, p):
        p1 = self.initial_p3(p)
        p2 = self.initial_p4(p)
        p3 = self.initial_p5(p)
        mid = torch.cat((p1, p2, p3), 1)
        p4 = self.final_p3(mid)
        p5 = self.final_p4(mid)
        p6 = self.final_p5(mid)
        output = torch.cat((p4, p5, p6), 1)
        return output

# Hiding Network (5 conv layers)
class HidingNetwork(nn.Module):
    def __init__(self):
        super(HidingNetwork, self).__init__()
        # hiding network
        self.initial_h3 = nn.Sequential(nn.Conv2d(153, 50, kernel_size=3, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=3, padding=1), nn.ReLU(
        ), nn.Conv2d(50, 50, kernel_size=3, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=3, padding=1), nn.ReLU())
        self.initial_h4 = nn.Sequential(nn.Conv2d(153, 50, kernel_size=4, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=4, padding=2), nn.ReLU(
        ), nn.Conv2d(50, 50, kernel_size=4, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=4, padding=2), nn.ReLU())
        self.initial_h5 = nn.Sequential(nn.Conv2d(153, 50, kernel_size=5, padding=2), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=5, padding=2), nn.ReLU(
        ), nn.Conv2d(50, 50, kernel_size=5, padding=2), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=5, padding=2), nn.ReLU())
        self.final_h3 = nn.Sequential(
            nn.Conv2d(150, 50, kernel_size=3, padding=1), nn.ReLU())
        self.final_h4 = nn.Sequential(nn.Conv2d(150, 50, kernel_size=4, padding=1), nn.ReLU(
        ), nn.Conv2d(50, 50, kernel_size=4, padding=2), nn.ReLU())
        self.final_h5 = nn.Sequential(nn.Conv2d(150, 50, kernel_size=5, padding=2), nn.ReLU())
        self.final_h = nn.Sequential(nn.Conv2d(150, 3, kernel_size=1, padding=0))

    def forward(self, h):
        h1 = self.initial_h3(h)
        h2 = self.initial_h3(h)
        h3 = self.initial_h3(h)
        mid = torch.cat((h1, h2, h3), 1)
        h4 = self.final_h3(mid)
        h5 = self.final_h4(mid)
        h6 = self.final_h5(mid)
        mid2 = torch.cat((h4, h5, h6), 1)
        output = self.final_h(mid2)
        output_noise = Variable(
            output.data + nn.init.normal_(torch.Tensor(output.data.size()), 0, 0.1))
        return output, output_noise

#Reveal Network (2 conv layers)
class RevealNetwork(nn.Module):
    def __init__(self):
        super(RevealNetwork, self).__init__()
        # hiding network
        self.initial_r3 = nn.Sequential(nn.Conv2d(3, 50, kernel_size=3, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=3, padding=1), nn.ReLU(
        ), nn.Conv2d(50, 50, kernel_size=3, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=3, padding=1), nn.ReLU())
        self.initial_r4 = nn.Sequential(nn.Conv2d(3, 50, kernel_size=4, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=4, padding=2), nn.ReLU(
        ), nn.Conv2d(50, 50, kernel_size=4, padding=1), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=4, padding=2), nn.ReLU())
        self.initial_r5 = nn.Sequential(nn.Conv2d(3, 50, kernel_size=5, padding=2), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=5, padding=2), nn.ReLU(
        ), nn.Conv2d(50, 50, kernel_size=5, padding=2), nn.ReLU(), nn.Conv2d(50, 50, kernel_size=5, padding=2), nn.ReLU())
        self.final_r3 = nn.Sequential(
            nn.Conv2d(150, 50, kernel_size=3, padding=1), nn.ReLU())
        self.final_r4 = nn.Sequential(nn.Conv2d(150, 50, kernel_size=4, padding=1), nn.ReLU(
        ), nn.Conv2d(50, 50, kernel_size=4, padding=2), nn.ReLU())
        self.final_r5 = nn.Sequential(nn.Conv2d(150, 50, kernel_size=5, padding=2), nn.ReLU())
        self.final_r = nn.Sequential(nn.Conv2d(150, 3, kernel_size=1, padding=0))

    def forward(self, r):
        r1 = self.initial_r3(r)
        r2 = self.initial_r4(r)
        r3 = self.initial_r5(r)
        mid = torch.cat((r1, r2, r3), 1)
        r4 = self.final_r3(mid)
        r5 = self.final_r4(mid)
        r6 = self.final_r5(mid)
        mid2 = torch.cat((r4, r5, r6), 1)
        output = self.final_r(mid2)
        return output

# Join three networks in one module
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.m1 = PrepNetwork()
        self.m2 = HidingNetwork()
        self.m3 = RevealNetwork()
    
    def forward(self, original, secret):
        x1 = self.m1(secret)
        mid = torch.cat((x1, original), 1)
        x2, x2_noise = self.m2(mid)
        x3 = self.m3(x2_noise)
        return x2, x3

net = Net()

def preprocess(tensor):
    tensor = tensor.unsqueeze(0)
    tensor = torch.swapaxes(tensor, -2, -1)
    tensor = torch.swapaxes(tensor, -3, -2)
    return tensor

def gaussian(tensor, mean=0, std=.1):
    noise = nn.init.normal_(torch.Tensor(tensor.size()), mean, std)
    return Variable(tensor+noise)

def customized_loss(original_prime, secret_prime, original, secret, gamma):
    loss_original = F.mse_loss(original_prime, original)
    loss_secret = F.mse_loss(secret_prime, secret)
    loss_total = loss_original + gamma * loss_secret
    return loss_total, loss_original, loss_secret
  
def denormalize(image, std, mean):
    for t in range(3):
        image[t, :, :] = (image[t, :, :] * std[t]) + mean[t]
    return image

def imshow(img, idx, learning_rate, gamma):
 
    img = denormalize(img, std, mean)
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.title('Example '+str(idx)+', lr='+str(learning_rate)+', B='+str(gamma))
    plt.show()
    return


def train_model(train_loader, gamma, learning_rate, num_epochs):
    # Save optimizer
    optimizer = optim.Adam(net.parameters(), lr=learning_rate)
    loss_history = []
    #Iterate over batches performing forward and backward passes
    for epoch in range(num_epochs):
        #Train mode
        net.train()
        train_losses = []
        #Train one epoch
        for idx, train_batch in enumerate(train_loader):
            
            train_original, train_secret = train_batch

            train_original = Variable(train_original, requires_grad=False).float()
            train_secret = Variable(
                train_secret, requires_grad=False).float()

            train_original = preprocess(train_original)
            train_secret = preprocess(train_secret)
            
            #Forward+Backward+Optimize
            optimizer.zero_grad()
            train_hidden, train_output = net(train_original, train_secret)

            train_loss, train_loss_original, train_loss_secret = customized_loss(train_output, train_hidden, train_original, train_secret, gamma)
            train_loss.backward()
            optimizer.step()

            train_losses.append(train_loss.data.item())
            loss_history.append(train_loss.data.item())

            print(
                f"Training: Batch {idx+1}/{len(train_loader)}. Loss of {train_loss.data.item():.4f}, original loss of {train_loss_original.data.item():.4f}, secret loss of {train_loss_secret.data.item():.4f}")
        
        train_loss_mean = np.mean(train_losses)

        print(f"Epoch {epoch+1}/{num_epochs}, Average loss: {train_loss_mean:.4f}")

    return net, men_train_loss, loss_history

net, mean_train_loss, loss_history = train_model(train_loader, gamma, learning_rate, num_epochs)

plt.plot(loss_history)
plt.title("Model loss")
plt.ylabel("Loss")
plt.xlabel("Batch")
plt.show()

# net.load_state_dict(torch.load(MODELS_PATH+'Epoch N4.pkl'))

# Switch to evaluate mode

with torch.no_grad():
    net.eval()
    test_losses = []

    for idx, test_batch in enumerate(test_loader):
        # Saves images
        test_original, test_secret = test_batch

        test_original = Variable(test_original).float()
        test_secret = Variable(test_secret).float()
        
        test_original = preprocess(test_original)
        test_secret = preprocess(test_secret)
        # Compute output
        test_hidden, test_output = net(test_original, test_secret)
        
        # Calculate loss
        test_loss, test_loss_original, test_loss_secret = customized_loss(test_output, test_hidden, test_original, test_secret, gamma)   
        test_losses.append(test_loss.data.item())
            
    mean_test_loss = np.mean(test_losses)

    print(f"Average loss on test set: {mean_test_loss:.2f}")

plt.plot(test_losses)
plt.title("Model loss")
plt.ylabel("Loss")
plt.xlabel("Batch")
plt.show()

kodak_images = []
for file in os.listdir("kodak"):
    if file.endswith(".png"):
        image = Image.open(os.path.join("kodak", file)).convert("RGB")
        image_size = tuple(list(image.size)+[3])
        kodak_images.append(np.array(image.getdata()).reshape(image_size))
kodak_test = np.array(kodak_images) / 255
kodak_test_loader = DataLoader(kodak_test, batch_size=2, pin_memory=True, shuffle=True)

with torch.no_grad():
    net.eval()
    test_losses = []

    for idx, test_batch in enumerate(kodak_test_loader):
        test_original, test_secret = test_batch

        test_original = Variable(test_original).float()
        test_secret = Variable(test_secret).float()

        test_original = preprocess(test_original)
        test_secret = preprocess(test_secret)
        test_hidden, test_output = net(test_original, test_secret)

        test_loss, test_loss_original, test_loss_secret = customized_loss(
            test_output, test_hidden, test_original, test_secret, gamma)
        test_losses.append(test_loss.data.item())

    mean_test_loss = np.mean(test_losses)

    print(f"Average loss on test set: {mean_test_loss:.2f}")

plt.plot(test_losses)
plt.title("Model loss")
plt.ylabel("Loss")
plt.xlabel("Batch")
plt.show()











