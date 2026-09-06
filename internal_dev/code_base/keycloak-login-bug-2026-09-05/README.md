# Bug: Keycloak provider's own `/api/auth/login` always fails

**Status:** Fixed in gold source (`api_logic_server_cli/prototypes/base/security/...`),
copied to all 9 identical sample snapshots + venv. **Not yet committed or pushed** —
Val asked to hold the commit pending review of this report.

**Found:** 2026-09-05, while getting `samples/basic_demo_eai` running under Podman
(unrelated task — Kafka/Keycloak-via-Podman verification surfaced this).

**Files:** `security/authentication_provider/keycloak/auth_provider.py` and
`security/system/authentication.py` (the second is shared with the SQL provider —
see "Blast radius" below for why the fix there is safe for SQL).

**Attached:** `old/` (pre-fix, from git HEAD) and `fixed/` (post-fix, current working
tree) copies of both files — diff them directly for the exact change.

---

## When would a customer actually hit this?

**Not through the Admin App.** Checked directly (not assumed): the Admin App's login
mode is decided entirely server-side, from `Config.SECURITY_PROVIDER` — confirmed live
by fetching a Keycloak-secured project's actual served `admin.yaml`, which always
contains a real `authentication.keycloak: {url, realm, clientId}` block. The safrs-
react-admin frontend uses that block to redirect straight to Keycloak's own hosted
login page whenever it's present — which it always is, for every Keycloak-secured
project, unconditionally. (There's an unrelated, unused `use_keycloak: 'false'` line
elsewhere in `admin.yaml`'s style_guide section — it's a dead template constant that
nothing reads; earlier drafts of this report incorrectly treated it as the switch.
It isn't.) So the Admin App never hits this bug.

**Where it does bite: anything that logs in by POSTing a username and password
directly to the project's own `/api/auth/login` endpoint, instead of going through
Keycloak's hosted login page.** That's not the Admin App — it's:
- A `curl` call or Postman request against the API
- An integration script or backend service authenticating on a user's behalf
- A Behave/pytest test suite using the standard `get_auth_token()` pattern
- An MCP client, or any other tool that treats "POST username+password, get a token"
  as the normal way to log in

Any customer with one of those pointed at a Keycloak-secured project gets a server
error on every login attempt, regardless of the password. It won't show up from just
clicking around the Admin App — you have to actually be calling the login endpoint
directly to see it.

**Reproduction (100% — not intermittent, not user-specific):**
```bash
genai-logic add-auth --provider-type=keycloak --db-url=localhost
# start Keycloak, start the server
curl -X POST http://localhost:5656/api/auth/login \
  -H "Content-Type: application/json" -d '{"username":"<any valid user>","password":"<correct password>"}'
# → 500 Internal Server Error, every time, even with the right password
```

---

## Root cause — three separate bugs, all in the Keycloak-specific code

`get_user(id, password)` is called from **two different places** in
`security/system/authentication.py`, and the two callers mean two different things by
`password`:

1. `login()` (the `/api/auth/login` handler) calls it with the **real plaintext
   password** — nothing has been checked yet.
2. `user_lookup_callback` (a Flask-JWT-Extended hook that reloads the user on every
   *subsequent* `@jwt_required()` request, from a token already verified) calls it
   with the **already-decoded JWT claims dict** — there's nothing left to check.

### Bug 1 — `get_user()` can't tell the two callers apart

The old code used a hardcoded switch:
```python
try_kc = 'authentication#user_lookup_callback'  # activate favorite experiment
```
This is a **compile-time constant**, not a dispatch on which caller is invoking the
function — so *every* call, including `login()`'s real-password call, took the branch
written for case 2 above. That branch does:
```python
jwt_data : dict = password
rtn_user = Authentication_Provider.get_user_from_jwt(jwt_data)
```
`get_user_from_jwt()` immediately does `jwt_data["preferred_username"]` — and when
`password` is really a plain string (e.g. `"p"`), that raises
`TypeError: string indices must be integers, not 'str'`. This is the exact 500 you get
back from `/api/auth/login`, for every user, unconditionally.

### Bug 2 — the branch that *would* do a real login was itself broken

There was a second, unreachable branch (`try_kc == 'api'`, dead because of Bug 1's
hardcoded switch) that attempted the real Keycloak call, but:
- posted to `{KC_BASE}/.well-known/openid-configuration` (the OIDC *discovery
  document*) instead of the actual token endpoint
  (`{KC_BASE}/realms/{realm}/protocol/openid-connect/token`)
- never extracted `access_token` from the response, then referenced an undefined
  `access_token` variable in `jsonify(access_token=access_token)`
- returned a Flask `Response` object from `get_user()`, whose contract is "return a
  user object" — even with the URL fixed, this shape would break the caller

So even if Bug 1 were fixed by simply routing plaintext-password calls into this
branch, it still wouldn't have worked.

### Bug 3 — `check_password()` was never overridden for Keycloak

`login()`'s gate is:
```python
if not user or not authentication_provider.check_password(user=user, password=password):
    return jsonify("Wrong username or password"), 401
```
The **SQL** provider overrides `check_password()` to compare against a stored hash.
The **Keycloak** provider's `Authentication_Provider` class has no such override —
it silently inherits `Abstract_Authentication_Provider.check_password()`, whose
default body is `return False`. So even a hypothetically-fixed `get_user()` that
correctly authenticated against Keycloak and returned a real user would still be
rejected immediately afterward, unconditionally, by this second, independent gate.

**All three bugs had to be fixed together** — fixing any one or two of them alone
still leaves login broken.

---

## The fix

1. **`get_user()` dispatches on the actual type of `password`** instead of a hardcoded
   switch: a `dict` means "already-verified JWT claims" (existing, correct behavior,
   unchanged); anything else means "real plaintext password, authenticate it now."
2. **The real-login path now correctly calls Keycloak's token endpoint**
   (`Args.instance.keycloak_base_url + '/protocol/openid-connect/token'`, password
   grant), and on success decodes the returned token's claims (Keycloak already
   verified the credentials — that's what the 200 means — so the decode does not
   re-verify the signature) and builds the user via the existing, unchanged
   `get_user_from_jwt()`.
