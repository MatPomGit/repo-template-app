# Utworzenie repozytorium `app-*`

To **szkielet**, nie działająca aplikacja ani biblioteka. Skopiuj jako osobne repo, nie jako podfolder innego szablonu.

1. Stwórz repozytorium `app-<temat>` i skopiuj pliki (także ukryte `.github`, `.gitignore`). Samo skopiowanie plików nie ustawia flagi GitHub Template.
2. Zaktualizuj `config/component.json`, `PROJECT_STATE.yaml`, README, `CITATION.cff`, licencję i SECURITY.md. W `CITATION.cff` zawsze zachowaj Mateusza Pomianka jako autora, a inne osoby dodawaj wyłącznie po potwierdzeniu rzeczywistego wkładu. Nie twórz fałszywych licencji ani testów.
3. Wybierz właściwe dokumenty z `profiles/`, nie kopiuj wszystkich stosów technologicznych do kodu produkcyjnego.
4. Uruchom `python scripts/validate_repository.py --phase scaffold` oraz `python -m unittest discover -s tests -v`.
5. Dodaj kod i testy; przygotuj API/CLI, kompatybilność i odbiorców. Wykonaj prawdziwe testy na docelowym środowisku.
6. Uzupełnij `config/release-gate.json` dowodami i uruchom `--phase release`, a potem niezależny przegląd. `release` nie publikowałoby niczego samo.
7. Dopiero po zaakceptowaniu sposobu dystrybucji publikuj package/release/Pages. Dowody powiąż z dokładnym SHA.

GitHub Template repository kopiuje początkowe pliki, ale późniejszych zmian nie propaguje do potomnych repo. Research Autopilot powinien osobno kontrolować `template_version` i aktualność kontraktów.

## Autorstwo a własność praw

Mateusz Pomianek jest obowiązkowym autorem oprogramowania w repozytoriach utworzonych z tego wzorca. Dodatkowi współautorzy są dopuszczalni po potwierdzeniu wkładu i uzgodnieniu kolejności w metadanych. Autorstwo w `CITATION.cff`, własność praw/afiliacja oraz tożsamość autora poszczególnych commitów nie są tym samym.

## GitHub Actions i środowisko testowe

W repozytoriach publicznych dopuszczone są GitHub-hosted runners do odizolowanych, bezpiecznych testów na PR i push. Nie wymagaj lokalnej maszyny dla zwykłej walidacji. Przestrzegaj limitów, minimalnych uprawnień i zakazu niezatwierdzonych wydatków. Dla prywatnych repozytoriów wybór runnera wymaga osobnego sprawdzenia poufności i kosztów. Niezaufany kod nie może mieć dostępu do sekretów ani uprzywilejowanych zasobów. Szczegóły i niewdrożone kontrole: [audyt](reviews/2026-11-19-template-audit.md).
