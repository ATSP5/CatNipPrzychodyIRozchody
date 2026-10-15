# Przychody i rozchody — symulator rentowności papierni

Interaktywny symulator **„co, jeśli?”** zbudowany na podatkowej księdze przychodów i rozchodów (KPiR)
za 2025 rok. Program wczytuje księgę z Excela, odtwarza z niej co do złotówki przychody, wydatki
i dochód firmy, a następnie pozwala suwakami sprawdzić, jak zmieni się wynik, gdy wzrosną płace,
zdrożeją surowce lub energia albo zmienią się ceny sprzedawanych wyrobów.

Przykładowa firma to **fikcyjna papiernia** produkująca testliner, fluting i papier pakowy
(50 etatów w 5 działach). Projekt służy do prezentacji tego, jak z surowej księgi zrobić czytelny
model rentowności.

Projekt jest zbudowany w CatNip — wizualnym edytorze Pythona opartym na blokach. Każdy blok to jedna
klasa w osobnym pliku `.py`.

> [!WARNING]
> **To jest projekt poglądowy (demonstracyjny), a nie porada inwestycyjna, podatkowa ani księgowa.**
> Wszystkie dane w `KsiegaPrzychodowIRozchodow2025.xlsx` są **fikcyjne** — firma „Papiernia Modelowa
> s.c.”, kontrahenci, numery NIP i adresy zostały wymyślone na potrzeby prezentacji, a podobieństwo
> do prawdziwych podmiotów jest przypadkowe. Model upraszcza rzeczywistość (np. stała struktura
> kosztów, liniowa elastyczność popytu) i nie uwzględnia podatku dochodowego ani zmian przepisów.
> Wyniki nie mogą być podstawą decyzji biznesowych, inwestycyjnych ani rozliczeń podatkowych —
> w tych sprawach skonsultuj się z księgowym lub doradcą podatkowym. Autor nie ponosi
> odpowiedzialności za decyzje podjęte na podstawie wyników programu.

## Co pokazuje

- **5 gotowych scenariuszy**: rok 2025 (bez zmian), płace 2026, szok energetyczny, słaby rynek papieru,
  podwyżka cennika.
- **Kafelki**: przychody, wydatki, dochód i rentowność — ze zmianą względem 2025.
- **Próg rentowności cenowej** — o ile musiałyby się zmienić ceny wszystkich wyrobów, by dochód był zerowy.
- **Most dochodu** 2025 → ceny sprzedaży → wynagrodzenia → surowce i półprodukty → energia → scenariusz.
- **Dochód miesięczny** 2025 a scenariusz, **wrażliwość** na zmianę każdej dźwigni o +1 pp,
  **struktura wydatków**.
- **Tabele**: wyroby, koszty osobowe działów, wydatki według kategorii.

## Jak liczy

1. Księga jest agregowana do linii *miesiąc × kategoria × dział × wyrób*.
2. Wynik bez zmian **odtwarza sumy z KPiR co do złotówki**.
3. W scenariuszu:
   - wynagrodzenia i składki pracodawcy (ZUS, FP, FGŚP, PPK) zmieniają się o % płac swojego działu,
   - makulatura, skrobia i chemia, opakowania, gaz i prąd — o % ceny × zmiana wolumenu produkcji;
     celuloza — z wolumenem papieru pakowego,
   - transport, woda i ścieki, odpady — tylko z wolumenem,
   - pozostałe wydatki (amortyzacja, remonty, ubezpieczenia, podatki lokalne, odsetki, usługi obce) są stałe,
   - przychód z wyrobu = przychód 2025 × (1 + % ceny) × współczynnik wolumenu, gdzie
     wolumen = 1 − elastyczność × % ceny (wzrost ograniczony zapasem mocy, domyślnie 5%).

## Suwaki na stronie

| Grupa | Dźwignie | Zakres |
|---|---|---|
| Wynagrodzenia | Produkcja, Utrzymanie ruchu, Logistyka i magazyn, Sprzedaż, Administracja i zarząd | −10…+30% |
| Surowce i półprodukty | Makulatura OCC, celuloza NBSK, skrobia i chemia, gilzy/folia/etykiety | −30…+50% |
| Energia | Gaz ziemny, energia elektryczna | −40…+80% |
| Ceny sprzedaży | Testliner, fluting, papier pakowy | −20…+20% |
| Popyt | Elastyczność popytu (spadek wolumenu przy wzroście ceny) | — |

## Wymagania

- **Python 3.9 lub nowszy**.
- Pakiet z [`requirements.txt`](requirements.txt): `matplotlib` (wykresy). Skoroszyt Excela jest czytany
  bez dodatkowych bibliotek (biblioteka standardowa: `zipfile` + `xml`).
