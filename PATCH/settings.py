import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(path):
    """Read KEY=VALUE lines from a local .env file into the environment (real env vars win)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        os.environ.setdefault(key, value.strip().strip("'\""))


_load_env_file(BASE_DIR / ".env")

def _env_flag(name, default):
    value = os.environ.get(name)
    return default if value is None else value.strip().lower() in ("1", "true", "yes", "on")


# On Railway (or any server) everything comes from environment variables; on a developer
# machine with no such variables the defaults below keep the local setup working as before.
ON_RAILWAY = bool(os.environ.get("RAILWAY_ENVIRONMENT_NAME") or os.environ.get("RAILWAY_ENVIRONMENT"))
DEBUG = _env_flag("DJANGO_DEBUG", default=not ON_RAILWAY)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("Set DJANGO_SECRET_KEY: a long random value, kept secret.")
    SECRET_KEY = "django-insecure-local-development-only"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
ALLOWED_HOSTS += [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]
if os.environ.get("RAILWAY_PUBLIC_DOMAIN"):
    ALLOWED_HOSTS.append(os.environ["RAILWAY_PUBLIC_DOMAIN"])
# Forms posted from the public https address must be trusted for CSRF.
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h not in ("127.0.0.1", "localhost")]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "accounts",
    "reports",
    "damages",
    "repairs",
    "vision",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serves the collected CSS/JS files efficiently when DEBUG is off.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "PATCH.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.pending_role_requests",
            ],
        },
    },
]

WSGI_APPLICATION = "PATCH.wsgi.application"

def _database_from_url(url):
    """Django settings for a postgres:// URL, such as the DATABASE_URL Railway provides."""
    parts = urlparse(url)
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parts.path.lstrip("/")),
        "USER": unquote(parts.username or ""),
        "PASSWORD": unquote(parts.password or ""),
        "HOST": parts.hostname or "",
        "PORT": str(parts.port or 5432),
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
    }


if os.environ.get("DATABASE_URL"):
    DATABASES = {"default": _database_from_url(os.environ["DATABASE_URL"])}
else:
    # Local PostgreSQL; the password lives in .env as DB_PASSWORD.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "PATCH"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "bg"
LANGUAGES = [
    ("bg", "Български"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Sofia"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Uploaded photos must survive redeploys, so on Railway they go on the attached volume.
MEDIA_URL = "media/"
if os.environ.get("MEDIA_ROOT"):
    MEDIA_ROOT = Path(os.environ["MEDIA_ROOT"])
elif os.environ.get("RAILWAY_VOLUME_MOUNT_PATH"):
    MEDIA_ROOT = Path(os.environ["RAILWAY_VOLUME_MOUNT_PATH"]) / "media"
else:
    MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CSRF_FAILURE_VIEW = "PATCH.errors.csrf_failure"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

if not DEBUG:
    # Railway ends HTTPS at its proxy and forwards plain HTTP; this header says the original was HTTPS.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Errors and warnings go to the console, which Railway shows in its deploy logs.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
# Email, in order of preference:
#  1. RESEND_API_KEY set: send through Resend's HTTPS API (works on Railway's Hobby plan,
#     which blocks SMTP).
#  2. GMAIL_PASSWORD/EMAIL_HOST_PASSWORD and EMAIL_HOST_USER set: send through Gmail SMTP
#     (fine locally and on Railway Pro).
#  3. Neither: save emails as files in sent_emails/; the profile page shows the link instead,
#     so the site never claims to have emailed anyone.
_RESEND_KEY = os.environ.get("RESEND_API_KEY")
_EMAIL_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD") or os.environ.get("GMAIL_PASSWORD")
_EMAIL_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_SENDS_REAL_MAIL = bool(_RESEND_KEY or (_EMAIL_PASSWORD and _EMAIL_USER))
if _RESEND_KEY:
    # Without your own domain verified in Resend, only its test sender works.
    DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "PATCH <onboarding@resend.dev>")
    MAILERS = {
        "default": {
            "BACKEND": "accounts.email_backends.ResendEmailBackend",
            "OPTIONS": {"api_key": _RESEND_KEY},
        },
    }
elif EMAIL_SENDS_REAL_MAIL:
    DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", f"PATCH <{_EMAIL_USER}>")
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "OPTIONS": {
                "host": os.environ.get("EMAIL_HOST", "smtp.gmail.com"),
                "port": int(os.environ.get("EMAIL_PORT", "587")),
                "username": _EMAIL_USER,
                "password": _EMAIL_PASSWORD,
                "use_tls": _env_flag("EMAIL_USE_TLS", default=True),
                "timeout": 15,
            },
        },
    }
else:
    DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "PATCH <no-reply@patch.local>")
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.filebased.EmailBackend",
            "OPTIONS": {"file_path": BASE_DIR / "sent_emails"},
        },
    }
