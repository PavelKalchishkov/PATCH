from django.db.models import F

from accounts.models import User


def pending_role_requests(request):
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated and user.is_admin_role):
        return {}
    try:
        count = User.objects.exclude(requested_role="").exclude(requested_role=F("role")).count()
    except Exception:
        # Never let the nav badge break a page, least of all the error page itself.
        return {}
    return {"pending_role_requests": count}
