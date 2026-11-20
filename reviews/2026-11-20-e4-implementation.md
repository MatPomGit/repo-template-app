# E4.0 — implementacja poprawek po niezależnej recenzji

Data: 2026-11-20. Źródło: [E3.0 #3](https://github.com/MatPomGit/repo-template-app/issues/3).

| Ustalenie | Status | Implementacja |
| --- | --- | --- |
| E3-01 | **Otwarte** | Ruleset `main` nie wymaga jeszcze PR review ani status check. Wymaga osobnej operacji administracyjnej w GitHub; nie wolno uznawać zielonego CI za wymuszone. |
| E3-02 | Częściowo | Walidator odrzuca nieobsługiwane identyfikatory SPDX; zgodność prawna pełnego tekstu licencji pozostaje kontrolą człowieka. |
| E3-03 | Częściowo | Release evidence i test report wymagają `schema_version: 1`; do evidence dodano SHA-256 raportu. To test integralności, **nie atestacja pochodzenia, uprawnień ani autoryzacja publikacji**. |
| E3-04 | Naprawiono kontrolę spójności | Porównanie `release_status` komponentu i stanu, tytułu i wersji CFF z manifestem, testy negatywne. |
| E3-05 | Wdrożono przykład | Idempotentny inicjalizator jednego profilu i deterministyczne syntetyczne CLI z walidacją zdarzenia w smoke teście. Realna aplikacja i sprzęt pozostają NOT_RUN. |
| E3-06 | Częściowo | SemVer 2.0 ze sprawdzaniem zer wiodących i czytana wersja szablonu. Osobne migracje kontraktów pozostają backlogiem. |
| E3-07 | Otwarte | Przypięte bezpośrednie zależności nie gwarantują powtarzalności wszystkich zależności tranzytywnych. Skan sekretów jest heurystyczny. |

## Odbiór

- `python scripts/validate_repository.py --phase scaffold`
- `python -m unittest discover -s tests -v` (zawiera CLI smoke, idempotentny inicjalizator, testy negatywne).
- Po uruchomieniu GitHub Actions odnotować exact SHA i PASS/FAIL.
- Release gate pozostaje domyślnie zablokowany; wydanie nie jest autoryzowane przez testy fixture.
- Oddzielnie skonfigurować wymagalność check `Validate scaffold and security` i recenzji w rulesecie `main`, bez obchodzenia ochrony.

## Dodatkowy przegląd odporności

W trakcie kontynuacji E4.0 wykryto dwa punkty, w których dopuszczalny formalnie schemat JSON Schema (wartość boolowska dla property) lub błędnie stypowany SPDX (lista zamiast stringa) powodowały wyjątek Pythona. Dodano kontrolowane błędy walidacji i osobne testy negatywne. Inicjalizator odrzuca aplikacje wykraczające poza stan `scaffold/not_released`, niezależnie od zawartości metadanych, oraz błędne wartości jednoliniowe. W CI dodano `pip check`, który diagnozuje niespójność zainstalowanych zależności, ale **nie zastępuje** blokady hashy zależności tranzytywnych.

Komunikat pozytywnej walidacji wydania zmieniono na `PASS: app release-evidence consistency (NOT publication approval)`; nie stanowi on decyzji o wydaniu. Dodano test odrzucenia deklaracji Apache-2.0 przy tekście licencji MIT.
