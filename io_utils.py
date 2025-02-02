import numpy as np
import os
import glob
import argparse
import backbone

import numpy as np
import os
import glob
import argparse
import backbone
import torch
import torch.nn as nn
import random
#from methods.resnet import ResNetDCT_Upscaled_Static


model_dict = dict(
            Conv4 = backbone.Conv4,
            Conv4S = backbone.Conv4S,
            Conv6 = backbone.Conv6,
            ResNet10 = backbone.ResNet10,
            ResNet18 = backbone.ResNet18,
            ResNet34 = backbone.ResNet34,
            ResNet50 = backbone.ResNet50,
            ResNet101 = backbone.ResNet101,
            WideResNet28_10 = backbone.WideResNet28_10,
            WideResNet28_10_dct = backbone.WideResNet28_10_dct,
            ResNet10dct = backbone.ResNet10dct,
            ResNet18dct = backbone.ResNet18dct,
            ResNet34dct = backbone.ResNet34dct,
            ResNet50dct = backbone.ResNet50dct)

def parse_args(script):
    parser = argparse.ArgumentParser(description= 'few-shot script %s' %(script))
    parser.add_argument('--dataset'     , default='cifar',        help='CUB/miniImagenet/cross/cifar')
    parser.add_argument('--model'       , default='WideResNet28_10',      help='model:  WideResNet28_10 /Conv{4|6} /ResNet{10|18|34|50|101}') # 50 and 101 are not used in the paper
    parser.add_argument('--method'      , default='rotation',   help='baseline++/rotation/manifold_mixup/S2M2_R') #relationnet_softmax replace L2 norm with softmax to expedite training, maml_approx use first-order approximation in the gradient for efficiency
    parser.add_argument('--train_n_way' , default=5, type=int,  help='class num to classify for training') #baseline and baseline++ would ignore this parameter
    parser.add_argument('--test_n_way'  , default=5, type=int,  help='class num to classify for testing (validation) ') #baseline and baseline++ only use this parameter in finetuning
    parser.add_argument('--n_shot'      , default=5, type=int,  help='number of labeled data in each class, same as n_support') #baseline and baseline++ only use this parameter in finetuning
    parser.add_argument('--train_aug'   , action='store_true',  help='perform data augmentation or not during training ') #still required for save_features.py and test.py to find the model path correctly
    parser.add_argument('--channels'  , default = '24',type = int,  help = '24/64' )
    parser.add_argument('--dct_status', action='store_true', help = 'true/false')
    parser.add_argument('--seed', type=int, default=42, metavar='s', help='random seed( default: 42)')
    parser.add_argument('--filter_size', default=8, type=int)
 
    if script == 'train':
        parser.add_argument('--num_classes' , default=200, type=int, help='total number of classes in softmax, only used in baseline') #make it larger than the maximum label value in base class
        parser.add_argument('--save_freq'   , default=10, type=int, help='Save frequency')
        parser.add_argument('--start_epoch' , default=0, type=int,help ='Starting epoch')
        parser.add_argument('--stop_epoch'  , default=400, type=int, help ='Stopping epoch') #for meta-learning methods, each epoch contains 100 episodes. The default epoch number is dataset dependent. See train.py
        parser.add_argument('--resume'      , action='store_true', help='continue from previous trained model with largest epoch')
        parser.add_argument('--lr'          , default=0.001, type=int, help='learning rate') 
        parser.add_argument('--batch_size' , default=16, type=int, help='batch size ')
        parser.add_argument('--test_batch_size' , default=2, type=int, help='batch size ')

        parser.add_argument('--alpha'       , default=2.0, type=int, help='for manifold_mixup or S2M2 training ')
        parser.add_argument('--warmup'      , action='store_true', help='continue from baseline, neglected if resume is true') #never used in the paper
    elif script == 'save_features':
        parser.add_argument('--split'       , default='novel', help='base/val/novel') #default novel, but you can also test base/val class accuracy if you want

        parser.add_argument('--save_iter', default=-1, type=int,help ='save feature from the model trained in x epoch, use the best model if x is -1')
    elif script == 'test':
        parser.add_argument('--split'       , default='novel', help='base/val/novel') #default novel, but you can also test base/val class accuracy if you want 

        parser.add_argument('--save_iter', default=-1, type=int,help ='saved feature from the model trained in x epoch, use the best model if x is -1')
        parser.add_argument('--adaptation'  , action='store_true', help='further adaptation in test time or not')
        parser.add_argument('--num_classes' , default=200, type=int, help='total number of classes')  
    else:
       raise ValueError('Unknown script')
    args = parser.parse_args()

    for arg in vars(args):
        print("{}={}".format(arg, getattr(args, arg)))
    if args.seed is not None:
        print('haveseed:args.seed:{}'.format(args.seed))
        # CUDNN seed
        nn.benchmark = True
        nn.deterministic = True

        # pytorch seed
        torch.manual_seed(args.seed)  # 为CPU设置随机种子
        torch.cuda.manual_seed(args.seed)  # 为当前GPU设置随机种子
        torch.cuda.manual_seed_all(args.seed)  # 所有GPU设置随机种子

        # python & numpy seed
        random.seed(args.seed)
        np.random.seed(args.seed)
        print('finish init s:args.seed:{}'.format(args.seed))

    return parser.parse_args()





def get_assigned_file(checkpoint_dir,num):
    assign_file = os.path.join(checkpoint_dir, '{:d}.tar'.format(num))
    return assign_file

def get_resume_file(checkpoint_dir):
    filelist = glob.glob(os.path.join(checkpoint_dir, '*.tar'))
    if len(filelist) == 0:
        return None

    filelist =  [ x  for x in filelist if os.path.basename(x) != 'best.tar' ]
    epochs = np.array([int(os.path.splitext(os.path.basename(x))[0]) for x in filelist])
    max_epoch = np.max(epochs)
    resume_file = os.path.join(checkpoint_dir, '{:d}.tar'.format(max_epoch))
    return resume_file

def get_best_file(checkpoint_dir):    
    best_file = os.path.join(checkpoint_dir, 'best.tar')
    if os.path.isfile(best_file):
        return best_file
    else:
        return get_resume_file(checkpoint_dir)


