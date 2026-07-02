# Org Management — Design

**Date:** 2026-07-02
**Status:** Approved
**Project 2 of 4** in the multi-org platform roadmap (builds on
`2026-07-02-tenancy-rbac-foundation-design.md`, implemented on `staging-gov`).

## Goal

Give super-admins CRUD over organizations and give org-admins self-service
management of their own org's users, using the RBAC primitives from project 1
(`require_role`, `require_org_access`, temp-password + `must_change_password`
flow).

## Requirements (agreed)

- **UI shape:** one role-adaptive page. Single nav item "Organization" at
  `/dashboard/org` visible to `org_admin` and `super_admin` (first consumer of
  the nav `roles` field). Super-admin sees the org list and drills into any
  org's users; org-admin lands directly on their own org's user panel.
- **Operations:** create user, change role, deactivate/reactivate, admin
  password reset. No hard delete, no org transfer.
- **Temp passwords:** server-generated (`secrets.token_urlsafe(9)`), returned
  exactly once in the create/reset response, never stored in plaintext or
  returned by any list endpoint. UI shows it once with a copy button.
- **Frontend data layer:** follows `.claude/skills/tanstack-query-conventions`
  — two-layer split (`src/lib/api/orgs.ts` transport,
  `src/lib/queries/orgs.ts` keys/options/mutations/hooks); components import
  only from the queries layer.

## Backend design

New feature module following the existing pattern
(`api/app/features/location/{controller,service,models}.py`):

```
api/app/features/orgs/
├── __init__.py
├── controller.py   # routes + dependency wiring
├── service.py      # DB logic, temp password generation
└── models.py       # Pydantic request/response schemas
```

### Endpoints (router prefix `/api/orgs`, tag `orgs`)

| Method/path | Access | Behavior |
|---|---|---|
| `GET /api/orgs` | super_admin | List all orgs: `{id, name, description, is_active, created_at, user_count}` |
| `POST /api/orgs` | super_admin | Create org `{name, description?}`; duplicate name → 409 |
| `PATCH /api/orgs/{org_id}` | super_admin | Partial update: `name?`, `description?`, `is_active?`; duplicate name → 409 |
| `GET /api/orgs/{org_id}/users` | super_admin or that org's org_admin | List org users: `{id, email, full_name, role, is_active, must_change_password, created_at}` |
| `POST /api/orgs/{org_id}/users` | same | Create user `{email, full_name?, role}`; returns user + `temp_password`; duplicate email → 409 |
| `PATCH /api/orgs/{org_id}/users/{user_id}` | same | Partial update: `role?`, `is_active?` |
| `POST /api/orgs/{org_id}/users/{user_id}/reset-password` | same | New generated temp password, sets `must_change_password=True`; returns `{temp_password}` |

Access is enforced with `require_role(ROLE_ORG_ADMIN)` (super_admin passes
implicitly) plus `require_org_access(org_id, current_user)` inside each
org-scoped route. User-scoped routes 404 when `user_id` does not belong to
`org_id`.

### Guard rails (service layer, each with a test)

- Assignable roles are exactly `org_admin` and `member`. Creating or changing
  a user to `super_admin` → 422. Editing an existing `super_admin` through
  these endpoints → 404 (super-admins have no org, so org-scoped lookup
  misses them naturally).
- Admins cannot deactivate, demote, or reset-password **themselves** via
  these endpoints → 400 `"Cannot modify your own account here"`.
- Org must exist and (for user creation) be active → 404 / 400.
- `temp_password` appears only in create-user and reset-password responses.

## Frontend design

### Data layer (per tanstack-query-conventions)

- `src/lib/api/http.ts` — small authenticated fetch helper: reads the
  `ai4sids_token` from localStorage, sets `Authorization`, JSON-encodes,
  transforms FastAPI error shapes (`detail` string / 422 array) into
  `Error` with a useful message. (The existing `client.ts` is unauthenticated
  legacy transport for the public dashboard; it stays untouched.)
- `src/lib/api/orgs.ts` — named fetchers only: `getOrgs`, `createOrg`,
  `updateOrg`, `getOrgUsers`, `createOrgUser`, `updateOrgUser`,
  `resetOrgUserPassword`. Typed payloads from `src/lib/api/orgs.types.ts`.
- `src/lib/queries/tanstack-helpers.ts` — re-exports `mutationOptions` from
  `@tanstack/react-query` (native in v5.66).
- `src/lib/queries/orgs.ts` — four sections in order: `orgKeys` key factory
  (`all/lists/list/details/detail(id)/users(orgId)`), `orgQueries`,
  `orgMutations` (bare), hook wrappers (`useCreateOrg`, `useUpdateOrg`,
  `useCreateOrgUser`, `useUpdateOrgUser`, `useResetOrgUserPassword`) owning
  invalidation + toasts. User-list mutations invalidate `orgKeys.users(orgId)`
  and `orgKeys.lists()` (user_count changes).
- **Toasts:** add `sonner` dependency; mount `<Toaster richColors />` in
  `__root.tsx`.

### Page structure

```
frontend/src/features/org/
├── OrgManagementPage.tsx        # role switch: org list (super) / own org panel (org_admin)
├── components/
│   ├── OrgTable.tsx             # super_admin: orgs with user counts, status badge
│   ├── OrgFormDialog.tsx        # create/edit org
│   ├── OrgUsersPanel.tsx        # shared user table for one org
│   ├── UserFormDialog.tsx       # create user (email, full name, role select)
│   └── TempPasswordDialog.tsx   # shows generated password once + copy button
└── __tests__/
```

- Route `frontend/src/routes/dashboard/org.tsx` → `OrgManagementPage`
  (inherits the dashboard `beforeLoad` token guard).
- Nav: add `{ label: 'Organization', to: '/dashboard/org', icon: Building2,
  roles: ['org_admin', 'super_admin'] }` to `NAV_ITEMS`.
- In-page role handling: `member` (deep link) sees a "Not authorized" card;
  `org_admin` renders `OrgUsersPanel` for `user.org.id`; `super_admin`
  renders `OrgTable` with a sheet/section opening `OrgUsersPanel` for the
  selected org.
- Row actions (role change, activate/deactivate, reset password) via the
  existing dropdown-menu component; self-row actions disabled with a tooltip.

## Error handling

- 409 duplicate email/org name → inline error in the open dialog.
- 400/403/404 from mutations → `toast.error` with server detail.
- Query 401 → existing AuthContext logout path handles it.

## Testing

Backend (pytest, existing fixtures + factories):
- Permission matrix per endpoint: member 403, org_admin own-org 200,
  org_admin other-org 403, super_admin 200.
- Guard rails: assign super_admin → 422; self-deactivate/demote/reset → 400;
  duplicate email/name → 409; cross-org user_id → 404; temp_password absent
  from list responses.
- Temp password from create/reset works for login and trips the
  `must_change_password` gate.

Frontend (Vitest + RTL):
- `orgKeys` factory shapes.
- `OrgUsersPanel`: renders users, add-user flow surfaces TempPasswordDialog
  exactly once with the returned password.
- `OrgManagementPage` role switch: member → not authorized, org_admin → own
  panel, super_admin → org table.

## Out of scope

- Email invites/notifications, hard delete, org transfer (revisit later).
- Org-scoped data/documents (project 3).
- Audit log UI (data exists via created_at only).