- **CatNip** — do wyświetlenia interaktywnej strony.

Internet nie jest potrzebny.

## Instalacja

```bash
git clone <adres-repozytorium>
cd PrzychodyIRozchody

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## Uruchomienie

### W CatNip (zalecane)

1. Otwórz `PrzychodyIRozchody.catnip` w CatNip.
2. Wybierz środowisko Pythona z zainstalowanym `matplotlib` (venv albo Docker).
3. Uruchom przepływ (Run). Symulator pojawi się w zakładce **Output** i reaguje na suwaki, dopóki
   karta jest otwarta.

### Bez CatNip

```bash
python main_1.py
```

Księga zostanie wczytana i model zbudowany (w konsoli pojawi się liczba odczytanych wierszy i zapisów),
ale interaktywną stronę wyświetla tylko Run Engine CatNip — poza nim zostanie wypisany jedynie
komunikat, że strony nie ma gdzie pokazać.

## Struktura projektu

```mermaid
flowchart LR
    X["KPiR 2025 (Excel)"] --> R[XlsxSheetReader]
    R --> L[LedgerLoader]
    L --> P[ProfitabilityModel]
    P --> S[SymulatorRentownosci]
    S --> M["Main (main_1.py)"]
```

### Bloki, które wykonują pracę

| Blok | Do czego służy |
|---|---|
| `KPiR 2025 (Excel)` | Wskazuje plik `KsiegaPrzychodowIRozchodow2025.xlsx` na kanwie CatNip. |
| `XlsxSheetReader` | Czyta arkusz `KPiR 2025` ze skoroszytu `.xlsx` (bez openpyxl — sam rozpakowuje XML). |
| `LedgerLoader` | Rozpoznaje wiersze z zapisami KPiR (pomija nagłówki) i zamienia je na rekordy `LedgerEntry`. |
| `ProfitabilityModel` | Model rentowności: agregacja księgi, symulacja scenariusza, most dochodu, wrażliwość, próg rentowności. |
| `SymulatorRentownosci` | Interaktywna strona z suwakami, scenariuszami, wykresami i tabelami. |
| `Main` | Punkt wejścia; z niego CatNip generuje `main_1.py`. |

### Rekordy danych

| Blok | Co przechowuje |
|---|---|
| `LedgerEntry` | Jeden zapis KPiR: data, dowód, kontrahent, opis, kolumny przychodów i wydatków oraz analityka (kategoria, dział, wyrób, ilość). |
| `ScenarioLevers` | Wartości dźwigni scenariusza (płace działów, ceny surowców i energii, ceny wyrobów, elastyczność) i ich opis dla strony. |
| `ScenarioResult` | Wynik scenariusza: przychody, wydatki, dochód, rentowność, serie miesięczne i podziały na kategorie, działy i wyroby. |

### Pliki

| Ścieżka | Opis | W repozytorium |
|---|---|---|
| `PrzychodyIRozchody.catnip` | Projekt CatNip (graf bloków). | tak |
| `*.py`, `*.md` | Kod i dokumentacja bloków; `main_1.py` — wygenerowany punkt wejścia. | tak |
| `KsiegaPrzychodowIRozchodow2025.xlsx` | Fikcyjna KPiR 2025 z analityką. **Wymagany** — leży obok `.catnip`. | tak |
| `requirements.txt` | Zależności Pythona. | tak |

## Własne dane

Skoroszyt ma układ ustawowej KPiR (kolumny 1–17) uzupełniony o kolumny analityczne: **Kategoria**,
**Dział**, **Produkt** i **Ilość** [t / MWh] — to na nich opiera się model. Aby przeliczyć inną firmę,
przygotuj arkusz w tym samym układzie i dopasuj listę dźwigni w `ScenarioLevers.LEVERS` do swoich
działów, surowców i wyrobów. Nazwę arkusza ustawia parametr `sheet_name` bloku `XlsxSheetReader`
(domyślnie `KPiR 2025`), a zapas mocy produkcyjnych — `capacity_headroom` w `ProfitabilityModel`
(domyślnie 0,05).

Jeśli używasz **prawdziwej księgi**, nie umieszczaj jej w publicznym repozytorium — dodaj plik do
`.gitignore`.

## Licencja

Licencja nie została jeszcze wybrana — do czasu dodania pliku `LICENSE` wszystkie prawa zastrzeżone.

## Zastrzeżenie

Projekt ma charakter wyłącznie **poglądowy i edukacyjny**. Dane są fikcyjne, a model jest
uproszczeniem. Nie stanowi porady inwestycyjnej, podatkowej, księgowej ani prawnej. Wszelkie decyzje
podejmujesz na własną odpowiedzialność.
