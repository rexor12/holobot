from dataclasses import dataclass, field

@dataclass
class SearchAppsItem:
    appid: str
    name: str
    icon: str
    logo: str
