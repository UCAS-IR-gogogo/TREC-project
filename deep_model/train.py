from sklearn import metrics
from data_utils import build_tokenizer, build_embedding_matrix, ABSADataset
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
# from tensorboardX import SummaryWriter
import matplotlib.pyplot as plt
import datetime
import argparse
import math
import os

from models.cnn import CNN


class Instructor:
    def __init__(self, opt):
        self.opt = opt

        tokenizer = build_tokenizer(
            fnames=[opt.dataset_file['train'], opt.dataset_file['test']],
            max_seq_len=opt.max_seq_len,
            dat_fname='{0}_tokenizer_train.dat'.format(opt.dataset))
        embedding_matrix = build_embedding_matrix(
            word2idx=tokenizer.word2idx,
            embed_dim=opt.embed_dim,
            dat_fname='{0}_{1}_embedding_matrix.dat'.format(str(opt.embed_dim), opt.dataset))
        trainset = ABSADataset(opt.dataset_file['train'], tokenizer)
        testset = ABSADataset(opt.dataset_file['test'], tokenizer)
        self.train_data_loader = DataLoader(dataset=trainset, batch_size=opt.batch_size, shuffle=True)
        self.test_data_loader = DataLoader(dataset=testset, batch_size=opt.batch_size, shuffle=False)

        self.model = opt.model_class(embedding_matrix, opt).to(opt.device)
        if opt.device.type == 'cuda':
            print("cuda memory allocated:", torch.cuda.memory_allocated(device=opt.device.index))
        self._print_args()

    def _print_args(self):
        n_trainable_params, n_nontrainable_params = 0, 0
        for p in self.model.parameters():
            n_params = torch.prod(torch.tensor(p.shape))
            if p.requires_grad:
                n_trainable_params += n_params
            else:
                n_nontrainable_params += n_params
        print('n_trainable_params: {0}, n_nontrainable_params: {1}'.format(n_trainable_params, n_nontrainable_params))
        print('> training arguments:')
        for arg in vars(self.opt):
            print('>>> {0}: {1}'.format(arg, getattr(self.opt, arg)))

    def _reset_params(self):
        for p in self.model.parameters():
            if p.requires_grad:
                if len(p.shape) > 1:
                    self.opt.initializer(p)
                else:
                    stdv = 1. / math.sqrt(p.shape[0])
                    torch.nn.init.uniform_(p, a=-stdv, b=stdv)

    def _train(self, criterion, optimizer, max_test_f1_overall=0):
        #writer = SummaryWriter(log_dir=self.opt.logdir)
        max_test_precision = 0
        max_recall = 0
        max_f1 = 0
        global_step = 0
        for epoch in range(self.opt.num_epoch):
            print('>' * 100)
            print('epoch: ', epoch)
            for i_batch, sample_batched in enumerate(self.train_data_loader):
                global_step += 1

                # switch model to training mode, clear gradient accumulators
                self.model.train()
                optimizer.zero_grad()

                inputs = [sample_batched[col].to(self.opt.device) for col in self.opt.inputs_cols]
                outputs = self.model(inputs)
                targets = sample_batched['polarity'].to(self.opt.device)

                loss = criterion(outputs.squeeze(1), targets.float())
                loss.backward()
                optimizer.step()
                if global_step % self.opt.log_step == 0:
                    precision, recall, f1 = self._evaluate_acc_f1()
                    if f1 > max_f1:
                        max_test_precision = precision
                        max_recall = recall
                        max_f1 = f1
                        if f1 > max_test_f1_overall:
                            if not os.path.exists('state_dict'):
                                os.mkdir('state_dict')
                            path = 'state_dict/{0}_{1}'.format(self.opt.model_name, self.opt.dataset)
                            torch.save(self.model.state_dict(), path)
                            print('>> saved: ' + path)

                    #writer.add_scalar('loss', loss, global_step)
                    #writer.add_scalar('test_precision', precision, global_step)
                    print('loss: {:.4f}, pre: {:.4f}, rec: {:.4f} f1: {:.4f}'.format(loss.item(), precision, recall, f1))

        #writer.close()
        return max_test_precision, max_recall, max_f1

    def _evaluate_acc_f1(self):
        # switch model to evaluation mode
        self.model.eval()

        n_test_correct, n_test_total = 0, 0
        t_targets_all, t_outputs_all = None, None
        with torch.no_grad():
            for t_batch, t_sample_batched in enumerate(self.test_data_loader):
                t_inputs = [t_sample_batched[col].to(opt.device) for col in self.opt.inputs_cols]
                t_targets = t_sample_batched['polarity'].to(opt.device)
                t_outputs = self.model(t_inputs)

                n_test_correct += (torch.argmax(t_outputs, -1) == t_targets).sum().item()
                n_test_total += len(t_outputs)

                if t_targets_all is None:
                    t_targets_all = t_targets
                    t_outputs_all = t_outputs
                else:
                    t_targets_all = torch.cat((t_targets_all, t_targets), dim=0)
                    t_outputs_all = torch.cat((t_outputs_all, t_outputs), dim=0)

        t_outputs_all = t_outputs_all.squeeze(1)
        t_outputs_all[t_outputs_all >= self.opt.threshold] = 1
        t_outputs_all[t_outputs_all < self.opt.threshold] = 0
        precision_t, recall_t, f1_t, _ = metrics.precision_recall_fscore_support(t_targets_all.cpu(),
                                                                                 t_outputs_all.cpu(), average='binary')
        return precision_t, recall_t, f1_t

    def run(self, repeats=1):
        # Loss and Optimizer
        criterion = nn.BCELoss()
        _params = filter(lambda p: p.requires_grad, self.model.parameters())
        optimizer = self.opt.optimizer(_params, lr=self.opt.learning_rate, weight_decay=self.opt.l2reg)

        max_test_precision_overall = 0
        max_f1_overall = 0
        max_recall_overall = 0
        for i in range(repeats):
            print('repeat: ', i)
            self._reset_params()
            max_test_precision, max_recall, max_f1 = self._train(criterion, optimizer, max_test_f1_overall=max_f1_overall)
            print('max_test_precision: {0}     max_recall: {1}     max_f1: {2}'.format(max_test_precision, max_recall, max_f1))
            if max_f1 > max_f1_overall:
                max_test_precision_overall = max_test_precision
                max_recall_overall = max_recall
                max_f1_overall = max_f1
            print('#' * 100)
        print("max_test_precision_overall:", max_test_precision_overall)
        print("max_recall_overall:", max_recall_overall)
        print("max_f1_overall:", max_f1_overall)


