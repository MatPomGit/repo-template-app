# Niezależny audyt szablonu `repo-template-app`

**Data:** 2026-11-19. **Punkt odniesienia:** `main` @ `7ba3e7078cf7d9fb22a7eee59d5f1f85bf53410d`.  
**Metoda:** statyczny przegląd struktury, dokumentacji, kodu walidatora, testów i ustawień GitHub. Testów ani wdrożenia nie wykonano; opisane ryzyka nie oznaczają potwierdzonych incydentów.  
**Granice:** szablon `app-*` dla niezależnej aplikacji/adaptera; nie jest szablonem manuskryptu `msc-*` ani biblioteki `lib-*`.

## Werdykt

**Ocena orientacyjna: 6,5/10 (osąd ekspercki, nie automatyczny wynik testów).** Projekt rozdziela kod aplikacji od repozytoriów naukowych, opisuje wieloplatformowość i ma konserwatywną bramkę wydania. Główną słabością jest dysproporcja między dobrą dokumentacją a automatycznym dowodzeniem zgodności kontraktów oraz wydania.

| Obszar | Ocena |
| --- | ---: |
| Architektura i separacja repozytoriów | 8/10 |
| Kontrakty i kompatybilność | 7/10 |
| Bezpieczeństwo i prywatność (projekt) | 7/10 |
| Reprodukowalność i wydania | 7/10 |
| Walidacja automatyczna | 4/10 |
| CI i egzekwowanie jakości | 2/10 |
| Onboarding i profile platformowe | 7/10 |
| Integracja z `msc-*` i `lib-*` | 8/10 |

### Potwierdzone zalety

1. Repo ma flagę `is_template=true`, jest publiczne, a katalogi `src/`, `contracts/`, `config/`, `docs/`, `profiles/` i `tests/` rozdzielają odpowiedzialności.
2. `config/release-gate.json` domyślnie blokuje wydanie, a `scripts/validate_repository.py --phase release` wymaga wielu deklaracji zgodności.
3. `contracts/events.schema.json` i `examples/event.synthetic.json` dostarczają punkt wyjścia do kontraktu eksportu. Przykład jest oznaczony jako syntetyczny.
4. Profile `android`, `desktop`, `sensor`, `unity`, `web` są opcjonalne. Nie wymuszają instalacji pięciu stosów technologicznych.
5. Dokumentacja rozróżnia test strukturalny, integracyjny, urządzeniowy oraz `NOT_VERIFIED`; unika przedstawiania testów syntetycznych jako potwierdzonych pomiarów sprzętowych.

## Ustalenia wymagające działań

