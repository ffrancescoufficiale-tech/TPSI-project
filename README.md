# TPSI-project
Quiz AI Creator è un'applicazione desktop sviluppata in Python che permette di generare quiz personalizzati sfruttando la potenza dell'intelligenza artificiale. Il progetto è stato realizzato come parte del percorso scolastico per la materia TPSI.

IL TEAM
Francesco Forganni - Team Leader, Sviluppatore, Redattore e Tester

Giacomo Manganaro - Co-sviluppatore

Martin Sansone - Tester e Propositore

Eliana Perrone - Tester e Supporto

Gabriele Cardile - Supporto e Propositore


Requisiti Tecnici

    Python 3.13.0 o superiore

    Librerie: flet, groq, python-dotenv


Installazione e Avvio

    Clona il repository:
    Bash

    git clone https://github.com/ffrancescoufficiale-tech/TPSI-project.git
    cd TPSI-project


2.  **Crea un ambiente virtuale (consigliato):**
    
    python -m venv venv
    source venv/bin/activate  # Su Linux/macOS
    venv\Scripts\activate     # Su Windows
    

3.  **Installa le dipendenze:**
    
    pip install -r requirements.txt
    

4.  **Configura le API Key:**
    *   Copia il file `.env.example` e rinominalo in `.env`.
    *   Inserisci la tua `GROQ_API_KEY` all'interno del file.

5.  **Avvia l'applicazione:**
    
    python main.py
    