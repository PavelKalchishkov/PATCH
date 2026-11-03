"""Friendly error screens for failed requests and operations."""
from django.shortcuts import render
from django.utils.translation import gettext as _


def error_page(request, code, title, message, status=None, **extra):
    context = {"code": code, "title": title, "message": message, **extra}
    return render(request, "error.html", context, status=status or code)


def bad_request(request, exception=None):
    return error_page(
        request, 400, _("Something was wrong with that request"),
        _("The page couldn't understand what was sent. Go back and try again."),
    )


def permission_denied(request, exception=None):
    return error_page(
        request, 403, _("You don't have access to this page"),
        _("Your account's role can't open this section. If you think it should, ask an administrator."),
    )


def page_not_found(request, exception=None):
    return error_page(
        request, 404, _("Page not found"),
        _("The page or report you're looking for doesn't exist. It may have been deleted, or the link is wrong."),
    )


def server_error(request):
    return error_page(
        request, 500, _("Something went wrong on our side"),
        _("The action didn't go through and nothing was changed. Please try again in a moment."),
    )


def csrf_failure(request, reason=""):
    return error_page(
        request, 403, _("Your form expired"),
        _("For your security, forms expire after a while or when you sign in somewhere else. "
          "Nothing was saved. Reload the page and submit it again."),
        retry_url=request.META.get("HTTP_REFERER") or None,
        retry_label=_("Reload the form"),
    )


def preview(request, code):
    """DEBUG-only: show an error screen, since Django replaces 404/500 with its own pages while DEBUG is on."""
    views = {400: bad_request, 403: permission_denied, 404: page_not_found, 500: server_error}
    if code == 419:
        return csrf_failure(request)
    return views.get(code, page_not_found)(request)
