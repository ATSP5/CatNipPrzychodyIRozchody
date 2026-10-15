from dataclasses import dataclass, field, replace
from typing import ClassVar, Dict, List, Mapping, NamedTuple, Tuple


class Lever(NamedTuple):
    key: str
    group: str
    section: str
    target: str
    label: str


@dataclass(frozen=True)
class ScenarioLevers:
    wage_pct: Dict[str, float] = field(default_factory=dict)
    input_pct: Dict[str, float] = field(default_factory=dict)
    price_pct: Dict[str, float] = field(default_factory=dict)
    elasticity: float = 0.0

    SECTIONS: ClassVar[Tuple[str, ...]] = ("Ceny sprzedaży", "Wynagrodzenia", "Surowce i półprodukty", "Energia")

    LEVERS: ClassVar[Tuple[Lever, ...]] = (
        Lever("wage_produkcja", "wage_pct", "Wynagrodzenia", "Produkcja", "Produkcja (32 etaty)"),
        Lever("wage_utrzymanie", "wage_pct", "Wynagrodzenia", "Utrzymanie ruchu", "Utrzymanie ruchu (6)"),
        Lever("wage_logistyka", "wage_pct", "Wynagrodzenia", "Logistyka i magazyn", "Logistyka i magazyn (5)"),
        Lever("wage_sprzedaz", "wage_pct", "Wynagrodzenia", "Sprzedaż", "Sprzedaż (3)"),
        Lever("wage_administracja", "wage_pct", "Wynagrodzenia", "Administracja i zarząd", "Administracja i zarząd (4)"),
        Lever("input_makulatura", "input_pct", "Surowce i półprodukty", "Makulatura (OCC)", "Makulatura OCC"),
        Lever("input_celuloza", "input_pct", "Surowce i półprodukty", "Celuloza (półprodukt)", "Celuloza NBSK (półprodukt)"),
        Lever("input_chemia", "input_pct", "Surowce i półprodukty", "Skrobia i chemia papiernicza", "Skrobia i chemia"),
        Lever("input_opakowania", "input_pct", "Surowce i półprodukty", "Opakowania i materiały pomocnicze", "Gilzy, folia, etykiety"),
        Lever("input_gaz", "input_pct", "Energia", "Gaz ziemny", "Gaz ziemny"),
        Lever("input_prad", "input_pct", "Energia", "Energia elektryczna", "Energia elektryczna"),
        Lever("price_testliner", "price_pct", "Ceny sprzedaży", "Testliner", "Testliner"),
        Lever("price_fluting", "price_pct", "Ceny sprzedaży", "Fluting", "Fluting"),
        Lever("price_pakowy", "price_pct", "Ceny sprzedaży", "Papier pakowy", "Papier pakowy"),
    )

    @classmethod
    def from_state(cls, state: Mapping[str, object]) -> "ScenarioLevers":
        levers = cls(elasticity=cls._number(state.get("elasticity", 0)))
        for lever in cls.LEVERS:
            levers = levers.with_lever(lever, cls._number(state.get(lever.key, 0)))
        return levers

    @classmethod
    def in_section(cls, section: str) -> List[Lever]:
        return [lever for lever in cls.LEVERS if lever.section == section]

    def pct(self, lever: Lever) -> float:
        return getattr(self, lever.group).get(lever.target, 0.0)

    def with_lever(self, lever: Lever, value: float) -> "ScenarioLevers":
        changed = dict(getattr(self, lever.group))
        changed[lever.target] = float(value)
        return replace(self, **{lever.group: changed})

    @staticmethod
    def _number(value: object) -> float:
        try:
            return float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 0.0
