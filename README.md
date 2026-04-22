Part 3: Including screenshot of check
# U.S. Air Quality & Weather Explorer

A full-stack Django web application for browsing and analyzing daily air-quality index records from U.S. monitoring stations, with live weather data fetched from the Open-Meteo API.

---

## Group Members

| Name | Student ID |
|------|------------|
| Sofia Bernal| sb22i |
| Aidan Thompson | amt22m |
| Ashley Oliv | |
| | |

---

## Dataset & API

- **Dataset:** [U.S. Air Pollution Dataset](https://www.kaggle.com/datasets/sogun3/uspollution) — Kaggle
- **API:** [Open-Meteo Weather API](https://open-meteo.com/en/docs)

---

## Application Features

- `/` — Homepage with dataset description and navigation
- `/air-quality/` — Paginated list of all air quality records
- `/air-quality/<pk>/` — Detail view for a single record
- `/air-quality/add/` — Create a new air quality record
- `/air-quality/<pk>/edit/` — Update an existing record
- `/air-quality/<pk>/delete/` — Delete a record
- `/weather/` — Paginated list of weather records
- `/analytics/` — Analytics dashboard with charts and summary stats
- `/fetch/` — Staff-only view to trigger live weather data fetch

---

## Setup Instructions

```bash
git clone https://github.com/sofiabernal5/python-project1-group3.git
cd python-project1-group3/project3/mysite
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your SECRET_KEY
python3 manage.py migrate
python3 manage.py seed_data
python3 manage.py runserver
```

---

## Screenshots

### Homepage
![Homepage](screenshots/homepage.png)

### List View
![List View](screenshots/list.png)

### Analytics Dashboard
![Analytics](screenshots/analytics.png)

---

## Deployment Check

<img width="1890" height="498" alt="Screenshot 2026-04-21 at 11 11 11 PM" src="https://github.com/user-attachments/assets/b42c6c9d-ad2b-41f9-a918-f21e8a10c64a" />
