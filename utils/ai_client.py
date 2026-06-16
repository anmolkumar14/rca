import os
from dotenv import load_dotenv

load_dotenv()


def generate_rca(title, severity, systems, description, timeline, root_cause, fix_applied, output_style, logs=None, history=None):
    """Generate a banking RCA document using Anthropic Claude when available, otherwise return a fallback draft."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key and api_key != "your_anthropic_api_key_here":
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            model = os.getenv("MODEL_NAME", "claude-sonnet-4-6")
            prompt = build_prompt(title, severity, systems, description, timeline, root_cause, fix_applied, output_style, logs=logs, history=history)
            system_prompt = """
You are a Senior SRE and incident management specialist at an investment bank.
Behave as a senior banking operations and reliability engineer, not as a generic chatbot.

Core rules:
1. Always write in blameless language. Describe systems, controls, and processes that failed, not people.
2. Apply 5-Whys methodology to identify the root cause chain and clearly show why the incident occurred.
3. Include SOX, PCI-DSS, and control-governance language where relevant to banking operations.
4. Format every action item with: Owner, Due Date, Priority, Status.
5. Automatically calculate MTTR from the incident start and end times when those times are provided.
6. Suggest 3 specific monitoring improvements after each RCA.
7. Reference ITIL incident management terminology such as Incident, Problem, Change, Known Error, Major Incident, CAB, and Post-Incident Review.
8. Explicitly flag whether the incident should trigger a CAB review based on the impact, scope, and change dependency.

Output requirements:
- Produce a professional RCA document for banking production incidents.
- Include: Executive Summary, Impact, Detection, Timeline, 5-Whys analysis, Contributing Factors, Root Cause, Corrective Actions, Preventive Actions, Monitoring Recommendations, ITIL terminology notes, and CAB review assessment.
- Keep the tone enterprise, precise, and audit-ready for SRE, risk, compliance, and technology leadership.
"""

            response = client.messages.create(
                model=model,
                max_tokens=1800,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            return {"summary": text[:240] + "...", "document": text}
        except Exception:
            pass

    return fallback_rca(title, severity, systems, description, timeline, root_cause, fix_applied, output_style, logs=logs, history=history)


def build_prompt(title, severity, systems, description, timeline, root_cause, fix_applied, output_style, logs=None, history=None):
    history_section = ""
    if history:
        history_excerpt = history[:5000]
        history_section = f"\n\nPast incidents for comparison:\n{history_excerpt}\n\nPlease identify whether the current incident matches any previous patterns and what fixed those prior incidents."

    log_section = ""
    if logs:
        log_excerpt = logs[:5000]
        log_section = f"\n\nProduction logs:\n{log_excerpt}\n\nPlease analyze the provided logs to identify the first error, the exact root cause, affected services, and the fix recommendations. Include key details from the logs in the RCA."

    return f"""
Create a production-grade RCA document for a banking incident.

Style: {output_style}
Incident title: {title}
Severity: {severity}
Affected systems: {systems}

Description:
{description}

Timeline:
{timeline}

Root cause:
{root_cause}

Fix applied:
{fix_applied}
{history_section}
{log_section}

Requirements:
- Use blameless language and focus on process, system, and control weaknesses.
- Apply the 5-Whys methodology to the incident and explicitly show the causal chain.
- Include SOX/PCI-DSS relevant control observations where applicable.
- Include action items in the format: Owner, Due Date, Priority, Status.
- Calculate MTTR automatically from the provided start and end times if available.
- Add 3 precise monitoring improvements after the RCA.
- Reference ITIL terminology (Incident, Problem, Change, Known Error, CAB, Post-Incident Review).
- Clearly state whether the incident should trigger a CAB review.
- Include: Executive Summary, Impact, Detection, Timeline, 5-Whys analysis, Contributing Factors, Root Cause, Corrective Actions, Preventive Actions, Monitoring Recommendations, Lessons Learned, and CAB review assessment.
- Make it suitable for banking operations, audit, compliance, and SRE teams.
"""


def fallback_rca(title, severity, systems, description, timeline, root_cause, fix_applied, output_style, logs=None, history=None):
    summary = f"{output_style} RCA draft prepared for {title} with severity {severity}. The incident affected {systems} and highlights control gaps, monitoring, and response coordination."
    document = f"""
{output_style} RCA
Incident: {title}
Severity: {severity}
Affected Systems: {systems}

Executive Summary
This incident was handled through standard banking incident management procedures. The event caused service degradation in the impacted environment and required immediate mitigation. The analysis below is written in a blameless format to support operational learning, audit readiness, and continuous improvement.

Incident Description
{description}

Timeline
{timeline}

Root Cause Analysis
{root_cause}

Remediation and Fix Applied
{fix_applied}

Contributing Factors
- Monitoring thresholds were not sufficient to surface the issue at the earliest point of degradation.
- Cross-team coordination and incident documentation should be strengthened.
- Runbooks and change validation controls should be reviewed for high-impact banking workflows.

Corrective Actions
1. Improve observability and alerting coverage for the affected systems.
2. Review change management and deployment guardrails.
3. Update the incident response runbook and stakeholder communication templates.
4. Conduct a post-incident review with technology, operations, and risk stakeholders.

Preventive Actions
- Add synthetic transaction tests for critical payment or settlement paths.
- Introduce automated rollback validation for release changes.
- Establish weekly review of recurring incident patterns and control gaps.
"""
    return {"summary": summary, "document": document}
