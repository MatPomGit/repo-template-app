# Dokumentacja architektury

Źródłem krótkiego opisu systemu jest [ARCHITECTURE.md](../../ARCHITECTURE.md). Tutaj przechowujemy rozdzielone szczegóły **rzeczywiście istniejącej aplikacji**, bez powielania całego opisu.

- [Komponenty i interfejsy](components.md) obejmują własność kodu, granice modułów i zależności.
- [Przepływy danych](data-flow.md) opisują źródła, odbiorców, obszary zaufania i retencję.
- [Środowiska i wdrożenie](deployment.md) odróżniają build, instalację i weryfikację działania.
- [ADR](../adr/README.md) przechowują uzasadnienia konkretnych decyzji.
- [Model zagrożeń](../security/threat-model.md) rozdziela ryzyka od potwierdzonych kontroli.

**Etap scaffold:** dokumenty są mapą zagadnień, a nie opisem gotowej implementacji. Przy pierwszym module zastąp opisy planistyczne faktami, referencjami do kodu i testów. Usuń nieaktualne elementy zamiast tworzyć nowe kopie sekcji.

Standard aktualizacji i budżety znaków: [Dokumentacja](../documentation.md).
