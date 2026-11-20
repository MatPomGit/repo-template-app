# Rejestr decyzji architektonicznych (ADR)

ADR zapisuje **dlaczego** wybrano rozwiązanie i jakie rozważono alternatywy. Nie zastępuje opisu aktualnego kodu w [architekturze](../../ARCHITECTURE.md). Numeracja jest rosnąca i nie jest ponownie używana.

| ADR | Temat | Stan |
| --- | --- | --- |
| [0001](0001-contract.md) | Kanoniczny właściciel komponentu | proposed |
| [0002](0002-security-boundaries.md) | Granice bezpieczeństwa aplikacji | proposed |

Każdy nowy rekord stosuje strukturę: **Kontekst, Status, Decyzja lub propozycja, Alternatywy, Konsekwencje, Dowody, Powiązane kontrakty, Data**. Statusy: `proposed`, `accepted`, `rejected`, `superseded`. Status `proposed` nie daje prawa do produkcyjnej zmiany.

Gdy istnieje akceptowana decyzja, zmiana wymaga następnego ADR z uzasadnieniem, a starszy otrzymuje odsyłacz i `superseded`. Nie twórz ADR dla kosmetycznych zmian; rozstrzygnięcia są istotne, gdy wpływają na bezpieczeństwo, kontrakty, zgodność, platformę albo utrzymanie. Pliki muszą spełniać [budżety znaków](../documentation.md).
