# Gemeente Rotterdam Voorjaarsnota Dashboard

Een interactief dashboard voor de visualisatie van de Voorjaarsnota 2024 van de Gemeente Rotterdam.

## Lokaal uitvoeren

1. Installeer de vereiste packages:
   ```
   pip install -r requirements.txt
   ```

2. Start de applicatie:
   ```
   python dashboard.py
   ```

3. Open een browser en ga naar http://127.0.0.1:9053/

## Online deployment

### Render.com (Gratis optie)

1. Maak een account aan op [Render.com](https://render.com/)
2. Klik op "New Web Service"
3. Connect je GitHub repository of upload de code direct
4. Stel de volgende opties in:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn dashboard:server`
5. Klik op "Create Web Service"

### Heroku (Betaalde optie)

1. Maak een account aan op [Heroku](https://www.heroku.com/)
2. Installeer de Heroku CLI
3. Login via de terminal:
   ```
   heroku login
   ```
4. Maak een nieuwe app:
   ```
   heroku create rotterdam-dashboard
   ```
5. Push je code naar Heroku:
   ```
   git push heroku main
   ```

### PythonAnywhere (Gratis optie)

1. Maak een account aan op [PythonAnywhere](https://www.pythonanywhere.com/)
2. Upload je bestanden via de Files tab
3. Maak een nieuwe web app via de Web tab
4. Kies voor Flask en configureer de WSGI file om te verwijzen naar `dashboard:server`

## Benodigde bestanden voor deployment

- `dashboard.py`: De hoofdapplicatie
- `requirements.txt`: Lijst met benodigde packages
- `Procfile`: Instructies voor de webserver
- `data/`: Map voor het opslaan van gecachte data
