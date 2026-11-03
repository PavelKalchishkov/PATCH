# Deploying PATCH on Railway

The project is ready for Railway: `railway.json` holds the start command, `requirements.txt` the
packages and `.python-version` the Python version. Everything secret comes from Railway's
**Variables**, never from the code.

## 1. Put the code on GitHub (recommended)

Railway redeploys automatically on every push. From the project folder:

```bash
git init
git add .
git commit -m "PATCH: ready for Railway"
```

Create an **empty private** repository on GitHub, then push to it (GitHub shows the two commands).
`.gitignore` keeps `.env` (your passwords), `media/`, `sent_emails/` and `.venv/` out of git.

> Without GitHub: install the Railway CLI and run `railway up` in this folder instead.

## 2. Create the Railway project

1. On [railway.com](https://railway.com) → **New Project** → **Deploy from GitHub repo** → pick the repository.
2. In the same project: **+ Create** → **Database** → **PostgreSQL**.
3. Open the web service → **Settings** → **Networking** → **Generate Domain**. You get
   `something.up.railway.app` with HTTPS (needed for the camera and location on phones).
4. Web service → right-click → **Attach volume**, mount path **`/data`**. Photos are stored
   there, so they survive redeploys.

## 3. Set the variables

Web service → **Variables** → add:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (Railway offers it as a reference) |
| `DJANGO_SECRET_KEY` | a long random value, see below |
| `RESEND_API_KEY` | your Resend API key (step 4) |

Make the secret key on your PC and paste the output:

```bash
.venv/Scripts/python.exe -c "import secrets; print(secrets.token_urlsafe(50))"
```

Railway sets the rest by itself: `RAILWAY_PUBLIC_DOMAIN` (allowed host), `RAILWAY_VOLUME_MOUNT_PATH`
(photos go to `/data/media`), `PORT`, and `RAILWAY_ENVIRONMENT_NAME`, which switches `DEBUG` off.

Optional: `DEFAULT_FROM_EMAIL` (see step 4), `DJANGO_ALLOWED_HOSTS` for a custom domain
(comma-separated).

## 4. Email through Resend

Railway's Trial and Hobby plans **block SMTP**, so Gmail won't work there.

1. Sign up at [resend.com](https://resend.com) → **API Keys** → create one → paste it into
   `RESEND_API_KEY`.
2. Without your own domain, Resend only lets you send **from `onboarding@resend.dev` to the
   address you signed up with**. That's enough to test verification on your own account.
3. To email everyone: in Resend **Domains** → add a domain you own → add the DNS records it shows →
   then set `DEFAULT_FROM_EMAIL` to e.g. `PATCH <no-reply@yourdomain.bg>`.

If sending fails, the site says so ("couldn't be sent") instead of pretending it worked.

## 5. Deploy and create your admin

Railway builds and starts automatically. On every start it runs, in order: database migrations,
`collectstatic`, loading the damage catalog (`seed_patch --catalog-only`, which creates **no**
demo accounts), then `gunicorn`.

Create your administrator once the first deploy is green. Install the
[Railway CLI](https://docs.railway.com/guides/cli), then in the project folder:

```bash
railway login
```
```bash
railway link
```
```bash
railway ssh
```

That opens a terminal inside the running app. There, run:

```bash
python manage.py createsuperuser
```

It asks for email, name and password. Sign in on the site with them.

## 6. Check it works

- Open the domain: the home page and the map load.
- Register a test citizen with the email you used for Resend → open the link in the email.
- On a phone: **Report damage** → the camera opens → take a photo → it's pinned on the map.

## Things to know

- **Costs:** the Trial is a one-time $5 credit for 30 days; trial data is deleted 30 days after
  it runs out. Hobby is $5/month including $5 of usage.
- **Photos** are served by Django from the volume. Fine for testing; a busy site would move them to
  object storage (S3, Cloudflare R2).
- **Your local data stays local.** The online site starts empty apart from the damage catalog.
  Copying it over is possible with `pg_dump`/`pg_restore` plus the `media/` folder.
- **Logs:** web service → **Deployments** → **View logs**. Errors show up there.
- **Street autofill** uses OpenStreetMap's free Nominatim service, fine for testing; heavy use needs
  a self-hosted or paid geocoder.
