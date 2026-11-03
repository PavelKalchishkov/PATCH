"""Copy translations from bg_translations.py into the Bulgarian .po file.

Usage (from the project root):
    python manage.py makemessages -l bg --ignore=.venv --ignore=_*
    python locale/fill_bg.py
    python manage.py compilemessages -l bg
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bg_translations import BG  # noqa: E402

PO = HERE / "bg" / "LC_MESSAGES" / "django.po"


def unquote(block):
    return "".join(re.findall(r'^"(.*)"$', block, flags=re.M)).encode("utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8")


def quote(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\n") + '"'


def field(entry, name):
    m = re.search(rf'^{re.escape(name)} ((?:".*"\n?)+)', entry, flags=re.M)
    return unquote(m.group(1)) if m else None


def main():
    text = PO.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = re.sub(r'"Plural-Forms: .*\n"', r'"Plural-Forms: nplurals=2; plural=(n != 1);\n"', text)
    entries = text.split("\n\n")
    missing = []
    for i, entry in enumerate(entries):
        msgid = field(entry, "msgid")
        if not msgid:
            # The header is marked fuzzy by makemessages; gettext would then ignore its charset.
            entries[i] = re.sub(r"^#, fuzzy\n", "", entry, flags=re.M)
            continue
        ctx = field(entry, "msgctxt")
        key = (ctx, msgid) if ctx else msgid
        value = BG.get(key)
        if value is None:
            missing.append(key)
            continue
        # Our translation replaces any guess gettext made, so drop the fuzzy flag.
        entry = re.sub(r"^#, fuzzy\n", "", entry, flags=re.M)
        entry = re.sub(r"^#, fuzzy, ", "#, ", entry, flags=re.M)
        entry = re.sub(r"^#\| .*\n", "", entry, flags=re.M)
        if field(entry, "msgid_plural") is not None:
            one, many = value
            entry = re.sub(r'^msgstr\[0\] (?:".*"\n?)+', f"msgstr[0] {quote(one)}\n", entry, flags=re.M)
            entry = re.sub(r'^msgstr\[1\] (?:".*"\n?)+', f"msgstr[1] {quote(many)}", entry, flags=re.M)
        else:
            entry = re.sub(r'^msgstr (?:".*"\n?)+', f"msgstr {quote(value)}", entry, flags=re.M)
        entries[i] = entry.rstrip("\n")
    PO.write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    if missing:
        print("Missing translations:")
        for key in missing:
            print("  ", repr(key))
        sys.exit(1)
    print("All strings translated.")


if __name__ == "__main__":
    main()
