# White Whale — Build Spec
**Version:** 1.0  
**Stack:** FastAPI · PostgreSQL · Celery · Redis · React · Railway  
**Purpose:** Multi-tenant buying signal intelligence platform with LinkedIn-aware outreach

---

## What It Is

White Whale monitors job postings, news, executive changes, and funding events across a configurable ICP, classifies signals against each tenant's service categories using Claude, cross-references those signals against the tenant's LinkedIn network, and generates ready-to-send outreach drafts — email or LinkedIn — from a modular prompt system built on personas, angles, and voices.

Every account (tenant) gets its own ICP config, signal preferences, service categories, target account watchlist (White Whales), prompt library, and delivery settings. The system works for any business that sells into a specific profile of company and benefits from knowing when to strike.

---

## Core Concepts

**Discovery mode** — signal engine surfaces companies matching the tenant's ICP that the tenant didn't know to watch. New companies arrive via the Signal Feed.

**Hunt mode** — tenant pins specific companies as White Whales. The system watches those companies specifically and fires an alert the moment a signal appears.

**Connection overlay** — tenant's LinkedIn connections are synced via Unipile. When a signal fires on any company (discovered or pinned), the system flags whether the tenant has a 1st-degree connection there, a mutual connection, or a potential partnership/farming relationship. Cold outreach becomes warm intro routing.

**Action queue** — all triggered drafts land in a review queue. Tenant approves, edits, or skips. Approved items fire via Resend (email) or Unipile (LinkedIn message or connection request).

