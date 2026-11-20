# Agent: profil Unity

Stosuj nadrzędny [AGENTS.md](../../AGENTS.md), [procedurę](../../.github/AGENT_WORKFLOW.md) oraz lokalny [README](README.md).

Przed zmianą ustal wersję Unity Editora, `Packages/manifest.json`, `packages-lock.json`, render pipeline, platformę kompilacji oraz dostępne urządzenia XR. Nie kopiuj kodu bibliotek UPM: przypinaj wersję lub commit. Zachowaj `Assets/`, `Packages/`, `ProjectSettings/`; nie commituj katalogów wygenerowanych `Library/`, `Temp/`, `Logs/`. Dowód kompilacji Editor nie oznacza poprawności buildu Android/Quest ani działania kontrolera i śledzenia wzroku. Bez urządzenia lub uprawnień oznacz `NOT_RUN`.
