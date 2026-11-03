"""Send email through Resend's HTTPS API.

Railway's Trial and Hobby plans block outgoing SMTP, so Gmail can't be used there; Resend
works over ordinary HTTPS. Configured in settings.MAILERS when RESEND_API_KEY is set.
"""
import json
import urllib.request

from django.core.mail.backends.base import BaseEmailBackend

RESEND_URL = "https://api.resend.com/emails"


class ResendEmailBackend(BaseEmailBackend):
    def __init__(self, *, api_key=None, timeout=15, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.timeout = timeout

    def send_messages(self, email_messages):
        sent = 0
        for message in email_messages:
            payload = {
                "from": message.from_email,
                "to": list(message.to),
                "subject": message.subject,
                "text": message.body,
            }
            if message.cc:
                payload["cc"] = list(message.cc)
            if message.bcc:
                payload["bcc"] = list(message.bcc)
            if message.reply_to:
                payload["reply_to"] = list(message.reply_to)
            request = urllib.request.Request(
                RESEND_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "PATCH-road-inspector/1.0",
                },
                method="POST",
            )
            # urllib raises (an OSError subclass) on any non-2xx answer, e.g. a bad key or sender;
            # accounts.verification turns that into "couldn't be sent" for the user.
            with urllib.request.urlopen(request, timeout=self.timeout):
                sent += 1
        return sent
