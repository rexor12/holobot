from dataclasses import dataclass, field

@dataclass
class Screenshot:
    path_full: str = ""

@dataclass
class AppDetailsData:
    name: str = ""
    required_age: int = 0
    is_free: bool = False
    short_description: str = ""
    screenshots: list[Screenshot] = field(default_factory=list)

@dataclass
class AppDetails:
    success: bool = False
    data: AppDetailsData = field(default_factory=AppDetailsData)

@dataclass
class GetAppDetailsResponse:
    apps: dict[str, AppDetails] = field(default_factory=dict)
