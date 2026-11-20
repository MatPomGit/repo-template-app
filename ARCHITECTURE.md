# Architektura aplikacji

**Stan: SCAFFOLD / NOT_DEFINED.** Szablon nie zawiera gotowego produktu. Referencyjne CLI generuje dane syntetyczne i nie jest adapterem sprzętowym.

## Kontekst i cel

Po utworzeniu `app-*` opisz rzeczywistego użytkownika, najważniejszy przypadek użycia, ograniczenia systemu i odpowiedzialność repozytorium. Zapisz konkretne systemy zewnętrzne i interfejsy tylko po ich wdrożeniu lub jednoznacznie oznacz je jako planowane.

## Kanoniczne granice

- **Source of truth:** to repozytorium posiada kod aplikacji i publiczne kontrakty.
- **Upstream:** zależności muszą mieć wersjonowane wydania, lockfile lub przypięty SHA/digest, w zakresie obsługiwanym przez dany ekosystem.
- **Downstream:** `msc-*` i inne odbiorniki korzystają ze stabilnego wydania lub ustalonego SHA, a nie z kopii źródła.
- **Moduły:** adaptery sprzętowe, UI/rendering, I/O i logika domenowa są rozdzielane, gdy powstają takie komponenty.
- **Dane:** eksport jest wersjonowany przez [contracts/events.schema.json](contracts/events.schema.json), a faktyczne przepływy wymagają oceny prywatności.
- **Odtwarzalność:** dokumentuj środowisko, konfigurację, jednostki, zależności oraz wynik rzeczywistych testów.

## Dokumentacja powiązana

Szczegółowe źródła prawdy: [komponenty](docs/architecture/components.md), [przepływy danych](docs/architecture/data-flow.md), [topologia](docs/architecture/deployment.md), [model zagrożeń](docs/security/threat-model.md) i [ADR](docs/adr/README.md). Właściciel kontraktu i decyzje nie powinny być powielane w wielu dokumentach.

**Przy pierwszej implementacji:** zastąp stan `NOT_DEFINED` diagramem aktualnych granic (np. C4 Context/Container), opisz rzeczywiste komponenty i ich źródła, wskaż kontrakty i testy. Nie przedstawiaj planu jako działającego środowiska. Zmiany architektury i dokumentacji wprowadzaj w tym samym PR. Limity: [standard dokumentacji](docs/documentation.md).
