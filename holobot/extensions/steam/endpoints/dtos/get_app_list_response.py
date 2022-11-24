from dataclasses import dataclass, field

@dataclass
class App:
    appid: int
    name: str

@dataclass
class AppList:
    apps: list[App] = field(default_factory=list)

@dataclass
class GetAppListResponse:
    applist: AppList = field(default_factory=AppList)
