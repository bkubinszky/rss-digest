# Mock data for testing without consuming any API tokens.
# Used when MOCK_MODE = True in config.py.

MOCK_ANALYZED_ITEMS = [
    {
        "title": "OpenAI stellt neues Sprachmodell vor",
        "source": "TechCrunch",
        "link": "https://techcrunch.com/mock-article-1",
        "score": 9,
        "summary": "OpenAI hat ein neues Sprachmodell angekündigt, das bisherige Benchmarks deutlich übertrifft und speziell für den Einsatz in Unternehmensanwendungen optimiert wurde."
    },
    {
        "title": "Österreichische Koalitionsverhandlungen stocken",
        "source": "Der Standard",
        "link": "https://derstandard.at/mock-article-2",
        "score": 8,
        "summary": "Die Koalitionsverhandlungen in Wien geraten ins Stocken, nachdem sich die Parteien in Budgetfragen nicht einigen konnten. Politische Beobachter rechnen mit einer Verlängerung der Gespräche."
    },
    {
        "title": "Europäische KI-Regulierung tritt in Kraft",
        "source": "Euractiv",
        "link": "https://euractiv.com/mock-article-3",
        "score": 8,
        "summary": "Der EU AI Act tritt offiziell in Kraft und stellt neue Anforderungen an Anbieter von Hochrisiko-KI-Systemen. Unternehmen haben 24 Monate Zeit, sich anzupassen."
    },
    {
        "title": "Novo Nordisk meldet starke Quartalsergebnisse",
        "source": "Financial Times",
        "link": "https://ft.com/mock-article-4",
        "score": 7,
        "summary": "Novo Nordisk übertrifft die Erwartungen der Analysten mit einem starken Quartalsergebnis, angetrieben durch die anhaltend hohe Nachfrage nach Ozempic und Wegovy."
    },
    {
        "title": "Groq kündigt neue LPU-Generation an",
        "source": "The Verge",
        "link": "https://theverge.com/mock-article-5",
        "score": 7,
        "summary": "Groq präsentiert die nächste Generation seiner Language Processing Units mit deutlich gesteigerter Inferenzgeschwindigkeit und verbesserter Energieeffizienz."
    },
    {
        "title": "No-Code-Tools gewinnen im DACH-Markt an Bedeutung",
        "source": "t3n",
        "link": "https://t3n.de/mock-article-6",
        "score": 6,
        "summary": "Eine neue Studie zeigt, dass No-Code- und Low-Code-Plattformen im DACH-Raum stark wachsen, insbesondere bei kleinen und mittelständischen Unternehmen."
    },
    {
        "title": "Ungarn blockiert erneut EU-Beschluss",
        "source": "Politico Europe",
        "link": "https://politico.eu/mock-article-7",
        "score": 6,
        "summary": "Ungarn hat erneut einen EU-Ratsbeschluss blockiert und damit die Spannungen zwischen Budapest und Brüssel weiter verschärft."
    },
]

MOCK_DEDUPED_ITEMS = [
    {
        "title": "OpenAI stellt neues Sprachmodell vor",
        "score": 9,
        "summary": "OpenAI hat ein neues Sprachmodell angekündigt, das bisherige Benchmarks deutlich übertrifft und speziell für den Einsatz in Unternehmensanwendungen optimiert wurde.",
        "links": [
            {"source": "TechCrunch", "url": "https://techcrunch.com/mock-article-1"},
            {"source": "The Verge", "url": "https://theverge.com/mock-article-1b"},
        ]
    },
    {
        "title": "Österreichische Koalitionsverhandlungen stocken",
        "score": 8,
        "summary": "Die Koalitionsverhandlungen in Wien geraten ins Stocken, nachdem sich die Parteien in Budgetfragen nicht einigen konnten. Politische Beobachter rechnen mit einer Verlängerung der Gespräche.",
        "links": [
            {"source": "Der Standard", "url": "https://derstandard.at/mock-article-2"}
        ]
    },
    {
        "title": "Europäische KI-Regulierung tritt in Kraft",
        "score": 8,
        "summary": "Der EU AI Act tritt offiziell in Kraft und stellt neue Anforderungen an Anbieter von Hochrisiko-KI-Systemen. Unternehmen haben 24 Monate Zeit, sich anzupassen.",
        "links": [
            {"source": "Euractiv", "url": "https://euractiv.com/mock-article-3"}
        ]
    },
    {
        "title": "Novo Nordisk meldet starke Quartalsergebnisse",
        "score": 7,
        "summary": "Novo Nordisk übertrifft die Erwartungen der Analysten mit einem starken Quartalsergebnis, angetrieben durch die anhaltend hohe Nachfrage nach Ozempic und Wegovy.",
        "links": [
            {"source": "Financial Times", "url": "https://ft.com/mock-article-4"}
        ]
    },
    {
        "title": "Groq kündigt neue LPU-Generation an",
        "score": 7,
        "summary": "Groq präsentiert die nächste Generation seiner Language Processing Units mit deutlich gesteigerter Inferenzgeschwindigkeit und verbesserter Energieeffizienz.",
        "links": [
            {"source": "The Verge", "url": "https://theverge.com/mock-article-5"}
        ]
    },
    {
        "title": "No-Code-Tools gewinnen im DACH-Markt an Bedeutung",
        "score": 6,
        "summary": "Eine neue Studie zeigt, dass No-Code- und Low-Code-Plattformen im DACH-Raum stark wachsen, insbesondere bei kleinen und mittelständischen Unternehmen.",
        "links": [
            {"source": "t3n", "url": "https://t3n.de/mock-article-6"}
        ]
    },
    {
        "title": "Ungarn blockiert erneut EU-Beschluss",
        "score": 6,
        "summary": "Ungarn hat erneut einen EU-Ratsbeschluss blockiert und damit die Spannungen zwischen Budapest und Brüssel weiter verschärft.",
        "links": [
            {"source": "Politico Europe", "url": "https://politico.eu/mock-article-7"}
        ]
    },
]