**Prompt system** — every draft is assembled from four modular blocks: Persona (who's sending), Value Prop (what they offer), Angle (how they open), Voice (how it sounds). All blocks are DB-driven and swap at runtime, so the same signal can produce a completely different draft depending on the combo selected.

---

## Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Backend API | FastAPI | Python 3.11+, async where possible |
| Task queue | Celery + Redis | Signal runs, draft generation, LinkedIn sync |
| Database | PostgreSQL 15 | All tables prefixed `ww_` |
| ORM | SQLAlchemy 2.0 | Alembic for migrations |
| Auth | JWT (python-jose) | Per-tenant, per-user tokens |
| AI classification + drafting | Anthropic claude-sonnet-4-20250514 | Prompt assembled at runtime from DB |
| Signal sources | Apollo API, NewsAPI, SerpAPI | Priority order defined per signal type |
| LinkedIn | Unipile API | OAuth connect, connection sync, send messages/requests |
| Email sending | Resend | Per-tenant from-address support |
| Contact enrichment | Apollo API | Find person by title at company, return email + LinkedIn URL |
| Frontend | React 18 + Vite | Tailwind CSS, dark terminal aesthetic |
| Hosting | Railway | One project, multiple services |
| Scheduler | Railway cron | Trigger Celery tasks on schedule |

---

## Repository Structure

```
white-whale/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings, env vars
│   ├── database.py                # DB connection, session factory
│   ├── models/                    # SQLAlchemy models (one file per domain)
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── signal.py
│   │   ├── whale.py
│   │   ├── prompt.py
│   │   ├── action.py
│   │   └── linkedin.py
│   ├── routers/                   # FastAPI routers
│   │   ├── auth.py
│   │   ├── tenants.py
│   │   ├── whales.py
│   │   ├── signals.py
│   │   ├── actions.py
│   │   ├── prompts.py
│   │   ├── linkedin.py
│   │   └── admin.py
│   ├── services/                  # Business logic
│   │   ├── signal_engine.py       # ICP matching, signal collection
│   │   ├── classifier.py          # Claude classification
│   │   ├── drafter.py             # Claude draft generation
│   │   ├── contact_finder.py      # Apollo contact lookup
│   │   ├── linkedin_service.py    # Unipile integration
│   │   ├── connection_matcher.py  # Cross-reference signals vs connections
│   │   └── delivery.py            # Resend + Unipile send logic
│   ├── workers/                   # Celery tasks
│   │   ├── celery_app.py
│   │   ├── run_signals.py
│   │   ├── sync_linkedin.py
│   │   └── process_drafts.py
│   ├── prompts/                   # Static prompt templates (base layer)
│   │   └── base_system.txt
│   └── alembic/                   # DB migrations
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── SignalFeed.jsx
│   │   │   ├── WhiteWhales.jsx
│   │   │   ├── ActionQueue.jsx
│   │   │   ├── PromptStudio.jsx
│   │   │   ├── Settings.jsx
│   │   │   └── Admin.jsx
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── SignalCard.jsx
│   │   │   ├── WhaleCard.jsx
│   │   │   ├── DraftCard.jsx
│   │   │   ├── ConnectionBadge.jsx
│   │   │   └── PersonaSelector.jsx
│   │   └── api/                   # API client functions
├── docker-compose.yml             # Local dev
└── .env.example
```

---

## Database Schema

All tables prefixed `ww_`. Run as Alembic migrations. PostgreSQL 15.

### Tenants & Users

```sql
CREATE TABLE ww_tenants (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name                TEXT NOT NULL,
  slug                TEXT UNIQUE NOT NULL,
  plan                TEXT DEFAULT 'starter',      -- starter | pro | agency
  is_active           BOOLEAN DEFAULT true,
  created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE ww_users (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  email               TEXT UNIQUE NOT NULL,
  hashed_password     TEXT NOT NULL,
  full_name           TEXT,
  role                TEXT DEFAULT 'member',       -- owner | admin | member
  is_active           BOOLEAN DEFAULT true,
  created_at          TIMESTAMPTZ DEFAULT now()
);
```

### ICP Configuration (per tenant)

```sql
CREATE TABLE ww_icp_configs (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  name                TEXT NOT NULL DEFAULT 'Default ICP',
  -- Company filters
  industries          TEXT[],                      -- ['SaaS', 'FinTech']
  company_stages      TEXT[],                      -- ['Series B', 'PE-backed', 'Post-acquisition']
  employee_min        INTEGER,
  employee_max        INTEGER,
  geos                TEXT[],                      -- ['US', 'Canada']
  keywords_include    TEXT[],                      -- must appear in profile/news
  keywords_exclude    TEXT[],
  -- Signal preferences
  watch_job_postings  BOOLEAN DEFAULT true,
  watch_exec_changes  BOOLEAN DEFAULT true,
  watch_news_pr       BOOLEAN DEFAULT true,
  watch_funding       BOOLEAN DEFAULT true,
  watch_acquisitions  BOOLEAN DEFAULT true,
  -- Scoring thresholds
  min_signal_score    INTEGER DEFAULT 60,          -- 0-100, below this is ignored
  is_active           BOOLEAN DEFAULT true,
  created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE ww_service_categories (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  name                TEXT NOT NULL,               -- 'GTM Execution', 'Leadership Bridging'
  description         TEXT,                        -- what this service is (Claude uses this)
  signal_patterns     TEXT[],                      -- patterns that suggest this category
  is_active           BOOLEAN DEFAULT true,
  sort_order          INTEGER DEFAULT 0
);

CREATE TABLE ww_signal_routing_rules (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  signal_type         TEXT NOT NULL,               -- job_posting | exec_change | news | funding | acquisition
  service_category_id UUID REFERENCES ww_service_categories(id),
  default_persona_id  UUID,                        -- FK to ww_prompt_personas
  default_angle_id    UUID,                        -- FK to ww_prompt_angles
  default_voice_id    UUID,                        -- FK to ww_prompt_voices
  default_channel     TEXT DEFAULT 'email',        -- email | linkedin
  auto_queue_draft    BOOLEAN DEFAULT true,
  priority            INTEGER DEFAULT 0
);
```

### White Whales (Target Accounts)

```sql
CREATE TABLE ww_white_whales (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  created_by          UUID REFERENCES ww_users(id),
  -- Company identity
  company_name        TEXT NOT NULL,
  domain              TEXT,                        -- anchor for signal matching and dedup
  linkedin_company_id TEXT,                        -- LinkedIn company page ID (from Unipile)
  linkedin_company_url TEXT,
  apollo_org_id       TEXT,
  -- Context
  why_they_matter     TEXT,                        -- free text, used in draft context
  ideal_entry_point   TEXT,                        -- 'VP RevOps', 'CRO', 'CEO'
  internal_notes      TEXT,
  -- Status
  status              TEXT DEFAULT 'cold',         -- cold | warming | active | won | lost | paused
  priority_tier       INTEGER DEFAULT 2,           -- 1 | 2 | 3
  -- Signal settings
  signal_sensitivity  TEXT DEFAULT 'all',          -- all | high_only | custom
  custom_signal_types TEXT[],
  -- Tracking
  last_signal_at      TIMESTAMPTZ,
  last_contacted_at   TIMESTAMPTZ,
  last_replied_at     TIMESTAMPTZ,
  added_at            TIMESTAMPTZ DEFAULT now(),
  updated_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE ww_whale_contacts (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  whale_id            UUID REFERENCES ww_white_whales(id) ON DELETE CASCADE,
  -- Person
  full_name           TEXT,
  title               TEXT,
  email               TEXT,
  linkedin_url        TEXT,
  linkedin_member_id  TEXT,
  -- Connection status (relative to the tenant's LinkedIn account)
  connection_degree   INTEGER,                     -- 1 | 2 | null
  connected_via       TEXT,                        -- name of mutual if 2nd degree
  is_connection       BOOLEAN DEFAULT false,
  connection_synced_at TIMESTAMPTZ,
  -- Source
  source              TEXT,                        -- apollo | manual | linkedin_sync
  is_primary          BOOLEAN DEFAULT false,
  created_at          TIMESTAMPTZ DEFAULT now()
);
```

### Signals

```sql
CREATE TABLE ww_companies (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  company_name        TEXT NOT NULL,
  domain              TEXT,
  linkedin_company_id TEXT,
  linkedin_company_url TEXT,
  apollo_org_id       TEXT,
  industry            TEXT,
  employee_count      INTEGER,
  stage               TEXT,
  geo                 TEXT,
  white_whale_id      UUID REFERENCES ww_white_whales(id),  -- set if this is also a whale
  first_seen_at       TIMESTAMPTZ DEFAULT now(),
  updated_at          TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, domain)
);

CREATE TABLE ww_signals (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  company_id          UUID REFERENCES ww_companies(id),
  white_whale_id      UUID REFERENCES ww_white_whales(id),  -- set if whale-specific
  -- Signal data
  signal_type         TEXT NOT NULL,               -- job_posting | exec_change | news_pr | funding | acquisition
  signal_source       TEXT,                        -- apollo | newsapi | serpapi | manual
  raw_data            JSONB,                       -- full API response stored here
  signal_summary      TEXT NOT NULL,               -- human-readable, used in drafts
  signal_url          TEXT,
  signal_date         TIMESTAMPTZ,
  -- Classification (Claude output)
  service_category_id UUID REFERENCES ww_service_categories(id),
  classification_confidence INTEGER,              -- 0-100
  classification_rationale TEXT,
  urgency_score       INTEGER,                     -- 0-100, based on signal recency + type
  -- Connection overlay
  has_connection      BOOLEAN DEFAULT false,       -- tenant has 1st-degree connection at company
  connection_count    INTEGER DEFAULT 0,
  opportunity_type    TEXT,                        -- warm_intro | partnership | farming | null
  -- Lifecycle
  status              TEXT DEFAULT 'new',          -- new | reviewed | actioned | dismissed
  dismissed_reason    TEXT,
  detected_at         TIMESTAMPTZ DEFAULT now(),
  reviewed_at         TIMESTAMPTZ
);

CREATE TABLE ww_signal_connections (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  signal_id           UUID REFERENCES ww_signals(id) ON DELETE CASCADE,
  connection_id       UUID REFERENCES ww_linkedin_connections(id),
  match_type          TEXT,                        -- direct | mutual
  opportunity_type    TEXT,                        -- warm_intro | partnership | farming
  flagged_at          TIMESTAMPTZ DEFAULT now()
);

-- Dedup table — prevents surfacing same signal twice within window
CREATE TABLE ww_signal_dedup (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  company_domain      TEXT NOT NULL,
  signal_type         TEXT NOT NULL,
  signal_fingerprint  TEXT NOT NULL,               -- hash of key signal fields
  first_seen_at       TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, signal_fingerprint)
);
```

### LinkedIn Integration

```sql
CREATE TABLE ww_linkedin_accounts (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  user_id             UUID REFERENCES ww_users(id),
  unipile_account_id  TEXT UNIQUE NOT NULL,        -- Unipile's account ID for this LinkedIn
  linkedin_member_id  TEXT,
  linkedin_name       TEXT,
  linkedin_url        TEXT,
  status              TEXT DEFAULT 'active',       -- active | expired | error
  last_sync_at        TIMESTAMPTZ,
  connection_count    INTEGER DEFAULT 0,
  created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE ww_linkedin_connections (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  linkedin_account_id UUID REFERENCES ww_linkedin_accounts(id) ON DELETE CASCADE,
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  -- Person data
  linkedin_member_id  TEXT NOT NULL,
  full_name           TEXT,
  headline            TEXT,
  current_title       TEXT,
  current_company     TEXT,
  current_company_domain TEXT,                     -- normalized for matching
  linkedin_url        TEXT,
  profile_image_url   TEXT,
  -- Connection metadata
  connected_since     DATE,
  connection_degree   INTEGER DEFAULT 1,
  -- Synced state
  last_synced_at      TIMESTAMPTZ DEFAULT now(),
  UNIQUE (linkedin_account_id, linkedin_member_id)
);

CREATE TABLE ww_connection_opportunities (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  connection_id       UUID REFERENCES ww_linkedin_connections(id),
  company_id          UUID REFERENCES ww_companies(id),
  white_whale_id      UUID REFERENCES ww_white_whales(id),
  -- Opportunity classification
  opportunity_type    TEXT NOT NULL,               -- warm_intro | partnership | farming | referral
  opportunity_summary TEXT,                        -- Claude-generated one-liner
  confidence_score    INTEGER,                     -- 0-100
  -- Status
  status              TEXT DEFAULT 'new',          -- new | reviewed | actioned | dismissed
  created_at          TIMESTAMPTZ DEFAULT now()
);
```

### Prompt System

```sql
CREATE TABLE ww_prompt_personas (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  name                TEXT NOT NULL,               -- 'Rachel — Fractional CMO'
  sender_name         TEXT NOT NULL,
  sender_title        TEXT NOT NULL,
  sender_company      TEXT NOT NULL,
  sender_bio_short    TEXT,                        -- 2-3 sentences for Claude context
  signature_block     TEXT,
  is_default          BOOLEAN DEFAULT false,
  is_active           BOOLEAN DEFAULT true,
  created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE ww_prompt_value_props (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  service_category_id UUID REFERENCES ww_service_categories(id),
  name                TEXT NOT NULL,
  one_liner           TEXT NOT NULL,               -- "We build the GTM engine between your last CMO and your next one"
  proof_points        JSONB,                       -- ["Helped 3 PE-backed SaaS companies...", ...]
  ideal_for           TEXT,                        -- "PE-backed SaaS post-acquisition"
  is_active           BOOLEAN DEFAULT true
);

CREATE TABLE ww_prompt_angles (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  name                TEXT NOT NULL,               -- 'Signal Lead', 'Social Proof Lead'
  instructions        TEXT NOT NULL,               -- natural language, fed directly to Claude
  best_for_signals    TEXT[],                      -- signal types this angle works best with
  best_for_channels   TEXT[],                      -- email | linkedin
  is_default          BOOLEAN DEFAULT false,
  is_active           BOOLEAN DEFAULT true
);

CREATE TABLE ww_prompt_voices (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  name                TEXT NOT NULL,               -- 'Peer Casual', 'Direct', 'Executive Formal'
  instructions        TEXT NOT NULL,               -- tone guidance, fed to Claude
  words_to_avoid      TEXT[],
  words_to_use        TEXT[],
  example_sentences   TEXT[],                      -- 2-3 examples to calibrate Claude
  is_default          BOOLEAN DEFAULT false,
  is_active           BOOLEAN DEFAULT true
);

CREATE TABLE ww_prompt_constraints (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  channel             TEXT NOT NULL,               -- email | linkedin_connection | linkedin_dm
  max_words           INTEGER,
  max_chars           INTEGER,                     -- 300 for linkedin connection note
  forbidden_phrases   TEXT[],                      -- ["I hope this finds you well", ...]
  required_elements   TEXT[],                      -- ["must include a question", ...]
  output_format       TEXT DEFAULT 'json'          -- json returns {subject, body} or {note}
);
```

### Action Queue

```sql
CREATE TABLE ww_action_queue (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  signal_id           UUID REFERENCES ww_signals(id),
  white_whale_id      UUID REFERENCES ww_white_whales(id),
  whale_contact_id    UUID REFERENCES ww_whale_contacts(id),
  connection_opportunity_id UUID REFERENCES ww_connection_opportunities(id),
  -- Contact (resolved at queue time)
  contact_name        TEXT,
  contact_title       TEXT,
  contact_company     TEXT,
  contact_email       TEXT,
  contact_linkedin_url TEXT,
  contact_linkedin_member_id TEXT,
  -- Draft config
  channel             TEXT NOT NULL,               -- email | linkedin_connection | linkedin_dm
  persona_id          UUID REFERENCES ww_prompt_personas(id),
  angle_id            UUID REFERENCES ww_prompt_angles(id),
  voice_id            UUID REFERENCES ww_prompt_voices(id),
  -- Draft content (Claude output)
  draft_subject       TEXT,
  draft_body          TEXT,
  draft_connection_note TEXT,                      -- linkedin only, 300 char max
  draft_generated_at  TIMESTAMPTZ,
  draft_generation_count INTEGER DEFAULT 1,        -- how many times regenerated
  -- Status
  status              TEXT DEFAULT 'pending',      -- pending | approved | sent | skipped | failed
  urgency             TEXT DEFAULT 'normal',       -- high | normal | low
  reviewed_by         UUID REFERENCES ww_users(id),
  reviewed_at         TIMESTAMPTZ,
  sent_at             TIMESTAMPTZ,
  send_error          TEXT,
  created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE ww_sequences (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  name                TEXT NOT NULL,
  steps               JSONB NOT NULL,
  -- Example steps structure:
  -- [
  --   {"day": 0, "channel": "linkedin_connection", "angle": "signal_lead"},
  --   {"day": 5, "channel": "linkedin_dm", "condition": "if_connected"},
  --   {"day": 5, "channel": "email", "condition": "if_not_connected"},
  --   {"day": 10, "channel": "email", "condition": "if_no_reply"}
  -- ]
  is_active           BOOLEAN DEFAULT true,
  created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE ww_sequence_enrollments (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  sequence_id         UUID REFERENCES ww_sequences(id),
  whale_contact_id    UUID REFERENCES ww_whale_contacts(id),
  current_step        INTEGER DEFAULT 0,
  status              TEXT DEFAULT 'active',       -- active | paused | completed | replied
  enrolled_at         TIMESTAMPTZ DEFAULT now(),
  next_step_at        TIMESTAMPTZ,
  completed_at        TIMESTAMPTZ
);
```

### Delivery Tracking

```sql
CREATE TABLE ww_delivery_settings (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  digest_enabled      BOOLEAN DEFAULT true,
  digest_frequency    TEXT DEFAULT 'daily',        -- realtime | daily | thrice_weekly | weekly
  digest_email        TEXT,
  digest_time         TIME DEFAULT '08:00',
  digest_timezone     TEXT DEFAULT 'America/Chicago',
  auto_approve        BOOLEAN DEFAULT false,        -- skip review queue, send automatically
  from_name           TEXT,
  from_email          TEXT,                        -- verified sender in Resend
  linkedin_account_id UUID REFERENCES ww_linkedin_accounts(id)
);

CREATE TABLE ww_sent_log (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID REFERENCES ww_tenants(id) ON DELETE CASCADE,
  action_queue_id     UUID REFERENCES ww_action_queue(id),
  channel             TEXT,
  to_name             TEXT,
  to_email            TEXT,
  to_linkedin_member_id TEXT,
  subject             TEXT,
  body_preview        TEXT,                        -- first 200 chars
  provider_message_id TEXT,                        -- Resend or Unipile message ID
  status              TEXT,                        -- sent | delivered | opened | replied | bounced
  sent_at             TIMESTAMPTZ DEFAULT now()
);
```

---

## LinkedIn Integration — Unipile

All LinkedIn actions go through Unipile. Never attempt direct LinkedIn API calls.

### Connect Flow

```
1. Frontend calls POST /api/linkedin/connect
2. Backend calls Unipile: POST /accounts (returns hosted auth URL)
3. Redirect user to Unipile hosted auth page
4. User logs into LinkedIn on Unipile's page
5. Unipile webhooks back to POST /api/linkedin/callback
6. Backend stores account: ww_linkedin_accounts.unipile_account_id
7. Trigger background task: sync_linkedin_connections(account_id)
```

### Connection Sync

```python
# workers/sync_linkedin.py
async def sync_linkedin_connections(linkedin_account_id: str):
    """
    Pull all 1st-degree connections from Unipile.
    Store in ww_linkedin_connections.
    Normalize current_company to domain for signal matching.
    Run after initial connect and on schedule (weekly).
    """
    # GET /users/{account_id}/relations from Unipile
    # Paginate through all connections
    # For each connection: normalize company name to domain via Apollo or clearbit
    # Upsert into ww_linkedin_connections
    # After sync: run connection_matcher for any pending signals
```

### Connection Matching

```python
# services/connection_matcher.py
async def match_connections_to_signal(signal_id: str, tenant_id: str):
    """
    Called every time a new signal is classified.
    Checks if any of the tenant's LinkedIn connections work at the signal company.
    Also checks if the company looks like a partnership/farming opportunity.
    """
    # 1. Get signal company domain
    # 2. Query ww_linkedin_connections WHERE tenant_id = ? 
    #    AND current_company_domain = signal_company_domain
    # 3. If matches found:
    #    - Set ww_signals.has_connection = true
    #    - Set ww_signals.connection_count = len(matches)
    #    - Classify opportunity_type via Claude (see below)
    #    - Insert ww_signal_connections rows
    #    - Insert ww_connection_opportunities rows
    # 4. Update signal urgency_score upward if connection found
```

### Opportunity Classification

When a connection match is found, call Claude to classify the opportunity type:

```
warm_intro    — connection works at the target company and is relevant to the outreach
               (e.g., you know their Head of RevOps, you're selling RevOps services)

partnership   — connection works at a company that could refer business to you
               (e.g., they're a recruiting firm, you're a fractional CMO — they place execs,
               you build the motion after the exec is placed)

farming       — connection is adjacent, not a direct intro path, but worth nurturing
               (e.g., they're a VC who invests in your ICP)

referral      — connection has explicitly referred or is likely to refer based on their role
```

Claude prompt for opportunity classification:
```
Given:
- Tenant service: {tenant service description}
- Connection: {name}, {title} at {company}
- Signal company: {company name}, {signal summary}

Classify the opportunity as one of: warm_intro | partnership | farming | referral
Return JSON: {"type": "...", "summary": "one sentence explaining the opportunity", "confidence": 0-100}
```

### Sending via Unipile

```python
# services/delivery.py
async def send_linkedin_connection_request(action_queue_id: str):
    # GET action from ww_action_queue
    # POST /users/{unipile_account_id}/relations
    # Body: { "profile_url": contact_linkedin_url, "message": draft_connection_note }
    # Store result in ww_sent_log

async def send_linkedin_message(action_queue_id: str):
    # For already-connected contacts
    # POST /chats from Unipile
    # Body: { "account_id": unipile_account_id, "attendees_ids": [linkedin_member_id], "text": draft_body }
    # Store result in ww_sent_log
```

---

## Signal Engine

### Run Schedule

```
Daily at 6am tenant timezone — full ICP sweep (job postings + news + funding)
Realtime (on demand) — manual "Run Now" button
Hourly — White Whale specific monitoring for Tier 1 accounts only
Weekly Sunday — LinkedIn connection sync for all active tenants
```

### Signal Collection Flow

```python
# services/signal_engine.py
async def run_signal_engine(tenant_id: str):
    config = get_icp_config(tenant_id)
    
    signals = []
    
    if config.watch_job_postings:
        signals += await collect_job_signals(config)      # Apollo API
    
    if config.watch_news_pr or config.watch_acquisitions:
        signals += await collect_news_signals(config)     # NewsAPI + SerpAPI
    
    if config.watch_exec_changes:
        signals += await collect_exec_signals(config)     # Apollo people search
    
    if config.watch_funding:
        signals += await collect_funding_signals(config)  # NewsAPI + SerpAPI
    
    # Also run targeted sweep for White Whale companies
    whale_signals = await run_whale_sweep(tenant_id)
    signals += whale_signals
    
    for signal in signals:
        # Dedup check
        if is_duplicate(tenant_id, signal):
            continue
        
        # Classify via Claude
        classification = await classify_signal(signal, tenant_id)
        
        if classification.confidence < config.min_signal_score:
            continue
        
        # Save signal
        saved = await save_signal(tenant_id, signal, classification)
        
        # Connection matching
        await match_connections_to_signal(saved.id, tenant_id)
        
        # Queue draft if routing rule says to
        routing = get_routing_rule(tenant_id, signal.signal_type)
        if routing.auto_queue_draft:
            await queue_draft(saved.id, routing)
```

### Apollo Signal Queries

```python
# Job postings signal: search for companies matching ICP that have relevant open roles
apollo_job_query = {
    "organization_industry_tag_ids": [...],    # from config.industries
    "organization_num_employees_ranges": [...], # from config.employee ranges  
    "currently_using_any_of_technology_uids": [],
    "job_titles": ["RevOps", "Revenue Operations", "VP Sales", "CRO", "CMO", "ABM"],
    "posted_at_after": "7d"
}

# Exec change signal: people who recently changed jobs into ICP companies
apollo_exec_query = {
    "person_titles": ["CRO", "VP Sales", "CMO", "VP Revenue", "Head of RevOps"],
    "organization_industry_tag_ids": [...],
    "changed_job_in_last": "30d"
}
```

---

## Prompt Assembly — Draft Generation

```python
# services/drafter.py
async def generate_draft(action_queue_id: str):
    action = get_action(action_queue_id)
    signal = get_signal(action.signal_id)
    persona = get_persona(action.persona_id)
    value_prop = get_value_prop_for_category(signal.service_category_id, action.tenant_id)
    angle = get_angle(action.angle_id)
    voice = get_voice(action.voice_id)
    constraints = get_constraints(action.channel, action.tenant_id)
    
    # Check for connection opportunity — changes the opening if warm intro available
    connection_opps = get_connection_opps_for_signal(signal.id)
    connection_context = build_connection_context(connection_opps) if connection_opps else ""
    
    system_prompt = f"""
You are drafting {action.channel} outreach on behalf of {persona.sender_name}, 
{persona.sender_title} at {persona.sender_company}.

SENDER CONTEXT:
{persona.sender_bio_short}

WHAT THEY OFFER (context only — do not recite verbatim):
{value_prop.one_liner}
Proof points to draw from if relevant: {', '.join(value_prop.proof_points)}
This service is ideal for: {value_prop.ideal_for}

OPENING ANGLE — how to frame this message:
{angle.instructions}

VOICE — how this should sound:
{voice.instructions}
Example sentences in the right voice:
{chr(10).join(voice.example_sentences)}

{f"CONNECTION CONTEXT — use this to warm the opening:{chr(10)}{connection_context}" if connection_context else ""}

HARD CONSTRAINTS:
- Channel: {constraints.channel}
- Max words: {constraints.max_words or 'no limit'}
- Max characters: {constraints.max_chars or 'no limit'}
- Never use these phrases: {', '.join(constraints.forbidden_phrases or [])}
- Must include: {', '.join(constraints.required_elements or [])}

OUTPUT FORMAT: Return only valid JSON.
{"{'subject': '...', 'body': '...'}" if action.channel == 'email' else "{'note': '...'}"}
No markdown, no preamble, no explanation. JSON only.
"""
    
    user_prompt = f"""
SIGNAL DETECTED:
{signal.signal_summary}

TARGET COMPANY: {action.contact_company}
CONTACT: {action.contact_name}, {action.contact_title}

CONTEXT (from our watchlist notes):
{signal.white_whale.why_they_matter if signal.white_whale else 'Newly discovered via signal engine'}

Draft the outreach now.
"""
    
    response = await claude_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    draft = json.loads(response.content[0].text)
    
    # Save to action queue
    await update_action_draft(action_queue_id, draft)
```

---

## Connection Overlay — UI Display Logic

When rendering a signal card or whale card, the connection badge logic:

```
No connections found       → no badge shown
1 connection, warm_intro   → "You know someone here — [Name], [Title]" (teal badge)
1 connection, partnership  → "Partnership opportunity — [Name] at [Company]" (blue badge)  
1 connection, farming      → "Network overlap — [Name]" (gray badge)
2+ connections             → "3 connections at this company" (teal badge, expandable)
2nd degree                 → "2nd degree — connected via [Mutual Name]" (lighter badge)
```

Draft generation for warm_intro opportunity:
```
Instead of cold open, Claude references the shared connection:
"[Connection name] and I have worked together — she mentioned you might be navigating [X]..."

Or more subtle:
"We have a mutual connection in [Name] — wanted to reach out directly..."
```

---

## API Endpoints

### Auth
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
GET    /api/auth/me
```

### Signals
```
GET    /api/signals                          # tenant signal feed, paginated
GET    /api/signals/{id}
POST   /api/signals/run                      # trigger manual run
PATCH  /api/signals/{id}/status             # reviewed | dismissed
POST   /api/signals/{id}/queue-draft        # manually queue a draft from signal
```

### White Whales
```
GET    /api/whales                           # all tenant white whales
POST   /api/whales                           # create new whale
GET    /api/whales/{id}
PATCH  /api/whales/{id}
DELETE /api/whales/{id}
GET    /api/whales/{id}/signals              # signals for this whale
GET    /api/whales/{id}/contacts             # contacts at this whale company
POST   /api/whales/{id}/contacts             # add contact manually
POST   /api/whales/{id}/find-contacts       # trigger Apollo contact lookup
```

### Action Queue
```
GET    /api/actions                          # pending queue, paginated
GET    /api/actions/{id}
PATCH  /api/actions/{id}/approve            # approve and send
PATCH  /api/actions/{id}/skip
PATCH  /api/actions/{id}/channel            # swap email/linkedin
POST   /api/actions/{id}/regenerate         # regenerate draft with same or new config
PUT    /api/actions/{id}/draft              # save manual edits to draft
```

### Prompts
```
GET    /api/prompts/personas
POST   /api/prompts/personas
PUT    /api/prompts/personas/{id}
DELETE /api/prompts/personas/{id}

GET    /api/prompts/angles
POST   /api/prompts/angles
PUT    /api/prompts/angles/{id}

GET    /api/prompts/voices
POST   /api/prompts/voices
PUT    /api/prompts/voices/{id}

GET    /api/prompts/value-props
POST   /api/prompts/value-props
PUT    /api/prompts/value-props/{id}

GET    /api/prompts/constraints             # by channel
PUT    /api/prompts/constraints/{channel}
```

### LinkedIn
```
POST   /api/linkedin/connect               # initiate Unipile OAuth
GET    /api/linkedin/callback              # Unipile webhook callback
GET    /api/linkedin/accounts              # tenant's connected LinkedIn accounts
DELETE /api/linkedin/accounts/{id}
POST   /api/linkedin/sync                  # trigger manual connection sync
GET    /api/linkedin/connections           # paginated connection list
GET    /api/linkedin/opportunities         # connection opportunity feed
```

### ICP Config
```
GET    /api/icp
PUT    /api/icp
GET    /api/icp/service-categories
POST   /api/icp/service-categories
PUT    /api/icp/service-categories/{id}
GET    /api/icp/routing-rules
PUT    /api/icp/routing-rules/{id}
```

### Admin (owner role only)
```
GET    /api/admin/tenants
POST   /api/admin/tenants
PATCH  /api/admin/tenants/{id}
GET    /api/admin/tenants/{id}/usage
POST   /api/admin/tenants/{id}/seed        # seed default ICP + prompt config
```

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/whitewhale

# Redis
REDIS_URL=redis://localhost:6379/0

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Apollo
APOLLO_API_KEY=...

# NewsAPI
NEWSAPI_KEY=...

# SerpAPI
SERPAPI_KEY=...

# Unipile (LinkedIn)
UNIPILE_API_KEY=...
UNIPILE_DSN=...                            # your Unipile DSN endpoint
UNIPILE_WEBHOOK_SECRET=...

# Resend (email)
RESEND_API_KEY=...

# Auth
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080                   # 7 days

# App
APP_URL=https://yourapp.railway.app
ENVIRONMENT=production
```

---

## Build Phases

### Phase 1 — Foundation (3-4 days)
**Goal:** Tenant auth working, schema live, your own F3 Growth account seeded

- [ ] Initialize FastAPI project structure
- [ ] Set up PostgreSQL + Alembic, run all migrations
- [ ] Implement JWT auth (register, login, me)
- [ ] Tenant creation + seeding endpoint (admin)
- [ ] Seed F3 Growth tenant with:
  - ICP config (PE-backed SaaS, RevOps/GTM signals)
  - Service categories (GTM Execution, GTM Engines, Leadership Bridging, RevOps Build-Out)
  - Signal routing rules
  - Default persona (Rachel — Fractional CMO)
  - Default angles (Signal Lead, Social Proof Lead, Curiosity Lead, Peer Lead)
  - Default voices (Peer Casual, Direct, Warm Consultant, Executive Formal)
  - Prompt constraints per channel
- [ ] Basic React shell — sidebar + 4 view placeholders
- [ ] Deploy to Railway (backend + PostgreSQL + Redis)

**Done when:** You can log in, see your tenant, and the DB schema is live on Railway.

---

### Phase 2 — Signal Engine (3-4 days)
**Goal:** Real signals hitting your F3 Growth feed

- [ ] Apollo API integration — job posting signal collector
- [ ] NewsAPI integration — news/funding/acquisition signal collector
- [ ] Signal dedup logic
- [ ] Claude signal classifier — maps raw signal to service category
- [ ] `ww_companies` and `ww_signals` write logic
- [ ] Celery worker + Railway cron — daily signal run
- [ ] GET /api/signals endpoint
- [ ] Signal Feed UI — card list with type badges, service match, timestamp
- [ ] Manual "Run Now" button

**Done when:** Real signals appear in your Signal Feed every morning.

---

### Phase 3 — White Whales (2-3 days)
**Goal:** Pin target accounts, see their signals specifically

- [ ] CRUD endpoints for `ww_white_whales`
- [ ] Whale-targeted signal sweep — hourly run for Tier 1
- [ ] White Whale list UI — card grid with tier, status, signal indicator
- [ ] Add Whale from Signal card (one click)
- [ ] Whale detail view — signals timeline, contacts, notes
- [ ] Status transitions (cold → warming → active)
- [ ] Seed your 6 real target accounts as White Whales

**Done when:** Your actual target accounts are in the system and you see their signals separately from the feed.

---

### Phase 4 — LinkedIn Connection Sync (3-4 days)
**Goal:** Your LinkedIn network cross-referenced against every signal

- [ ] Unipile account connect flow (OAuth handshake, callback, store account)
- [ ] Connection sync worker — pull all 1st-degree connections, normalize domains
- [ ] Connection matcher — runs after every signal classification
- [ ] Opportunity classifier (Claude) — warm_intro vs partnership vs farming
- [ ] `ww_connection_opportunities` population
- [ ] Connection badge on Signal Feed cards
- [ ] Connection badge on Whale cards
- [ ] LinkedIn Opportunities tab/view (connections that unlock warm paths)

**Done when:** Signal cards show "You know someone here" when relevant.

---

### Phase 5 — Draft Generation & Action Queue (3-4 days)
**Goal:** Claude writes the outreach, you approve and send

- [ ] Draft generator — assembles prompt from DB, calls Claude, saves to queue
- [ ] Auto-queue trigger on signal classification (per routing rules)
- [ ] Action Queue UI — pending cards with contact, draft, controls
- [ ] Persona / Angle / Voice dropdowns on each card
- [ ] Regenerate endpoint — reruns draft with updated config
- [ ] Inline edit draft body in UI
- [ ] Approve & send — email path via Resend
- [ ] Approve & send — LinkedIn path via Unipile (connection request or DM)
- [ ] Sent log writes

**Done when:** You can go from signal → reviewed draft → sent LinkedIn connection request or email in under 60 seconds.

---

### Phase 6 — Prompt Studio UI (2 days)
**Goal:** Full self-serve prompt management without touching the DB

- [ ] Persona CRUD UI (name, title, bio, signature)
- [ ] Angle CRUD UI (name, instructions, best-for tags)
- [ ] Voice CRUD UI (name, instructions, words to avoid/use, examples)
- [ ] Value Prop CRUD UI (linked to service category)
- [ ] Signal routing rules UI (which combo fires for which signal type)
- [ ] Preview draft button — generates a test draft from current config

**Done when:** You can fully manage your prompt system from the UI.

---

### Phase 7 — Multi-tenant Admin (2-3 days)
**Goal:** Create and manage client accounts

- [ ] Admin panel — tenant list, create tenant, activate/deactivate
- [ ] Per-tenant onboarding seed (creates default categories + routing rules)
- [ ] Tenant switching (for you as admin)
- [ ] Per-tenant usage stats (signal count, drafts sent, connections synced)
- [ ] Per-tenant delivery settings (digest email, frequency, from-address)
- [ ] First client account created and onboarded

**Done when:** You can create a new tenant account in 5 minutes and they have a working system.

---

### Phase 8 — Sequences (2-3 days)
**Goal:** Multi-step outreach logic, not just one-shot drafts

- [ ] Sequence template builder (steps with day, channel, condition)
- [ ] Enrollment logic — enroll a contact in a sequence from the action queue
- [ ] Sequence worker — checks enrollments daily, fires next step when due
- [ ] Condition logic — "if connected, send DM; if not, send email instead"
- [ ] Sequence status UI on Whale contact cards

**Done when:** A contact can be enrolled in a 3-step sequence and the system fires each step automatically.

---

### Phase 9 — Polish & Self-serve Onboarding (2 days)
**Goal:** A new client can onboard themselves without you configuring the DB

- [ ] Onboarding wizard — 5 questions that auto-populate ICP config + service categories
- [ ] LinkedIn connect flow built into onboarding
- [ ] Email verification for Resend from-address
- [ ] Digest email — daily HTML email of new signals + pending actions
- [ ] Notification preferences per user

**Done when:** You could hand someone a login link and they'd be set up in 15 minutes.

---

## Key Decisions & Constraints

**Always use `claude-sonnet-4-20250514` for all Claude calls.** Don't use Haiku — draft quality matters.

**Store raw API responses in `ww_signals.raw_data` (JSONB).** Never discard source data. Reclassification or reprocessing may be needed later.

**Dedup window is 30 days per company per signal type.** Don't surface the same hiring signal from the same company twice in a month.

**LinkedIn connection sync on demand + weekly only.** Don't hammer Unipile. Cache connections aggressively — they don't change daily.

**Never auto-send without explicit approval unless `auto_approve = true`.** Default is always review queue. Trust is built before automation is enabled.

**All DB queries must be tenant-scoped.** Every query includes `WHERE tenant_id = ?`. No exceptions. Audit this at code review.

**Signal urgency scoring:**
- Tier 1 White Whale signal: +30 urgency
- Signal age < 6 hours: +20 urgency  
- Connection found (warm intro): +25 urgency
- Signal age > 48 hours: -20 urgency
- Already contacted this company in last 30 days: -40 urgency

**Connection note hard limit is 300 characters.** Claude must output ≤300 chars for LinkedIn connection notes. Add this to the constraints table and enforce in the drafter.

---

## Starting Point for Claude Code

Begin with Phase 1. First command:

```bash
mkdir white-whale && cd white-whale
mkdir backend frontend
cd backend
pip install fastapi uvicorn sqlalchemy asyncpg alembic python-jose passlib celery redis anthropic httpx resend
```

First file to build: `backend/models/` — all SQLAlchemy models from this spec. Get the schema right before touching any API logic.

Reference this document throughout the build. Every table name, column, and relationship is intentional.
