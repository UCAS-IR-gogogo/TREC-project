
import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN(nn.Module):
    def __init__(self, embedding_matrix, opt):
        super(CNN, self).__init__()
        self.opt = opt
        self.embed = nn.Embedding.from_pretrained(torch.tensor(embedding_matrix, dtype=torch.float))
        self.weight1 = nn.Parameter(torch.Tensor(1))
        self.weight2 = nn.Parameter(torch.Tensor(1))
        self.convs = nn.ModuleList([nn.Conv2d(in_channels=1, out_channels=opt.n_filters,
                                              kernel_size=(kernel_size, opt.embed_dim)) for kernel_size in range(1, opt.max_kernel_size+1)])
        self.dense = nn.Linear(opt.max_kernel_size * opt.n_filters, opt.polarities_dim)
        self.dropout = nn.Dropout(opt.dropout)

    def forward(self, inputs):
        text_raw_indices = inputs[0]
        x = self.embed(text_raw_indices)  # (batch_size, seq_len, embed_dim)
        x = x.unsqueeze(dim=1)
        x = [F.relu(conv(x)).squeeze(3) for conv in self.convs]   #(batch_size, n_filters, seq_len-kernel_size) is a list
        x = [F.max_pool1d(feature, feature.size(2)).squeeze(2) for feature in x]  #(batch_size, n_filters) is a list
        x = torch.cat(x, dim=1)
        out = self.dense(x)
        output = self.dropout(out)

        output = torch.sigmoid(output)
        return output