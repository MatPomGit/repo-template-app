# GitHub Pages dla aplikacji `app-*`

**Status szablonu:** `scaffold`, bez konfiguracji produkcyjnej witryny. Strona publiczna jest wizytówką i dokumentacją użytkową aplikacji, **nie interfejsem wewnętrznym repozytorium** ani miejscem przechowywania danych pomiarowych. Niniejsze wytyczne dotyczą aplikacji desktop, web, Android, Unity i aplikacji współpracujących z aparaturą.

## 1. Granica publikacji

- Strony źródłowe umieszczaj **wyłącznie w `pages/`**; dokumentacja techniczna, polityki agentów, ADR, logi, konfiguracja i kod pozostają poza witryną w `docs/` i innych katalogach repozytorium.
- W `mkdocs.yml` wymagane są `docs_dir: pages` i `site_dir: site`. `config/pages-policy.json` określa jawnie dopuszczone pliki źródłowe, hashe SHA-256 statycznych zasobów motywu i zatwierdzone obrazy. Motyw `mkdocs` ma `highlightjs: false`, aby nie ładować kodu z CDN. Aktualizację listy uzasadnij przeglądem diff.
- Nie używaj w ustawieniach GitHub Pages trybu „Deploy from a branch” wskazującego `main`, root ani `/docs`. Preferuj oddzielnie zatwierdzony workflow publikujący **wyłącznie zbudowany katalog `site/`**, z minimalnymi uprawnieniami i kontrolowanym środowiskiem. Alternatywna gałąź `gh-pages` może zawierać wyłącznie zatwierdzone pliki wynikowe.
- Repozytorium szablonu **nie zawiera workflow publikacji**. Wynik testów, merge PR ani przygotowanie zawartości `pages/` nie uruchamiają deploymentu. Włączanie Pages i publikacja są osobnymi czynnościami R3 wymagającymi zgody właściciela.

## 2. Zawartość i nawigacja

Publiczna strona ma odpowiedzieć na pytania: **czym jest aplikacja, co robi, dla kogo, jakie ma ograniczenia, jak ją bezpiecznie uzyskać i skąd pochodzą aktualne informacje**. Krótki zakres zalecanych podstron, dodawanych *tylko gdy istnieje treść*:

| Sekcja | Zawartość użytkowa |
| --- | --- |
| Start | Przeznaczenie, główne funkcje, platforma, reprezentatywny zrzut interfejsu |
| Funkcje | Istniejące możliwości; wyraźne rozróżnienie demonstracji i funkcji zweryfikowanych |
| Instalacja | Wymagania, wersja, obsługiwane systemy, link do rzeczywistego wydania i sum kontrolnych |
| Obsługa | Krótka instrukcja, format eksportu, znane ograniczenia kompatybilności |
| Prywatność | Rzeczywiste operacje na danych, sieć, przechowywanie, zgody, kontakt bezpieczeństwa |
| Wydania | Changelog użytkowy, data i wersja, odnośnik do zatwierdzonego GitHub Release |

Dla desktop/Android pokaż wymagania OS, instalację i uprawnienia. Dla web opisz wymagania przeglądarki i działanie sieciowe. Dla Unity/XR rozdziel kompatybilność wersji silnika i sprzętu. Dla aplikacji pomiarowej podaj obsługiwane urządzenia, firmware/SDK, wymaganą kalibrację i status **rzeczywistej** weryfikacji. Nie kopiuj do strony prywatnych identyfikatorów urządzeń, danych uczestników ani operacyjnych instrukcji dla agentów.

Pisz po polsku lub w jawnie utrzymywanych wersjach językowych. Nazwy zakładek odpowiadają nagłówkom i treściom podstron. Nie publikuj pustych sekcji, tekstów „do uzupełnienia”, notatek redakcyjnych, komunikatów dla właściciela, wytycznych do zarządzania repozytorium, promptów ani instrukcji dla AI. **Nie twórz publicznej strony CONTRIBUTING.**

## 3. Projekt interfejsu i dostępność

Witryna powinna być responsywna, czytelna na telefonie i w trybie ciemnym, jeśli motyw go obsługuje. Stosuj poprawną hierarchię nagłówków, kontrast i obsługę klawiatury zgodne z WCAG 2.2 AA jako cel weryfikacji; tekst alternatywny dla obrazów i podpisy dla materiałów demonstracyjnych. Nie używaj automatycznie odtwarzanych mediów, agresywnych animacji ani sztucznych deklaracji certyfikacji. Testuj linki, kolejność tabulacji, skalowanie tekstu i szerokość tabel. Nie dodawaj skryptów analitycznych, zewnętrznych fontów/CDN ani trackerów bez uprzedniej oceny prywatności i zgody.

Obrazuj aplikację rzeczywistymi zrzutami, fotografiami pozbawionymi metadanych lokalizacji i identyfikatorów, albo czytelnie oznaczonymi ilustracjami poglądowymi. Dane demonstracyjne powinny być syntetyczne. Przed zatwierdzeniem sprawdź EXIF/XMP/IPTC, miniatury, komentarze, podpisy, osadzone pliki i zasoby SVG; **automatyczny filtr nie zastępuje przeglądu multimediów**. Obrazy i skrypty muszą znaleźć się w zatwierdzonej liście plików, a kod JS/CSS przejść osobny audyt.

## 4. Kontrola bezpieczeństwa przed każdą publikacją

1. Ustal exact SHA źródeł, właściciela decyzji, docelową widoczność strony, domenę, konfigurację ustawień Pages i platformę docelową. Prywatność repozytorium **nie gwarantuje prywatności witryny**.
2. Uruchom `python scripts/validate_pages.py`, `python -m mkdocs build --strict` i `python scripts/validate_pages.py --site-dir site`. Pierwsza kontrola obejmuje źródła, a druga także HTML i wygenerowane pliki. Budowanie nie publikuje strony.
3. Zweryfikuj listę **wszystkich** plików w `site/`; sprawdź dozwolone skrypty motywu i brak niezatwierdzonych inline scripts, ścieżek wewnętrznych, sekretów, metadanych zdjęć i notatek skierowanych do agenta. Sprawdź końcowy render oraz linki z poziomu przeglądarki.
4. Wymagaj aktualnego CI na exact SHA oraz niezależnego przeglądu publicznej zawartości. Zatwierdzenie i deployment muszą być udokumentowane odrębnie. Po wdrożeniu sprawdź **rzeczywistą** publiczną stronę i plan wycofania.

**Granica zaufania:** kontrola syntaktyczna i regex wykrywają jedynie znane wzorce. Każdy nowy motyw, plugin, zależność MkDocs, obraz, zasób JS lub zmiana konfiguracji publikacji wymaga ponownej analizy. Nigdy nie traktuj wyniku „PASS: pages” jako automatycznej zgody na upublicznienie.

## 5. Aktualizacje i wycofanie

Zmiany treści utrzymuj wraz z wersją aplikacji i publicznym changelogiem, ale **nie łącz automatycznie release aplikacji z publikacją Pages**. W razie wykrycia wycieku wyłącz publiczne źródło, ustal zawartość i SHA, przywróć sprawdzony build lub wycofaj witrynę; zachowaj minimalny bezpieczny zapis incydentu zgodnie z `docs/security/incident-response.md`. Usunięcie z bieżącej strony nie gwarantuje usunięcia kopii w pamięci podręcznej lub archiwach.
