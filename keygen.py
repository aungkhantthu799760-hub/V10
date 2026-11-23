# ============================================================
# keygen.py — Kavin Scanner Key Generator (Admin Tool) FINAL
#   ✓ Same key format as original
#   ✓ Generate / List / Revoke-Delete / Unbind Device
#   ✓ Compatible with license.py (validate / bind / device lock)
# ============================================================
import os
import time
import random
import string
import calendar
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.prompt import IntPrompt
from rich.table import Table
from rich.box import ROUNDED, DOUBLE

from license import load_keys, save_keys, KEY_PREFIX

console = Console()


# ============================================================
# HELPERS
# ============================================================
def _add_months(dt, months):
    year = dt.year + (dt.month - 1 + months) // 12
    month = (dt.month - 1 + months) % 12 + 1
    max_day = calendar.monthrange(year, month)[1]
    day = min(dt.day, max_day)
    return dt.replace(year=year, month=month, day=day)


def _fmt_remaining(expiry_iso):
    try:
        expiry = datetime.fromisoformat(expiry_iso)
        remain = expiry - datetime.now()
        secs = int(remain.total_seconds())
        if secs <= 0:
            return "EXPIRED", True
        if secs < 3600:
            return f"{secs // 60}m", False
        if secs < 86400:
            return f"{secs // 3600}h", False
        return f"{remain.days}d", False
    except Exception:
        return "N/A", False


# ============================================================
# KEY GENERATION
# ============================================================
def generate_unique_key():
    keys = load_keys()
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(200):
        raw = "".join(random.choices(alphabet, k=16))
        formatted = f"{raw[0:4]}-{raw[4:8]}-{raw[8:12]}-{raw[12:16]}"
        full_key = f"{KEY_PREFIX}-{formatted}"
        if full_key not in keys:
            return full_key
    while True:
        raw = "".join(random.choices(alphabet, k=16))
        full_key = f"{KEY_PREFIX}-{raw[0:4]}-{raw[4:8]}-{raw[8:12]}-{raw[12:16]}"
        if full_key not in keys:
            return full_key


def create_key(expiry_dt, max_uses=1, note=""):
    keys = load_keys()
    new_key = generate_unique_key()
    safe_max_uses = max(1, int(max_uses)) if str(max_uses).isdigit() else 1
    keys[new_key] = {
        "created": datetime.now().isoformat(),
        "expiry": expiry_dt.isoformat(),
        "max_uses": safe_max_uses,
        "used": 0,
        "note": str(note or "").strip(),
        "bound_device": None,
        "bound_at": None,
        "last_fingerprint": None,
        "active": True,
        "last_used": None,
    }
    save_keys(keys)
    return new_key


