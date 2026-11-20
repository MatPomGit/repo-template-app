# Standard dokumentacji i limity objętości

**Status:** wymagania redakcyjne szablonu. Docelowa aplikacja może dodać nowe rozdziały, lecz nie może po cichu obniżać kontroli i zacierać informacji o stanie.

## Jedno źródło prawdy

- [README](../README.md): krótki opis użytkowy, funkcje, odbiorcy, instalacja lub odnośniki.
- [ARCHITECTURE](../ARCHITECTURE.md): kontekst systemu, granice, referencje do komponentów i przepływów, bez szczegółowych dzienników.
- [Architektura szczegółowa](architecture/README.md): rzeczywiste komponenty, przepływy i wdrożenie.
- [ADR](adr/README.md): uzasadnienia decyzji, alternatywy i konsekwencje, nie bieżący status kodu.
- [SECURITY](../SECURITY.md): zgłaszanie podatności, zakres wsparcia, znane ograniczenia i kontakt.
- [Model zagrożeń](security/threat-model.md): ryzyka rzeczywistego systemu i dowody kontroli.
- [Code of Conduct](../CODE_OF_CONDUCT.md): oczekiwane zachowania i obsługa zgłoszeń.
- [GOVERNANCE](../GOVERNANCE.md): role, proces podejmowania decyzji, odpowiedzialność.
- [SUPPORT](../SUPPORT.md): sposób uzyskiwania pomocy i zgłaszania awarii.
- [Runbook](operations/runbook.md): instalacja operacyjna, diagnostyka, rollback, bez sekretów.
- [GitHub Pages](pages.md): odrębne `pages/`, tylko materiały publiczne, bez instrukcji agentowych i uwag redakcyjnych.

## Budżet znaków

Maszynowym źródłem limitów jest [config/documentation-policy.json](../config/documentation-policy.json). Liczymy **znaki Unicode** (punkty kodowe Pythona, `len(text)`), włącznie ze spacjami i końcami wierszy, **nie bajty UTF-8 ani słowa**. Walidator nie obcina dokumentów automatycznie.

| Grupa | Maks. znaków |
| --- | ---: |
| Główne `AGENTS.md`, `README.md`, `ARCHITECTURE.md` | 12 000 |
| `SECURITY.md`, główna procedura agentów | 10 000 |
| Rozdziały architektury i model zagrożeń | 8 500 |
| `CODE_OF_CONDUCT.md`, `SUPPORT.md`, pojedynczy ADR (także nowy) | 6 000–6 500 |
| Lokalne `profiles/*/AGENTS.md` | 3 000 |
| Pozostałe dokumenty `docs/` bez własnego limitu | 10 000 |
| Strony `pages/**/*.md` | 6 000 |

Sprawdzaj limity poleceniem `python scripts/validate_documentation.py`. Ta sama kontrola jest częścią walidatora repozytorium i testów CI. Przekroczenie limitu to **FAIL** z nazwą pliku i liczbą znaków.

## Jak rozwijać dokumenty

**Scaffold:** zachowaj informację `NOT_DEFINED`, `NOT_ASSESSED` lub `NOT_DEPLOYED`. Nie przedstawiaj pytań kontrolnych jako wykonanych testów.

**Publiczna witryna:** redaguj wyłącznie w `pages/`, nigdy w `docs/`. Zapisz każdy zasób na allowliście, usuń instrukcje wewnętrzne, przejrzyj render i widoczność strony. [Polityka Pages](pages.md).

**Pierwszy działający moduł:** uaktualnij README, diagram i tabelę faktycznych modułów, ich API i zależności, obsługiwane platformy oraz testy. Usuń nieaktualne fragmenty szablonowe z zakresu wdrożonej funkcji.

**Pierwszy przepływ danych lub integracja:** dodaj rzeczywisty przepływ, klasyfikację i retencję danych, model zagrożeń, ograniczenia uprawnień i odpowiedni ADR. Nie publikuj prywatnych danych ani sekretów.

**Przed wydaniem:** zweryfikuj wersje, instrukcję instalacji, kompatybilność, kanał bezpieczeństwa, wsparcie, rollback, licencję, testy i zatwierdzenie. Dokument nie może przypisywać projektowi nieistniejących zabezpieczeń ani certyfikatów.

**W razie przekroczenia limitu:** usuń dublujące się opisy, przenieś szczegóły do odpowiadającego im już istniejącego dokumentu albo utwórz **jeden** uzasadniony rozdział z nawigacją. Zmianę samego limitu uzasadnij w PR, dodaj test, sprawdź odnośniki i ryzyko rozproszenia wiedzy. Nie zwiększaj limitu automatycznie, nie zatajaj brakującej dokumentacji i nie usuwaj treści prawnych dla spełnienia budżetu.

Dla każdej aktualizacji sprawdź zgodność dokumentu ze źródłami, podpisane osie i jednostki na wykresach, aktualność odnośników, język, status testów oraz wskazanie wersji/SHA dla twierdzeń technicznych. Nie kopiuj prywatnych procedur operacyjnych do publicznej strony.
