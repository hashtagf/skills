# Criteria & edge-case library by domain

Use these as a starting point and adapt them to the real system — never paste a block
unchanged, because criteria that don't match the system make QA report failures for correct
behaviour.

## Contents

1. Form / CRUD
2. List / search / filter
3. File upload / download
4. Money / payment
5. Notification / email
6. Report / export
7. Realtime
7b. Authentication
8. RBAC / permissions
9. Cron / batch job
10. NFR checklist (re-run per module)

---

## 1. Form / CRUD

```markdown
- [ ] creating succeeds and the row appears in the list without a refresh
- [ ] a required empty field shows an error under that field and focus moves to the first invalid one
- [ ] the save button stays disabled until everything is filled and no error remains
- [ ] hammering save fires one request and creates no duplicate
- [ ] editing then saving updates what changed and leaves untouched fields alone
- [ ] cancelling mid-edit saves nothing, and warns if data would be lost
- [ ] delete asks for confirmation — one click never deletes
- [ ] deleting a row someone else already deleted says "already removed", not a 500
- [ ] editing a row someone else edited concurrently behaves per spec — never a silent overwrite
- [ ] a duplicate name/code is rejected with a clear message
- [ ] a user without permission sees no button, and calling the API directly gets 403
- [ ] values with special characters / emoji / non-Latin scripts save and render back correctly
```

## 2. List / search / filter

```markdown
- [ ] the empty state shows a message and a create-first-item action, not a bare table
- [ ] paging: first page, a middle page, last page, and the total count are correct
- [ ] a page number beyond the end (typed into the URL) does not crash
- [ ] every sortable column sorts both ways, and sorting survives paging
- [ ] several filters at once combine correctly (not "last one wins")
- [ ] a filter with no results shows a different empty state than "no data at all"
- [ ] searching with non-Latin scripts / special characters / spaces / mixed case behaves per spec
- [ ] a very long search string does not hang the query
- [ ] 10,000 rows load within the agreed time and scrolling stays smooth
- [ ] filter + search + sort + paging used together stay correct
- [ ] only data the user may see is listed (verify with two accounts of different permission)
- [ ] refreshing keeps filter and page state (when the spec says it should live in the URL)
```

## 3. File upload / download

```markdown
- [ ] uploading an allowed type succeeds and shows a preview / filename
- [ ] a disallowed type is rejected, stating what is supported
- [ ] renaming a file's extension to look allowed still fails — the check uses real content type
- [ ] a file over the size limit is rejected before the upload completes
- [ ] a 0-byte file and a corrupted file are rejected gracefully
- [ ] filenames with non-Latin scripts / special characters / extreme length save and download back
- [ ] progress is shown during upload and can be cancelled mid-way
- [ ] a dropped connection shows an error and allows a retry, leaving no half file in the system
- [ ] uploading a duplicate filename renames or prompts, per spec
- [ ] someone else's file cannot be fetched with a direct URL (403/404)
- [ ] file URLs expire on schedule (when signed URLs are used)
```

## 4. Money / payment

```markdown
- [ ] amount 0 and negative amounts are rejected
- [ ] more decimals than the currency supports are rounded or rejected, per spec
- [ ] total = line items + shipping + tax − discount, identical on every screen and on the receipt
- [ ] hammering pay charges once (the idempotency key works)
- [ ] payment succeeds at the gateway but the webhook never arrives — reconciliation resolves it and no status is left hanging
- [ ] the same webhook arriving twice does not book the amount twice
- [ ] a webhook arriving before the redirect still renders the right result
- [ ] cancelling at the gateway returns a pending/cancelled state, never paid
- [ ] a price change while the user sits on checkout is surfaced before charging
- [ ] refund in full / in part / above the paid amount (must fail) / twice (must fail)
- [ ] an expired, over-quota, or already-used coupon is rejected
- [ ] two concurrent requests for the last remaining coupon — only one succeeds
- [ ] another customer's order cannot be read or modified by passing its id
- [ ] every transaction has an audit record of who, when, and how much
```

## 5. Notification / email

```markdown
- [ ] the message really sends and arrives within the agreed time
- [ ] the template renders correctly in Gmail, Outlook, and Apple Mail (web and app)
- [ ] it does not land in spam (SPF, DKIM, DMARC pass)
- [ ] every template variable is substituted — no {{name}} leaks through
- [ ] names or data with special characters neither break the template nor allow HTML injection
- [ ] links work and reach the right page, with a plain URL fallback
- [ ] when the provider is down the primary action still succeeds and the message is queued for retry
- [ ] retries do not deliver duplicates to the recipient
- [ ] rate limiting on repeated resends applies in the UI and at the API
- [ ] users who disabled notifications or unsubscribed receive nothing
- [ ] messages are sent in the user's configured language
```

## 6. Report / export

```markdown
- [ ] empty data exports a file with headers and no rows, not an error
- [ ] very large data (100,000 rows) exports, or is queued asynchronously with feedback — never a silent timeout
- [ ] CSV opens in Excel with non-Latin text intact (BOM present)
- [ ] leading zeros survive and numbers are not auto-converted to dates
- [ ] totals in the file match the totals on screen exactly
- [ ] the selected date range follows the user's timezone, not UTC
- [ ] only data the user may see is exported
- [ ] the filename carries the date / range so files can be told apart
- [ ] hammering export does not stack jobs and slow the system
```

