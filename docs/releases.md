# Wydawanie aplikacji `app-*`

**Stan szablonu: SCAFFOLD / NOT_RELEASED.** Zmiana kodu, zielony CI, poprawny `release-evidence.json` ani automatyczny `PASS` walidatora nie stanowią autoryzacji wydania. Wydanie aplikacji i osobna publikacja GitHub Pages mają **odrębne bramki**.

## 1. Wersjonowanie i tożsamość wydania

- Wersja oprogramowania w `config/component.json:version` podlega **SemVer 2.0.0**: `MAJOR` dla niezgodnych zmian kontraktu/API, `MINOR` dla zgodnych funkcji, `PATCH` dla zgodnych poprawek. Wydania testowe oznacz np. `1.2.0-rc.1`; metadane build nie zmieniają kolejności wersji.
- `template_version` oznacza wersję wzorca i nie jest numerem wersji gotowej aplikacji. `CITATION.cff`, `PROJECT_STATE.yaml:source_version`, changelog, nazwa artefaktu i tag `vX.Y.Z` muszą być spójne.
- Każdy tag wydania wiąż z **jednym exact commit SHA**, identyfikatorem przebiegu CI i niezmiennym digestem SHA-256 każdego artefaktu. Nie przenoś opublikowanych tagów na inny commit; poprawki wydawaj jako nową wersję.
- Zachowaj w `CITATION.cff` autorów według potwierdzonego wkładu. Autorstwo naukowe, własność kodu i licencja dystrybucyjna są odrębnymi zagadnieniami. Nie przypisuj DOI bez realnej rejestracji.

## 2. Bramki jakości i bezpieczeństwa

**R1 — definicja produktu:** aplikacja ma rzeczywistą implementację, uruchamialny instalator/CLI, instrukcję użycia, licencję z prawami dystrybucji, zweryfikowaną obsługę danych i kontakt bezpieczeństwa. Szkielet `src/example_cli.py` z danymi syntetycznymi nie wystarcza.

**R2 — dowody techniczne:** pełny test unit/contract/integration, uruchomienie z czystej instalacji, kompatybilność platform, skan zależności i licencji, kontrola prywatności, krytyczne testy negatywne oraz test artefaktu wynikowego. Testy muszą dotyczyć exact SHA i **tej samej wersji pakietu, która zostanie opublikowana**. Wymagane obowiązkowe CI i odpowiednia, niezależna recenzja PR; jeżeli ruleset nie wymusza testów/review, oznacz **GATE_UNENFORCED**, a nie „zatwierdzone”.

**R3 — decyzja wydawnicza:** osobne, jawne upoważnienie właściciela do konkretnej wersji, kanału dystrybucji, zakresu publikacji i ewentualnych kosztów. Ocenę uprawnień, licencji i danych przeprowadza człowiek; żadne pole `publisher_approved: true` samo w sobie nie jest wiarygodnym podpisem.

## 3. Macierz artefaktów

| Profil | Typowy artefakt | Minimalne dowody oprócz CI |
| --- | --- | --- |
| Desktop Windows/Linux | EXE/MSI, AppImage/DEB/RPM lub ZIP | Instalacja i odinstalowanie na wspieranych systemach, zależności runtime, podpis/kontrola pochodzenia, alerty AV |
| Android | APK/AAB | `minSdk`/`targetSdk`, uprawnienia, instalacja na urządzeniu, podpis pakietu, kompatybilność |
| Web | Zweryfikowany build frontendu i opcjonalny oddzielny backend | Testy przeglądarek, CSP, zależności zewnętrzne, separacja sekretów i backendu, ochrona danych |
| Unity/XR | UPM package lub build docelowy | Wersja Unity, pluginy, platformy, realne urządzenia, zgodność wejścia/wyjścia, licencje zasobów |
| Aparatura / sensory | Paczka aplikacji wraz z adapterami | SDK/firmware, identyfikacja urządzeń, kalibracja, częstotliwość i synchronizacja, walidacja fizyczna i bezpieczeństwo |

Stany `NOT_RUN`, `UNAVAILABLE`, `NOT_APPLICABLE` i `PASS` są różne; każde pominięcie wymaga uzasadnienia. Test emulatora nie zastępuje testu urządzenia. Nie udostępniaj surowych danych, numerów seryjnych, prywatnych ścieżek, sekretów ani logów zawierających dane uczestników w wydaniach.

## 4. Dowody, integralność i pochodzenie

