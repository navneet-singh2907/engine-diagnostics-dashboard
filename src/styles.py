GLOBAL_CSS = """
<style>
/* ── Cards ─────────────────────────────────────────────────────────────────── */
.card {
    background: #1a1a2e;
    border: 1px solid #2e5f8a;
    border-radius: 10px;
    padding: 20px 24px;
    margin: 12px 0;
}
.card-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #38bdf8;
    margin-bottom: 12px;
    letter-spacing: 0.02em;
}

/* ── Status badges ──────────────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 5px;
    font-weight: 700;
    font-size: 0.9rem;
    letter-spacing: 0.03em;
    margin: 6px 0;
}
.badge-fault {
    background: #ef4444;
    color: #fff;
}
.badge-warning {
    background: #f59e0b;
    color: #0f172a;
}
.badge-nominal {
    background: #22c55e;
    color: #0f172a;
}

/* ── Hero header ────────────────────────────────────────────────────────────── */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
    border: 1px solid #2e5f8a;
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    color: #f1f5f9;
    margin: 0;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1rem;
    color: #94a3b8;
    margin-top: 6px;
}

/* ── NHTSA panel ────────────────────────────────────────────────────────────── */
.nhtsa-stat {
    font-size: 1.6rem;
    font-weight: 700;
    color: #38bdf8;
}
.nhtsa-label {
    font-size: 0.8rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.nhtsa-link {
    color: #38bdf8;
    text-decoration: none;
    font-size: 0.9rem;
}
.recall-item {
    background: #0f172a;
    border-left: 3px solid #ef4444;
    padding: 10px 14px;
    margin: 8px 0;
    border-radius: 0 6px 6px 0;
    font-size: 0.85rem;
    color: #cbd5e1;
}

/* ── Sidebar footer ─────────────────────────────────────────────────────────── */
.sidebar-footer {
    font-size: 0.75rem;
    color: #475569;
    text-align: center;
    padding-top: 12px;
    border-top: 1px solid #1e293b;
}
</style>
"""


def badge(label: str, variant: str = "nominal") -> str:
    """Return an HTML badge string. variant: 'fault' | 'warning' | 'nominal'"""
    return f'<span class="badge badge-{variant}">{label}</span>'


def card(content: str, header: str = "") -> str:
    """Wrap content in a styled card div."""
    header_html = f'<div class="card-header">{header}</div>' if header else ""
    return f'<div class="card">{header_html}{content}</div>'