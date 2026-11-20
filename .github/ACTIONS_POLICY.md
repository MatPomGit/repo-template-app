# Polityka GitHub Actions

Dla publicznych repozytoriów `app-*` **dopuszcza się GitHub-hosted runners** (np. `ubuntu-latest`) do krótkich, bezpiecznych testów `pull_request` i `push`. Nie ma obowiązku używania runnerów lokalnych. Zanim dodasz CI, sprawdź limity, naliczanie kosztów, uprawnienia oraz izolację środowiska; nie ponosimy dodatkowych wydatków bez autoryzacji.

Szablon zawiera `.github/workflows/quality.yml`: w publicznym repo na GitHub-hosted runner uruchamia instalację przypiętych zależności walidatora, `python scripts/validate_repository.py --phase scaffold`, walidację i budowę MkDocs bez publikacji oraz `python -m unittest discover -s tests -v`. Workflow używa wyłącznie uprawnień `contents: read` i nie wydaje pakietów. Dopiero wynik faktycznego uruchomienia można traktować jako dowód PASS.

Dla niezaufanych PR ustaw `permissions: contents: read` i nie przekazuj sekretów. Nie stosuj uprzywilejowanego `pull_request_target` do wykonywania kodu z forków; nie uruchamiaj niezweryfikowanych zmian na stałych, zaufanych runnerach. Sprzętowe i uprzywilejowane testy wymagają osobnego, autoryzowanego trybu; bez takiego testu status to `NOT_RUN`.

Wydawanie pakietów i publikacja Pages są osobnymi, jawnie zatwierdzonymi operacjami. Zobacz [audyt szablonu](../reviews/2026-11-19-template-audit.md).

## Wymagana reguła ochrony `main`

Przed uznaniem szablonu za gotowy do integracji właściciel musi skonfigurować regułę (Settings → Rules → Rulesets) dla gałęzi domyślnej: **pull request wymagany przed scaleniem**, **minimum jedno zatwierdzenie od innej tożsamości niż autor**, **wymagany status check `Validate scaffold and security`** z workflow `Template quality`, blokowanie usuwania i non-fast-forward. Należy ograniczyć `bypass_mode=always` do zatwierdzonych wyjątków i unikać samodzielnego omijania kontroli przez automatyzacje. Przed włączeniem required checks potwierdź dokładną nazwę checka i jego dostępność na gałęzi.

Weryfikacja administracyjna wymaga negatywnego testu odrzuconego scalenia PR z niezaliczonym/niewykonanym CI oraz bez zatwierdzenia. Sam plik YAML, zielony workflow i zatwierdzenie przez tego samego autora **nie są egzekwowaniem ochrony**. Jeśli plan lub uprawnienia uniemożliwiają poprawną konfigurację, odnotuj `GATE_UNENFORCED / HOLD`; nie oznaczaj bramki jako zakończonej. Zmiana ustawień GitHub nie może być zastąpiona commitem w repozytorium.
