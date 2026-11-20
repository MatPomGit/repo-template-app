# Historia zmian

## [Unreleased]

- 2026-11-20: wydzielono źródła GitHub Pages w `pages/` zamiast `docs/`, wprowadzono allowlistę i wykrywanie instrukcji agentowych oraz notatek redakcyjnych. Usunięto `CONTRIBUTING.md` i powiązane odsyłacze.

- 2026-11-20: dodano strukturę architektury, Code of Conduct, governance i support, model zagrożeń, ADR bezpieczeństwa, runbook oraz politykę limitów znaków. Walidator dokumentacji z testami regresyjnymi jest częścią scaffold CI.

- 2026-11-20: ujednolicono kontrakt agentów APP z zasadami Research Autopilot, HomeServer i PRz: R0-R3, DoR/DoD, exact-SHA, granice uprawnień, bezpieczne merge/release, współpraca agentów i pięć lokalnych profili; dodano testy spójności dokumentacji.

- 2026-11-20 (E4.0 hardening): kontrolowane błędy dla boolowskiego JSON Schema i nieskalarnych SPDX; blokada ponownego inicjalizowania aplikacji wydanej; testy regresyjne oraz `pip check` w CI.

- 2026-11-20 (E4.0): inicjalizator metadanych app, syntetyczny przykład CLI i smoke test, mocniejsze kontrole SemVer, CFF, statusu release, SPDX i integralności raportów testowych. Pozostaje odrębna konfiguracja zasad ochrony gałęzi i rzeczywista atestacja wydania.

- Wersja początkowa szablonu. Nie jest to wydanie oprogramowania.

- 2026-11-19: dodano bezpieczny CI szablonu, walidację JSON Schema / RFC 3339 i YAML, testy negatywne, kontrolę podejrzanych plików oraz wzmocnioną bramkę wydania z SHA i sumami kontrolnymi. Wydanie aplikacji nadal pozostaje zablokowane do czasu rzeczywistych testów i zatwierdzenia.

### E4.0 — utwardzenie walidacji i weryfikacji PR #5

- Testy PR wykonują dokładne SHA gałęzi HEAD, a nie domyślny syntetyczny merge SHA.
- W CI budowana i kontrolowana jest wynikowa witryna MkDocs bez publikacji.
- Rozszerzono filtr poleceń agentowych i aktywnego HTML, walidację tytułu aplikacji oraz regresję negatywną.
- Ustawienia rulesetu `main` wymagają odrębnej administracyjnej zmiany; automatyczny PASS nie oznacza approval ani merge.
