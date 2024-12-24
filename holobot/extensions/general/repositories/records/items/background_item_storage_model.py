from dataclasses import dataclass

from .item_storage_model_base import ItemStorageModelBase

@dataclass(kw_only=True)
class BackgroundItemStorageModel(ItemStorageModelBase):
    background_id: int
