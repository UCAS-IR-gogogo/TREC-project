import torch
import torch.nn.functional as F
import argparse

from deep_model.data_utils import build_tokenizer, build_embedding_matrix
from deep_model.models.cnn import CNN
from configs.config import config



class Inferer:
    """A simple inference example"""
    def __init__(self, opt):
        self.opt = opt
        self.tokenizer = build_tokenizer(
            fnames=[opt.dataset_file['train'], opt.dataset_file['test']],
            max_seq_len=opt.max_seq_len,
            # dat_fname='{0}_tokenizer.dat'.format(opt.dataset))
            dat_fname= config.deep_model_dir / f'{opt.dataset}_tokenizer.dat')
        embedding_matrix = build_embedding_matrix(
            word2idx=self.tokenizer.word2idx,
            embed_dim=opt.embed_dim,
            dat_fname=config.deep_model_dir / '{0}_{1}_embedding_matrix.dat'.format(str(opt.embed_dim), opt.dataset))
        self.model = opt.model_class(embedding_matrix, opt)
        print('loading model {0} ...'.format(opt.model_name))
        if not torch.cuda.is_available():
            self.model.load_state_dict(torch.load(opt.state_dict_path, map_location = torch.device('cpu')))
        else:
            self.model.load_state_dict(torch.load(opt.state_dict_path))
        self.model = self.model.to(opt.device)
        # switch model to evaluation mode
        self.model.eval()
        torch.autograd.set_grad_enabled(False)

    def evaluate(self, raw_text):
        #context_seqs = [self.tokenizer.text_to_sequence(raw_text.lower().strip()) for raw_text in raw_texts]
        context_seqs = [self.tokenizer.text_to_sequence(raw_text.lower().strip())]
        context_indices = torch.tensor(context_seqs, dtype=torch.int64).to(self.opt.device)

        t_inputs = [context_indices]
        t_outputs = self.model(t_inputs)
        t_outputs[t_outputs >= 0.5] =1
        t_outputs[t_outputs < 0.5] = 0
        return t_outputs

        #t_probs = F.softmax(t_outputs, dim=-1).cpu().numpy()
        #return t_probs



model_classes = {
    'cnn': CNN,
}
# set your trained models here
model_state_dict_paths = {
    'cnn': config.deep_model_dir / 'state_dict/cnn_PM_acc0.612',
}
class Option(object): pass
opt = Option()
opt.model_name = 'cnn'
opt.model_class = model_classes[opt.model_name]
opt.dataset = 'PM'
opt.dataset_file = {
    'train': config.deep_model_dir / 'dataset/description2017.txt',
    'test': config.deep_model_dir / 'dataset/description2018.txt',
}
opt.state_dict_path = model_state_dict_paths[opt.model_name]
opt.embed_dim = 300
opt.hidden_dim = 300
opt.max_seq_len = 100
opt.polarities_dim = 1
opt.max_kernel_size = 3
opt.n_filters = 100
opt.dropout = 0.5
# opt.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
opt.device = torch.device('cpu')


