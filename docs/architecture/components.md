# Komponenty i interfejsy

**Status: NOT_DEFINED.** Szablon nie deklaruje produkcyjnej architektury aplikacji. Referencyjne `src/example_cli.py` jest przykładem syntetycznym.

## Gdy pojawi się pierwszy moduł

Dla każdego **istniejącego** modułu zapisz nazwę i ścieżkę źródeł, odpowiedzialność, publiczne API/CLI/zdarzenia, zależności oraz wywołujące go komponenty. Nie wpisuj hipotetycznych modułów jako zaimplementowanych.

| Moduł | Źródło | Odpowiedzialność | Publiczny kontrakt | Test |
| --- | --- | --- | --- | --- |
| Brak modułów produkcyjnych | NOT_APPLICABLE | Scaffold | [Kontrakty](../contracts.md) | NOT_RUN |

## Zasady granic

Oddziel logikę aplikacji od transportu, zapisu, interfejsu i adapterów urządzeń, **jeżeli te części istnieją**. Dla współdzielonej logiki używaj wersjonowanej biblioteki zamiast kopiowania implementacji. Wszelkie zmiany API odnotuj w [kompatybilności](../compatibility.md) i, gdy są decyzją architektoniczną, w [ADR](../adr/README.md).

Przy rozwoju projektu aktualizuj tabelę po włączeniu lub usunięciu modułu. Link do kodu i rzeczywisty test są bardziej użyteczne niż schemat przyszłych klas.