| ID | Priorytet | Dowód i zagrożenie | Działanie |
| --- | --- | --- | --- |
| A01 | P0 | Brak `.github/workflows/` i uruchomień Actions. `ACTIONS_POLICY.md` zakłada obecnie wyłącznie testy ręczne. | Dodać bezpieczny, bezkosztowy CI dla struktury, kontraktów i testów jednostkowych, z wymaganym statusem PR po ustabilizowaniu. |
| A02 | P0 | Walidator wyłącznie parsuje JSON Schema jako JSON, nie wykonuje walidacji `examples/event.synthetic.json` względem `contracts/events.schema.json`. Sprawdzenie `contract.get("schema_version", 1)` przy braku pola przepuszcza wartość domyślną. | Uruchamiać walidację schematu i przykładów, zestaw testów pozytywnych i negatywnych; jasno rozdzielić wersję schematu od `schema_version` danych. |
| A03 | P0 | `release-gate.json` zawiera wartości logiczne o dowolnie deklarowanym stanie; walidator weryfikuje format `tested_commit_sha` i `release_artifact_sha256`, ale nie ich zgodność z rzeczywistym HEAD lub artefaktem. | Powiązać dowody z rzeczywistym commit SHA, wykonanym testem i checksum artefaktu; bez dowodu oznaczać `NOT_VERIFIED`. |
| A04 | P0 | `LICENSE` może pozostać placeholderem przy deklaracji `license_spdx` w JSON. `.gitignore` nie blokuje `git add -f` ani już śledzonych sekretów. | Skontrolować zgodność licencji z manifestem oraz włączyć skan sekretów i niedozwolonych artefaktów, niezależnie od `.gitignore`. |
| A05 | P1 | `PROJECT_STATE.yaml` jest wymagany, ale walidator nie parsuje jego treści ani nie porównuje z `config/component.json`. | Walidować YAML i zgodność identyfikatora, wersji, typu, statusu wydania oraz właściciela. |
| A06 | P1 | `CITATION.cff` zawiera placeholder `REPLACE_FAMILY/REPLACE_GIVEN`; reguła stałego autora nie jest zapisana w procesie tworzenia projektu. | Wpisać Mateusza Pomianka jako autora podstawowego i dopuszczać zweryfikowanych współautorów; sprawdzać jego obecność w metadanych wydania. |
| A07 | P1 | Brak inicjalizatora, który skonfiguruje identyfikatory, profil aplikacji, URL, metadane i zależności; łatwo pozostawić `REPLACE_*`. | Dodać idempotentną inicjalizację i test generowania aplikacji z wybranym profilem, bez instalacji niepotrzebnych stosów. |
| A08 | P1 | `main-branch-ruleset` blokuje usuwanie i non-fast-forward, lecz nie wymaga CI ani review; dopuszcza obejście przez uprawnioną rolę. | Po wdrożeniu CI wymagać status checks i odpowiedniej recenzji PR, jeśli wspiera to plan i konfiguracja GitHub. |
| A09 | P1 | Profile platformowe są wskazówkami, lecz brak działającego testu aplikacji, instalacji w czystym środowisku i demonstracji integracji konsumenta. | Dostarczyć jeden najmniejszy przykład referencyjny (np. CLI zapisujące zdarzenie syntetyczne) i smoke test; bez pięciu pełnych aplikacji. |
| A10 | P2 | Wersja szablonu `1.0.0` jest zaszyta w walidatorze; brak testów zgodności ewolucji kontraktów i migracji potomnych repo. | Ujednolicić SemVer, CHANGELOG i wymagania migracyjne; rozdzielić wersję szablonu od wersji aplikacji. |
| A11 | P2 | Kontrakt `events.schema.json` ma ogólne `payload`, pola `source` i `event_type` bez ograniczeń, a wymagania dotyczące czasu i jednostek są tylko opisowe. | Wprowadzić wersjonowane profile kontraktowe i testy zgodności tam, gdzie potrzebna jest rzeczywista interoperacyjność; unikać uniwersalnego „wszystko-schema”. |

### Polityki obowiązujące przy stosowaniu szablonu

**Autorstwo.** Mateusz Pomianek jest zawsze co najmniej jednym z autorów oprogramowania w `CITATION.cff` i publikowanych metadanych repozytorium. Współautorów dodaje się wyłącznie po ustaleniu rzeczywistego wkładu i uzgodnieniu autorstwa. Autorstwo, własność praw i autor commita w Git to odrębne pojęcia: nie należy utożsamiać ich automatycznie.

**Runnery.** Publiczne repozytoria `app-*` **mogą** używać GitHub-hosted runners do bezpiecznych, krótkich kontroli `pull_request`/`push`, bez narzucania lokalnych maszyn. Konfiguracja musi uwzględnić limity, uprawnienia i ewentualne opłaty; dodatkowe koszty wymagają zatwierdzenia. Dla prywatnych repo decyzja jest zależna od polityki i poufności. Nigdy nie udostępniać sekretów niezaufanym PR ani nie wykonywać ich kodu z podwyższonymi uprawnieniami; preferować `permissions: contents: read`, izolowane środowisko oraz brak `pull_request_target` do wykonywania kodu z forków. Buildy wymagające sprzętu uruchamiać wyłącznie w zaufanym trybie, z wyraźnym statusem `NOT_RUN` w standardowym CI.

**Oddzielenie odpowiedzialności.** Aplikacja utrzymuje własną implementację, API/CLI, testy, artefakty i dokumentację integracji. Biblioteki i projekty naukowe są zewnętrznymi konsumentami/zależnościami. Nie kopiować między nimi kodu ani nie tworzyć lokalnego systemu orkiestracji.

### Backlog i kryteria akceptacji

#### P0 — przed uznaniem za obowiązkowy wzorzec operacyjny
- [ ] Bezpieczny workflow CI ze stabilnymi testami struktury, kontraktu i regresji; dla repo publicznych GitHub-hosted runner jest dozwolony.
- [ ] Rzeczywiste walidowanie JSON Schema, danych przykładowych i testów negatywnych.
- [ ] Fail-closed release gate powiązany ze SHA, raportami testów, plikiem LICENSE i rzeczywistą sumą SHA-256 artefaktu.
- [ ] Kontrola sekretów, ryzykownej zawartości i praw do wydania.

