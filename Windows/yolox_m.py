from yolox.exp import Exp as MyExp

class Exp(MyExp):
    def __init__(self):
        super().__init__()
        self.num_classes = 1  # only 1 class: 'failure'
        self.depth = 0.33
        self.width = 0.50
        self.max_epoch = 100  # or however many epochs you want
        self.max_epoch = 100 
        self.input_size = (640, 640)  # image size
        self.data_dir = "datasets\split"
        self.train_ann = "instances_train.json"
        self.val_ann = "instances_val.json"
        self.exp_name = "my_yolox_m"
        self.num_workers = 0

        