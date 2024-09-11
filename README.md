# FSPDF


## Training 
### dataset (miniImagenet/cifar/CUB)
### methodname (S2M2_R/rotation)  
### ① first run rotation ② second run S2M2_R

1. train frequency-domain
```
python train_dct.py --dataset [DATASETNAME] --method [METHODNAME] --model WideResNet28_10 --train_aug --dct_status
```
2. train spatial-domain
```
python train_dct.py --dataset [DATASETNAME] --method [METHODNAME] --model WideResNet28_10 --train_aug
```

## Save features 

1. save frequency-domain features
```
python save_features.py --dataset [DATASETNAME] --method S2M2_R --model WideResNet28_10 --train_aug --dct_status
```
2. save spatial-domain features
```
python save_features.py --dataset [DATASETNAME] --method S2M2_R --model WideResNet28_10 --train_aug --dct_status
```
2. save dual-domain features
```
python save_features_both.py --dataset [DATASETNAME] --method S2M2_R --model WideResNet28_10 --train_aug
```

## Testing
1. test frequency-domain
```
python test_dct.py --dataset [DATASETNAME] --method S2M2_R --model WideResNet28_10 --n_shot [1/5] --train_aug --dct_status	
```
1. test spatial-domain
```
python test_dct.py --dataset [DATASETNAME] --method S2M2_R --model WideResNet28_10 --n_shot [1/5] --train_aug	
```
1. test dual-domain
```
python test_dct_both.py --dataset [DATASETNAME] --method S2M2_R --model WideResNet28_10 --n_shot [1/5] --train_aug
```

## Acknowledgment

Our project references the codes in the following repos.
- [S2M2_R](https://github.com/nupurkmr9/S2M2_fewshot)


