import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np

class YelpDataSet(Dataset):
    def __init__(self, file):
        """
        Initialize the Dataset object with our dataframe
        """
        data = np.load(file)
        self.counts = data["counts"]
        self.X_int = data['X_num']
        self.X_cat = data['X_cat']
        self.y = data['y']
        self.m_den = self.X_int.shape[1]
        self.n_emb = len(self.counts)
        print("Sparse features= %d, Dense features= %d" % (self.n_emb, self.m_den))

    def __getitem__(self, index):
        '''
        Support indexing operations into the dataset. This is used for batching operations carried out
        by DataLoader
        '''
        if isinstance(index, slice):
            return [
                self[idx] for idx in range(
                    index.start or 0, index.stop or len(self), index.step or 1)]

        else:
            i = index

        return self.X_int[i], self.X_cat[i], self.y[i]

    def __len__(self):
        # WARNING: note that we produce bacthes of outputs in __getitem__
        # therefore we should use num_batches rather than data_size below
        return len(self.y)