## 7. Realtime

```markdown
- [ ] messages / updates reach the other side within the agreed time
- [ ] a dropped connection reconnects on its own and back-fills everything missed
- [ ] no duplicates appear after reconnecting
- [ ] ordering stays correct under rapid sends
- [ ] sending while offline queues with a status the user can see, and flushes on reconnect
- [ ] two tabs / two devices show the same thing without duplication
- [ ] a user whose access was revoked stops receiving new messages immediately
- [ ] very long messages / emoji / links / attachments render correctly
- [ ] unread counts stay truthful after reading on another device
- [ ] a server restart mid-session recovers without a manual reload
```

## 7b. Authentication

The highest-frequency critical domain. This is the short list — the full 12-module treatment is
in `examples/auth-l4.md`.

```markdown
- [ ] login with correct credentials succeeds and lands on the intended page
- [ ] wrong password and unknown email return the identical message, status, and response size
- [ ] response time for a known vs unknown email differs by under 100 ms (measure 100 requests)
- [ ] the account locks at exactly the configured attempt count, and a countdown is shown
- [ ] lockout counts attempts across IPs; a separate per-IP limit exists for distributed attempts
- [ ] an unverified account cannot log in, and is offered a resend without exposing that state to wrong-password attempts
- [ ] a password reset link is single-use, expires on schedule, and cannot be replayed
- [ ] an account created via social login cannot request a password reset (no password exists)
- [ ] a completed password change or reset revokes sessions on every other device
- [ ] refresh tokens rotate, and reusing a spent one revokes the whole session family
- [ ] a tampered token (changed role/sub, alg=none, foreign signing key) is refused on every endpoint
- [ ] 2FA cannot be skipped by calling an API directly with the pre-auth token
- [ ] recovery codes are single-use and regenerating invalidates the old set
- [ ] logging out revokes server-side, and the back button reveals no cached user data
- [ ] auth cookies carry HttpOnly + Secure + SameSite; no token sits in localStorage
- [ ] redirect targets are validated (reject `//host`, `/\host`, absolute URLs, double encoding)
- [ ] logs and error pages contain no passwords, tokens, OTPs, or stack traces
```

## 8. RBAC / permissions

```markdown
- [ ] every role sees exactly the menus in the permission matrix (test every role)
- [ ] the UI's permissions match the API's — no button that returns 403 when pressed
- [ ] a lower role cannot open a higher role's page by URL, and never glimpses its content before redirecting
- [ ] calling a privileged API with a lower role's token returns 403 on every endpoint
- [ ] editing the role client-side (localStorage/state) and reloading still gets refused by the API
- [ ] another user's data cannot be reached by passing their id (IDOR) — test every endpoint that takes one
- [ ] passing the id in the body or query instead of the path is also refused
- [ ] a permission change during an active session takes effect within the spec's window
- [ ] every unauthorized attempt is recorded in the audit log
- [ ] the permission matrix is exercised in full (every role × resource cell)
```

## 9. Cron / batch job

```markdown
- [ ] the job runs at the scheduled time (verified in logs)
- [ ] re-running with the same input produces the same result and no duplicates (idempotent)
- [ ] a job that dies mid-run can resume or restart safely
- [ ] a few bad rows don't kill the whole run, and get reported
- [ ] two instances starting together are locked so only one works
- [ ] a run that overshoots the next schedule doesn't overlap itself
- [ ] the processed count matches the expected count (compare before and after)
- [ ] there is an alert when the job fails or fails to start
- [ ] the schedule's timezone is right, including across DST changes
```

## 10. NFR checklist (re-run per module)

Create a task named `NFR : <module>` and paste the relevant sections.

### Performance
```markdown
- [ ] the primary action's p95 meets the agreed threshold
- [ ] page load (LCP) meets the threshold on 4G
- [ ] under expected load, error rate < 1%
- [ ] the main queries use indexes — no full table scans
```

### Accessibility
```markdown
- [ ] fully operable with the keyboard alone, and tab order matches visual order
- [ ] the focus ring is clearly visible on every focusable element
- [ ] errors are tied to their field via aria-describedby and announced via aria-live
- [ ] a screen reader reads labels, errors, and button states correctly
- [ ] contrast meets WCAG AA (4.5:1)
- [ ] meaning is never carried by colour alone
- [ ] at 200% zoom everything remains usable
```

### Compatibility
```markdown
- [ ] Chrome desktop / Safari macOS / Safari iOS (real device) / Chrome Android (real device)
- [ ] Firefox / Edge
- [ ] viewports 375 / 768 / 1440
```

### Localization
```markdown
- [ ] every string is translated — nothing falls back to English unintentionally
- [ ] no text overflows its container in the longest supported language
- [ ] dates, numbers, and currency follow the locale
```

### Observability
```markdown
- [ ] success/failure metrics exist for the primary action
- [ ] an alert fires on abnormal failure rate, and it has been test-fired
- [ ] the audit log covers the significant events and is searchable by user id
- [ ] logs contain no secrets (passwords, tokens, OTPs) — verify by grepping
```

### Change-related
```markdown
- [ ] every bug the developer marked fixed is re-tested using the ticket's original steps
- [ ] every closed bug has a permanent criterion in the related scenario
- [ ] all Happy paths are run before release (smoke)
- [ ] all Security paths are run before any release touching sensitive code
```