# ============================================================
# MENU 1 — GENERATE
# ============================================================
def generate_key_menu():
    os.system("clear")
    console.print(Panel(Align.center(Text("KEY GENERATOR", style="default")),
                        border_style="default", box=DOUBLE, height=3))
    console.print("\n  Select Duration:\n")
    console.print("  1. 1 Hour")
    console.print("  2. 6 Hours")
    console.print("  3. 12 Hours")
    console.print("  4. 1 Day")
    console.print("  5. 7 Days")
    console.print("  6. 30 Days (1 Month)")
    console.print("  7. 90 Days (3 Months)")
    console.print("  8. 1 Year")
    console.print("  9. Custom Expiry\n")

    try:
        print("  ➜ ", end="", flush=True)
        c = input().strip()
    except (KeyboardInterrupt, EOFError):
        return

    now = datetime.now()
    if c == "1":
        expiry = now + timedelta(hours=1)
    elif c == "2":
        expiry = now + timedelta(hours=6)
    elif c == "3":
        expiry = now + timedelta(hours=12)
    elif c == "4":
        expiry = now + timedelta(days=1)
    elif c == "5":
        expiry = now + timedelta(days=7)
    elif c == "6":
        expiry = _add_months(now, 1)
    elif c == "7":
        expiry = _add_months(now, 3)
    elif c == "8":
        expiry = _add_months(now, 12)
    elif c == "9":
        try:
            console.print("\n  Custom Expiry:\n")
            y = IntPrompt.ask("  Year (YYYY)", default=now.year)
            m = IntPrompt.ask("  Month (1-12)", default=now.month)
            d = IntPrompt.ask("  Day (1-31)", default=now.day)
            h = IntPrompt.ask("  Hour (0-23)", default=now.hour)
            mn = IntPrompt.ask("  Minute (0-59)", default=0)
            expiry = datetime(int(y), int(m), int(d), int(h), int(mn))
        except Exception:
            console.print("Invalid input")
            time.sleep(1.5)
            return
    else:
        return

    if expiry <= now:
        console.print("Expiry must be in the future")
        time.sleep(1.5)
        return

    note = ""
    try:
        print("\n  Note (customer name / phone) [optional]: ", end="", flush=True)
        note = input().strip()
    except (KeyboardInterrupt, EOFError):
        pass

    new_key = create_key(expiry, max_uses=1, note=note)

    remain = expiry - now
    total_secs = max(0, int(remain.total_seconds()))
    if total_secs < 3600:
        remain_str = f"{total_secs // 60} minutes"
    elif total_secs < 86400:
        remain_str = f"{total_secs // 3600} hours"
    else:
        remain_str = f"{remain.days} days"

    print("\n")
    print("=" * 55)
    print("KEY CREATED SUCCESSFULLY")
    print("=" * 55)
    print(f"KEY      : {new_key}")
    print("-" * 55)
    print(f"EXPIRY   : {expiry.strftime('%Y-%m-%d %H:%M')}")
    print(f"REMAINING: {remain_str}")
    print("MAX USES : 1 device (ဖုန်းတစ်လုံးပဲ)")
    if note:
        print(f"NOTE     : {note}")
    print("=" * 55)
    print("\n  ⚠ Key ကို ဖုန်းတစ်လုံးပဲ ပေးပါ။")
    print("  ⚠ တခြားဖုန်းမှာ ထည့်ရင် 'Key Sharing Detected' ပြမယ်။\n")

    try:
        print("  Enter နှိပ်ပါ...", end="", flush=True)
        input()
    except Exception:
        pass


# ============================================================
# MENU 2 — LIST
# ============================================================
def list_keys_menu():
    os.system("clear")
    console.print(Panel(Align.center(Text("KEY LIST", style="default")),
                        border_style="default", box=DOUBLE, height=3))

    keys = load_keys()
    if not keys:
        console.print("\n  No keys found.\n")
        try:
            input("  Enter နှိပ်ပါ...")
        except Exception:
            pass
        return

    table = Table(show_header=True, header_style="default", expand=True,
                  box=ROUNDED, border_style="default")
    table.add_column("#", justify="center", width=3)
    table.add_column("KEY", justify="center")
    table.add_column("EXPIRY", justify="center")
    table.add_column("REMAIN", justify="center")
    table.add_column("STATUS", justify="center")
    table.add_column("DEVICE", justify="center")
    table.add_column("NOTE", justify="center")

    for i, (k, info) in enumerate(keys.items(), 1):
        if not isinstance(info, dict):
            continue
        remain_str, expired = _fmt_remaining(info.get("expiry", ""))
        active = info.get("active", True)
        bound = info.get("bound_device")
        if not active:
            status = "REVOKED"
        elif expired:
            status = "EXPIRED"
        elif bound:
            status = "BOUND"
        else:
            status = "UNUSED"
        dev_short = (bound[:8] + "..") if bound else "—"
        note_short = (info.get("note", "") or "")[:18]
        table.add_row(
            str(i),
            k.replace(KEY_PREFIX + "-", ""),
            (info.get("expiry", "") or "")[:16].replace("T", " "),
            remain_str,
            status,
            dev_short,
            note_short or "—",
        )

    console.print(table)
    console.print(f"\n  Total: {len(keys)} keys\n")
    try:
        input("  Enter နှိပ်ပါ...")
    except Exception:
        pass


