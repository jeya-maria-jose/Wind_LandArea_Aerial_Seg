# Code for KiU-Net
# Author: Jeya Maria Jose
import argparse
import torch
import torchvision
from torch import nn
from torch.autograd import Variable
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.utils import save_image
from torchvision.datasets import MNIST
import torch.nn.functional as F
import os
import matplotlib.pyplot as plt
import torch.utils.data as data
from PIL import Image
import numpy as np
from torchvision.utils import save_image
import torch
import torch.nn.init as init
from arch.ae import kiunet,kinetwithsk,unet,autoencoder
from utils import JointTransform2D, ImageToImage2D, Image2D
from metrics import jaccard_index, f1_score, LogNLLLoss,classwise_f1
from utils import chk_mkdir, Logger, MetricList
import cv2
from functools import partial
from random import randint


parser = argparse.ArgumentParser(description='KiU-Net')
parser.add_argument('-j', '--workers', default=16, type=int, metavar='N',
                    help='number of data loading workers (default: 8)')
parser.add_argument('--epochs', default=100, type=int, metavar='N',
                    help='number of total epochs to run(default: 1)')
parser.add_argument('--start-epoch', default=0, type=int, metavar='N',
                    help='manual epoch number (useful on restarts)')
parser.add_argument('-b', '--batch_size', default=1, type=int,
                    metavar='N', help='batch size (default: 8)')
parser.add_argument('--learning_rate', default=1e-3, type=float,
                    metavar='LR', help='initial learning rate (default: 0.01)')
parser.add_argument('--momentum', default=0.9, type=float, metavar='M',
                    help='momentum')
parser.add_argument('--weight-decay', '--wd', default=1e-5, type=float,
                    metavar='W', help='weight decay (default: 1e-4)')
parser.add_argument('--lfw_path', default='../lfw', type=str, metavar='PATH',
                    help='path to root path of lfw dataset (default: ../lfw)')
parser.add_argument('--train_dataset',  type=str)
parser.add_argument('--val_dataset', type=str)
parser.add_argument('--save_freq', type=int,default = 5)

parser.add_argument('--modelname', default='off', type=str,
                    help='turn on img augmentation (default: False)')
parser.add_argument('--cuda', default="on", type=str, 
                    help='switch on/off cuda option (default: off)')

parser.add_argument('--load', default='default', type=str,
                    help='turn on img augmentation (default: default)')
parser.add_argument('--save', default='default', type=str,
                    help='turn on img augmentation (default: default)')
parser.add_argument('--model', default='overcomplete_udenet', type=str,
                    help='model name')
parser.add_argument('--direc', default='./special', type=str,
                    help='directory to save')
parser.add_argument('--crop', type=int, default=None)
parser.add_argument('--device', default='cuda', type=str)
parser.add_argument('--loaddirec', default='load', type=str)

args = parser.parse_args()

direc = args.direc
modelname = args.modelname
loaddirec = args.loaddirec

def add_noise(img):
    noise = torch.randn(img.size()) * 0.1
    noisy_img = img + noise.cuda()

    return noisy_img
     

if args.crop is not None:
    crop = (args.crop, args.crop)
else:
    crop = None

tf_train = JointTransform2D(crop=crop, p_flip=0.5, color_jitter_params=None, long_mask=True)
tf_val = JointTransform2D(crop=crop, p_flip=0, color_jitter_params=None, long_mask=True)
# train_dataset = ImageToImage2D(args.train_dataset, tf_val)
val_dataset = ImageToImage2D(args.val_dataset, tf_val)
predict_dataset = Image2D(args.val_dataset)
# dataloader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
valloader = DataLoader(val_dataset, 1, shuffle=True)

device = torch.device("cuda")

if modelname == "unet":
    model = unet()
elif modelname =="autoencoder":
    model =autoencoder()
elif modelname == "kiunet":
    model = kiunet()
elif modelname == "kinetwithsk":
    model = kinetwithsk()
elif modelname == "kinet":
    model = kinet()
elif modelname == "pspnet":
    model = psp.PSPNet(layers=5, bins=(1, 2, 3, 6), dropout=0.1, classes=21, zoom_factor=1, use_ppm=True, pretrained=False).cuda()

# if torch.cuda.device_count() > 1:
#   print("Let's use", torch.cuda.device_count(), "GPUs!")
#   # dim = 0 [30, xxx] -> [10, ...], [10, ...], [10, ...] on 3 GPUs
#   model = nn.DataParallel(model,device_ids=[0,1]).cuda()
model.to(device)
# model.apply(weight_init)
# print(model)
bestdice=0

criterion = LogNLLLoss()

optimizer = torch.optim.Adam(list(model.parameters()), lr=args.learning_rate,
                             weight_decay=1e-5)

metric_list = MetricList({'jaccard': partial(jaccard_index),
                          'f1': partial(f1_score)})


model.load_state_dict(torch.load(loaddirec))
model.eval()


for batch_idx, (X_batch, y_batch, *rest) in enumerate(valloader):
    # print(batch_idx)
    if isinstance(rest[0][0], str):
                image_filename = rest[0][0]
    else:
                image_filename = '%s.png' % str(batch_idx + 1).zfill(3)

    X_batch = Variable(X_batch.to(device='cuda'))
    y_batch = Variable(y_batch.to(device='cuda'))

    y_out = model(X_batch)

    tmp2 = y_batch.detach().cpu().numpy()
    tmp = y_out.detach().cpu().numpy()
    tmp[tmp>=0.5] = 1
    tmp[tmp<0.5] = 0
    tmp2[tmp2>0] = 1
    tmp2[tmp2<=0] = 0
    tmp2 = tmp2.astype(int)
    tmp = tmp.astype(int)

    # print(np.unique(tmp2))
    yHaT = tmp
    yval = tmp2

    epsilon = 1e-20
    
    del X_batch, y_batch,tmp,tmp2, y_out

    # count = count + 1
    yHaT[yHaT==1] =255
    yval[yval==1] =255
    fulldir = direc+"/"
    # print(fulldir+image_filename)
    if not os.path.isdir(fulldir):
        
        os.makedirs(fulldir)
   
    cv2.imwrite(fulldir+image_filename, yHaT[0,1,:,:])
    # cv2.imwrite(fulldir+'/gt_{}.png'.format(count), yval[0,:,:])
    # torch.save(model.state_dict(), fulldir+args.model)
    # torch.save(model.state_dict(), direc+"model.pth")
    
# if bestdice<tf1:
#     bestdice = tf1 
#     print("bestdice = {}".format(bestdice/count))  
#     print(epoch) 

