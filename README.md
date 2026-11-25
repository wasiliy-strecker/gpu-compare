# GPU Compare — Benchmarking Local LLMs on Cloud GPUs

Vergleiche lokale Gemma-3-Modelle auf unterschiedlichen NVIDIA-GPUs. Wähle eine Karte aus dem Vast.ai-Angebot und schicke dieselbe Prompt-Suite an Ollama. Der Messbericht zeigt Tokens pro Sekunde, Zeit bis zur ersten Ausgabe, Antwortdauer und VRAM-Spitze zusammen mit GPU, Modelldigest und Quantisierung.

[GPU Compare auf AWS öffnen](https://dkvxgcdy40zyv.cloudfront.net) · [API-Dokumentation](https://dkvxgcdy40zyv.cloudfront.net/api/docs)

Die öffentliche Demo läuft in AWS Stockholm. Mit **Angebote laden** siehst du aktuelle Vast.ai-Angebote mit GPU-Modell, VRAM und Stundenpreis. GPU-Mieten sind gesperrt. Der Vergleich zeigt Ergebnisse, sobald die ersten echten Hardwareläufe abgeschlossen sind.

## Lokal starten

Mit Docker und Docker Compose ab 2.24:

```sh
docker compose up --build -d
```

[GPU Compare öffnen](http://localhost:5180) · [Lokale API](http://localhost:5180/api/docs)

Die lokale Demo startet ohne Schlüssel. Mit **Angebote laden** lässt sich der Verbindungsstatus prüfen. Solange keine echten Läufe vorliegen, bleibt der Vergleich leer. PostgreSQL und der lokale S3/SQS-Emulator laufen in eigenen Containern. Zum Beenden genügt `docker compose down`.

## Messungen und Betrieb

Der Standardlauf schließt einen Warm-up aus und misst drei Runden mit fünf festen Prompts. Für einen GPU-Vergleich zwei Karten nacheinander mit demselben Modell, derselben Quantisierung und demselben Protokoll testen. Modell-Download und Ladezeit sind separat ausgewiesen. Öffentliche Sitzungen verwenden synthetische Prompts. Eigene Texte erfordern eine Operator-Anmeldung.

[Architektur und Messprotokoll](docs/ARCHITECTURE.md) · [AWS-Betrieb und Hardwaretest](docs/AWS.md)

## Entwicklung

```sh
python3 scripts/init_env.py
uv sync --frozen
docker compose up -d --wait db aws
uv run python -m gpu_compare.bootstrap
uv run pytest
uv run ruff check backend scripts tests
npm --prefix frontend ci
npm --prefix frontend run build
```

Die Browserprüfungen verwenden Playwright gegen die laufende lokale Anwendung. Provider-Antworten für Fehlerfälle und Vergleichstests existieren ausschließlich in den Tests.
