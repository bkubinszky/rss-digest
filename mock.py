# Mock data for testing without consuming any API tokens.
# Used when MOCK_MODE = True in config.py.

MOCK_ANALYZED_ITEMS = [
    {
        "title": "OpenAI Announces New Language Model",
        "source": "TechCrunch",
        "link": "https://techcrunch.com/mock-article-1",
        "score": 9,
        "summary": "OpenAI hat ein neues Sprachmodell angekündigt, das bisherige Benchmarks deutlich übertrifft und speziell für Unternehmensanwendungen optimiert wurde. Die Verfügbarkeit über die API soll im nächsten Quartal erfolgen.",
        "why_it_matters": "Für SaaS-Entwickler bietet dieses Modell eine Möglichkeit, leistungsfähigere KI-Funktionen zu niedrigeren Kosten in bestehende Produkte zu integrieren."
    },
    {
        "title": "EU AI Act Enters Into Force",
        "source": "TechCrunch",
        "link": "https://techcrunch.com/mock-article-2",
        "score": 8,
        "summary": "Der EU AI Act tritt offiziell in Kraft und stellt neue Anforderungen an Anbieter von Hochrisiko-KI-Systemen. Unternehmen haben 24 Monate Zeit, sich anzupassen.",
        "why_it_matters": "DACH-SaaS-Anbieter müssen ihre KI-Produkte auf Konformität prüfen, was Beratungsdienstleistungen und Compliance-Tools zu einer attraktiven Nische macht."
    },
    {
        "title": "Groq Announces Next-Gen LPU",
        "source": "TechCrunch",
        "link": "https://techcrunch.com/mock-article-3",
        "score": 7,
        "summary": "Groq präsentiert die nächste Generation seiner Language Processing Units mit deutlich gesteigerter Inferenzgeschwindigkeit. Die neue Hardware soll Ende des Jahres verfügbar sein.",
        "why_it_matters": "Günstigere und schnellere Inferenz senkt die Betriebskosten für KI-basierte SaaS-Produkte und verbessert die Margen."
    },
    {
        "title": "Austrian Coalition Talks Stall",
        "source": "Der Standard",
        "link": "https://derstandard.at/mock-article-1",
        "score": 8,
        "summary": "Die Koalitionsverhandlungen in Wien geraten ins Stocken, nachdem sich die Parteien in Budgetfragen nicht einigen konnten. Politische Beobachter rechnen mit einer Verlängerung der Gespräche.",
        "why_it_matters": "Politische Unsicherheit in Österreich kann Investitionsentscheidungen im Immobilien- und Finanzbereich kurzfristig beeinflussen."
    },
    {
        "title": "Hungary Blocks EU Council Decision Again",
        "source": "Der Standard",
        "link": "https://derstandard.at/mock-article-2",
        "score": 6,
        "summary": "Ungarn hat erneut einen EU-Ratsbeschluss blockiert und damit die Spannungen zwischen Budapest und Brüssel weiter verschärft. Die Abstimmung betraf die Verlängerung von Sanktionen.",
        "why_it_matters": "Anhaltende politische Instabilität in der CEE-Region schafft Chancen für Analysetools und Informationsprodukte rund um europäische Politik."
    },
    {
        "title": "Novo Nordisk Reports Strong Quarterly Earnings",
        "source": "Financial Times",
        "link": "https://ft.com/mock-article-1",
        "score": 9,
        "summary": "Novo Nordisk übertrifft die Erwartungen der Analysten mit einem starken Quartalsergebnis, angetrieben durch die anhaltend hohe Nachfrage nach Ozempic und Wegovy. Der Aktienkurs stieg nachbörslich um 4%.",
        "why_it_matters": "Starke Fundamentaldaten bestätigen die langfristige Investitionsthese; kurzfristig könnte eine Erholungsrally Gewinne ermöglichen."
    },
    {
        "title": "No-Code Tools Growing Fast in DACH Market",
        "source": "t3n",
        "link": "https://t3n.de/mock-article-1",
        "score": 7,
        "summary": "Eine neue Studie zeigt, dass No-Code- und Low-Code-Plattformen im DACH-Raum stark wachsen, insbesondere bei KMU. Der Markt soll bis 2027 auf 1,2 Mrd. Euro anwachsen.",
        "why_it_matters": "Wachsende Nachfrage nach No-Code-Lösungen im DACH-Markt unterstützt die Validierung eines SaaS-Produkts in dieser Nische."
    },
    {
        "title": "Mistral AI Raises $600M Series B",
        "source": "t3n",
        "link": "https://t3n.de/mock-article-2",
        "score": 6,
        "summary": "Das französische KI-Unternehmen Mistral AI hat eine Series-B-Finanzierungsrunde über 600 Millionen Euro abgeschlossen. Die Bewertung liegt nun bei über 6 Milliarden Euro.",
        "why_it_matters": "Europäische KI-Investitionen signalisieren wachsendes institutionelles Vertrauen in nicht-amerikanische LLM-Anbieter als Basis für eigene Produkte."
    },
]

