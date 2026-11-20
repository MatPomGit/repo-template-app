# Topologia uruchomienia i wdrożenia

**Status: NOT_DEPLOYED.** Kopia szablonu nie oznacza uruchomionej usługi.

## Po powstaniu aplikacji

Opisz oddzielnie środowiska develop/test/staging/production (tylko te rzeczywiście stosowane), wymagane runtime, porty, uprawnienia, zależności i lokalizacje konfiguracji. Nie zamieszczaj haseł, pełnych prywatnych ścieżek, adresów uczestników ani tokenów.

Każde wdrożenie powinno mieć identyfikator wydania i commit SHA, plan migracji, kopię zapasową gdy modyfikuje dane, procedurę rollbacku, smoke test, obserwowalne kryteria zdrowia oraz raport wykonania. Instalacja pakietu, działający proces i zweryfikowany przypadek użycia to trzy różne stany.

Zmiany środowisk produkcyjnych muszą respektować rzeczywiste uprawnienia i lokalne polityki hosta. Scalenie PR nie upoważnia do automatycznego restartu usług. Używaj [runbook](../operations/runbook.md), [instalacji](../installation.md) i [wydań](../releases.md).
