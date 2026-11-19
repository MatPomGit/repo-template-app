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
python scripts/validate_repository.py --phase scaffold
python -m unittest discover -s tests -v
```

Rozpocznij od [TEMPLATE_SETUP.md](TEMPLATE_SETUP.md). Strona Pages jest opcjonalna i nie jest bazą danych.

## Audyt wzorca i CI

Zobacz [niezależny audyt z 2026-11-19](reviews/2026-11-19-template-audit.md) i plan napraw P0–P2. Repozytoria publiczne mogą używać bezpiecznych GitHub-hosted runners do podstawowych testów; sam szablon nie ma jeszcze workflow CI.
