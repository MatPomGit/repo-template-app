# Polityka publikacji GitHub Pages

Strona przeznaczona dla odwiedzających jest **oddzielona od repozytorium**. Źródłem treści jest wyłącznie `pages/`, a dokumentacja techniczna pozostaje w `docs/`. Nie publikuj `AGENTS.md`, `.github/`, dokumentacji operacyjnej, notatek, ADR ani całego katalogu repozytorium.

## Granice publikacji

Konfiguracja `mkdocs.yml` musi wskazywać `docs_dir: pages` oraz `site_dir: site`. Każdy zasób `pages/` musi zostać jawnie wymieniony w [public_files](../config/pages-policy.json). Bez zatwierdzenia tej listy nie dodawaj nowych stron, obrazów ani skryptów. Nie używaj symlinków, automatycznego kopiowania z `docs/`, pluginów z dostępem do pozostałych plików repozytorium ani publikacji wszystkich plików projektu.

## Zasady języka

Na stronie **nigdy** nie umieszczaj instrukcji skierowanych do agenta AI, promptów systemowych, uwag edytorskich i redakcyjnych, `TODO`, `REPLACE`, poleceń dla autora, planów zmian ani informacji o tym, jak pomagać w prowadzeniu repozytorium. Nie twórz publicznego przewodnika `CONTRIBUTING` ani zachęt do PR. Każdy opis ma być samodzielny, neutralny i zrozumiały dla czytelnika spoza projektu.

Nie publikuj sekretów, danych uczestników i studentów, prywatnych logów, adresów hostów ani niejawnych informacji o metodologii i działalności agentów. Linki, obrazy i metadane obrazów traktuj tak samo jak treść.

## Szczególnie dla repozytoriów prywatnych

**Prywatne repozytorium nie oznacza prywatnej witryny GitHub Pages.** Przed włączeniem Pages sprawdź rzeczywiste ustawienia widoczności witryny, plan i zasady organizacji, domenę, uprawnienia wykonawcy oraz wszystkie wygenerowane pliki. Jeśli wymagana prywatność nie jest zapewniona, nie publikuj.

Uruchom `python scripts/validate_pages.py` oraz kontrolę szkieletu. Automatyczny filtr wykrywa część niedozwolonych instrukcji i ścieżek, lecz nie gwarantuje kompletnego przeglądu poufności. **Każdą publikację** zatwierdza właściciel po niezależnym przeglądzie zawartości, wygenerowanego HTML i zasobów na aktualnym SHA. Nie uruchamiaj automatycznej publikacji na każdym merge. Sam katalog `pages/` niczego nie publikuje.
