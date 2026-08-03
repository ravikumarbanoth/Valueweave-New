"""ValueWeave knowledge operations — how the platform is actually doing.

Composes the summaries every subsystem already writes into one snapshot, adds
the three things nobody computes (connectivity, freshness, quality), and hands
the result to a dashboard, a weekly report and a CLI.

Reads Git. Never queries Supabase — live signals are passed in by the caller,
so "we have no data" stays visible as None instead of becoming a zero.
"""
