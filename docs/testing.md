# Testy i dowody

**Walidacja szkieletu:** zainstaluj zależności w izolowanym środowisku i uruchom:

```bash
python -m pip install -r requirements-ci.txt
python scripts/validate_repository.py --phase scaffold
python -m unittest discover -s tests -v
```

Walidator sprawdza JSON Schema Draft 2020-12, format `date-time` przykładowego zdarzenia syntetycznego, zgodność metadanych, autorstwo oraz wybrane sygnatury sekretów i ryzykowne ścieżki. Skaner nie zastępuje audytu prywatności ani badania rzeczywistych danych. Walidacja strukturalna jest niezależna od testów sprzętowych.

**Hierarchy dowodów:** test strukturalny, jednostkowy, kontraktowy, integracyjny, instalacyjny, kompatybilności oraz walidacja fizycznego urządzenia (gdy dotyczy). Test na emulatorze nie jest dowodem walidacji fizycznej. Dla każdego raportu zapisz exact SHA, runtime, środowisko, wersje, parametry, wynik i ograniczenia. `NOT_RUN` nie znaczy `PASS`.

Testy wykonuj w izolowanym środowisku, z minimalnymi uprawnieniami i bez ujawniania sekretów. Wydanie jest odrębną czynnością, patrz [Wydania](releases.md).
