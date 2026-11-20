# ADR-0002: granice zaufania i zabezpieczenia aplikacji

**Status:** proposed  
**Data:** 2026-11-20  
**Kategoria:** security, privacy, architecture

## Kontekst

Szablon `app-*` może być używany do aplikacji webowych, desktopowych, Android, Unity lub programów współpracujących z aparaturą. Nie ma jeszcze konkretnego transportu, modelu tożsamości ani produkcyjnego środowiska. Nie można więc zadeklarować rzeczywistych zabezpieczeń.

## Propozycja do rozstrzygnięcia w projekcie potomnym

Każde wejście z użytkownika, pliku, sieci lub urządzenia stanowi granicę zaufania wymagającą jawnej walidacji. Dostęp do zasobów ma wykorzystywać minimalne uprawnienia, a sekrety pozostają poza kodem, repo i artefaktami. Przetwarzanie i eksport danych wrażliwych wymaga odrębnej polityki, uprawnień oraz testów. Kod z nieufnego PR jest izolowany od stałych runnerów i produkcji.

**To nie jest zatwierdzona decyzja dotycząca nieistniejącej aplikacji.** Po określeniu architektury właściciel dokumentuje faktyczne granice, mechanizmy uwierzytelniania, role i wyjątki albo odrzuca propozycję.

## Alternatywy

W pełni offline, lokalny backend, usługa zdalna lub architektura hybrydowa. Każda zmienia powierzchnię ataku i obowiązki dotyczące danych. Wybór wymaga realnego przypadku użycia, nie preferencji szablonu.

## Konsekwencje i dowody

Przed przejściem do pierwszej obsługi prawdziwych danych trzeba zaktualizować [przepływy](../architecture/data-flow.md), [model zagrożeń](../security/threat-model.md), [SECURITY.md](../../SECURITY.md) i [testy](../testing.md). Wynikiem jest decyzja zaakceptowana lub odrzucona z referencją do testów na exact SHA, a nie sam wypełniony formularz.
