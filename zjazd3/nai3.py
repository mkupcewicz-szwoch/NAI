"""
Wykonawcy: Szymon Witowski s29099, Maciej Kupcewicz-Szwoch s29467

Do uruchomienia programu potrzebna jest instalacja:
pip install pandas scikit-learn requests

Kod implementuje system rekomendacji filmow i seriali dla wybranego
uzytkownika na podstawie ocen, preferencji gatunkowych i klastrow
podobnych uzytkownikow.

Dane wejsciowe:
- dane-z-ankiety.csv - oceny uzytkownikow
- filmy_tmdb.json - gatunki i srednie oceny z TMDB (tworzony przez program)

Program wyznacza:
- 5 rekomendacji - tytuly najlepiej dopasowane do uzytkownika
- 5 antyrekomendacji - tytuly najslabiej dopasowane do uzytkownika

Sposob dzialania:
Program pobiera brakujace informacje z TMDB, tworzy macierz ocen,
grupuje uzytkownikow za pomoca K-Means, oblicza wyniki filmow
i wyswietla rekomendacje oraz antyrekomendacje.

Uruchomienie: python nai3.py
"""

import json
import os

import pandas as pd
import requests
from sklearn.cluster import KMeans

os.chdir(os.path.dirname(os.path.abspath(__file__)))
API_KEY = ''  # Klucz TMDB po pobraniu danych zostaw pusty


# Wczytanie ankiety i utworzenie tabeli ocen
# W CSV po nazwie uzytkownika wystepuja kolejne pary: film, ocena
raw = pd.read_csv('dane-z-ankiety.csv', header=None, skiprows=1).iloc[:, 1:]

oceny = []
for _, row in raw.iterrows():
    user = row.iloc[0]
    for film, score in zip(row.iloc[1::2], row.iloc[2::2]):
        if pd.notna(film) and pd.notna(score):
            oceny.append([user, str(film).strip(), float(score)])

ratings = pd.DataFrame(oceny, columns=['user', 'movie', 'rating'])

# W macierzy wiersz oznacza osobe, kolumna film, a puste pole brak oceny
matrix = ratings.pivot_table(index='user', columns='movie', values='rating')


# Dane TMDB - korzystamy z JSON-a, a brakujace tytuly mozemy pobrac z API
if os.path.exists('filmy_tmdb.json'):
    with open('filmy_tmdb.json', encoding='utf-8') as file:
        movies = json.load(file)['filmy']
else:
    movies = {}

missing = [film for film in matrix.columns if film not in movies]

if missing and API_KEY:
    # Zamiana numerow gatunkow TMDB na ich nazwy
    genre_names = {}
    for kind in ['movie', 'tv']:
        response = requests.get(
            f'https://api.themoviedb.org/3/genre/{kind}/list',
            params={'api_key': API_KEY, 'language': 'en-US'}, timeout=15
        )
        response.raise_for_status()
        for genre in response.json()['genres']:
            genre_names[genre['id']] = genre['name']

    for number, film in enumerate(missing, 1):
        # Jezeli tytul zawiera rok, szukamy odpowiedniej wersji filmu
        title, year = film, ''
        if film.endswith(')') and film[-5:-1].isdigit():
            title, year = film[:-7], film[-5:-1]

        response = requests.get(
            'https://api.themoviedb.org/3/search/multi',
            params={'api_key': API_KEY, 'query': title, 'language': 'pl-PL'}, timeout=15
        )
        response.raise_for_status()

        found = None
        for result in response.json()['results']:
            if result['media_type'] in ['movie', 'tv']:
                date = result.get('release_date') or result.get('first_air_date') or ''
                if not year or date.startswith(year):
                    found = result
                    break

        if found:
            movies[film] = {
                'id': found['id'],
                'tytul_tmdb': found.get('title') or found.get('name'),
                'gatunki': [genre_names[g] for g in found['genre_ids'] if g in genre_names],
                'ocena': found['vote_average'],
                'glosy': found['vote_count']
            }
        else:
            movies[film] = None
            print('Nie znaleziono:', film)

        # Przy duzym pobieraniu zapisujemy postep co 20 tytulow
        if number % 20 == 0 or number == len(missing):
            with open('filmy_tmdb.json', 'w', encoding='utf-8') as file:
                json.dump({'filmy': movies}, file, ensure_ascii=False, indent=2)

    print('Zakonczono pobieranie danych TMDB')
