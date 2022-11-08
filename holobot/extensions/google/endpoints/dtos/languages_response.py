from dataclasses import dataclass, field

@dataclass
class Language:
    language: str
    name: str

@dataclass
class LanguageData:
    languages: list[Language] = field(default_factory=list)

@dataclass
class LanguagesResult:
    data: LanguageData = field(default_factory=LanguageData)
