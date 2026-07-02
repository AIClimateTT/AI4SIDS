# Tenancy + RBAC Foundation — Design

**Date:** 2026-07-02
**Status:** Approved
**Project 1 of 4** in the multi-org platform roadmap:
1. **Tenancy + RBAC foundation (this spec)**
2. Org management (admin CRUD UI + endpoints)
3. Data management + RAG ingestion (org-scoped uploads)
4. Real-time monitoring page (Flood Hub-style)

## Goal

Let multiple government organizations use AI4SIDS-Gov with role-based access.
This project delivers the underlying model and enforcement only: organizations,
roles, protected routes, and account bootstrap. No admin UI yet (project 2).

## Requirements (agreed)

- **Roles:** `super_admin` (platform operator), `org_admin` (manages own org's
  users), `member` (views data, uses assistant).
- **Provisioning:** invite-only. No self-signup endpoint. Admins create users
  with a temporary password; users must change it on first login.
- **Data scope:** existing environmental data (sensors, river levels, weather,
  alerts) remains shared across all orgs. `org_id` scopes only users, future
  uploaded documents, and org settings.
- **Approach:** extend the existing JWT auth (`api/app/core/auth.py`) in place.
  No identity provider, no policy engine. Nothing built here is discarded if an
  IdP is added later.

## Backend design

### Schema (one Alembic migration)

`organizations` (new table):
- `id` int PK
- `name` string, unique, non-null
- `description` string, nullable
- `is_active` bool, default true
- `created_at` timestamp, server default now

`users` (new columns):
- `org_id` int FK → organizations.id, nullable (super-admins have no org)
- `role` string, non-null, default `member` (`super_admin` | `org_admin` | `member`)
- `full_name` string, nullable
- `must_change_password` bool, default false

Migration defaults existing users to `role='member'`, `org_id=NULL`.

### Enforcement

- `get_current_user` already loads the user from the DB per request.
  Authorization decisions read **role/org from the DB row**, never from token
  claims — role changes and deactivations take effect immediately despite the
  8-hour JWT lifetime.
- JWT gains `role` and `org_id` claims as a frontend convenience only.
- New dependencies in `auth.py` (or a small `permissions.py` beside it):
  - `require_role(*roles)` → 403 unless `current_user.role` is in `roles`
    (`super_admin` always passes).
  - `require_org_access(org_id)` → passes for super-admin or users whose
    `org_id` matches; 403 otherwise.
- `get_current_user` rejects requests with 403 when `must_change_password` is
  set, except the password-change endpoint itself — temp credentials cannot be
  used to browse.
- Login (`POST /auth/token`) rejects users whose org has `is_active=false`,
  and inactive users (existing `is_active` check).

### Endpoints (this project only)

- `POST /auth/change-password` — current user; requires current + new
  password; clears `must_change_password`.
- `GET /auth/me` — returns `{ id, email, full_name, role,
  org: { id, name } | null, must_change_password }`.
- Org/user CRUD endpoints are **project 2**, not here.

### Bootstrap

- Idempotent seed script `api/app/seed_auth.py` (runnable via
  `python -m app.seed_auth`): creates a super-admin from `SUPERADMIN_EMAIL` /
  `SUPERADMIN_PASSWORD` env vars if no user with that email exists.
- Optional dev-only flag seeds two demo orgs with an org-admin and a member
  each, for exercising the guards before project 2 exists.

## Frontend design

### AuthContext

- After login and on app load with a stored token, fetch `GET /auth/me`;
  store `user` in context state.
- Any 401 clears the token and redirects to login.
- Expose `user`, `isAuthenticated`, `hasRole(...roles)`, `login`, `logout`.

### Routing

- New `/login` route (page, not modal). Form logic lifted from the existing
  `login-modal.tsx`; the modal remains only if the public site still uses it.
- `dashboard/route.tsx` `beforeLoad`: unauthenticated → redirect to `/login`
  with a `redirect` search param; return to the intended page after login.
- Role-gated routes declare required roles in `beforeLoad`; unauthorized
  authenticated users are redirected to `/dashboard`.
- Nav config entries gain optional `roles: Role[]`; the sidebar filters items
  by the current user's role.
- If `user.must_change_password`, all dashboard routes redirect to a minimal
  change-password screen; completing it clears the flag and releases the user.

## Error handling

- 401 (bad/expired token) → frontend logout + redirect to login.
- 403 role/org denied → distinct from 401; frontend shows "not authorized",
  does not log out.
- 403 with a `password_change_required` detail (the must_change_password
  gate) → frontend redirects to the change-password screen instead.
- Deactivated org or user → login fails with a clear message.

## Testing

Backend (pytest, in-memory/temp SQLite):
- member → super-admin-only dependency → 403; org_admin → own org passes,
  other org 403; super_admin passes everywhere.
- `must_change_password` user: blocked on a protected endpoint, allowed on
  change-password, unblocked after changing.
- Inactive org → login rejected.
- Migration applies cleanly to a SQLite DB with existing users.

Frontend (Vitest + RTL, existing setup):
- Unauthenticated access to a dashboard route redirects to `/login`.
- Nav renders only role-appropriate items for member vs org_admin vs
  super_admin.
- `must_change_password` user is routed to the change-password screen.

## Out of scope

- Org management UI and org/user CRUD endpoints (project 2).
- Upload scoping and document visibility (project 3).
- Email delivery, invite links, password reset, refresh tokens, SSO/IdP.
- Multi-tenancy of environmental data (explicitly shared).
