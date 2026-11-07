# WUPHF: from this repository to a working app

This is an implementation checklist based on your current code, reviewed October 22, 2026. The boxes are future work; this document does not mean those fixes have been implemented. I inspected the source, but did not start the app or test live delivery.

Work through the phases in order. Each phase has a concrete finish line so you can stop thinking about everything else while working on it.

## What you are building

A person logs in, saves contacts, selects recipients, types a message, and clicks **Send WUPHF**. Django saves that message and sends a copy through every supported channel available for each recipient. The website shows which attempts succeeded or failed.

Your first complete version should support **email and Telegram**. Add SMS and other platforms afterward, once you have checked their actual API access, permissions, and costs. A social media username alone does not necessarily let an app message someone.

```text
React: screens and forms
        | HTTP requests containing JSON
        v
Django: login, validation, permissions, sending logic
        |                         |
        v                         v
Database: contacts, messages   Email / Telegram services
and delivery results
```

**JSON** is a structured format for exchanging data. An **API endpoint** is a URL React calls to ask Django for data or an action. A **migration** is a versioned change to the database structure. A **session** lets Django remember which user logged in through a browser cookie.

Keep React and Django. Keep SQLite for local development. Django can send Telegram messages itself, so the Node and Java bots do not need to become additional production servers.

## What you already have

| Part | Existing files | Current state |
| --- | --- | --- |
| Users and authentication | `Project/mysite/settings.py`, Django auth URLs | Django's built-in auth is configured; React login is still a placeholder. |
| Contacts | `Project/wuphf/models.py` | `WuphfReceiver` stores contact details, but has no owner or Telegram chat ID. |
| Messages | `Project/wuphf/models.py` | `Wuphf` stores sender, recipients, message, and creation date. |
| Dispatch | `Wuphf.send_wuphf()` | Calls email; other channels only print placeholder text. |
| Email | `Project/wuphf/utils/notify.py` | SMTP code exists, but overrides the selected recipient with a fixed address and hides errors by printing them. |
| Old Django page | `Project/wuphf/views.py`, templates | The GET page just displays recipients. POST saves/sends, then redirects to a nonexistent `sent` route. |
| API | `Project/api/` | Views and URL patterns are effectively empty; the project URL configuration does not mount this API. |
| React | `Project/wuphffront/` | Navigation works structurally; pages are placeholders with no backend requests. |
| Telegram | `bot/index.js`, `bot/src/main/java/wuphf/` | Separate echo-bot experiments, not connected to WUPHF delivery. |
| Tests | `Project/wuphf/tests.py` | Checks email dispatch arguments using a mock. Does not exercise the real email helper or API. |

## Phase 1: make the project reproducible and protect credentials

**Goal:** you know how to run the two app components, and credentials stay on the backend.

- [ ] Replace the token-shaped hardcoded webhook path in `bot/index.js`. If it is a real bot token, revoke/regenerate it through BotFather and update the private environment configuration. Removing it from the file does not invalidate old copies or Git history.
- [ ] Keep secrets out of React and Git. Anything shipped in React, including `VITE_` environment variables, is visible to visitors.
- [ ] Add a root `.env.example` containing variable names and dummy values. Keep `.env` ignored. Document the existing `SECRETKEY` variable name, or rename it consistently in both settings and setup instructions.
- [ ] Load the root `.env` from an explicit path so starting Django from another directory does not unexpectedly change configuration.
- [ ] Create a Python dependency manifest with the packages Django actually needs, including Django, Django REST Framework, and python-dotenv. Record compatible versions from a working environment; do not copy every unrelated installed package.
- [ ] Check the installed Django version and select a currently supported release before deployment. Test any upgrade as its own change.
- [ ] Update `.gitignore` for `env/`, nested `node_modules/`, `__pycache__/`, `*.pyc`, `bot/target/`, and the frontend `dist/` folder. Ignoring a file does not untrack copies already committed; remove generated files from Git's index carefully, keeping local files.
- [ ] Keep the `bot/` experiments as reference for now. Stop running them while developing the Django Telegram integration.
- [ ] Replace the short README with setup instructions, required environment variables, and the commands for starting both servers.

