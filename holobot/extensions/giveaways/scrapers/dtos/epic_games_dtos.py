from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class DiscountSetting:
    discountType: str
    discountPercentage: float

@dataclass
class ChildPromotionalOffer:
    startDate: datetime | None
    endDate: datetime | None
    discountSetting: DiscountSetting

@dataclass
class PromotionalOffer:
    promotionalOffers: list[ChildPromotionalOffer] = field(default_factory=list)

@dataclass
class Promotions:
    promotionalOffers: list[PromotionalOffer] = field(default_factory=list)

@dataclass
class CustomAttribute:
    key: str
    value: str

@dataclass
class CatalogNsEntry:
    pageSlug: str
    pageType: str

@dataclass
class CatalogNs:
    mappings: list[CatalogNsEntry] = field(default_factory=list)

@dataclass
class Image:
    type: str
    url: str

@dataclass
class Offer:
    title: str
    promotions: Promotions = field(default_factory=Promotions)
    keyImages: list[Image] = field(default_factory=list)
    catalogNs: CatalogNs = field(default_factory=CatalogNs)
    customAttributes: list[CustomAttribute] = field(default_factory=list)

@dataclass
class SearchStore:
    elements: list[Offer] = field(default_factory=list)

@dataclass
class OfferCatalog:
    searchStore: SearchStore = field(default_factory=SearchStore)

@dataclass
class Data:
    Catalog: OfferCatalog = field(default_factory=OfferCatalog)

@dataclass
class FreeGamesPromotions:
    data: Data = field(default_factory=Data)
