# Kod źródłowy

Docelowy układ zależy od platformy; ten katalog nie zawiera działającego produktu.
W przypadku UPM poprawnym korzeniem może być `Runtime/` i `Editor/`, dla Androida `app/src`, dla web `src/`, a dla Pythona `src/<package>/`.
Pozostań przy jednym kanonicznym właścicielu źródeł.

## Referencyjny CLI

`example_cli.py` zapisuje deterministyczny, jawnie syntetyczny rekord w formacie `contracts/events.schema.json`. Przykład nie odczytuje urządzeń, nie wykonuje pomiarów i nie stanowi implementacji interfejsu konkretnej aplikacji. Test dymny uruchamia kod w osobnym procesie i waliduje zapisany JSON.
