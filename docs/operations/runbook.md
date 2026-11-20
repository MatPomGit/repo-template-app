# Instrukcja operacyjna (runbook)

**Stan: NOT_CONFIGURED.** Ten plik nie opisuje działającego serwisu ani dostępu do hosta.

## Po pierwszym uruchomieniu aplikacji

Podaj zweryfikowane polecenia instalacji, uruchomienia i zatrzymania **jedynie na posiadanym lub zatwierdzonym środowisku**, identyfikator wersji, porty i logi bez danych wrażliwych. Opisz kryteria zdrowia aplikacji, typowe objawy usterek, diagnostykę tylko do odczytu, sposób backupu/odtworzenia, rollback, aktualizację zależności i właściciela kontaktu. Jeśli program jest aplikacją lokalną, nie twórz fikcyjnej procedury usługi systemowej.

Przed każdą operacją modyfikującą środowisko sprawdź uprawnienia, właściwy SHA, izolację, możliwe działania uboczne i dostępność zasobów. Nie przerywaj obliczeń innych osób i nie udostępniaj prywatnych logów. Brak środowiska oznacza `NOT_RUN`.

Zobacz [instalację](../installation.md), [wdrożenie](../architecture/deployment.md), [wydania](../releases.md) i [obsługę incydentów](../security/incident-response.md).