#### P1 — dla bezpiecznego wdrażania w repo potomnych
- [ ] Parser i walidator `PROJECT_STATE.yaml` oraz zgodności z JSON.
- [ ] Inicjalizacja zachowująca Mateusza Pomianka jako autora i umożliwiająca współautorów.
- [ ] Minimalny uruchamialny przykład aplikacji i smoke test w czystym środowisku.
- [ ] Status CI i przegląd wymagane przed merge do `main`, w zakresie obsługiwanym przez GitHub.

#### P2 — rozszerzenia rozwojowe
- [ ] Wersjonowanie/migracje szablonu, API compatibility tests, opcjonalne profile/plug-iny.

### Scenariusz akceptacyjny

1. Utworzyć testowe repo `app-example` przez `Use this template`, wskazać jeden profil i wypełnić metadane z zachowaniem Mateusza Pomianka; dodać opcjonalnego współautora testowego.
2. Uruchomić CI na GitHub-hosted runner (dla repo publicznego), sprawdzić syntetyczne zdarzenie zgodnie z JSON Schema oraz wywołać kontrolowane błędy.
3. Wykazać, że wydanie jest blokowane przez niespójne SHA, spreparowany checksum, brak raportu testu i placeholder licencji.
4. Potwierdzić, że poprawnie podpisane dowody odnoszą się do dokładnie zbudowanego artefaktu; test sprzętowy pozostaje `NOT_RUN`, dopóki faktycznie go nie wykonano.
5. Sprawdzić działanie wymaganego CI/review dla PR oraz odtworzenie procesu instalacji.

**Zakres obecnego PR:** zapis audytu i planu napraw, spójna polityka autorstwa, dopuszczenie GitHub-hosted runners oraz korekta metadanych wzorcowych. **Nie wdraża:** CI, release gate, inicjalizatora, skanów bezpieczeństwa, przykładów aplikacji, zmian rulesetów lub publikacji. Wszystkie checkboxy pozostają otwarte.

---

## Aktualizacja wdrożeniowa — PR #2 (19.11.2026)

Poniższy status dotyczy zmian w gałęzi PR, nie ich scalenia do main ani niezależnego zatwierdzenia wydania. Pierwotny audyt pozostaje historycznym zapisem ustaleń.

| Ustalenie | Status po PR #2 | Zakres i ograniczenia |
| --- | --- | --- |
| A01 | Częściowo wdrożone | Dodano GitHub-hosted CI dla scaffold i testów; wymagane status checks/review w ruleset main nie zostały skonfigurowane. |
| A02 | Wdrożono kontrole statyczne | JSON Schema Draft 2020-12, przykład syntetyczny, dodatkowe sprawdzenie RFC 3339/UTC, reguły wymaganych pól i testy negatywne. To nie jest test runtime aplikacji. |
| A03 | Częściowo wdrożone | SHA HEAD, raport, obliczenie SHA-256 rzeczywistego artefaktu, czystość śledzonych plików; bez weryfikacji podpisów, tożsamości recenzenta ani pochodzenia raportu z zaufanego systemu. |
| A04 | Częściowo wdrożone | Placeholder licencji blokuje release; wprowadzono kontrolę wybranych wzorców SPDX/tekstu, sygnatur sekretów i zakazanych ścieżek. Nie zastępuje to audytu PII, pełnego skanera sekretów i przeglądu prawnego. |
| A05 | Częściowo wdrożone | Weryfikacja YAML, autora i zgodności PROJECT_STATE.yaml/JSON dla kluczowych pól; bez kompleksowego schematu wszystkich statusów. |
| A06 | Wdrożone wcześniej | Autor podstawowy Mateusz Pomianek w CITATION.cff i dokumentacji; sprawdzany przy walidacji. |
| A07–A11 | Otwarte | Inicjalizator, ruleset, działający przykład aplikacji, migracje i profilowane kontrakty wymagają osobnej implementacji. |

### Weryfikacja zmian

Workflow .github/workflows/quality.yml uruchamia kontrolę scaffold i testy jednostkowe/negatywne na izolowanym GitHub-hosted runner. Bramka release nie jest uruchamiana automatycznie na niezaufanych PR, a domyślny scaffold nadal blokuje wydanie. Do release potrzebne są rzeczywiste dane testowe i artefakt oraz nieśledzony plik dowodowy; demonstracyjne testy w repo są syntetyczne.

Automatyczna walidacja nie poświadcza metodologii, zgodności etycznej ani faktycznego działania urządzenia. Przed scaleniem wymagane są PASS dla bieżącego SHA i recenzja diffu. Przed aktywacją obowiązkowych statusów w ruleset należy zweryfikować stabilność workflow.
