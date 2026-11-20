# Historia zmian

## [Unreleased]

- 2026-11-20 (E4.0 hardening): kontrolowane błędy dla boolowskiego JSON Schema i nieskalarnych SPDX; blokada ponownego inicjalizowania aplikacji wydanej; testy regresyjne oraz `pip check` w CI.

- 2026-11-20 (E4.0): inicjalizator metadanych app, syntetyczny przykład CLI i smoke test, mocniejsze kontrole SemVer, CFF, statusu release, SPDX i integralności raportów testowych. Pozostaje odrębna konfiguracja zasad ochrony gałęzi i rzeczywista atestacja wydania.

- Wersja początkowa szablonu. Nie jest to wydanie oprogramowania.

- 2026-11-19: dodano bezpieczny CI szablonu, walidację JSON Schema / RFC 3339 i YAML, testy negatywne, kontrolę podejrzanych plików oraz wzmocnioną bramkę wydania z SHA i sumami kontrolnymi. Wydanie aplikacji nadal pozostaje zablokowane do czasu rzeczywistych testów i zatwierdzenia.
