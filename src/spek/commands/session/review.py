from __future__ import annotations

import json

import click

from spek.core.session import Finding, FindingSeverity, FindingType, ReviewPass, next_finding_key, next_pass_key
from ._helpers import load_session_or_exit, save_session_and_emit_hashes
from spek.commands._utils import read_text_arg_json


@click.group("review")
def session_review() -> None:
    """Manage review passes and findings."""


@session_review.command("start")

@click.option("--json", "as_json", is_flag=True)
def review_start(as_json: bool) -> None:
    """Start a new review pass (idempotent if last pass is empty)."""
    state, h = load_session_or_exit()

    # idempotent: reuse last pass only if it is open and has no findings
    if state.review:
        last_key = list(state.review.keys())[-1]
        last_pass = state.review[last_key]
        if not last_pass.findings and last_pass.status == "open":
            if as_json:
                click.echo(json.dumps({"before": h, "after": h, "pass_key": last_key}))
            else:
                click.echo(f"Using existing empty pass: {last_key}")
            return

    key = next_pass_key(state)
    state.review[key] = ReviewPass()
    save_session_and_emit_hashes(state, as_json, {"pass_key": key})


@session_review.command("add-finding")
@click.argument("pass_key")
@click.argument("type", type=click.Choice([t.value for t in FindingType]))
@click.argument("severity", type=click.Choice([s.value for s in FindingSeverity]))
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True, help="Parse TEXT argument as JSON string")
def review_add_finding(pass_key: str, type: str, severity: str, text: str, as_json: bool, input_json: bool) -> None:
    """Add a finding to a review pass."""
    state, _ = load_session_or_exit()
    rpass = state.review.get(pass_key)
    if rpass is None:
        click.echo(f"Review pass {pass_key!r} not found.", err=True)
        raise SystemExit(1)
    fkey = next_finding_key(state)
    rpass.findings[fkey] = Finding(type=FindingType(type), severity=FindingSeverity(severity), text=read_text_arg_json(text, input_json))
    count = len(rpass.findings)
    save_session_and_emit_hashes(state, as_json, {"finding_key": fkey, "count": count})


@session_review.command("approve")
@click.argument("pass_key")

@click.option("--json", "as_json", is_flag=True)
def review_approve(pass_key: str, as_json: bool) -> None:
    """Approve a review pass (all findings must be closed)."""
    state, _ = load_session_or_exit()
    rpass = state.review.get(pass_key)
    if rpass is None:
        click.echo(f"Review pass {pass_key!r} not found.", err=True)
        raise SystemExit(1)
    open_findings = [k for k, f in rpass.findings.items() if f.status in ("open", "reopened")]
    if open_findings:
        click.echo(f"Cannot approve: findings still open: {', '.join(open_findings)}", err=True)
        raise SystemExit(1)
    rpass.status = "approved"
    save_session_and_emit_hashes(state, as_json, {"pass_key": pass_key})


@session_review.command("close-finding")
@click.argument("pass_key")
@click.argument("key")

@click.option("--json", "as_json", is_flag=True)
def review_close_finding(pass_key: str, key: str, as_json: bool) -> None:
    """Close a finding."""
    state, _ = load_session_or_exit()
    rpass = state.review.get(pass_key)
    if rpass is None:
        click.echo(f"Review pass {pass_key!r} not found.", err=True)
        raise SystemExit(1)
    finding = rpass.findings.get(key)
    if finding is None:
        click.echo(f"Finding {key!r} not found in pass {pass_key!r}.", err=True)
        raise SystemExit(1)
    finding.status = "closed"
    save_session_and_emit_hashes(state, as_json, {"finding_key": key})


@session_review.command("reopen-finding")
@click.argument("pass_key")
@click.argument("key")

@click.option("--json", "as_json", is_flag=True)
def review_reopen_finding(pass_key: str, key: str, as_json: bool) -> None:
    """Reopen a finding."""
    state, _ = load_session_or_exit()
    rpass = state.review.get(pass_key)
    if rpass is None:
        click.echo(f"Review pass {pass_key!r} not found.", err=True)
        raise SystemExit(1)
    finding = rpass.findings.get(key)
    if finding is None:
        click.echo(f"Finding {key!r} not found in pass {pass_key!r}.", err=True)
        raise SystemExit(1)
    finding.status = "reopened"
    save_session_and_emit_hashes(state, as_json, {"finding_key": key})


@session_review.command("set-fix-note")
@click.argument("pass_key")
@click.argument("key")
@click.argument("text")

@click.option("--json", "as_json", is_flag=True)
@click.option("--input-json", "input_json", is_flag=True, help="Parse TEXT argument as JSON string")
def review_set_fix_note(pass_key: str, key: str, text: str, as_json: bool, input_json: bool) -> None:
    """Set the fix note for a finding."""
    state, _ = load_session_or_exit()
    rpass = state.review.get(pass_key)
    if rpass is None:
        click.echo(f"Review pass {pass_key!r} not found.", err=True)
        raise SystemExit(1)
    finding = rpass.findings.get(key)
    if finding is None:
        click.echo(f"Finding {key!r} not found in pass {pass_key!r}.", err=True)
        raise SystemExit(1)
    finding.fix_note = read_text_arg_json(text, input_json)
    save_session_and_emit_hashes(state, as_json, {"finding_key": key})


@session_review.command("status")
@click.option("--pass", "pass_key", default=None)
@click.option("--finding", "finding_key", default=None)

@click.option("--json", "as_json", is_flag=True)
def review_status(pass_key: str | None, finding_key: str | None, as_json: bool) -> None:
    """Show review status."""
    state, h = load_session_or_exit()

    if pass_key and finding_key:
        rpass = state.review.get(pass_key)
        if rpass is None:
            click.echo(f"Review pass {pass_key!r} not found.", err=True)
            raise SystemExit(1)
        finding = rpass.findings.get(finding_key)
        if finding is None:
            click.echo(f"Finding {finding_key!r} not found in pass {pass_key!r}.", err=True)
            raise SystemExit(1)
        if as_json:
            click.echo(json.dumps({"hash": h, "pass_key": pass_key, "finding_key": finding_key, **finding.model_dump()}))
        else:
            click.echo(f"[{finding.status}] {finding.type}/{finding.severity}: {finding.text}")
            if finding.fix_note:
                click.echo(f"  fix: {finding.fix_note}")
        return

    if pass_key:
        rpass = state.review.get(pass_key)
        if rpass is None:
            click.echo(f"Review pass {pass_key!r} not found.", err=True)
            raise SystemExit(1)
        if as_json:
            click.echo(json.dumps({
                "hash": h,
                "pass_key": pass_key,
                "status": rpass.status,
                "findings": {fk: f.model_dump() for fk, f in rpass.findings.items()},
            }))
        else:
            click.echo(f"{pass_key} [{rpass.status}]:")
            for fk, f in rpass.findings.items():
                click.echo(f"  {fk} [{f.status}] {f.type}/{f.severity}: {f.text}")
        return

    if as_json:
        click.echo(json.dumps({
            "hash": h,
            "passes": {
                pk: {
                    "status": rp.status,
                    "findings": {fk: f.model_dump() for fk, f in rp.findings.items()},
                }
                for pk, rp in state.review.items()
            },
        }))
        return

    for pk, rp in state.review.items():
        click.echo(f"{pk} [{rp.status}]:")
        for fk, f in rp.findings.items():
            click.echo(f"  {fk} [{f.status}] {f.type}/{f.severity}: {f.text}")
