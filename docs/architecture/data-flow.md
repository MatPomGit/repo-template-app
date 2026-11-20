# Przepływy i granice danych

**Status: NOT_ASSESSED.** Wzorzec zawiera jedynie schemat syntetycznego zdarzenia; nie przetwarza danych uczestników.

## Opis wymagany dla aplikacji

Po dodaniu pierwszej ścieżki I/O udokumentuj:

1. Źródło danych, podstawę pozyskania, identyfikator urządzenia lub sesji i format wejściowy.
2. Granicę zaufania pomiędzy użytkownikiem, procesem aplikacji, lokalnym dyskiem, siecią, serwerem i usługą zewnętrzną, o ile występują.
3. Kolejne przekształcenia, walidację, jednostki, znaczniki czasu, retencję i odbiorców.
4. Transport, szyfrowanie, autoryzację, zakres zgód i proces usuwania danych.
5. Kontrakt eksportu wraz z wersją oraz dowodem testu bez danych rzeczywistych.

Nie przypisuj gotowości istniejącym jedynie w projekcie przepływom. Jeżeli funkcja jest offline, potwierdź brak ruchu sieciowego w rzeczywistym teście, zamiast zakładać go na podstawie konfiguracji. Dane i metadane uczestników przechowuj poza publicznym repozytorium.

Spójne źródła: [Kontrakty](../contracts.md), [Prywatność](../privacy.md), [Model zagrożeń](../security/threat-model.md).
