from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ScenarioResult:
    revenue: float
    expenses: float
    volume_t: float
    monthly_revenue: List[float]
    monthly_expenses: List[float]
    expenses_by_category: Dict[str, float]
    expenses_by_department: Dict[str, float]
    personnel_by_department: Dict[str, float]
    revenue_by_product: Dict[str, float]
    volume_by_product: Dict[str, float]

    @property
    def income(self) -> float:
        return self.revenue - self.expenses

    @property
    def margin(self) -> float:
        return self.income / self.revenue if self.revenue else 0.0

    @property
    def monthly_income(self) -> List[float]:
        return [r - e for r, e in zip(self.monthly_revenue, self.monthly_expenses)]
