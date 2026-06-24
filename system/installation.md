# Install python 3.9.7

https://www.python.org/downloads/release/python-397/

# Add python to PATH
You don't need to do this, you select "Add to PATH" while installing python

```
C:\Users\arvyd\AppData\Local\Programs\Python\Python39
```

# Add pip to PATH
You don't need to do this, you select "Add to PATH" while installing python

```
C:\Users\arvyd\AppData\Local\Programs\Python\Python39\Scripts
```


# Create a virtual environment inside a cloned 3D-Spaghetti folder 

```
python -m venv yolo
yolo\scripts\activate
```

# Install Git
```
https://github.com/git-for-windows/git/releases/tag/v2.49.0.windows.1
```

# Clone YoloX repo
```
git clone https://github.com/Megvii-BaseDetection/YOLOX.git
```

# Install 3D-Spaghetti/Windows and Yolov5 requirements

```
pip install -r requirements.txt
```

# Install vc_redist.x64

```
https:/aka.ms/vs/16/release/vc_redist.x64.exe
```

# Install more dependancies

```
cd YOLOX
pip install -v -e .
```
# In Windows/ launch:

```
python main.py
```
