from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CodeResult:
    C1_separation_distress: bool = False
    C2_fear_abandonment: bool = False
    C3_proximity_seeking: bool = False
    C4_reassurance_seeking: bool = False
    C5_romantic_dependency: bool = False


@dataclass
class QuoteResult:
    C1: Optional[str] = None
    C2: Optional[str] = None
    C3: Optional[str] = None
    C4: Optional[str] = None
    C5: Optional[str] = None


@dataclass
class PostAnalysis:
    post_id: str
    title: str
    relevant: bool
    codes: CodeResult = field(default_factory=CodeResult)
    quotes: QuoteResult = field(default_factory=QuoteResult)
    trauma_context: bool = False
    trauma_note: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.post_id,
            "title": self.title,
            "relevant": self.relevant,
            "C1_separation_distress": self.codes.C1_separation_distress,
            "C2_fear_abandonment": self.codes.C2_fear_abandonment,
            "C3_proximity_seeking": self.codes.C3_proximity_seeking,
            "C4_reassurance_seeking": self.codes.C4_reassurance_seeking,
            "C5_romantic_dependency": self.codes.C5_romantic_dependency,
            "quote_C1": self.quotes.C1,
            "quote_C2": self.quotes.C2,
            "quote_C3": self.quotes.C3,
            "quote_C4": self.quotes.C4,
            "quote_C5": self.quotes.C5,
            "trauma_context": self.trauma_context,
            "trauma_note": self.trauma_note,
            "error": self.error
        }

    @classmethod
    def from_api_response(cls, post_id: str, title: str, response: dict):
        codes_raw = response.get("codes", {})
        quotes_raw = response.get("quotes", {})

        codes = CodeResult(
            C1_separation_distress=codes_raw.get("C1_separation_distress", False),
            C2_fear_abandonment=codes_raw.get("C2_fear_abandonment", False),
            C3_proximity_seeking=codes_raw.get("C3_proximity_seeking", False),
            C4_reassurance_seeking=codes_raw.get("C4_reassurance_seeking", False),
            C5_romantic_dependency=codes_raw.get("C5_romantic_dependency", False),
        )

        quotes = QuoteResult(
            C1=quotes_raw.get("C1"),
            C2=quotes_raw.get("C2"),
            C3=quotes_raw.get("C3"),
            C4=quotes_raw.get("C4"),
            C5=quotes_raw.get("C5"),
        )

        return cls(
            post_id=post_id,
            title=title,
            relevant=response.get("relevant", False),
            codes=codes,
            quotes=quotes,
            trauma_context=response.get("trauma_context", False),
            trauma_note=response.get("trauma_note"),
        )
