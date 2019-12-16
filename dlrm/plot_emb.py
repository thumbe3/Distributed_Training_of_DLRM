import pickle
import matplotlib.pyplot as plt
from numpy import linalg as LA
import pandas as pd
import os

emb1=pickle.load(open("emb1.pickle","rb"))
emb0=pickle.load(open("emb0.pickle","rb"))
emb1_seed=pickle.load(open("emb1_part.pickle","rb"))
emb0_seed=pickle.load(open("emb0_part.pickle","rb"))

emb_norms=[]
emb_seed_norms=[]

for i in range(len(emb1)):
    print(len(emb1[i]))
    emb_norms.append(LA.norm(emb1[i][0][1]-emb0[i][0][1])) 

for i in range(len(emb1_seed)):
    print(len(emb1_seed[i]))
    emb_seed_norms.append(LA.norm(emb1_seed[i][0][1]-emb0_seed[i][0][1]))   

epochs=range(20)

fig=plt.figure()
fig.suptitle("||E0-E1|| with and without data partitioning")
plt.plot(epochs, emb_norms, label="With data partitioning")
plt.plot(epochs, emb_seed_norms, label="Without data partitioning and different seeds")
plt.legend()

plt.xlabel('Epochs')
plt.ylabel('||E0-E1||')
train_figure = 'embedding_norms' + '.png'
plt.figtext(0.99, 0.01, 'Ei: embedding parameter in node i', horizontalalignment='right')
plt.savefig(train_figure)
plt.close()
