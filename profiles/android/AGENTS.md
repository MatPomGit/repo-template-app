# Agent: profil Android

Stosuj nadrzędny [AGENTS.md](../../AGENTS.md), [procedurę](../../.github/AGENT_WORKFLOW.md) oraz lokalny [README](README.md). Ten profil dotyczy tylko zmian w aplikacji Android.

Przed implementacją ustal Kotlin/Java, wersję Android SDK/Gradle, `minSdk` i `targetSdk`, uprawnienia kamera/BLE/sensory oraz politykę danych. Sprawdzaj rzeczywiście obecne polecenia Gradle i pliki lock, bez wymyślania zadań builda. Test emulatora nie jest testem fizycznego urządzenia. Nie publikuj APK/AAB ani nie podpisuj aplikacji bez osobnej zgody, odpowiedniej licencji, integralnego artefaktu i raportu testów. Zapisz statusy `NOT_RUN` dla niedostępnego SDK lub urządzenia.
