from dataclasses import dataclass

@dataclass(kw_only=True)
class AggregatedRating:
    average_score1: float
    average_score2: float
    average_score3: float
    average_score4: float
    average_score5: float
    average_score6: float
