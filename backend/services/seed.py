import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.icp import WwIcpConfig, WwServiceCategory, WwSignalRoutingRule
from backend.models.prompt import (
    WwPromptAngle,
    WwPromptConstraint,
    WwPromptPersona,
    WwPromptVoice,
)


async def seed_f3_growth(db: AsyncSession, tenant_id: uuid.UUID) -> None:
    """Seed a tenant with F3 Growth default config: ICP, categories, persona, angles, voices, constraints."""

    # --- ICP Config ---
    icp = WwIcpConfig(
        tenant_id=tenant_id,
        name="F3 Growth Default ICP",
        industries=["SaaS", "FinTech", "B2B Software"],
        company_stages=["Series B", "Series C", "PE-backed", "Post-acquisition"],
        employee_min=50,
        employee_max=2000,
        geos=["US", "Canada"],
        keywords_include=["RevOps", "revenue operations", "GTM", "go-to-market", "ABM", "demand gen"],
        keywords_exclude=["nonprofit", "government"],
        watch_job_postings=True,
        watch_exec_changes=True,
        watch_news_pr=True,
        watch_funding=True,
        watch_acquisitions=True,
        min_signal_score=60,
    )
    db.add(icp)

    # --- Service Categories ---
    categories = {}
    category_data = [
        (
            "GTM Execution",
            "Hands-on go-to-market execution — demand gen campaigns, ABM programs, pipeline acceleration. For companies that need marketing muscle now, not a strategy deck.",
            ["hiring marketing", "demand gen", "ABM", "pipeline", "campaign"],
        ),
        (
            "GTM Engines",
            "Building repeatable GTM infrastructure — ICP definition, scoring models, tech stack, attribution, reporting. The system that makes marketing scalable.",
            ["marketing ops", "tech stack", "HubSpot", "Salesforce", "attribution", "reporting"],
        ),
        (
            "Leadership Bridging",
            "Fractional CMO / CRO leadership to bridge gaps between executive departures and hires. Strategic oversight with operational execution.",
            ["CMO", "CRO", "VP Marketing", "head of marketing", "leadership", "interim", "fractional"],
        ),
        (
            "RevOps Build-Out",
            "Revenue operations architecture — funnel design, handoff processes, forecasting, CRM optimization. Connecting sales, marketing, and CS into a single revenue engine.",
            ["RevOps", "revenue operations", "funnel", "forecasting", "CRM", "handoff"],
        ),
    ]
    for i, (name, desc, patterns) in enumerate(category_data):
        cat = WwServiceCategory(
            tenant_id=tenant_id,
            name=name,
            description=desc,
            signal_patterns=patterns,
            sort_order=i,
        )
        db.add(cat)
        categories[name] = cat

    await db.flush()

    # --- Persona ---
    persona = WwPromptPersona(
        tenant_id=tenant_id,
        name="Rachel — Fractional CMO",
        sender_name="Rachel",
        sender_title="Fractional CMO",
        sender_company="F3 Growth",
        sender_bio_short=(
            "Rachel is a fractional CMO who builds GTM engines for PE-backed SaaS companies. "
            "She specializes in the gap between a company's last marketing leader and their next one — "
            "standing up demand gen, RevOps, and pipeline infrastructure so revenue doesn't stall during transitions."
        ),
        signature_block="Rachel\nFractional CMO, F3 Growth",
        is_default=True,
    )
    db.add(persona)

    # --- Angles ---
    angles_data = [
        (
            "Signal Lead",
            (
                "Open by referencing the specific signal that triggered this outreach. "
                "Be direct about what you noticed — a job posting, a leadership change, a funding round. "
                "Connect the signal to why it matters for the recipient's business. "
                "Do not be generic — the opening should only work for this specific signal."
            ),
            ["job_posting", "exec_change", "news_pr", "funding", "acquisition"],
            ["email", "linkedin_connection"],
            True,
        ),
        (
            "Social Proof Lead",
            (
                "Open with a relevant proof point or case study that mirrors the recipient's situation. "
                "The proof point should feel specific and earned, not boilerplate. "
                "Connect it naturally to their context. Avoid 'I helped a company just like yours' — "
                "instead name the pattern and let them see the parallel."
            ),
            ["job_posting", "exec_change"],
            ["email"],
            False,
        ),
        (
            "Curiosity Lead",
            (
                "Open with a question or observation that makes the recipient think. "
                "The question should be specific enough that it feels researched, not templated. "
                "Avoid yes/no questions. Ask something that implies you understand their world."
            ),
            ["news_pr", "funding", "acquisition"],
            ["email", "linkedin_connection"],
            False,
        ),
        (
            "Peer Lead",
            (
                "Open as a peer, not a vendor. Reference shared context — same industry, same challenge, "
                "same network. The tone should feel like a colleague reaching out, not a salesperson. "
                "Keep it short and human."
            ),
            ["exec_change"],
            ["linkedin_connection", "linkedin_dm"],
            False,
        ),
    ]
    for name, instructions, signals, channels, is_default in angles_data:
        angle = WwPromptAngle(
            tenant_id=tenant_id,
            name=name,
            instructions=instructions,
            best_for_signals=signals,
            best_for_channels=channels,
            is_default=is_default,
        )
        db.add(angle)

    # --- Voices ---
    voices_data = [
        (
            "Peer Casual",
            (
                "Write like a smart colleague sending a quick note. Conversational but substantive. "
                "Short sentences. No corporate speak. Use contractions. It should feel like a real person "
                "who respects the reader's time."
            ),
            ["synergy", "leverage", "circle back", "touch base", "I hope this finds you well", "reach out"],
            ["you", "we", "honestly", "actually", "quick"],
            [
                "Noticed you're hiring a RevOps lead — that usually means the pipeline math is getting real.",
                "We just wrapped something similar for a Series C SaaS company. Happy to share what worked.",
                "Not trying to sell you anything — just thought this might be useful context.",
            ],
            True,
        ),
        (
            "Direct",
            (
                "Get to the point immediately. No warm-up, no preamble. State the signal, state the relevance, "
                "state the ask. Every sentence should earn its place. This voice respects busy executives."
            ),
            ["leverage", "partnership", "I hope this finds you well", "just wanted to", "I'd love to"],
            ["here's why", "bottom line", "specifically"],
            [
                "You posted a VP RevOps role last week. That usually means pipeline infrastructure needs work.",
                "We build exactly that. Three PE-backed SaaS companies in the last year.",
                "Worth a 15-minute call? I can share what we've seen work at your stage.",
            ],
            False,
        ),
        (
            "Warm Consultant",
            (
                "Write like a trusted advisor who genuinely wants to help. Warm but not sycophantic. "
                "Show that you understand their situation before offering anything. "
                "Lead with empathy and insight, not product features."
            ),
            ["honestly", "leverage", "synergy", "game-changer", "revolutionary"],
            ["I've seen", "in my experience", "what usually happens", "the pattern I see"],
            [
                "Leadership transitions are always a window — the right moves now compound for the next 18 months.",
                "I've seen this pattern a few times with PE-backed companies post-acquisition. The GTM motion usually needs a reset.",
                "Happy to share some frameworks that have worked in similar situations — no strings attached.",
            ],
            False,
        ),
        (
            "Executive Formal",
            (
                "Write with executive-level polish. Clear, confident, authoritative. "
                "No fluff but not cold. The tone of a senior leader writing to a peer. "
                "Slightly more formal structure but still human."
            ),
            ["hey", "gonna", "kinda", "tbh", "lol", "no worries"],
            ["I wanted to share", "given your", "based on", "I believe"],
            [
                "Given your recent Series C announcement, I wanted to share a perspective on GTM scaling.",
                "We've supported several companies through similar transitions and the patterns are consistent.",
                "I'd welcome the opportunity to discuss how we might support your growth trajectory.",
            ],
            False,
        ),
    ]
    for name, instructions, avoid, use, examples, is_default in voices_data:
        voice = WwPromptVoice(
            tenant_id=tenant_id,
            name=name,
            instructions=instructions,
            words_to_avoid=avoid,
            words_to_use=use,
            example_sentences=examples,
            is_default=is_default,
        )
        db.add(voice)

    # --- Prompt Constraints ---
    constraints_data = [
        ("email", None, None, ["I hope this finds you well", "synergy", "leverage"], ["must include a question"]),
        ("linkedin_connection", None, 300, ["I hope this finds you well"], ["must include why connecting"]),
        ("linkedin_dm", 150, None, ["I hope this finds you well", "synergy"], ["must include a question"]),
    ]
    for channel, max_words, max_chars, forbidden, required in constraints_data:
        constraint = WwPromptConstraint(
            tenant_id=tenant_id,
            channel=channel,
            max_words=max_words,
            max_chars=max_chars,
            forbidden_phrases=forbidden,
            required_elements=required,
        )
        db.add(constraint)

    # --- Signal Routing Rules ---
    signal_types = ["job_posting", "exec_change", "news_pr", "funding", "acquisition"]
    for sig_type in signal_types:
        rule = WwSignalRoutingRule(
            tenant_id=tenant_id,
            signal_type=sig_type,
            default_channel="email",
            auto_queue_draft=True,
            priority=0,
        )
        db.add(rule)

    await db.commit()
