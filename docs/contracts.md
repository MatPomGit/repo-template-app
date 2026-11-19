# Interfejsy i eksport danych

Zdefiniuj transport: lokalny plik, CLI, REST/WebSocket/LSL, Bluetooth/USB, UPM lub plugin; nie obiecuj wsparcia bez testów.
Dla pomiarów ustal monotoniczny timestamp źródłowy i UTC wall-clock, jednostki, układ współrzędnych, status kalibracji, etykietę jakości, identyfikator sesji (pseudonim) i wersję kontraktu.
Syntetyczny przykład `examples/event.synthetic.json` waliduje tylko format, nie działanie sprzętu.
Nie zapisuj surowych danych osobowych w logach i nie kopiuj kart urządzeń z Research Autopilot.