if __name__ == '__main__':
    # Hyper Parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', default='cnn', type=str)
    parser.add_argument('--dataset', default='PM', type=str, help='')
    parser.add_argument('--optimizer', default='adam', type=str)
    parser.add_argument('--initializer', default='xavier_uniform_', type=str)
    parser.add_argument('--learning_rate', default=0.001, type=float)
    parser.add_argument('--dropout', default=0.5, type=float)
    parser.add_argument('--l2reg', default=0.00001, type=float)
    parser.add_argument('--num_epoch', default=20, type=int)
    parser.add_argument('--batch_size', default=32, type=int)
    parser.add_argument('--log_step', default=5, type=int)
    parser.add_argument('--logdir', default='log', type=str)
    parser.add_argument('--embed_dim', default=300, type=int)
    parser.add_argument('--hidden_dim', default=300, type=int)
    parser.add_argument('--n_filters', default=100, type=int)
    parser.add_argument('--max_kernel_size', default=3, type=int)
    parser.add_argument('--max_seq_len', default=100, type=int)
    parser.add_argument('--threshold', default=0.5, type=float)
    parser.add_argument('--polarities_dim', default=1, type=int)
    parser.add_argument('--device', default=None, type=str)
    opt = parser.parse_args()

    model_classes = {
        'cnn': CNN
    }
    dataset_files = {
        'PM': {
            'train': './dataset/description2017.txt',
            'test': './dataset/description2018.txt'
        }
    }
    input_colses = {
        'cnn': ['text_raw_indices']
    }
    initializers = {
        'xavier_uniform_': torch.nn.init.xavier_uniform_,
        'xavier_normal_': torch.nn.init.xavier_normal,
        'orthogonal_': torch.nn.init.orthogonal_,
    }
    optimizers = {
        'adadelta': torch.optim.Adadelta,  # default lr=1.0
        'adagrad': torch.optim.Adagrad,  # default lr=0.01
        'adam': torch.optim.Adam,  # default lr=0.001
        'adamax': torch.optim.Adamax,  # default lr=0.002
        'asgd': torch.optim.ASGD,  # default lr=0.01
        'rmsprop': torch.optim.RMSprop,  # default lr=0.01
        'sgd': torch.optim.SGD,
    }
    opt.model_class = model_classes[opt.model_name]
    opt.dataset_file = dataset_files[opt.dataset]
    opt.inputs_cols = input_colses[opt.model_name]
    opt.initializer = initializers[opt.initializer]
    opt.optimizer = optimizers[opt.optimizer]
    opt.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') \
        if opt.device is None else torch.device(opt.device)

    ins = Instructor(opt)
    ins.run(1)
