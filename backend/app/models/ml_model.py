
import pandas as pd
import numpy as np
from ..utils.storage import MyStorage
from tqdm import tqdm

import os

from PIL import Image

import torch
import torch.nn as nn

from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, models, transforms
from typing import Callable, Dict, Mapping, Tuple, Optional, Union

DEVICE = 'cpu'
FOLDER_PATH = ''
st = MyStorage()
IMG_SIZE = (256, 256)
SEED = 42
torch.seed = SEED
torch.random.seed = SEED



def generate_submit(
        models: list,
        test_loader: DataLoader,
        name: str,
        device: str = DEVICE,
        visual: bool = False) -> np.ndarray:
    """Returns labels predicted by multiple models"""
    for i in range(len(models)):
        models[i].eval()

    y_pred = np.array([])
    with torch.no_grad():
        for i, (filename, img) in tqdm(enumerate(test_loader),
                                       total=len(test_loader)):
            img = img.to(device)
            pred_all = models[0](img)
            for model in models[1:]:
                pred_all += model(img)
            arg_pred = pred_all.argmax(1).cpu().numpy()
            y_pred = np.concatenate([y_pred, arg_pred], axis=0)

    return y_pred


def generate_submission_folder(models: list, link_to_folder: str) -> list:
    paths = []
    label = []
    for i in os.listdir(link_to_folder):
        paths.append(i)
        label.append(0)
    test_df = pd.DataFrame({"filename": paths, "label": label})
    test_dataset = TestDataset(test_df, link_to_folder, val_transform)
    test_loader = get_test_loader(test_dataset)
    pred = generate_submit(models, test_loader, 'third', visual=True)
    test_df["label"] = pred.astype(int)
    # test_df.save("submission.csv",index=False)
    return [list(test_df.iloc[i].values) for i in range(len(test_df))]


def get_resnet_152(device: str = DEVICE,
                   ckpt_path: Optional[str] = None
                   ) -> nn.Module:
    model = models.resnet152(True)
    model.fc = nn.Sequential(nn.Linear(2048, 3))
    model = model.to(device)
    if ckpt_path:
        try:
            checkpoint = torch.load(ckpt_path)
            model.load_state_dict(checkpoint)
        except:
            print("Wrong checkpoint")
    return model


def get_test_transform() -> Callable:
    tran = [
        transforms.Resize(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ]
    return transforms.Compose(tran)


class TestDataset(Dataset):
    def __init__(self,
                 data_df: pd.DataFrame,
                 path: str,
                 transform: Optional[Callable] = None):
        self.data_df = data_df
        self.path = path
        self.transform = transform

    def __getitem__(self, idx: int):
        image_name = self.data_df.iloc[idx].filename

        # читаем картинку
        image = self.load_sample(image_name)

        # преобразуем, если нужно
        if self.transform:
            image = self.transform(image)

        return image_name, image

    def load_sample(self, name: str) -> Image:
        name = Image.open(os.path.join(self.path, name))
        name.load()
        return name

    def __len__(self):
        return len(self.data_df)


def get_test_loader(test_dataset: Dataset) -> DataLoader:
    return DataLoader(dataset=test_dataset,
                      batch_size=16,
                      shuffle=False,
                      pin_memory=True,
                      num_workers=2)


device = torch.device(DEVICE)

val_transform = get_test_transform()

model = get_resnet_152(device, st.path("resnet(256,256).ckpt"))

# r = generate_submission_folder([model], "/content/data/animal") # вот эта строчка пример юзания