# PATCH — Road Inspector & Registry

A web app for reporting road damage. Citizens photograph damage, inspectors verify it,
contractors repair it, and everyone can follow progress on a map. The interface is in
Bulgarian by default, with an English switch (`BG | EN`).

Built with Django 6.1, Python 3.12 and PostgreSQL.

## Requirements

- **Python 3.12**
- **PostgreSQL** (any recent version) running locally
- Git

## Run it locally

### 1. Get the code and install the packages

```bash
git clone https://github.com/PavelKalchishkov/PATCH.git
cd PATCH
python -m venv .venv
```

Activate the virtual environment:

- Windows: `.venv\Scripts\activate`
- macOS / Linux: `source .venv/bin/activate`

```bash
pip install -r requirements.txt
```

### 2. Create the database

Create an empty PostgreSQL database called `PATCH`, for example with `psql` or pgAdmin:

```sql
CREATE DATABASE "PATCH";
```

### 3. Create a `.env` file

In the project folder, create a file called `.env`. The app reads it on startup, and git ignores it.
At minimum, set your PostgreSQL password:

```env
DB_PASSWORD=your-postgres-password
```

Optional settings (the defaults are shown):

| Variable | Default | Purpose |
| --- | --- | --- |
| `DB_NAME` | `PATCH` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |
| `EMAIL_HOST_USER` | — | Gmail address used to send emails |
| `GMAIL_PASSWORD` | — | Gmail app password for that address |

Without the email settings, emails are not sent. They are saved as files in `sent_emails/`
instead, and the profile page shows the verification link directly.

### 4. Set up the tables and demo data

```bash
python manage.py migrate
python manage.py seed_patch
```

`seed_patch` loads the damage catalog and four demo accounts:

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@patch.local` | `admin12345` |
| Inspector | `inspector@patch.local` | `inspector123` |
| Citizen | `citizen@patch.local` | `citizen123` |
| Contractor | `contractor@patch.local` | `contractor123` |

These passwords are public, so only use the demo accounts locally. On a real server,
run `python manage.py seed_patch --catalog-only`.

### 5. Start the server

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000>.

## Good to know

- **Reporting needs a camera and location.** Browsers only allow these on `localhost` or over
  HTTPS. On your computer, `http://127.0.0.1:8000` works. A phone opening your computer's
  local IP over plain HTTP won't get the camera. To test on a phone, use the deployed site or
  an HTTPS tunnel.
- **Uploaded photos** go to `media/`, which git ignores.
- **Django admin** is at `/admin/` (log in with the admin account).
- **Error page previews** are at `/errors/<code>/` (for example `/errors/404/`) while `DEBUG` is on.
- **Damage detection and face/number-plate blurring are placeholders**, not real models.
  They run in a background thread after each report. To run any queued jobs by hand:
  `python manage.py process_vision_jobs`.

## Translations

Bulgarian strings live in `locale/bg_translations.py`. After changing texts (requires GNU gettext):

```bash
python manage.py makemessages -l bg --ignore=.venv --ignore=_* --ignore=sent_emails --ignore=staticfiles
python locale/fill_bg.py
python manage.py compilemessages -l bg --ignore=.venv
```

`fill_bg.py` lists any strings that still have no translation.

## Project layout

| Folder | What's in it |
| --- | --- |
| `PATCH/` | Settings, URLs, error pages |
| `accounts/` | Users, roles, sign-up, email verification |
| `reports/` | Damage reports, confirmations, votes, anti-spam, photo quality checks |
| `damages/` | Damage catalog, detections, bill of quantities |
| `repairs/` | Repair tasks and their photos |
| `vision/` | Placeholder damage detection and privacy blur |
| `templates/` | HTML templates |
| `static/css/app.css` | All styles |
| `locale/` | Bulgarian translations |

## Deploying

The app runs on Railway. See [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md) for the full steps.
