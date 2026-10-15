Interaktywny symulator rentowności na potrzeby prezentacji. Strona pokazuje się w zakładce Output Run Engine'u po uruchomieniu wygenerowanego main (Code Run) i odpowiada na suwaki tak długo, jak karta jest otwarta.

**Co zawiera:**
- 5 gotowych scenariuszy (przyciski): rok 2025, płace 2026, szok energetyczny, słaby rynek papieru, podwyżka cennika,
- kafelki: przychody, wydatki, dochód, rentowność — ze zmianą względem 2025,
- pasek rentowności i próg rentowności cenowej,
- suwaki: płace 5 działów (−10…+30%), makulatura, celuloza, skrobia i chemia, opakowania (−30…+50%), gaz i prąd (−40…+80%), ceny 3 wyrobów (−20…+20%), elastyczność popytu,
- wykresy: most dochodu, dochód miesięczny 2025 vs scenariusz, wrażliwość na +1 pp, struktura wydatków,
- tabele: wyroby, koszty osobowe działów, wydatki według kategorii.

Kod klasy jest generowany z definicji strony — zmiany wprowadzaj w edytorze bloku (Markup / Python / Style).

## model
Instancja `ProfitabilityModel` z poprzedniego bloku.

## show
Wyświetla stronę w zakładce Output.

## preset_bazowy
Zeruje wszystkie suwaki — rok 2025 z KPiR.

## preset_place
Płace 2026: produkcja, UR i logistyka +7%, sprzedaż +5%, administracja +4%.

## preset_energia
Gaz +25%, energia elektryczna +15%.

## preset_rynek
Ceny: testliner −6%, fluting −7%, papier pakowy −3%; makulatura +10%.

## preset_cennik
Ceny +3…4% przy elastyczności popytu 0,8.
