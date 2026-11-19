# Polityka GitHub Actions

Dla publicznych repozytoriów `app-*` **dopuszcza się GitHub-hosted runners** (np. `ubuntu-latest`) do krótkich, bezpiecznych testów `pull_request` i `push`. Nie ma obowiązku używania runnerów lokalnych. Zanim dodasz CI, sprawdź limity, naliczanie kosztów, uprawnienia oraz izolację środowiska; nie ponosimy dodatkowych wydatków bez autoryzacji.

Szablon **nie ma jeszcze zdefiniowanych workflowów**. Minimalny planowany zestaw kontroli to `python scripts/validate_repository.py --phase scaffold`, `python -m unittest discover -s tests -v` i walidacja kontraktów. To zalecenie, a nie deklaracja wdrożenia.

Dla niezaufanych PR ustaw `permissions: contents: read` i nie przekazuj sekretów. Nie stosuj uprzywilejowanego `pull_request_target` do wykonywania kodu z forków; nie uruchamiaj niezweryfikowanych zmian na stałych, zaufanych runnerach. Sprzętowe i uprzywilejowane testy wymagają osobnego, autoryzowanego trybu; bez takiego testu status to `NOT_RUN`.

Wydawanie pakietów i publikacja Pages są osobnymi, jawnie zatwierdzonymi operacjami. Zobacz [audyt szablonu](../reviews/2026-11-19-template-audit.md).
