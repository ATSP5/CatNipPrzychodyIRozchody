Model rentowności papierni zbudowany na zapisach KPiR 2025. Agreguje księgę do linii (miesiąc × kategoria × dział × wyrób) i przelicza je dla scenariusza: płace działów, ceny surowców, półproduktów i energii oraz ceny wyrobów. Wyjście `model` to sam model — raport woła jego metody przy każdym ruchu suwaka.

## entries
Lista `LedgerEntry` z bloku `LedgerLoader`.

## capacity_headroom
Ile sprzedaż może wzrosnąć po obniżce ceny (domyślnie 0,05 = 5%) — maszyna papiernicza pracuje blisko pełnych mocy.

## price_search_range
Zakres zmian cen (%) przeszukiwany przy wyznaczaniu progu rentowności cenowej. Domyślnie (−60, 60).

## simulate
Zwraca `ScenarioResult` dla podanych `ScenarioLevers`. Reguły:
- wynagrodzenia i składki pracodawcy (ZUS, FP, FGŚP, PPK) zmieniają się o % płac swojego działu,
- makulatura, skrobia i chemia, opakowania, gaz i prąd: o % ceny × zmiana wolumenu produkcji; celuloza — × wolumen papieru pakowego,
- transport, woda i ścieki, odpady: tylko z wolumenem,
- pozostałe wydatki (amortyzacja, remonty, ubezpieczenia, podatki lokalne, odsetki, usługi obce) są stałe,
- przychód z wyrobu = przychód 2025 × (1 + % ceny) × współczynnik wolumenu; wolumen = 1 − elastyczność × % ceny.

## baseline
Wynik bez żadnych zmian — odtwarza sumy z KPiR co do złotówki.

## bridge
Most dochodu: 2025 → ceny sprzedaży → wynagrodzenia → surowce i półprodukty → energia → scenariusz. Grupy dokładane są kolejno, więc suma kroków równa się różnicy dochodów.

## sensitivity
Zmiana dochodu, gdy każda dźwignia z osobna wzrośnie o 1 punkt procentowy względem bieżącego scenariusza. Posortowane od największego wpływu.

## break_even_price_change
O ile procent musiałyby się zmienić ceny wszystkich wyrobów naraz, aby dochód wyniósł zero.

## model
Zwraca sam model (wyjście bloku).
