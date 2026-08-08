# Support tickets - Lakebase Databricks App

A Databricks App for tracking support tickets in Lakebase with a simple web UI.

## Current features

- View all support tickets
- Open a ticket and read its full message history
- Create a new ticket
- Add a message to an existing ticket
- Update a ticket's status
- Persist everything through SQLAlchemy ORM models and Pydantic request validation

## Project structure

- `app.py` - Flask entrypoint and health check
- `controllers/` - Flask route handlers for ticket APIs
- `services/` - ticket business logic and orchestration
- `repositories/` - ORM-backed repository layer for reading and writing tickets/messages
- `models/` - SQLAlchemy ORM models and Pydantic request/response schemas
- `infrastructure/` - database wiring for creating the SQLAlchemy session factory
- `templates/` - support ticket web UI
- `tests/` - automated tests for the ticket service flow
- `init.sql` - manual SQL script to create the Lakebase tables
- `requirements.txt` - Python dependencies

## Step-by-step setup

### 1. Create a Lakebase instance and a native-password role

1. In your Databricks workspace, go to **Catalog** (left sidebar) and select the **Lakebase** tab (or search "Lakebase" in the workspace search bar).
2. Click **Create Lakebase instance** (sometimes labeled **Create database instance**).
   - Give it a name (e.g. `support-tickets-db`).
   - Choose the capacity/compute size and region appropriate for your workload (defaults are fine to start).
   - Click **Create** and wait for the instance to reach the **Available**/**Running** state.
3. Open the newly created instance, then go to the **Roles & Databases** tab (sometimes called **Permissions** or **Roles**).
4. **Enable native (password) authentication** for the instance if it isn't already on:
   - Look for an authentication setting such as **Native passwords** or **Password authentication** and toggle/enable it. By default some Lakebase instances only support OAuth/token-based auth — you need password auth enabled so the role below gets a static password instead of a short-lived token.
5. **Create a new role**:
   - Click **Add role** / **Create role**.
   - Choose **Password** as the authentication method (not OAuth).
   - Name the role (e.g. `tickets_app`) and let Databricks generate (or set) a password.
6. **Copy the connection URL** shown for the role. It will look like:

``` text
postgresql://<role>:<password>@<host>.database.cloud.databricks.com:5432/databricks_postgres?sslmode=require
```

   Keep this URL — you'll paste it into `setup_secrets.py`'s prompt in the next step.

### 3. Store your secrets

Run once from a **Databricks notebook** in your workspace (no CLI needed):

1. Create a new notebook (or open the Git folder you'll create in step 5, once it's cloned) and attach it to any running cluster.
2. In a cell, run:

   ```python
   %sh python setup_secrets.py
   ```

   or open a terminal from the notebook (**Run** > **Open terminal**, if enabled on your cluster) and run `python setup_secrets.py` there.

This prompts (via `getpass`, so nothing is echoed or written to disk/shell history) for:

- Your **Lakebase connection URL** (from step 2) → stored as secret `database/lakebase-url`

### 4. Configure environment variables (local dev)

Copy `.env.example` to `.env` and paste your Lakebase URL as `LAKEBASE_URL` for local runs:

```bash
cp .env.example .env
```

For deployment, `app.yaml` already pulls `LAKEBASE_URL` from the `database/lakebase-url` secret automatically — no manual editing needed there.

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run locally

```bash
python app.py
```

### 7. Create a Git folder in Databricks and deploy the app (no CLI required)

All of this is done through the Databricks workspace UI:

1. **Create a Git folder**:
   - In the Databricks workspace sidebar, click **Workspace** > **Create** > **Git folder** (in older UIs this is called **Repos** > **Add Repo**).
   - Paste the Git URL of this project's repository (e.g. your GitHub/GitLab remote for this codebase).
   - Choose a folder name and click **Create Git folder**. Databricks will clone the repo directly into your workspace — this becomes the source for your app.

2. **Create the Databricks App**:
   - In the sidebar, go to **Compute** > **Apps** (or search "Apps" in the workspace search bar).
   - Click **Create app**, then choose **Custom** (or "From scratch").
   - Give the app a name (e.g. `massive-lakebase-sync`).

3. **Point the app at your Git folder**:
   - When prompted for the source code location, select **Workspace files** / **Git folder** and browse to the Git folder you created in step 1 (the folder containing `app.py` and `app.yaml`).
   - Databricks will read `app.yaml` from that folder automatically to configure the `command` and `env` (including the `LAKEBASE_URL`, `MASSIVE_API_BASE_URL`, and secret scope/key references).

4. **Deploy**:
   - Click **Deploy** (or **Create and deploy**) in the Apps UI. Databricks will build and start the app using the Git folder's current contents — no `databricks` CLI commands are needed.
   - Whenever you update the code, pull the latest changes into the Git folder (**Git folder** > **Pull**, via the UI) and click **Deploy** again in the Apps UI to redeploy.

5. Once deployed, open the app's URL from the Apps UI and hit `GET /healthz` to confirm it's running, then try `POST /sync` to pull data from Massive into Lakebase.

## Endpoints

- `GET /healthz` - health check
- `GET /tickets` - list all support tickets
- `POST /tickets` - create a new support ticket
- `GET /tickets/<ticket_id>` - get a ticket and its messages
- `POST /tickets/<ticket_id>/messages` - add a message to a ticket
- `PATCH /tickets/<ticket_id>/status` - update a ticket status

## Testing

Run the automated tests locally with:

```bash
python -m pytest -q
```

The current test coverage focuses on the ticket lifecycle flow: create a ticket, add a message, and update its status.

## Database setup

Before starting the app, run the SQL in `init.sql` against your Lakebase database so the `tickets` and `ticket_messages` tables exist.

The expected table structure is:

- `tickets(ticket_id, title, status, created_by, created_at)`
- `ticket_messages(message_id, ticket_id, message_text, author, created_at)`

## Notes

- Lakebase auth uses a single `LAKEBASE_URL` secret pointing at a native Postgres role with a
  static, non-expiring password — no token refresh logic needed in `lakebase.py`.
- For very large batch upserts, consider `psycopg2.extras.execute_values` instead of per-row inserts.
