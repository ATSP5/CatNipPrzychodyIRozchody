from XlsxSheetReader import XlsxSheetReader
from LedgerLoader import LedgerLoader
from ProfitabilityModel import ProfitabilityModel
from SymulatorRentownosci import SymulatorRentownosci

def main():
	rows = XlsxSheetReader()

	data_1 = rows.rows()
	entries = LedgerLoader(data_1)
	data_2 = entries.entries()
	model = ProfitabilityModel(data_2)
	data_3 = model.model()
	result = SymulatorRentownosci(data_3)
	result.show()
	pass

if __name__ == "__main__":
	main()