1. W zaufanym, odizolowanym procesie dla exact SHA zbuduj i przetestuj **finalne** artefakty. Zapisz środowisko, runtime, wersje zależności, parametry budowania, numer runu i zanonimizowane wyniki. Ustal sumy SHA-256 artefaktów.
2. Utwórz **nieśledzony** `outputs/test-report.json`: `schema_version: 1`, `tested_commit_sha`, `status: "passed"` i kontrole `unit`, `contract`, `installation`, `dependencies`, `compatibility`, `privacy` o wynikach `passed` wyłącznie po wykonaniu.
3. Utwórz `outputs/release-evidence.json` na podstawie `config/release-gate.json`, dodając `schema_version: 1`, `tested_commit_sha`, `test_report_path`, `test_report_sha256`, `release_artifact_path` i `release_artifact_sha256`, a także rzeczywiście potwierdzone pozostałe pola.
4. Wykonaj `python scripts/validate_repository.py --phase release --evidence outputs/release-evidence.json`. Wynik **`PASS: app release-evidence consistency (NOT publication approval)`** sprawdza wyłącznie **spójność lokalnych deklaracji i plików**. Mimo SHA-256 nie potwierdza źródła raportu ani tożsamości osoby zatwierdzającej.
5. Dla rzeczywistego wydania **oddzielnie** zweryfikuj zaufane pochodzenie artefaktu (np. GitHub artifact attestation z uprawnionego joba i sprawdzenie podpisu/claims, repozytorium, workflow, commit SHA oraz digestu), status wymaganych checks i recenzenta z innego konta. Brak zaufanej atestacji lub mechanizmu autoryzacji oznacz `PROVENANCE_UNVERIFIED` i **HOLD**, nie wymyślaj dowodów. Nie ufaj polom w samodzielnie wygenerowanym JSON jako atestacji.
6. Dopiero po osobnym zatwierdzeniu utwórz tag, GitHub Release i właściwy kanał dystrybucji. Udostępnij sumy, minimalny changelog, kompatybilność, datę, SHA, instrukcje aktualizacji i znane ograniczenia. Sprawdź tożsamość pobranego artefaktu.

**Uwaga techniczna:** testy pozytywne z atrapą `git_revision` są wyłącznie testami walidatora; nie stanowią rzeczywistego dowodu uruchomienia procesu release. Repozytorium szablonu nie wydaje pakietów i nie posiada automatycznego workflow publikacji.

## 5. Dystrybucja, bezpieczeństwo i rollback

- GitHub Releases służy do zatwierdzonych instalatorów, archiwów i sum; Android wymaga również kontroli podpisu i kanału dystrybucji. Python, npm/Maven/NuGet, UPM lub GHCR dobieraj dopiero do **rzeczywistego** profilu aplikacji, nie do samej nazwy repo.
- Zweryfikuj licencje aplikacji i wszystkich dołączonych składników, prawa do danych/treningu/bodźców, SBOM tam, gdzie adekwatne, zgodność ABI/API, sekrety w paczkach, CVE i zasady aktualizacji. Skrót SHA-256 nie zastępuje podpisu ani zaufanej atestacji.
- Dla niezgodnej aktualizacji przygotuj migrację, backup i test odtworzenia. Dla wdrożeń usługowych rozdziel release artefaktu od deployu; określ rollback wersji i danych, odpowiedzialnego operatora oraz kryteria zdrowia.
- Przy błędzie po publikacji zatrzymaj dystrybucję, oznacz wydanie jako wycofane/superseded, poinformuj odbiorców, utwórz poprawione wydanie pod **nową wersją** i zachowaj ślad decyzji. Nie nadpisuj potajemnie istniejących artefaktów/tagów.
- GitHub Pages podlega [odrębnej polityce](pages.md): dopuszczone źródła `pages/`, publiczny build `site/`, niezależny przegląd widoczności i osobna decyzja o wdrożeniu.

## 6. Lista decyzji wydawniczej

Przed wydaniem odpowiedz dowodowo: czy wersja i SHA są zgodne, CI zostało wymuszone, raporty pochodzą z zaufanego procesu, artefakty są podpisane/zweryfikowane, instalacja i kompatybilność rzeczywiście przeszły, dane i licencje są dopuszczone, aktualny runbook i kontakt bezpieczeństwa działają, rollback przetestowano, a właściciel wyraźnie zatwierdził **ten** kanał dystrybucji? Jeśli którekolwiek wymagane kryterium nie jest spełnione, status pozostaje **HOLD**.
