#!/usr/bin/env python

import os
import sys
import torch
import torch.distributed as dist
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from math import ceil
from random import Random
from torch.multiprocessing import Process
from torch.autograd import Variable
from torchvision import datasets, transforms



class Partition(object):
    """ Dataset-like object, but only access a subset of it. """

    def __init__(self, data, index):
        self.data = data
        self.index = index

    def __len__(self):
        return len(self.index)

    def __getitem__(self, index):
        data_idx = self.index[index]
        return self.data[data_idx]


class DataPartitioner(object):
    """ Partitions a dataset into different chuncks. """

    def __init__(self, data, sizes=[0.7, 0.2, 0.1], seed=1234):
        self.data = data
        self.partitions = []
        rng = Random()
        rng.seed(seed)
        data_len = len(data)
        indexes = [x for x in range(0, data_len)]
        rng.shuffle(indexes)

        for frac in sizes:
            part_len = int(frac * data_len)
            self.partitions.append(indexes[0:part_len])
            indexes = indexes[part_len:]

    def use(self, partition):
        return Partition(self.data, self.partitions[partition])


class Net(nn.Module):
    """ Network architecture. """

    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x)


def partition_dataset():
    """ Partitioning MNIST """
    dataset = datasets.MNIST(
        './data',
        train=True,
        download=True,
        transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307, ), (0.3081, ))
        ]))
    size = dist.get_world_size()
    bsz = int(128 / float(size))
    partition_sizes = [1.0 / size for _ in range(size)]
    partition = DataPartitioner(dataset, partition_sizes)
    partition = partition.use(dist.get_rank())
    train_set = torch.utils.data.DataLoader(
        partition, batch_size=bsz, shuffle=True)
    return train_set, bsz

count =0
def average_gradients(model,group,temp):
    """ Gradient averaging. """
    global count
    size = float(dist.get_world_size())
    for param in model.parameters():
        print("Number of average gardients computed".format(count))
        print(param.data)
        dist.all_reduce(param.grad.data, op=dist.reduce_op.SUM, group=group, async_op=True)
        dist.all_reduce(temp, op=dist.reduce_op.MAX, group=group, async_op=True)
        print("Temp is {}".format(temp.data))
        param.grad.data /= size
        print (param.grad.data)
        count+=1


def run(rank, size, group):
    """ Distributed Synchronous SGD Example """
    device = torch.device("cuda:{}".format(0))
    torch.manual_seed(1234)
    train_set, bsz = partition_dataset()
    model = Net().to(device)
    model = model
#    model = model.cuda(rank)
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)

    temp=torch.Tensor([1]).to(device)
    num_batches = ceil(len(train_set.dataset) / float(bsz))
    for epoch in range(10):
        epoch_loss = 0.0
        for data, target in train_set:
            data, target = data.to(device), target.to(device)
            data, target = Variable(data), Variable(target)
#            data, target = Variable(data.cuda(rank)), Variable(target.cuda(rank))
            optimizer.zero_grad()
            output = model(data)
            loss = F.nll_loss(output, target)
            epoch_loss += 1 #loss.data[0]
            loss.backward()
            average_gradients(model,group,temp)
            optimizer.step()
        print('Rank ',
              dist.get_rank(), ', epoch ', epoch, ': ',
              epoch_loss / num_batches)




if __name__ == "__main__":

    os.environ["MASTER_PORT"] = "8888"
    os.environ["MASTER_ADDR"] = sys.argv[2]
    os.environ["WORLD_SIZE"] = '2'
    os.environ["RANK"] =sys.argv[1]
    os.environ["NCCL_SOCKET_IFNAME"]="eth0"
    os.environ["NCCL_DEBUG"]="WARN"
    os.environ["NCCL_DEBUG_SUBSYS"]="ALL"
    rank = sys.argv[1]
    size = 2
    dist.init_process_group('nccl', rank=rank, world_size=2)
    group = dist.new_group([0,1])
    run(rank, size, group)


   
