import re
from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional, Tuple

from LedgerEntry import LedgerEntry
from ScenarioLevers import Lever, ScenarioLevers
from ScenarioResult import ScenarioResult


class BaseLine(NamedTuple):
    month: int
    category: str
    department: str
    product: str
    revenue: float
    expenses: float
    quantity: float


class ProfitabilityModel:
    SALES = "Sprzedaż wyrobów"
    PERSONNEL = ("Wynagrodzenia", "Składki ZUS, FP, FGŚP, PPK")
    VOLUME_DRIVEN = ("Transport sprzedaży", "Transport surowca", "Utylizacja odpadów",
                     "Woda, ścieki, opłaty środowiskowe")
    PRODUCT_DRIVEN = {"Celuloza (półprodukt)": "Papier pakowy"}
    INPUT_CATEGORIES = tuple(lever.target for lever in ScenarioLevers.LEVERS if lever.group == "input_pct")

    def __init__(self, entries: List[LedgerEntry], capacity_headroom: float = 0.05,
                 price_search_range: Tuple[float, float] = (-60.0, 60.0)):
        self._lines = self._aggregate(entries)
        self.capacity_headroom = capacity_headroom
        self.price_search_range = price_search_range
        self.headcount = self._headcount(entries)
        self.base_volume = self._base_volume()

    def model(self) -> "ProfitabilityModel":
        return self

    def baseline(self) -> ScenarioResult:
        return self.simulate(ScenarioLevers())

    def simulate(self, levers: ScenarioLevers) -> ScenarioResult:
        volume = self._volume_factors(levers)
        overall = self._overall_volume(volume)
        monthly_revenue = [0.0] * 12
        monthly_expenses = [0.0] * 12
        by_category: Dict[str, float] = defaultdict(float)
        by_department: Dict[str, float] = defaultdict(float)
        personnel: Dict[str, float] = defaultdict(float)
        by_product: Dict[str, float] = defaultdict(float)
        for line in self._lines:
            revenue = line.revenue
            if line.category == self.SALES and line.product:
                revenue *= (1 + levers.price_pct.get(line.product, 0.0) / 100) * volume[line.product]
                by_product[line.product] += revenue
            expenses = line.expenses * self._cost_factor(line, levers, volume, overall)
            monthly_revenue[line.month - 1] += revenue
            monthly_expenses[line.month - 1] += expenses
            if expenses:
                by_category[line.category] += expenses
                by_department[line.department] += expenses
            if line.category in self.PERSONNEL:
                personnel[line.department] += expenses
        tonnes = {product: qty * volume[product] for product, qty in self.base_volume.items()}
        return ScenarioResult(
            revenue=sum(monthly_revenue),
            expenses=sum(monthly_expenses),
            volume_t=sum(tonnes.values()),
            monthly_revenue=monthly_revenue,
            monthly_expenses=monthly_expenses,
            expenses_by_category=dict(by_category),
            expenses_by_department=dict(by_department),
            personnel_by_department=dict(personnel),
            revenue_by_product=dict(by_product),
            volume_by_product=tonnes,
        )

    def bridge(self, levers: ScenarioLevers) -> List[Tuple[str, float]]:
        current = ScenarioLevers(elasticity=levers.elasticity)
        income = self.simulate(current).income
        steps = [("Dochód bazowy", income)]
        for section in ScenarioLevers.SECTIONS:
            for lever in ScenarioLevers.in_section(section):
                current = current.with_lever(lever, levers.pct(lever))
            after = self.simulate(current).income
            steps.append((section, after - income))
            income = after
        steps.append(("Dochód w scenariuszu", income))
        return steps

    def sensitivity(self, levers: ScenarioLevers, step: float = 1.0) -> List[Tuple[Lever, float]]:
        income = self.simulate(levers).income
        impacts = [(lever, self.simulate(levers.with_lever(lever, levers.pct(lever) + step)).income - income)
                   for lever in ScenarioLevers.LEVERS]
        return sorted(impacts, key=lambda item: abs(item[1]), reverse=True)

    def break_even_price_change(self, levers: ScenarioLevers) -> Optional[float]:
        low, high = self.price_search_range
        if self._income_with_price_shift(levers, low) > 0 or self._income_with_price_shift(levers, high) < 0:
            return None
        for _ in range(40):
            middle = (low + high) / 2
            if self._income_with_price_shift(levers, middle) < 0:
                low = middle
            else:
                high = middle
        return (low + high) / 2

    def _income_with_price_shift(self, levers: ScenarioLevers, shift: float) -> float:
        shifted = levers
        for lever in ScenarioLevers.in_section("Ceny sprzedaży"):
            shifted = shifted.with_lever(lever, levers.pct(lever) + shift)
        return self.simulate(shifted).income

    def _cost_factor(self, line: BaseLine, levers: ScenarioLevers, volume: Dict[str, float], overall: float) -> float:
        if line.category in self.PERSONNEL:
            return 1 + levers.wage_pct.get(line.department, 0.0) / 100
        driver = volume.get(self.PRODUCT_DRIVEN[line.category], overall) if line.category in self.PRODUCT_DRIVEN else overall
        if line.category in self.INPUT_CATEGORIES:
            return (1 + levers.input_pct.get(line.category, 0.0) / 100) * driver
        if line.category in self.VOLUME_DRIVEN:
            return overall
        return 1.0

    def _volume_factors(self, levers: ScenarioLevers) -> Dict[str, float]:
        ceiling = 1 + self.capacity_headroom
        return {product: min(ceiling, max(0.0, 1 - levers.elasticity * levers.price_pct.get(product, 0.0) / 100))
                for product in self.base_volume}

    def _overall_volume(self, volume: Dict[str, float]) -> float:
        total = sum(self.base_volume.values())
        return sum(qty * volume[p] for p, qty in self.base_volume.items()) / total if total else 1.0

    def _base_volume(self) -> Dict[str, float]:
        volume: Dict[str, float] = defaultdict(float)
        for line in self._lines:
            if line.category == self.SALES and line.product:
                volume[line.product] += line.quantity
        return dict(volume)

    @staticmethod
    def _aggregate(entries: List[LedgerEntry]) -> List[BaseLine]:
        totals: Dict[Tuple[int, str, str, str], List[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
        for entry in entries:
            bucket = totals[(entry.month, entry.category, entry.department, entry.product)]
            bucket[0] += entry.revenue
            bucket[1] += entry.expenses
            bucket[2] += entry.quantity or 0.0
        return [BaseLine(month, category, department, product, revenue, expenses, quantity)
                for (month, category, department, product), (revenue, expenses, quantity) in totals.items()]

    @staticmethod
    def _headcount(entries: List[LedgerEntry]) -> Dict[str, int]:
        heads: Dict[str, int] = {}
        for entry in entries:
            found = re.search(r"\((\d+) etat", entry.description) if entry.category == "Wynagrodzenia" else None
            if found:
                heads[entry.department] = max(heads.get(entry.department, 0), int(found.group(1)))
        return heads