elif missing:
    print(f'Brak informacji TMDB dla {len(missing)} tytulow')


# Preferencje gatunkowe i podzial osob na klastry
# Preferencje gatunkowe liczymy na podstawie roznic ocen i sredniej uzytkownika
profiles = {}
for user in matrix.index:
    user_ratings = matrix.loc[user].dropna()
    average = user_ratings.mean()
    genres = {}

    for film, score in user_ratings.items():
        info = movies.get(film) or {}
        for genre in info.get('gatunki', []):
            genres.setdefault(genre, []).append(score - average)

    profiles[user] = {genre: sum(scores) / len(scores) for genre, scores in genres.items()}

# K-Means porownuje profile gatunkowe uzytkownikow
features = pd.DataFrame(profiles).T.fillna(0)
if features.empty:
    raise SystemExit('Brak danych o gatunkach do K-Means')

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = pd.Series(kmeans.fit_predict(features), index=features.index)

print('\n========== SYSTEM REKOMENDACJI ==========')
for cluster in range(3):
    users = clusters[clusters == cluster].index
    print(f'Klaster {cluster + 1}: {", ".join(users)}')


# Wybor uzytkownika i osob o podobnych preferencjach
print('\nWybierz uzytkownika:')
users = raw.iloc[:, 0].tolist()
for number, user in enumerate(users, 1):
    print(f'{number}. {user}')

number = int(input('Numer uzytkownika: '))
if not 1 <= number <= len(users):
    raise SystemExit('Niepoprawny numer')

user = users[number - 1]
similar = clusters[clusters == clusters[user]].index.drop(user)
print(f'\nWybrano: {user} (klaster {clusters[user] + 1})')


# Przewidywana ocena filmow, ktorych uzytkownik jeszcze nie ocenil
ranking = []
average_csv = ratings['rating'].mean()

for film in matrix.columns[matrix.loc[user].isna()]:
    all_scores = matrix[film].dropna()
    similar_scores = matrix.loc[similar, film].dropna()
    info = movies.get(film) or {}

    tmdb = info.get('ocena', 0)
    base = tmdb if tmdb > 0 else average_csv

    # Oceny z klastra liczymy dodatkowo, TMDB ma wage dwoch ocen
    score = (all_scores.sum() + similar_scores.sum() + 2 * base) / (
        len(all_scores) + len(similar_scores) + 2
    )

    # Drobna premia lub kara na podstawie lubianych gatunkow
    genres = info.get('gatunki', [])
    if genres:
        score += 0.4 * sum(profiles[user].get(g, 0) for g in genres) / len(genres)

    score = round(max(1, min(10, score)), 2)
    ranking.append([film, score, round(tmdb, 1) if tmdb else '-', ', '.join(genres)])


# Wyswietlenie 5 najlepszych i 5 najgorszych dopasowan
ranking.sort(key=lambda item: item[1], reverse=True)

for title, results in [
    ('TOP 5 REKOMENDACJI', ranking[:5]),
    ('TOP 5 ANTYREKOMENDACJI', ranking[-5:][::-1])
]:
    print(f'\n========== {title} ==========')
    for number, (film, score, tmdb, genres) in enumerate(results, 1):
        print(f'{number}. {film} - wynik {score}/10')
        print(f'   TMDB: {tmdb} | Gatunki: {genres or "brak danych"}')
