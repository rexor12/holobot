from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class DiscountSetting:
    discountType: str
    discountPercentage: float

@dataclass
class ChildPromotionalOffer:
    startDate: Optional[datetime]
    endDate: Optional[datetime]
    discountSetting: DiscountSetting

@dataclass
class PromotionalOffer:
    promotionalOffers: List[ChildPromotionalOffer] = field(default_factory=list)

@dataclass
class Promotions:
    promotionalOffers: List[PromotionalOffer] = field(default_factory=list)

@dataclass
class CustomAttribute:
    key: str
    value: str

@dataclass
class Image:
    type: str
    url: str

@dataclass
class Offer:
    title: str
    promotions: Promotions = field(default_factory=Promotions)
    keyImages: List[Image] = field(default_factory=list)
    customAttributes: List[CustomAttribute] = field(default_factory=list)

@dataclass
class SearchStore:
    elements: List[Offer] = field(default_factory=list)

@dataclass
class OfferCatalog:
    searchStore: SearchStore = field(default_factory=SearchStore)

@dataclass
class Data:
    Catalog: OfferCatalog = field(default_factory=OfferCatalog)

@dataclass
class FreeGamesPromotions:
    data: Data = field(default_factory=Data)
