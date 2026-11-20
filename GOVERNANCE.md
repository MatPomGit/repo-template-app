# Zarządzanie projektem

**Etap:** szablon, bez oddelegowanych maintainerów. Po utworzeniu konkretnej aplikacji zaktualizuj podział odpowiedzialności i zatwierdzanie zmian.

## Role i decyzje

Właściciel repozytorium odpowiada za uprawnienia, licencję, decyzję o wydaniu oraz publikację. Autorzy zmian odpowiadają za implementację, regresję i rzetelne raportowanie. Recenzenci oceniają finalny diff i dowody, nie nadają sobie sami uprawnień. Udział w projekcie ani wzmianka w `CITATION.cff` nie tworzy prawa administracyjnego.

Zwykłe zmiany przechodzą przez Issue, gałąź roboczą, PR i kontrole wskazane w [AGENTS.md](AGENTS.md). Zmiany API, zależności, bezpieczeństwa oraz publikacja wymagają dodatkowych bramek określonych w [AGENTS.md](AGENTS.md) i [SECURITY.md](SECURITY.md). Zasada minimalnych uprawnień obowiązuje także agentów.

## Zmiany architektury i decyzje

Istotną decyzję utrwal w [ADR](docs/adr/README.md) z kontekstem, alternatywami, konsekwencjami i statusem. Nie dopisuj dublujących się decyzji do wielu dokumentów. Zmiana przyjętej decyzji wymaga nowego ADR z odwołaniem do poprzedniego. Rozstrzygaj konflikt w aktualnym PR, nie traktuj automatycznie wygenerowanej rekomendacji jako zgody.

## Wydania i spory

Scalenie PR nie jest wydaniem ani wdrożeniem. Właściciel zatwierdza zakres publikacji i jej konsekwencje, a testy i zabezpieczenia platformy pozostają obowiązujące. Kwestie organizacyjne zgłaszaj w publicznych Issues bez danych wrażliwych, bezpieczeństwo prywatnie według [SECURITY.md](SECURITY.md). Nie zakładaj obecności moderatorów, kanałów komunikacji ani automatyzacji, których projekt nie skonfigurował.
