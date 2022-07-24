
### Prerequisites:

- Python 3.6
- Pytorch 1.4

<a href="https://pytorch.org/ "> Pytorch Installation </a>  


### Dataset Preparation

Prepare the dataset in the following format for easy use of the code. The train and test folders should contain two subfolders each: img and label. Make sure the images their corresponding segmentation masks are placed under these folders and have the same name for easy correspondance. Please change the data loaders to your need if you prefer not preparing the dataset in this format.



```bash
Train Folder-----
      img----
          0001.png
          0002.png
          .......
      label---
          0001.png
          0002.png
          .......
Validation Folder-----
      img----
          0001.png
          0002.png
          .......
      label---
          0001.png
          0002.png
          .......
Test Folder-----
      img----
          0001.png
          0002.png
          .......
      label---
          0001.png
          0002.png
          .......

```


### Training Command:

```bash 
python train.py --train_dataset "enter train directory" --val_dataset "enter validation directory" --direc 'path for results to be saved' --batch_size 1 --epoch 400 --save_freq 10 --modelname "denseunet" --learning_rate 0.001
```

### Testing Command:

```bash 
python test.py --loaddirec "./saved_model_path/model_name.pth" --val_dataset "test dataset directory" --direc 'path for results to be saved' --batch_size 1 --modelname "denseunet"
```


### Integrating with ArcGIS