# ============================================================
# MENU 3 — REVOKE / DELETE
# ============================================================
def revoke_key_menu():
    os.system("clear")
    console.print(Panel(Align.center(Text("REVOKE / DELETE KEY", style="default")),
                        border_style="default", box=DOUBLE, height=3))
    print("\n  Key (full or suffix): ", end="", flush=True)
    try:
        q = input().strip()
    except (KeyboardInterrupt, EOFError):
        return
    if not q:
        return

    keys = load_keys()
    matches = [k for k in keys if k == q or k.endswith(q) or q in k]

    if not matches:
        console.print("\n  ❌ No match found.\n")
        time.sleep(1.5)
        return

    if len(matches) > 1:
        console.print("\n  Multiple matches:")
        for i, m in enumerate(matches, 1):
            console.print(f"  {i}. {m}")
        try:
            print("\n  Select number (0 = cancel): ", end="", flush=True)
            c = input().strip()
            if c == "0" or not c.isdigit():
                return
            idx = int(c) - 1
            if idx < 0 or idx >= len(matches):
                return
            target = matches[idx]
        except (KeyboardInterrupt, EOFError):
            return
    else:
        target = matches[0]

    console.print(f"\n  Selected: {target}")
    try:
        action = input("  [1] Revoke (keep record)  [2] Delete permanently  [0] Cancel : ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if action == "1":
        keys[target]["active"] = False
        keys[target]["revoked_at"] = datetime.now().isoformat()
        save_keys(keys)
        console.print("\n  ✅ Key revoked.\n")
    elif action == "2":
        del keys[target]
        save_keys(keys)
        console.print("\n  ✅ Key deleted.\n")
    else:
        return
    time.sleep(1.5)


# ============================================================
# MENU 4 — UNBIND DEVICE
# ============================================================
def unbind_key_menu():
    os.system("clear")
    console.print(Panel(Align.center(Text("UNBIND KEY (Customer Support)", style="default")),
                        border_style="default", box=DOUBLE, height=3))
    console.print("\n  Device binding reset လုပ်ပေးပါမယ်။")
    console.print("  Customer ဖုန်းအသစ်ပြောင်းရင် သုံးပါ။\n")
    print("  Key (full or suffix): ", end="", flush=True)
    try:
        q = input().strip()
    except (KeyboardInterrupt, EOFError):
        return
    if not q:
        return

    keys = load_keys()
    matches = [k for k in keys if k == q or k.endswith(q) or q in k]
    if not matches:
        console.print("\n  ❌ No match found.\n")
        time.sleep(1.5)
        return

    target = None
    if len(matches) == 1:
        target = matches[0]
    else:
        console.print("\n  Multiple matches:")
        for i, m in enumerate(matches, 1):
            console.print(f"  {i}. {m}")
        try:
            print("\n  Select number (0 = cancel): ", end="", flush=True)
            c = input().strip()
            if c == "0" or not c.isdigit():
                return
            idx = int(c) - 1
            if 0 <= idx < len(matches):
                target = matches[idx]
            else:
                return
        except (KeyboardInterrupt, EOFError):
            return

    info = keys[target]
    bound = info.get("bound_device")
    console.print(f"\n  Key      : {target}")
    console.print(f"  Bound to : {bound or '(not bound)'}")
    console.print(f"  Used     : {info.get('used', 0)} / {info.get('max_uses', 1)}")

    try:
        confirm = input("\n  Unbind this device? (y/N): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        return
    if confirm != "y":
        return

    info["bound_device"] = None
    info["bound_at"] = None
    info["last_fingerprint"] = None
    info["used"] = 0
    save_keys(keys)
    console.print("\n  ✅ Device unbound — customer can bind a new phone.\n")
    time.sleep(1.5)


# ============================================================
# MAIN
# ============================================================
def main():
    while True:
        os.system("clear")
        console.print(Panel(Align.center(Text("KEY MANAGEMENT", style="default")),
                            border_style="default", box=DOUBLE, height=3))
        console.print()
        console.print("  1. ➕ Generate New Key")
        console.print("  2. 📋 List All Keys")
        console.print("  3. 🚫 Revoke / Delete Key")
        console.print("  4. 🔓 Unbind Device (Support)")
        console.print("  0. ❌ Exit\n")

        try:
            print("  ➜ ", end="", flush=True)
            c = input().strip()
        except (KeyboardInterrupt, EOFError):
            return

        if c == "0":
            return
        elif c == "1":
            generate_key_menu()
        elif c == "2":
            list_keys_menu()
        elif c == "3":
            revoke_key_menu()
        elif c == "4":
            unbind_key_menu()


if __name__ == "__main__":
    main()

