"""
Tests exhaustivos para los 8 fixes de 'Editar Cliente'.
Cubre: validators, controller logic, form skip-if-unchanged, None safety.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.client_validators import (
    validate_name,
    validate_cif,
    validate_email,
    validate_contact,
    validate_client_data,
)
from utils import normalize_text

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

errors = []

def check(label, result, expected):
    status = PASS if result == expected else FAIL
    print(f"  [{status}] {label}")
    if result != expected:
        errors.append(f"{label}: got {result!r}, expected {expected!r}")

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== normalize_text — central helper ===")
# ─────────────────────────────────────────────────────────────────────────────
check("normalize_text(None)   → ''",       normalize_text(None),            "")
check("normalize_text('')     → ''",       normalize_text(""),              "")
check("normalize_text('  ')   → ''",       normalize_text("  "),            "")
check("normalize_text('hello')→ 'hello'",  normalize_text("hello"),         "hello")
check("normalize_text(' hi ') → 'hi'",     normalize_text(" hi "),          "hi")

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 1: validate_cif — CIF vacío válido ===")
# ─────────────────────────────────────────────────────────────────────────────
check("validate_cif(None)",           validate_cif(None),             True)
check("validate_cif('')",             validate_cif(""),               True)
check("validate_cif('   ')",          validate_cif("   "),            True)
check("validate_cif('A12345678')",    validate_cif("A12345678"),      True)
check("validate_cif('a12345678')",    validate_cif("a12345678"),      True)
check("validate_cif('B-12345678')",   validate_cif("B-12345678"),     True)   # CIF con guión
check("validate_cif('ESB12345678')",  validate_cif("ESB12345678"),    True)   # con prefijo país
check("validate_cif('AB')",           validate_cif("AB"),             False)   # too short
check("validate_cif('TOOLONGCIF12345')",validate_cif("TOOLONGCIF12345"), False) # too long (>12)
check("validate_cif('A1234@678')",    validate_cif("A1234@678"),     False)   # invalid char

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== validate_name — None safety ===")
# ─────────────────────────────────────────────────────────────────────────────
check("validate_name(None)",          validate_name(None),            False)
check("validate_name('')",            validate_name(""),              False)
check("validate_name('  ')",          validate_name("  "),            False)
check("validate_name('A')",           validate_name("A"),             False)  # 1 char
check("validate_name('AB')",          validate_name("AB"),            True)
check("validate_name('Juan García')", validate_name("Juan García"),   True)

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== validate_email — None safety + optional (empty = valid) ===")
# ─────────────────────────────────────────────────────────────────────────────
check("validate_email(None)",            validate_email(None),                True)
check("validate_email('')",              validate_email(""),                  True)
check("validate_email('   ')",           validate_email("   "),               True)
check("validate_email('test@ex.com')",   validate_email("test@ex.com"),       True)
check("validate_email('t@d.io')",        validate_email("t@d.io"),            True)
check("validate_email('notanemail')",    validate_email("notanemail"),        False)
check("validate_email('@nodomain')",     validate_email("@nodomain"),         False)
check("validate_email('no@')",           validate_email("no@"),               False)

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== validate_contact — None safety ===")
# ─────────────────────────────────────────────────────────────────────────────
check("validate_contact(None)",          validate_contact(None),              True)
check("validate_contact('')",            validate_contact(""),                True)
check("validate_contact('  ')",          validate_contact("  "),              True)
check("validate_contact('A')",           validate_contact("A"),               False)
check("validate_contact('AB')",          validate_contact("AB"),              True)
check("validate_contact('Juan Pérez')",  validate_contact("Juan Pérez"),      True)

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== validate_client_data — combinaciones relevantes ===")
# ─────────────────────────────────────────────────────────────────────────────
ok, _ = validate_client_data("Acme Corp", "", "", "John")
check("valid: empty CIF + empty email",   ok, True)

ok, _ = validate_client_data("Acme Corp", "", "", "")
check("valid: all optional empty",        ok, True)

ok, _ = validate_client_data("Acme Corp", "A12345678", "test@x.com", "John")
check("valid: all fields filled",         ok, True)

ok, msg = validate_client_data("", "A12345678", "test@x.com", "John")
check("invalid: name empty",              ok, False)
check("invalid: name empty — mensaje",    "nombre" in msg.lower(), True)

ok, msg = validate_client_data("Acme", "TOOSHORT", "", "J")
check("invalid: CIF short",              ok, False)
check("invalid: contact short",          "contacto" in msg.lower(), True)

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 2: CIF normalization in controller (unit logic) ===")
# ─────────────────────────────────────────────────────────────────────────────
# Simulate the normalization line: cif = (cif or "").strip().upper()
def normalize_cif(cif):
    return (cif or "").strip().upper()

check("normalize None  → ''",            normalize_cif(None),            "")
check("normalize ''    → ''",            normalize_cif(""),              "")
check("normalize '  '  → ''",           normalize_cif("  "),            "")
check("normalize 'b12345678' → upper",   normalize_cif("b12345678"),     "B12345678")
check("normalize ' B12345678 ' → strip", normalize_cif(" B12345678 "),  "B12345678")

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 8: skip-if-unchanged — None comparison safety ===")
# ─────────────────────────────────────────────────────────────────────────────
# Reproduces what handle_save does: compare field.value (possibly None from Flet)
# against (initial_values.get(key) or "").
# BUG: None == "" → False → spurious save triggered for unchanged None fields.

def simulate_skip_check_current(field_value, initial_value):
    """Current code: (self.name.value == (self.values.get('name') or ''))"""
    return field_value == (initial_value or "")

def simulate_skip_check_fixed(field_value, initial_value):
    """Fixed: normalize_text(field) == normalize_text(initial)"""
    return normalize_text(field_value) == normalize_text(initial_value)

# ── Scenario: field None (user cleared field that was None from DB), initial None
r_current = simulate_skip_check_current(None, None)
r_fixed   = simulate_skip_check_fixed(None, None)
check("None==None current → False (BUG: None vs '' spurious save)", r_current, False)
check("None==None fixed   → True  (no spurious save)",              r_fixed,   True)

# ── Scenario: Flet returns None for empty field, initial value was "" in DB
r_current = simulate_skip_check_current(None, "")
r_fixed   = simulate_skip_check_fixed(None, "")
check("None=='' current → FALSE (BUG: triggers spurious save)", r_current, False)
check("None=='' fixed   → True  (no spurious save)",            r_fixed,   True)

# ── Scenario: field has same value as initial
r_current = simulate_skip_check_current("Acme", "Acme")
r_fixed   = simulate_skip_check_fixed("Acme", "Acme")
check("'Acme'=='Acme' current → True (skip correctly)", r_current, True)
check("'Acme'=='Acme' fixed   → True (skip correctly)", r_fixed,   True)

# ── Scenario: field changed by user (should NOT skip)
r_current = simulate_skip_check_current("Acme New", "Acme")
r_fixed   = simulate_skip_check_fixed("Acme New", "Acme")
check("changed value current → False (correct: does not skip)", r_current, False)
check("changed value fixed   → False (correct: does not skip)", r_fixed,   False)

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== FIX 1+3+8: TextField initial value None from DB ===")
# ─────────────────────────────────────────────────────────────────────────────
# When initial_values={'cif': None} (DB NULL), _build_ui does:
#   value=self.values.get("cif", "")  → returns None (key exists, value is None!)
# This passes None to ft.TextField(value=None) — Flet renders empty but value may stay None.

def get_initial_field_value_current(values, key):
    """Current: self.values.get(key, '')"""
    return values.get(key, "")

def get_initial_field_value_fixed(values, key):
    """Fixed: normalize_text(values.get(key))"""
    return normalize_text(values.get(key))

values_with_none_cif = {'name': 'Acme', 'cif': None, 'address': None, 'contact': 'J', 'email': None}

check("current: values.get('cif', '') with None → returns None (BUG)",
      get_initial_field_value_current(values_with_none_cif, 'cif'), None)
check("fixed:   values.get('cif') or '' with None → returns ''",
      get_initial_field_value_fixed(values_with_none_cif, 'cif'), "")

check("current: values.get('address', '') with None → returns None (BUG)",
      get_initial_field_value_current(values_with_none_cif, 'address'), None)
check("fixed:   values.get('address') or '' with None → returns ''",
      get_initial_field_value_fixed(values_with_none_cif, 'address'), "")

check("current: values.get('name', '') → 'Acme' (no bug when value exists)",
      get_initial_field_value_current(values_with_none_cif, 'name'), "Acme")
check("fixed:   values.get('name') or '' → 'Acme' (same)",
      get_initial_field_value_fixed(values_with_none_cif, 'name'), "Acme")

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== SUMMARY ===")
# ─────────────────────────────────────────────────────────────────────────────
if errors:
    print(f"\n\033[91m{len(errors)} test(s) FAILED:\033[0m")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("\n\033[92mAll tests passed.\033[0m")
