# Kompresja gramatykowa sekwencji DNA

Projekt demonstruje algorytmy kompresji gramatykowej (SLP/RLSLP) oraz równoważenie drzew wyprowadzeń, inspirowane pracami z literatury (m.in. RePair, Sequitur, recompression oraz balansowanie ścieżek ciężkich). Implementacje są proste, nastawione na eksperymenty i wizualizację.

## Cel projektu

Celem projektu jest dostarczenie eksperymentalnego frameworku do badania
kompresji gramatykowej sekwencji (SLP/RLSLP) oraz wpływu balansowania
drzew wyprowadzeń na ich własności strukturalne.

Projekt umożliwia porównanie klasycznych algorytmów kompresji
(RePair, Sequitur, recompression) pod względem rozmiaru gramatyki
oraz głębokości drzewa wyprowadzeń, a także wizualizację powstałych struktur.

## Zawartość repozytorium

Najważniejsze pliki:

- `slp.py` – struktura danych SLP/RLSLP (reguły terminalne, binarne i run-length). 
- `repair.py` – implementacja kompresora RePair.
- `sequitur.py` – uproszczona, offline wersja Sequitur.
- `jez.py` – recompression (wariant losowy oraz zachłanny) z regułami run-length.
- `balancing.py` – procedury balansowania SLP (heavy paths / longest path).
- `tests.py` – generator instancji „adversarial” do porównań.
- `visuals.py` – generowanie grafów drzew wyprowadzeń w TikZ.
- `plots.py` – generowanie wykresów rozmiaru i głębokości gramatyk.

## Wymagania

- Python 3.8+.
- Opcjonalnie: `matplotlib` do rysowania wykresów w `plots.py`.

## Opis techniczny

Repozytorium implementuje kilka wariantów kompresji gramatykowej oraz operacje na SLP/RLSLP:

- **SLP/RLSLP (`slp.py`)** – reguły terminalne, binarne oraz run-length; metody `length`, `access`, `size`, `depth` służą do weryfikacji poprawności i analizy złożoności wyprowadzeń.
- **RePair (`repair.py`)** – iteracyjne zastępowanie najczęstszych digramów, a na końcu budowa zbalansowanego drzewa binarnego z pozostałej sekwencji.
- **Sequitur (`sequitur.py`)** – offline wariant oparty o wykrywanie powtarzających się digramów i reużywanie reguł długości 2; końcowo normalizacja do CNF.
- **Recompression (`jez.py`)** – naprzemienne kompresje bloków (run-length) oraz par z losową/greedy partycją symboli; zawiera deterministyczny wariant zachłanny.
- **Balansowanie (`balancing.py`)** – algorytmy oparte o heavy paths i longest path, poprawiające wysokość drzewa wyprowadzeń do rzędu logarytmicznego.

## Wizualizacje i wykresy

- **Wykresy:** uruchom `plots.py`, aby wygenerować PDF-y (`sizes_adversarial.pdf`, `depths_adversarial.pdf`).
- **Rysunki drzew:** uruchom `visuals.py`, który wypisze kod TikZ do wyświetlenia w LaTeX.

## Autorzy i zakres prac

Podział zadań w projekcie:

- **Nikola Reguła** – implementacje kompresorów RePair i Sequitur oraz  wizualizacje drzew wyprowadzeń i wykresy porównawcze.
- **Aleksandra Rudnik** – algorytmy recompression (wariant losowy i zachłanny), w tym reguły run-length, testy poprawności
- **Maria Cicirko** – projekt i implementacja algorytmów balansowania SLP
