# Utworzenie repozytorium `app-*`

To **szkielet**, nie działająca aplikacja ani biblioteka. Skopiuj jako osobne repo, nie jako podfolder innego szablonu.

1. Stwórz repozytorium `app-<temat>` i skopiuj pliki (także ukryte `.github`, `.gitignore`). Samo skopiowanie plików nie ustawia flagi GitHub Template.
2. Uruchom `python scripts/init_app.py --id app-przyklad --title "Tytuł aplikacji" --repo-url https://github.com/OWNER/app-przyklad --platform desktop` po instalacji zależności `requirements-ci.txt`, następnie zweryfikuj `config/component.json`, `PROJECT_STATE.yaml`, README, `CITATION.cff`, licencję i SECURITY.md. W `CITATION.cff` zawsze zachowaj Mateusza Pomianka jako autora, a inne osoby dodawaj wyłącznie po potwierdzeniu rzeczywistego wkładu. Nie twórz fałszywych licencji ani testów.
3. Wybierz właściwe dokumenty z `profiles/`, przeczytaj odpowiednie `profiles/<platform>/AGENTS.md` i `README.md`, nie kopiuj wszystkich stosów technologicznych do kodu produkcyjnego. Dla pracy agentów stosuj [główny kontrakt](AGENTS.md) i [procedurę](.github/AGENT_WORKFLOW.md).
4. W izolowanym środowisku zainstaluj `python -m pip install -r requirements-ci.txt`, a następnie uruchom `python scripts/validate_repository.py --phase scaffold`, `python scripts/validate_documentation.py` oraz `python -m unittest discover -s tests -v`.
5. Dodaj kod i testy; przygotuj API/CLI, kompatybilność i odbiorców. **Przy pierwszej implementacji** uzupełnij [ARCHITECTURE.md](ARCHITECTURE.md), [komponenty](docs/architecture/components.md), [przepływy](docs/architecture/data-flow.md), [model zagrożeń](docs/security/threat-model.md) i odpowiednie [ADR](docs/adr/README.md) zgodnie z [limitem znaków](docs/documentation.md). Dla wybranego stosu opisz faktycznie istniejące moduły, testy i uprawnienia, nie pozostawiaj statusu scaffold przy funkcji już zaimplementowanej. Wykonaj prawdziwe testy na docelowym środowisku.
6. Po rzeczywistych testach zbudowanego artefaktu przygotuj nieśledzony plik dowodów `outputs/release-evidence.json`, powiąż raport i SHA-256 z dokładnym HEAD, a następnie uruchom `python scripts/validate_repository.py --phase release --evidence outputs/release-evidence.json`. Patrz `docs/releases.md`. Sama deklaracja `true` nie stanowi dowodu; walidacja niczego nie publikuje.
7. Dla strony publicznej umieszczaj materiały wyłącznie w `pages/` i dodaj każdy zasób do `config/pages-policy.json`. Nie publikuj `docs/`, instrukcji agentowych ani notatek redakcyjnych. Uruchom `python scripts/validate_pages.py` i sprawdź widoczność witryny, szczególnie w repozytorium prywatnym. Zobacz [politykę Pages](docs/pages.md). Przed zewnętrzną publikacją ustaw realny prywatny kanał zgłaszania podatności w [SECURITY.md](SECURITY.md), sprawdź zasady [Code of Conduct](CODE_OF_CONDUCT.md), [wsparcie](SUPPORT.md), [odpowiedzialność](GOVERNANCE.md), operacyjny [runbook](docs/operations/runbook.md) i faktyczny stan [ADR bezpieczeństwa](docs/adr/0002-security-boundaries.md). Dopiero po zaakceptowaniu sposobu dystrybucji publikuj package/release/Pages. Dowody powiąż z dokładnym SHA.

Po inicjalizacji sprawdź `python src/example_cli.py --output outputs/example.synthetic.json`. To syntetyczny smoke test referencyjnego CLI, nie rzeczywista walidacja docelowej aplikacji. `init_app.py` nie przyznaje licencji, nie zmienia statusu wydania i nie dodaje rzekomych współautorów.

GitHub Template repository kopiuje początkowe pliki, ale późniejszych zmian nie propaguje do potomnych repo. Research Autopilot powinien osobno kontrolować `template_version` i aktualność kontraktów.

## Autorstwo a własność praw

Mateusz Pomianek jest obowiązkowym autorem oprogramowania w repozytoriach utworzonych z tego wzorca. Dodatkowi współautorzy są dopuszczalni po potwierdzeniu wkładu i uzgodnieniu kolejności w metadanych. Autorstwo w `CITATION.cff`, własność praw/afiliacja oraz tożsamość autora poszczególnych commitów nie są tym samym.

## GitHub Actions i środowisko testowe

W repozytoriach publicznych dopuszczone są GitHub-hosted runners do odizolowanych, bezpiecznych testów na PR i push. Nie wymagaj lokalnej maszyny dla zwykłej walidacji. Przestrzegaj limitów, minimalnych uprawnień i zakazu niezatwierdzonych wydatków. Dla prywatnych repozytoriów wybór runnera wymaga osobnego sprawdzenia poufności i kosztów. Niezaufany kod nie może mieć dostępu do sekretów ani uprzywilejowanych zasobów. Aktualny stan zabezpieczeń i pozostające ryzyka: [audyt](reviews/2026-11-19-template-audit.md).

## Procedury publikacji i wydania

Dla **każdej** aplikacji potomnej używaj [wytycznych GitHub Pages](docs/pages.md) (osobny katalog `pages/`, allowlisty źródła i renderu, dostępność, prywatność oraz niezależne zatwierdzenie) i [procedury release](docs/releases.md) (SemVer, macierz platform, testy exact SHA, pochodzenie artefaktu, osobna autoryzacja i rollback). Bramka Pages **nie jest** bramką wydania aplikacji. Brak wymuszonego CI/review w ustawieniach `main` oznacza blokadę integracji do czasu naprawy zasad repozytorium.
