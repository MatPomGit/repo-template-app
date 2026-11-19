# Wydania i dowody dopuszczenia

Samo uzupełnienie `config/release-gate.json` wartościami `true` **nie dowodzi wykonania testów**. Wzorzec pozostaje zablokowany w stanie scaffold. Podstawowy CI **nie publikuje** paczek ani nie wykonuje `--phase release`.

Po wdrożeniu faktycznej aplikacji, testów oraz zatwierdzeniu wydania:

1. Zbuduj artefakt dla dokładnego `HEAD`; utrwal raport testów oraz sumę SHA-256 artefaktu.
2. Utwórz **nieśledzony** `outputs/release-evidence.json` według `config/release-gate.json` (ze ścieżkami `test_report_path`, `release_artifact_path`, `release_artifact_sha256` oraz `tested_commit_sha`). Dowody trzymaj poza historią Git, żeby nie powstało cykliczne uzależnienie SHA commita od wartości pola SHA w tym samym commicie.
3. Zapisz raport `outputs/test-report.json` z kluczami `tested_commit_sha`, `status: "passed"` i obiektem `checks`, w którym `unit`, `contract`, `installation`, `dependencies`, `compatibility`, `privacy` mają stan `"passed"` tylko po faktycznych pomiarach.
4. Uruchom:

```bash
python scripts/validate_repository.py --phase release --evidence outputs/release-evidence.json
```

Walidator wymaga zgodności SHA raportu z `HEAD`, czystego stanu śledzonych plików, istnienia artefaktu i zgodności obliczonego SHA-256, rzeczywistego tekstu `LICENSE`, właściwego SPDX oraz oznaczeń przeglądu. Jeśli aplikacja korzysta ze sprzętu, wymaga odrębnego raportu fizycznej weryfikacji. **Nie weryfikuje to niezależnie wiarygodności podpisów lub tożsamości zatwierdzającego**; decyzja właściciela pozostaje oddzielną bramką.

Publikacja Releases, pakietów i Pages wymaga odrębnego zatwierdzenia, oceny licencji i kosztów. Registry: npm/Maven/NuGet/GHCR w GitHub Packages; Python wheel w GitHub Releases lub osobno zatwierdzonym indeksie; Unity UPM po wersjonowanym URL Git. APK/EXE przez Releases po kwalifikacji. Nie przypisuj fikcyjnych DOI.
