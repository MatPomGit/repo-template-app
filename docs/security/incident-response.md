# Obsługa incydentów bezpieczeństwa

**Stan: procedura bazowa, nieuruchomiona usługa dyżurowa.** Kanał zgłoszeń i odpowiedzialne osoby wskazuje [SECURITY.md](../../SECURITY.md); w szablonie kontakt nie został jeszcze skonfigurowany.

## Kroki po stwierdzeniu podejrzenia incydentu

1. Ogranicz dostęp do poufnych danych i utrwal minimalny, bezpieczny zapis zdarzenia bez publikowania sekretów.
2. Ustal zakres, podatną wersję/SHA, systemy i dane mogące zostać dotknięte oraz faktyczny stan usług.
3. Skontaktuj się z upoważnionym właścicielem poza publicznymi Issues. Nie wyłączaj infrastruktury, nie rotuj cudzych kluczy i nie usuwaj danych bez upoważnienia.
4. Zaplanuj odwracalną naprawę, kontrolę regresji, rollback i weryfikację runtime.
5. Przeprowadź publikację informacji po ocenie skutków, zgód oraz obowiązujących zobowiązań prawnych.
6. Zapisz chronologię, wynik i działania zapobiegawcze w miejscu z kontrolą dostępu; publicznie udostępniaj tylko oczyszczone podsumowanie.

Nie deklaruj SLA, automatycznej detekcji ani certyfikacji bez faktycznego wdrożenia. Każda aktualizacja procedury musi zachowywać prywatność i polityki hosta.
