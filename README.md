# REPLACE_APP_TITLE

**Rodzaj:** `app-*` (nie `msc-*`) · **Etap:** scaffold · **Status pomiarowy:** NOT_VERIFIED.  
**Autor podstawowy:** Mateusz Pomianek; współautorzy opcjonalnie po potwierdzeniu wkładu.

## Funkcja i odbiorcy

REPLACE: zdefiniuj pojedynczą funkcję aplikacji, odbiorców, środowiska wykonania i granicę odpowiedzialności. Aplikacja nie jest artykułem naukowym.

## Integracja

Interfejsy i formaty danych: [docs/contracts.md](docs/contracts.md). Aparatura: [docs/hardware.md](docs/hardware.md).
Programy badawcze i projekty `msc-*` instalują określone wydanie, nigdy nie kopiują całego źródła.

## Stan

`config/component.json` określa docelową platformę i transport danych; `config/release-gate.json` blokuje wydanie do zakończenia testów.

## Walidacja szkieletu

```bash
python -m pip install -r requirements-ci.txt
python scripts/validate_repository.py --phase scaffold
python -m unittest discover -s tests -v
# Po skonfigurowaniu aplikacji można wykonać smoke test CLI:
python src/example_cli.py --output outputs/example.synthetic.json
```

Konfiguracja metadanych: `python scripts/init_app.py --help`. Wzorcowe CLI `src/example_cli.py` emituje wyłącznie zdarzenie syntetyczne; nie jest aplikacją produkcyjną ani adapterem sprzętu.

Agenci pracują zgodnie z [AGENTS.md](AGENTS.md), [procedurą](docs/agent-workflow.md) i lokalną instrukcją wybranego profilu. Sam dokument nie nadaje dostępu do produkcji.

Rozpocznij od [TEMPLATE_SETUP.md](TEMPLATE_SETUP.md). Strona Pages jest opcjonalna i nie jest bazą danych.

## Audyt wzorca i CI

Zobacz [niezależny audyt z 2026-11-19](reviews/2026-11-19-template-audit.md) i plan napraw P0–P2. Repozytoria publiczne mogą korzystać z bezpiecznych GitHub-hosted runners. Podstawowy workflow `.github/workflows/quality.yml` uruchamia walidację i testy, ale nie publikuje pakietów. Kontrolę wydania i ograniczenia dowodowe opisano w [docs/releases.md](docs/releases.md).
