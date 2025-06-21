from dataclasses import dataclass, field

@dataclass
class CloudsData:
    all: float | None = None

@dataclass
class WindData:
    speed: float | None = None
    deg: float | None = None

@dataclass
class CoordinatesData:
    lon: float = 0
    lat: float = 0

@dataclass
class MainData:
    temp: float | None = None
    feels_like: float | None = None
    humidity: int | None = None

@dataclass
class ConditionData:
    id: int
    main: str | None = None
    description: str | None = None
    icon: str | None = None

@dataclass
class SysData:
    country: str | None = None

@dataclass
class WeatherData:
    name: str = "Unknown"
    timezone: int | None = None
    weather: list[ConditionData] = field(default_factory=list)
    main: MainData = field(default_factory=MainData)
    coord: CoordinatesData = field(default_factory=CoordinatesData)
    wind: WindData = field(default_factory=WindData)
    clouds: CloudsData = field(default_factory=CloudsData)
    sys: SysData = field(default_factory=SysData)
