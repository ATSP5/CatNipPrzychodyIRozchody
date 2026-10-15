import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LedgerEntry:
    lp: int
    date: datetime.date
    document: str
    counterparty: str
    description: str
    sales: float
    other_revenue: float
    purchases: float
    purchase_costs: float
    wages: float
    other_expenses: float
    category: str
    department: str
    product: str
    quantity: Optional[float]

    @property
    def month(self) -> int:
        return self.date.month

    @property
    def revenue(self) -> float:
        return self.sales + self.other_revenue

    @property
    def expenses(self) -> float:
        return self.purchases + self.purchase_costs + self.wages + self.other_expenses