MOCK_DEDUPED_ITEMS = [
    {
        "title": "OpenAI Announces New Language Model",
        "score": 9,
        "summary": "OpenAI hat ein neues Sprachmodell angekündigt, das bisherige Benchmarks deutlich übertrifft und speziell für Unternehmensanwendungen optimiert wurde. Die Verfügbarkeit über die API soll im nächsten Quartal erfolgen.",
        "why_it_matters": "Für SaaS-Entwickler bietet dieses Modell eine Möglichkeit, leistungsfähigere KI-Funktionen zu niedrigeren Kosten in bestehende Produkte zu integrieren.",
        "links": [
            {"source": "TechCrunch", "url": "https://techcrunch.com/mock-article-1"},
            {"source": "The Verge",  "url": "https://theverge.com/mock-article-1b"},
        ]
    },
    {
        "title": "EU AI Act Enters Into Force",
        "score": 8,
        "summary": "Der EU AI Act tritt offiziell in Kraft und stellt neue Anforderungen an Anbieter von Hochrisiko-KI-Systemen. Unternehmen haben 24 Monate Zeit, sich anzupassen.",
        "why_it_matters": "DACH-SaaS-Anbieter müssen ihre KI-Produkte auf Konformität prüfen, was Beratungsdienstleistungen und Compliance-Tools zu einer attraktiven Nische macht.",
        "links": [
            {"source": "TechCrunch", "url": "https://techcrunch.com/mock-article-2"}
        ]
    },
    {
        "title": "Groq Announces Next-Gen LPU",
        "score": 7,
        "summary": "Groq präsentiert die nächste Generation seiner Language Processing Units mit deutlich gesteigerter Inferenzgeschwindigkeit. Die neue Hardware soll Ende des Jahres verfügbar sein.",
        "why_it_matters": "Günstigere und schnellere Inferenz senkt die Betriebskosten für KI-basierte SaaS-Produkte und verbessert die Margen.",
        "links": [
            {"source": "TechCrunch", "url": "https://techcrunch.com/mock-article-3"}
        ]
    },
    {
        "title": "Austrian Coalition Talks Stall",
        "score": 8,
        "summary": "Die Koalitionsverhandlungen in Wien geraten ins Stocken, nachdem sich die Parteien in Budgetfragen nicht einigen konnten. Politische Beobachter rechnen mit einer Verlängerung der Gespräche.",
        "why_it_matters": "Politische Unsicherheit in Österreich kann Investitionsentscheidungen im Immobilien- und Finanzbereich kurzfristig beeinflussen.",
        "links": [
            {"source": "Der Standard", "url": "https://derstandard.at/mock-article-1"}
        ]
    },
    {
        "title": "Hungary Blocks EU Council Decision Again",
        "score": 6,
        "summary": "Ungarn hat erneut einen EU-Ratsbeschluss blockiert und damit die Spannungen zwischen Budapest und Brüssel weiter verschärft.",
        "why_it_matters": "Anhaltende politische Instabilität in der CEE-Region schafft Chancen für Analysetools und Informationsprodukte rund um europäische Politik.",
        "links": [
            {"source": "Der Standard", "url": "https://derstandard.at/mock-article-2"}
        ]
    },
    {
        "title": "Novo Nordisk Reports Strong Quarterly Earnings",
        "score": 9,
        "summary": "Novo Nordisk übertrifft die Erwartungen der Analysten mit einem starken Quartalsergebnis, angetrieben durch die anhaltend hohe Nachfrage nach Ozempic und Wegovy.",
        "why_it_matters": "Starke Fundamentaldaten bestätigen die langfristige Investitionsthese; kurzfristig könnte eine Erholungsrally Gewinne ermöglichen.",
        "links": [
            {"source": "Financial Times", "url": "https://ft.com/mock-article-1"}
        ]
    },
    {
        "title": "No-Code Tools Growing Fast in DACH Market",
        "score": 7,
        "summary": "Eine neue Studie zeigt, dass No-Code- und Low-Code-Plattformen im DACH-Raum stark wachsen, insbesondere bei KMU.",
        "why_it_matters": "Wachsende Nachfrage nach No-Code-Lösungen im DACH-Markt unterstützt die Validierung eines SaaS-Produkts in dieser Nische.",
        "links": [
            {"source": "t3n", "url": "https://t3n.de/mock-article-1"}
        ]
    },
    {
        "title": "Mistral AI Raises $600M Series B",
        "score": 6,
        "summary": "Das französische KI-Unternehmen Mistral AI hat eine Series-B-Finanzierungsrunde über 600 Millionen Euro abgeschlossen.",
        "why_it_matters": "Europäische KI-Investitionen signalisieren wachsendes institutionelles Vertrauen in nicht-amerikanische LLM-Anbieter als Basis für eigene Produkte.",
        "links": [
            {"source": "t3n", "url": "https://t3n.de/mock-article-2"}
        ]
    },
]
