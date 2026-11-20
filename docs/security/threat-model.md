# Model zagrożeń aplikacji

**Ocena ryzyka: NOT_ASSESSED.** To lista obowiązkowych obszarów analizy, nie potwierdzenie zabezpieczeń. Decyzję architektoniczną dotyczącą granic bezpieczeństwa dokumentuje [ADR-0002](../adr/0002-security-boundaries.md).

## Minimalna analiza po rozpoczęciu implementacji

Dla każdej faktycznej granicy zaufania, zasobu i przepływu z [data-flow](../architecture/data-flow.md) opisz zagrożenie, scenariusz ataku, prawdopodobieństwo, skutek, kontrolę i dowód jej działania. Oznacz jako `NOT_APPLICABLE` tylko uzasadnione pominięcia.

| Obszar | Pytanie do zweryfikowania | Status szablonu |
| --- | --- | --- |
| Tożsamość i dostęp | Czy użytkownicy/usługi mogą podszyć się pod inne podmioty? | NOT_ASSESSED |
| Wejście i eksport | Czy zewnętrzne dane mogą spowodować nieprawidłowy stan lub wyciek? | NOT_ASSESSED |
| Zależności | Czy paczki/SDK mają zweryfikowane wersje, licencje i pochodzenie? | NOT_ASSESSED |
| Poufność i prywatność | Czy dane trafiają wyłącznie do uprawnionych odbiorców? | NOT_ASSESSED |
| Odporność | Czy przerwanie procesu, sieci lub urządzenia pozostawia spójne dane? | NOT_ASSESSED |
| Publikacja | Czy pakiet, log i artefakt wydania nie ujawniają prywatnych informacji? | NOT_ASSESSED |

Przed przetwarzaniem danych rzeczywistych i przed wydaniem przeprowadź ocenę adekwatną do konkretnej aplikacji. Wpisz wyniki testów oraz ryzyka rezydualne do PR i powiąż z [SECURITY.md](../../SECURITY.md) i [Prywatnością](../privacy.md). Nie uznawaj listy kontrolnej za zakończony audyt.
