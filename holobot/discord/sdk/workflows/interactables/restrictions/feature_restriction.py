from dataclasses import dataclass

from .restriction_base import RestrictionBase

@dataclass(kw_only=True)
class FeatureRestriction(RestrictionBase):
    """A restriction that requires a feature
    for the associated interactable to be allowed."""

    feature_name: str
    """The name of the feature the interactable is associated to."""
