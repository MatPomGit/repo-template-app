# ADR-0001: kanoniczny właściciel komponentu

**Status:** proposed  
**Data:** 2026-11-19  
**Kategoria:** ownership, compatibility

## Kontekst

Projekt `app-*` powinien przechowywać własny kod i publiczny kontrakt. Odbiorcy `msc-*` i `lib-*` wymagają stabilnych, odtwarzalnych wersji.

## Propozycja decyzji

Repozytorium aplikacji jest właścicielem kodu i kontraktów. Repozytoria manuskryptowe korzystają z wersjonowanych wydań albo przypiętego SHA zamiast kopiować implementację.

## Alternatywy

Kopiowanie źródeł do każdego odbiorcy upraszcza start, ale prowadzi do rozbieżności implementacji i trudnej kontroli bezpieczeństwa.

## Konsekwencje i odbiór

Potrzebne są testy zgodności kontraktów, kontrola wersji zależności i zgodność z [ARCHITECTURE.md](../../ARCHITECTURE.md). `proposed` nie oznacza, że zależności produkcyjne zostały już skonfigurowane. Przed zmianą statusu właściciel weryfikuje realnych odbiorców i akceptuje decyzję.
