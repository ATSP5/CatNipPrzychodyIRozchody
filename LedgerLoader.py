import datetime
from typing import List, Optional, Union

from LedgerEntry import LedgerEntry

CellValue = Union[str, float, bool, None]


class LedgerLoader:
    FIRST_PLAUSIBLE_DATE_SERIAL = 36526  # 2000-01-01; smaller numbers in column 2 are the column-number row

    def __init__(self, rows: List[List[CellValue]]):
        self.rows = rows

    def entries(self) -> List[LedgerEntry]:
        result = [entry for entry in (self._parse(row) for row in self.rows) if entry is not None]
        if not result:
            raise ValueError("Wiersze nie zawierają żadnych zapisów KPiR.")
        print("Rozpoznano %d zapisów KPiR" % len(result))
        return result

    def _parse(self, row: List[CellValue]) -> Optional[LedgerEntry]:
        cells = list(row) + [None] * (23 - len(row))
        lp = cells[0]
        if not isinstance(lp, float) or not lp.is_integer() or not isinstance(cells[1], float):
            return None
        if cells[1] < self.FIRST_PLAUSIBLE_DATE_SERIAL:
            return None
        return LedgerEntry(
            lp=int(lp),
            date=self._excel_date(cells[1]),
            document=self._text(cells[2]),
            counterparty=self._text(cells[4]),
            description=self._text(cells[6]),
            sales=self._amount(cells[7]),
            other_revenue=self._amount(cells[8]),
            purchases=self._amount(cells[10]),
            purchase_costs=self._amount(cells[11]),
            wages=self._amount(cells[12]),
            other_expenses=self._amount(cells[13]),
            category=self._text(cells[19]) or "Bez kategorii",
            department=self._text(cells[20]) or "Ogólnozakładowe",
            product=self._text(cells[21]),
            quantity=cells[22] if isinstance(cells[22], float) else None,
        )

    @staticmethod
    def _excel_date(serial: float) -> datetime.date:
        return datetime.date(1899, 12, 30) + datetime.timedelta(days=int(serial))

    @staticmethod
    def _amount(value: CellValue) -> float:
        return float(value) if isinstance(value, float) else 0.0

    @staticmethod
    def _text(value: CellValue) -> str:
        return "" if value is None else str(value).strip()
