# Zmiany i przegląd

Przed pracą przeczytaj [AGENTS.md](AGENTS.md) i [procedurę agentów](.github/AGENT_WORKFLOW.md). W Issue odnotuj DoR, poziom ryzyka R0-R3 i kryteria akceptacji; w PR potwierdź DoD, aktualny SHA, testy, review oraz decyzje o merge, release i deployment osobno.

Przestrzegaj [Code of Conduct](CODE_OF_CONDUCT.md). Proces decyzji opisuje [GOVERNANCE.md](GOVERNANCE.md); zgłaszanie podatności [SECURITY.md](SECURITY.md); pytania o użytkowanie [SUPPORT.md](SUPPORT.md). Dla zmiany architektury uaktualnij [ARCHITECTURE.md](ARCHITECTURE.md) i właściwy [ADR](docs/adr/README.md). Obowiązują [limity znaków](docs/documentation.md); sprawdź `python scripts/validate_documentation.py`.

Zmiany dotyczące API, formatów danych, protokołów i bezpieczeństwa wymagają testów oraz wpisu w CHANGELOG.md.
Przy PR podaj dokładny SHA, zakres testów i co **nie** zostało zweryfikowane.
Publiczne repozytoria mogą używać GitHub-hosted runners do bezpiecznych, odizolowanych testów CI, z minimalnymi uprawnieniami. Nie generuj dodatkowych kosztów ani nie uruchamiaj automatycznej publikacji bez zgody. Nie udostępniaj sekretów kodowi z niezaufanych PR.
Nie kopiuj implementacji bibliotek i aplikacji; wskazuj wersjonowaną zależność.

Mateusz Pomianek pozostaje co najmniej jednym z autorów oprogramowania wskazanych w `CITATION.cff`; kolejnych współautorów wpisuj po potwierdzeniu wkładu. Autorstwo naukowe/oprogramowania nie oznacza automatycznie autorstwa każdego commita ani własności praw.
