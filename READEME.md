DoBuDu - Advanced Discord Bot (AI, Multimedia & Real-time Data)
DoBuDu este un asistent virtual complex dezvoltat pentru platforma Discord, integrand modele de ultima generatie de Inteligenta Artificiala (Gemini 2.0 Flash) si utilitare de procesare media in timp real. Proiectul a fost realizat ca aplicatie practica pentru cursul de Python in cadrul UPB - ETTI de catre studentii Burtea Vlad-Florin ,Dumitrescu Robert-Andrei, Dovleac Gabriel-Dorinel.

Arhitectura Sistemului:
Aplicatia este construita pe o arhitectura asincrona, utilizand libraria discord.py pentru comunicarea de tip WebSocket cu serverele Discord.

Componente principale:

Core Engine: Gestionarea evenimentelor si sincronizarea comenzilor de tip Slash.

AI Context Manager: Un sistem de gestionare a memoriei care stocheaza istoricul conversatiilor intr-un dictionar indexat dupa ID-ul canalului, permitand raspunsuri contextuale.

Media Streamer: Utilizarea yt-dlp pentru extragerea metadatelor si a fluxului audio, trimis catre FFmpeg pentru encodare si redare in Discord Voice.

API Integrator: Module de interogare asincrona (aiohttp) pentru servicii externe: OpenWeather (Vreme) si NewsAPI (Stiri).

Functionalitati:
1. Inteligenta Artificiala cu Memorie (/ask)

    Model: Gemini 2.0 Flash.
    Capabilitati: Retine contextul dialogului, permitand intrebari de urmarire.
    Protectie: Include logica de tip „catch” pentru eroarea 429 (Resource Exhausted), informand utilizatorul despre limitele API-ului.

2. Modul Multimedia (/play, /stop)

    Cautare: Permite cautare directa prin cuvinte cheie sau link-uri YouTube.
    Procesare: Conversie asincrona a fluxului video in audio PCM pentru canalul vocal.

3. Utilitare in Timp Real (/vremea, /stiri)

    Vremea: Returneaza temperatura si conditiile atmosferice in format metric (Celsius).
    Stiri: Filtrare automata a celor mai relevante 3 articole pe subiectul ales, cu link-uri catre surse externe.

Instalare si Configurare Tehnica:

Python 3.12+
FFmpeg (instalat in variabila de mediu PATH)
Librarii necesare:    
    pip install discord.py google-genai yt-dlp python-dotenv aiohttp

Configurarea Variabilelor de Mediu (.env)
Pentru securitate, cheile API nu sunt hard-coded:    
    DISCORD_TOKEN=Token_de_la_Discord_Developer_Portal
    GEMINI_API_KEY=Cheie_Google_AI_Studio_v1_Stable
    WEATHER_API_KEY=Cheie_OpenWeather
    NEWS_API_KEY=Cheie_NewsAPI

Depanare si Optimizare (Debugging):

In timpul dezvoltarii, proiectul a trecut prin mai multe etape de optimizare pentru a rezolva problemele de conectivitate:
Rezolvare Eroare 404: S-a trecut de la versiunea instabila v1beta la endpoint-ul stabil v1 al Google API pentru a elimina eroarea de „Model Not Found”.
Gestionare Rate-Limit: Implementarea unui sistem de avertizare pentru eroarea 429 RESOURCE_EXHAUSTED atunci cand cota gratuita Google este depasita.
Sincronizare Comenzi: Rezolvarea conflictelor de „Ghost Commands” (comenzi duplicate) prin curatarea cache-ului global Discord si re-sincronizarea corecta a CommandTree.  

Structura Proiectului:
DoBuDu/
├── bot.py           # Logica principala si handlerele comenzilor
├── .env             # Cheile API (nu se uploadeaza pe GitHub)
├── requirements.txt # Lista de dependente
└── README.md        # Documentatia tehnica