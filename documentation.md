
# Table of Contents
1. [Idea of the project](#idea-of-the-project)
2. [MV model](#mv-model)
     1. [Training data](#training-data)
     2. [Data labeling](#data-labeling)
     3. [Model training](#model-training)
     4. [Model performance](#model-performance)
4. [Third Example](#third-example)
5. [Fourth Example](#fourth-examplehttpwwwfourthexamplecom)


## Idea of the project

![SpaghettiExample](https://github.com/user-attachments/assets/56b2ee48-3078-4bb3-a339-dc810db39534)

When using 3D printers, failures are inevitable. One of the most common types of failure occurs when the printed object detaches from the bed, resulting in a mess of stringy filament caused by the printer extruding into mid-air — commonly referred to as **spaghetti**. 

This unexpected behavior can lead to issues such as filament blobs forming on the hotend, potentially causing damage, as well as wasting filament and printing time. 

The goal of this project is to use **machine vision** to detect these failures early and stop the printing process before any serious damage occurs, ultimately saving both **filament** and **time**.

## MV model

The machine vision model used for this project is [Yolov5](https://docs.ultralytics.com/yolov5/) by Ultralytics. It may not be the newest model available today, but I have a lot of experience using it, and it is good enough for our purposes

## Training data

The training data was collected using 2 printers with 3-4 camera angles. Cameras were set to 720p and the lowest framerate it could go (24fps), so the video file size wouldn't be too massive.
From those videos, we then extracted the individual frames.
Some more data was collected using Roboflow's universe.

## Data labeling

For data labeling, software used was [Roboflow](https://roboflow.com/)

The first attempt of training the model, the decision was made to label the data like this:
![SpaghettiLargeBox](https://github.com/user-attachments/assets/e5fc8b5a-7f69-4d93-8355-376d60e2e949)

This approach proved to be unsuccessful because it made the model overly sensitive to false positives. For example:

*The printer is printing, but the model mistakenly predicts a false positive. Since we trained the model to only predict one large box, it became difficult to determine whether a prediction was correct or not.*

To address this issue, we decided to annotate the data with smaller boxes. This way, when predictions are made, there are many correct ones, and a few false positives won’t significantly affect the overall results. Currently, the dataset consists of approximately 100 pictures, but it contains over 2,500 annotations. This effectively provides the model with more than 2,500 training examples.


Example:

![SpaghettiSmallBox](https://github.com/user-attachments/assets/0807b903-b430-42db-beee-fcc02947a43c)

## Model training

The model used for training was Yolov5m.pt, though, we suspect that a smaller model would suffice. Hardware used for training was an Nvidia RTX3060 12GB

Parameters for training the model:

```
python train.py --img 640 --batch 16 --epochs 250 --patience 20 --data /data.yaml --weights yolov5m.pt --name Train --device 0 --workers 8 --cache disk
```
## Model performance

Parameters for performing predictions:

```
python detect.py --weights/runs/train/Train/weights/best.pt --source /videos --img-size 640 --conf-thres 0.45 --device 0
```

Due to a small amount of labeled data, the model reached its optimal performance after about 20 epochs.

The trained model predictions on a test dataset are seen below:

![2](https://github.com/user-attachments/assets/5b2028a4-e3de-4847-abdf-b92e10bb907a)

If we run the detection on a video, and plot the current frame and detection count we see something like this:


![EnderFail1](https://github.com/user-attachments/assets/3821122f-f4d1-4dde-8f00-07b51f895a4b)

Somewhere after the 50th frame, a print failure occured, and we can clearly see, that the detection count skyrocketed, indicating that there is a fault.