3. **`check_password()` is now overridden for Keycloak**: `return user is not None` —
   correct because step 2 already did the real check; a resolved user *is* proof of a
   successful login.
4. **`login()` (the shared file) now prefers a token already provided by the
   provider**, via Flask's request-scoped `g`, before minting its own with
   `create_access_token()`. This is necessary, not just tidy: `configure_auth()`
   configures this provider's `JWTManager` with **Keycloak's own public key only, no
   private key** (`do_priv_key = False`) — it's deliberately set up to *verify*
   Keycloak-signed tokens (that's what `get_jwt_public_key()` fetches), not to *mint*
   new ones. Calling `create_access_token()` under this config raises
   `RuntimeError: JWT_PRIVATE_KEY must be set to use asymmetric cryptography algorithm
   "RS256"` — confirmed by hitting this exact error live while testing steps 1–3 in
   isolation, before this step was added. So the fix hands the client Keycloak's own
   real, already-signed token — which is also the more correct design, since that's
   the same token `user_lookup_callback` will verify on every later request anyway.

## Blast radius / why the shared-file change is safe for the SQL provider

`authentication.py`'s `login()` is used by both providers. The change there is:
```python
access_token = getattr(g, 'access_token', None) or create_access_token(identity=user)
```
The SQL provider's `get_user()` never touches `g.access_token`, so `getattr(...)`
returns `None` there and `create_access_token()` runs exactly as before — this is a
no-op change for SQL logins. (Note: deliberately used `getattr(g, ...)` rather than an
attribute check on the returned user object — `DotMap`/`DotMapX` auto-vivifies missing
attributes as empty `DotMap`s on access, which would have made an
`is None`/`hasattr`-style check on the user object unreliable. `flask.g` is a plain
object with normal attribute semantics, and is already used in this exact function for
this exact purpose.)

## Verification (live, end-to-end, against `samples/basic_demo_eai`)

- `genai-logic add-auth --provider-type=keycloak --db-url=localhost`, Keycloak running
  via Podman, server restarted with the fix in place.
- `POST /api/auth/login` with correct `s1`/`p` → `200`, real Keycloak-issued JWT
  returned (decoded payload confirmed: `preferred_username: s1`,
  `realm_access.roles` includes `sales`, `attributes.region: "British Isles"`).
- Same endpoint with a wrong password → `401 "Wrong username or password"` (confirms
  bad credentials are still correctly rejected, not just "anything succeeds now").
- Used the token **returned by this project's own login endpoint** (not a token
  fetched directly from Keycloak) against `GET /api/Customer/`: the `sales`-role
  Grant in `declare_security.py`
  (`credit_limit >= 3000 or balance > 0`) was correctly enforced — one customer
  (`Diana`, credit_limit=1000/balance=0) correctly excluded, the other four correctly
  shown. This confirms the full path end-to-end: password → real Keycloak
  authentication → real token → RBAC-filtered data, all through the app's own public
  login endpoint.

## Where this has been applied

- Gold: `api_logic_server_cli/prototypes/base/security/authentication_provider/keycloak/auth_provider.py`
  and `.../security/system/authentication.py`
- Propagated (byte-identical to pre-fix base, confirmed via diff before overwriting)
  to all 9 sample snapshots under `prototypes/manager/samples/`: `demo_customs_clvs`,
  `demo_customs_surtax`, `basic_demo_ai_rules-supplier`, `demo_emp_types`,
  `allocate_dept_account_demo`, `basic_demo_eai`, `basic_demo_sample`,
  `basic_demo_logic_gov`, `library_rfi`
- Propagated to the venv-installed copy (`build_and_test/genai-logic/venv/...`) for
  immediate effect on next `genai-logic create`
- **Not applied** to `prototypes/manager/system/genai/examples/genai_demo/genai_demo_docs_logic/`
  — that copy already diverges from base independently (missing `safe_log()`, and a
  separate, unrelated bug: uses `keycloak_base` instead of `keycloak_base_url` for the
  JWKS fetch). Left untouched rather than silently pulling in unrelated changes;
  flagging here as a known follow-up if that example is still actively used.
- **Not committed, not pushed** — sitting in the gold-source working tree pending review.

## History (for context, not blame)

`try_kc` has been present since Keycloak support was first added
(`49c5318e`, "10.03.18: Keycloak initial inclusion", Mar 2024) — this is not a
regression from a recent change, it's been in every Keycloak-secured project since
Keycloak support existed at all. Most recent touch to `auth_provider.py` before this
fix: `9a6c1f59` ("keycloak fix to config.py - fixes for graphics"), Mar 2025.
