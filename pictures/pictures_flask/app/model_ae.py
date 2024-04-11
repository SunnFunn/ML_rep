#общие библиотеки
import numpy as np
import random

#фреймворк для работы с тензорами и нейросетями
import torch
import torch.nn as nn
import torch.nn.functional as F

nc=----
nef = ----
ndf=-----
num_embeddings = -------------

class depthwise_separable_conv(nn.Module):
    def __init__(self, nin, nout, kernel_size = ----, stride = -----, padding = -----, bias=---------):
        
    def forward(self, x):
        
class AE(nn.Module):
    def __init__(self):
        super().__init__()

        self.encoder = 

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

model_encoder = AE().eval()

def transform_encoder(pic):
	
