import os
from datetime import datetime


def get_latest_alert():
    """Return the most recent Azure Monitor P1 alert, or None if unable to fetch."""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.alertsmanagement import AlertsManagementClient
    except ImportError:
        return None

    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        return None

    try:
        credential = DefaultAzureCredential()
        client = AlertsManagementClient(credential, subscription_id)
        alerts = list(client.alerts.list())
        if not alerts:
            return None

        alerts.sort(key=lambda item: getattr(item, "started_on", datetime.min), reverse=True)
        latest = alerts[0]

        resources = getattr(latest, "target_resources", []) or []
        first_resource = resources[0] if resources else None
        resource_name = getattr(first_resource, "resource_name", None) if first_resource else None

        return {
            "id": getattr(latest, "alert_id", None) or getattr(latest, "id", None),
            "name": getattr(latest, "alert_rule_name", None) or getattr(latest, "name", None) or "Azure Monitor Alert",
            "severity": getattr(latest, "alert_severity", None) or getattr(latest, "severity", None) or "P2",
            "status": getattr(latest, "alert_state", None) or getattr(latest, "status", None) or "Unknown",
            "resource": resource_name or os.getenv("AZURE_RESOURCE_NAME", "Unknown Resource"),
            "description": getattr(latest, "description", None) or str(getattr(latest, "alert_context", ""))[:2000],
            "start_time": getattr(latest, "started_on", None) or getattr(latest, "start_date_time", None),
            "end_time": getattr(latest, "resolved_on", None) or getattr(latest, "end_date_time", None),
            "raw": repr(latest),
        }
    except Exception:
        return None
