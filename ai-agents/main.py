from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI GitOps Copilot")

class IncidentRequest(BaseModel):
    app_name: str
    argocd_status: str
    kubernetes_events: str
    pod_logs: str
    recent_git_change: str

@app.get("/")
def home():
    return {"message": "AI GitOps Copilot Running"}

@app.post("/analyze")
def analyze(data: IncidentRequest):
    return {
        "mode": "mock-ai-demo",
        "incident_report": {
            "root_cause": "ImagePullBackOff caused by invalid or missing container image tag.",
            "evidence": {
                "app": data.app_name,
                "argocd_status": data.argocd_status,
                "kubernetes_events": data.kubernetes_events,
                "pod_logs": data.pod_logs,
                "recent_git_change": data.recent_git_change
            },
            "impact": "Application is degraded because Kubernetes cannot start the new backend pod.",
            "recommended_fix": "Update Helm values to a valid image tag or rollback to the previous working image.",
            "rollback_plan": "Use ArgoCD rollback or revert the Git commit that changed the image tag.",
            "prevention": "Add CI validation to verify Docker image tags before updating Helm values.",
            "confidence": "95%"
        }
    }
