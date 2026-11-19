# Unity App (opcjonalne)

Dla projektu Unity ustal wersję Editora, profil Web/Android/Desktop/XR, render pipeline URP lub HDRP, ustawienia jakości i GPU/CPU; dokumentuj realny test builda.
URP jest bazowym wyborem dla Android/Web/Quest 3; HDRP jest rozwiązaniem desktopowym, nie domyślną alternatywą mobilną.
Dodaj sceny i assets pod `Assets/`, `Packages/manifest.json` oraz `Packages/packages-lock.json` i `ProjectSettings/`. Ignoruj `Library/`, `Temp/`, `Logs/`.
Moduły wielokrotnego użytku (np. OptiCore) instaluj jako UPM po tagu/SHA, nie kopiuj `Runtime/` do aplikacji.
