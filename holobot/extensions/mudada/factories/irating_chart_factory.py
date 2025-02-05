from dataclasses import dataclass
from typing import Protocol

@dataclass(kw_only=True)
class ChartData:
    score1: float
    score2: float
    score3: float
    score4: float
    score5: float
    score6: float

class IRatingChartFactory(Protocol):
    def get_chart_url(
        self,
        user_name: str,
        color: str | None,
        data: ChartData
    ) -> str:
        ...