After creating the dependency manifest, the intended local startup is:

```bash
# Terminal 1, starting at the repository root
source env/bin/activate
cd Project
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The commands assume you keep the existing `env/` virtual environment and place the new manifest at `Project/requirements.txt`. Recreate the environment if the existing one cannot run on your machine.

```bash
# Terminal 2, starting at the repository root
cd Project/wuphffront
npm ci
npm run dev
```

Use the URLs printed by the servers. Django admin is at `/admin/` on the Django server. These commands start services; they do not yet connect React to Django.

**Done when:** Django admin and the React home page open, and another person could follow the README without your private credentials.

## Phase 2: fix the data model and ownership

**Goal:** each user's contacts and messages belong to that user.

Edit `Project/wuphf/models.py`:

- [ ] Add an `owner` foreign key from `WuphfReceiver` to the Django user model. Prefer `settings.AUTH_USER_MODEL` for new user relations.
- [ ] Plan what happens to existing contacts before making ownership required: assign them to the correct existing user in a data migration, then make the field non-null. Back up any database you care about first.
- [ ] Add an optional `telegram_chat_id` to contacts. A string field is convenient for storing chat identifiers.
- [ ] Keep `Wuphf.sender`, `receivers`, `message`, and `date`; these already describe your main action.
- [ ] Decide whether `Socials` serves a real feature. It currently has no corresponding migration in this repository and is unused by sending. Remove it if unnecessary, or migrate it if keeping it.
- [ ] Define a message limit, such as 1,000 characters, and validate it consistently in Django and React. Remove the current silent `[:99]` truncation.
- [ ] Require a nonblank message and at least one valid, owned recipient when sending. Reject unknown or unauthorized IDs rather than silently dropping them.
- [ ] Validate contact details through API serializers/forms; saving a Django model alone does not automatically perform all field validation.

After intentional model edits, run from `Project/`:

```bash
python manage.py makemigrations wuphf
python manage.py migrate
python manage.py check
```

Review generated migrations before applying them. Do not delete migration history to work around an error.

**Done when:** contacts have owners, migrations match the models, and one user's contacts cannot be accessed or used by another user.

## Phase 3: make email delivery correct before building the screen

**Goal:** one selected contact receives the intended message, and failures are visible.

- [ ] Remove the fixed recipient override in `Project/wuphf/utils/notify.py`. Use the recipient passed into the function.
- [ ] Use Django's email utilities and settings instead of maintaining the raw SMTP session yourself. Start with Django's console email backend so development prints messages without sending them.
- [ ] Add SMTP configuration through environment variables when ready for a real test. Use credentials appropriate to the email provider.
- [ ] Set an email timeout and return a useful result or raise an exception. Printing an exception and continuing makes the caller unable to tell whether delivery worked.
- [ ] Move dispatch orchestration into a small module such as `Project/wuphf/services.py`. Keep database definitions in models, HTTP handling in views, and provider calls in notification helpers.
- [ ] Save the WUPHF and its recipients before attempting external delivery. Keep network calls outside long database transactions.
- [ ] Handle a failure for one recipient without skipping every other recipient.
- [ ] Extend the existing test to cover the email helper itself. Its current mock cannot catch the hardcoded recipient bug.

**Done when:** a local test prints the correct destination and message, a controlled real test reaches your inbox, and a simulated provider failure is distinguishable from success.

## Phase 4: create the API and login flow

**Goal:** React has a clear set of URLs to call.

Use Django REST Framework, which is already listed in `INSTALLED_APPS`. Add serializers in `Project/api/serializers.py`, views in `Project/api/views.py`, routes in `Project/api/urls.py`, and mount them under `/api/` in `Project/mysite/urls.py`.

The following routes are a proposed contract, not existing functionality:

| Method and path | Purpose |
| --- | --- |
| `GET /api/csrf/` | Establish the CSRF cookie before login or another write. |
| `POST /api/login/` | Validate credentials and create a Django session. |
| `POST /api/logout/` | End the session. |
| `GET /api/me/` | Report the current signed-in user. |
| `GET /api/receivers/` | List only the user's contacts. |
| `POST /api/receivers/` | Create a contact owned by the current user. |
| `PATCH /api/receivers/{id}/` | Edit an owned contact. |
| `DELETE /api/receivers/{id}/` | Delete an owned contact. |
| `POST /api/wuphfs/` | Validate, save, dispatch, and return delivery results. |
| `GET /api/wuphfs/` | List only the user's message history. |
| `GET /api/wuphfs/{id}/` | Show an owned message and its delivery results. |

- [ ] Use session authentication initially. There is no need to introduce JWTs for this browser app.
- [ ] Protect every contact/message endpoint with authentication and ownership checks. Derive sender and owner from `request.user`, never client-supplied IDs.
- [ ] Protect login and other state-changing requests with CSRF validation. An anonymous login endpoint needs explicit CSRF protection; DRF session authentication alone does not provide that for anonymous requests.
- [ ] Return JSON with useful field errors and appropriate HTTP status codes. Do not redirect an API request to an HTML success page.
- [ ] Use accounts created in Django admin initially. Add public signup/password reset later if you want other people to register themselves.

Example request body for creating a WUPHF:

```json
{
  "message": "Meeting in five minutes!",
  "receiver_ids": [1, 2]
}
```

The backend decides which supported channels each contact has. A contact without any usable supported channel should produce a clear validation error before sending.

**Done when:** authenticated API requests can create contacts and send a WUPHF, anonymous requests are denied, invalid requests explain the problem, and another user's records remain inaccessible.

## Phase 5: connect React to Django

**Goal:** the browser can complete the whole email flow.

- [ ] Add a Vite development proxy in `Project/wuphffront/vite.config.js` that forwards `/api` requests to the Django development server. React should request relative URLs such as `/api/receivers/`.
- [ ] Use one hostname consistently while developing. Configure Django's allowed hosts and, if necessary, trusted CSRF origins for the actual frontend origin. A development proxy does not remove CSRF requirements.
- [ ] Create one small API helper for JSON requests, cookies, CSRF headers, and error handling. Read the current CSRF token for writes, including after login because Django rotates it.
- [ ] Implement `pages/Login.jsx` with username/password inputs, loading state, errors, and redirect after login. Determine current login state through `/api/me/`.
- [ ] Replace `pages/Home.jsx` demo content with a recipient list, message textarea, and Send WUPHF button.
- [ ] Add a contact management screen. Django admin can manage contacts temporarily while you build this.
- [ ] Fetch real contacts from Django instead of hardcoding recipient data.
- [ ] Disable submission while a request is pending; show validation errors and per-channel results. A disabled button helps avoid accidental double-clicks but does not guarantee duplicate prevention on the server.
- [ ] Preserve the message on failure. Clear it only after an appropriate successful response.
- [ ] Remove demo logos, unused imports, tutorial links, and duplicate imports in `src/main.jsx`. Use consistent relative imports for your own components.
- [ ] Retire the old Django sending view once React replaces it, or protect and maintain it explicitly. The current view accepts an unauthenticated POST and redirects to an undefined `sent` route; do not leave a broken parallel send path exposed.

If you later use separate frontend/backend origins, configure CORS and cookie behavior deliberately. A same-origin setup is simpler for this app.

**Done when:** you can log in through React, select your contact, type a message, click Send, and see the correct email result without using the Django shell.

## Phase 6: save delivery results and add Telegram

**Goal:** one WUPHF can send through two channels and report partial success accurately.

- [ ] Add a delivery model, for example `WuphfDelivery`, with a WUPHF foreign key, recipient reference, channel, status, attempted time, and safe error description. Save a destination snapshot if history should remain understandable after contact edits. Choose deletion behavior deliberately so deleting a contact does not unexpectedly erase message history.
- [ ] Create one delivery row for each recipient/channel combination. Start with `pending`, `sent`, and `failed`. Here `sent` means the provider accepted the request, not that the person read it.
- [ ] Return these results in the send response and history API. An email success plus Telegram failure should be shown as partial success.
- [ ] Add a Python Telegram delivery helper using the bot token from the backend environment and Telegram's `sendMessage` API. Set a timeout and inspect both HTTP errors and Telegram's response body.
- [ ] Initially test with your own Telegram account: start a conversation with your bot and obtain the chat ID. A bot generally cannot initiate a private conversation with an arbitrary username.
- [ ] Store that chat ID on your contact and dispatch Telegram alongside email.
- [ ] Before offering account linking to other users, implement a one-time linking code and a bot update handler that verifies the code and associates the correct chat. Do not trust arbitrary chat IDs as proof of ownership.
- [ ] Keep bot update handling in Django if needed. Use one update mechanism per bot token; avoid running the old webhook and polling experiments against the same token.
- [ ] Test partial failure and make sure the successful channel is not automatically sent again when retrying the failed one.

**Done when:** one click sends the same message to your email and Telegram, and a forced failure on either channel appears correctly in history.

## Phase 7: verify the app and prepare to share it

**Goal:** sending remains understandable and controlled when other people use it.

- [ ] Add meaningful API tests: login, CSRF enforcement, ownership boundaries, blank messages, invalid recipients, provider failures, and saved delivery results. Explicitly enable CSRF checks in tests that verify CSRF; Django's test client normally relaxes them.
- [ ] Mock email and Telegram in automated tests so tests never contact real people.
- [ ] Add duplicate-request protection before automatic retries or public usage. For example, give each send action an idempotency key and enforce uniqueness per sender on the backend.
- [ ] Add sending limits and require recipient permission before allowing broader use. Start with your own accounts and willing testers.
- [ ] Run the backend tests and checks, plus frontend lint and production build. Fix existing lint issues rather than hiding them.
- [ ] Move delivery to a background worker when requests become slow or you need reliable retries. A worker is a separate process that executes queued jobs. At that point, return a queued result immediately and let React poll for delivery status.
- [ ] Queue only after database commit. Make retries bounded, channel-specific, and aware of ambiguous provider timeouts; exactly-once external delivery is not automatically guaranteed.
- [ ] For deployment, put React and `/api/` behind one HTTPS origin, use a production Django server, and configure static assets and frontend route fallback without intercepting API URLs.
- [ ] Set `DEBUG=False`, replace wildcard `ALLOWED_HOSTS` with real hosts, use secure session/CSRF cookies, keep secrets in the host's environment, and run Django's deployment checks.
- [ ] Choose persistent database storage and backups. SQLite is fine locally; decide whether a managed database fits your hosting setup before launch.
- [ ] Log delivery IDs and safe error summaries without logging passwords, tokens, or unnecessary message contents.
- [ ] Add signup and password reset if moving beyond administrator-created test accounts.

From `Project/`, after dependencies and configuration are ready:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

From `Project/wuphffront/`:

```bash
npm run lint
npm run build
```

Run `python manage.py check --deploy` against production settings before launch. Review its findings rather than running production with development settings.

**Done when:** the main flow passes tests, one user's data is isolated from another's, failures are visible, and the deployed app can send email and Telegram through HTTPS.

## Avoid getting sidetracked

You can postpone SMS, Facebook, Twitter/X, attachments, scheduling, fancy styling, public signup, and background workers until the earlier milestones work. Check each provider's current messaging rules before promising a new channel.

Clean unused imports and old tutorial comments as you touch each file. Avoid a big rename or rewrite while you are still learning how the pieces connect.

## Your next three tasks

1. Fix the exposed token-shaped value and document reproducible setup in Phase 1.
2. Add contact ownership and resolve the model/migration mismatch in Phase 2.
3. Fix the email destination and test sending with the console backend in Phase 3.

Your first big win is **React → Django → correct email recipient**. Your next is **one click → email + Telegram → visible results**. Finish each before adding more platforms.

## Official references

- [Django email utilities and development email backends](https://docs.djangoproject.com/en/5.2/topics/email/)
- [Django CSRF protection for JavaScript requests](https://docs.djangoproject.com/en/5.2/howto/csrf/)
- [Vite development proxy](https://vite.dev/config/server-options.html#server-proxy)
- [Telegram sendMessage API](https://core.telegram.org/bots/api#sendmessage)

The Django links use the 5.2 documentation. Match documentation to the supported version you choose during setup.
