# Testy i dowody

Minimalna hierarchia: walidacja szkieletu, testy jednostkowe, testy kontraktowe, test integracji, czysta instalacja i test docelowego środowiska.
Nie wolno wnioskować o poprawnym działaniu urządzenia z testów syntetycznych lub emulatora.
Każdy raport powinien zawierać środowisko, wersje, commit SHA, parametry, wynik, ograniczenia i identyfikator artefaktu. `NOT_RUN` jest poprawnym statusem, nie błędem logicznym.
Niezaufany PR nie może wykonywać kodu na stałym zaufanym runnerze. Dla publicznych repozytoriów dopuszcza się izolowane GitHub-hosted runners do podstawowego CI, przy minimalnych uprawnieniach i kontroli kosztów. Testy sprzętowe wymagają osobnej autoryzacji; brak rzeczywistej próby to `NOT_RUN`.
