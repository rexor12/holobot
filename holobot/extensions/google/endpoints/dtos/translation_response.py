from dataclasses import dataclass, field

@dataclass
class Translation:
    translatedText: str
    detectedSourceLanguage: str | None = None

@dataclass
class TranslationData:
    translations: list[Translation] = field(default_factory=list)

@dataclass
class TranslationResult:
    data: TranslationData = field(default_factory=TranslationData)
