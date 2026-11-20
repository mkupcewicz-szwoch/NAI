# System rekomendacji filmów i seriali

---

## Autorzy

- Szymon Witowski s29099
- Maciej Kupcewicz-Szwoch s29467

---

## Opis projektu

Program implementuje system rekomendacji filmów i seriali dla wybranego użytkownika na podstawie:

- ocen użytkowników,
- preferencji gatunkowych,
- klastrów podobnych użytkowników.

Dodatkowo system generuje antyrekomendacje, czyli tytuły najsłabiej dopasowane do użytkownika.

## Dane wejściowe

- `dane-z-ankiety.csv` – plik z ocenami filmów i seriali przez użytkowników
- `filmy_tmdb.json` – plik z informacjami o produkcjach z TMDB (tworzony przez program)

## Funkcjonalność

- Pobieranie informacji o produkcjach z TMDB API (gatunki i średnie oceny).
- Tworzenie macierzy ocen użytkowników i filmów.
- Grupowanie użytkowników za pomocą K-Means.
- Wyznaczanie preferencji gatunkowych użytkowników.
- Obliczanie wyników rekomendacji na podstawie ocen użytkowników, dodatkowych ocen osób z tego samego klastra oraz danych TMDB.
- Uwzględnianie preferowanych i niepreferowanych gatunków.
- Generowanie 5 rekomendacji i 5 antyrekomendacji spośród tytułów nieocenionych przez wybranego użytkownika.
- Wyświetlanie przewidywanego wyniku, oceny TMDB i gatunków.

## Instalacja

Wymagane biblioteki:

```bash
pip install pandas scikit-learn requests
```

## Uruchomienie

W folderze z plikami projektu uruchom program:

```bash
python nai3.py
```

Następnie wybierz numer użytkownika, dla którego mają zostać wygenerowane rekomendacje. Aby pobrać brakujące dane TMDB, wpisz klucz API v3 w zmiennej `API_KEY` w kodzie

## Wyjście programu

- **Rekomendacje** – 5 najlepiej dopasowanych, nieocenionych tytułów wraz z wynikiem, oceną TMDB i gatunkami.
- **Antyrekomendacje** – 5 najsłabiej dopasowanych, nieocenionych tytułów wraz z wynikiem, oceną TMDB i gatunkami.
