from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


# ========================== Contratos (ajudam a desacoplar) ========================== #

class HttpClient(Protocol):
    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]: ...
    def post(self, url: str, json: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]: ...
    def put(self, url: str, json: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]: ...
    def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]: ...


# ======================== Camada de Infra: integração com API ======================== #

@dataclass(frozen=True)
class ApiConfig:
    base_url: str
    token: str


class ApiConnector:
    """Responsabilidade: conectar/autorizar e padronizar headers/URLs."""
    def __init__(self, config: ApiConfig, http: HttpClient) -> None:
        self._config = config
        self._http = http

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._config.token}"}

    def get(self, path: str) -> Dict[str, Any]:
        return self._http.get(f"{self._config.base_url}{path}", headers=self._headers())

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.post(f"{self._config.base_url}{path}", json=payload, headers=self._headers())

    def put(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.put(f"{self._config.base_url}{path}", json=payload, headers=self._headers())

    def delete(self, path: str) -> Dict[str, Any]:
        return self._http.delete(f"{self._config.base_url}{path}", headers=self._headers())


class TaskApiRepository:
    """Responsabilidade: CRUD de tasks na API (acesso a dados)."""
    def __init__(self, api: ApiConnector) -> None:
        self._api = api

    def create(self, title: str, description: str) -> Dict[str, Any]:
        return self._api.post("/tasks", {"title": title, "description": description})

    def update(self, task_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self._api.put(f"/tasks/{task_id}", fields)

    def remove(self, task_id: str) -> Dict[str, Any]:
        return self._api.delete(f"/tasks/{task_id}")

    def get(self, task_id: str) -> Dict[str, Any]:
        return self._api.get(f"/tasks/{task_id}")


# =================================== Notificações =================================== #

class NotificationService:
    """Responsabilidade: enviar notificações (e-mail, push, etc.)."""
    def send(self, user_id: str, message: str) -> None:
        # aqui entra SMTP, WhatsApp, Slack, etc.
        print(f"[NOTIFY] user={user_id} msg={message}")


# ==================================== Relatórios ==================================== #

class ReportGenerator:
    """Responsabilidade: montar o conteúdo do relatório."""
    def generate(self, tasks: list[Dict[str, Any]]) -> str:
        lines = ["RELATÓRIO DE TASKS", "-" * 20]
        for t in tasks:
            lines.append(f"- {t.get('title')} ({t.get('status', 'unknown')})")
        return "\n".join(lines)


class ReportSender:
    """Responsabilidade: enviar o relatório por algum canal."""
    def __init__(self, notifier: NotificationService) -> None:
        self._notifier = notifier

    def send(self, user_id: str, report_text: str) -> None:
        # poderia ser email com anexo, etc.
        self._notifier.send(user_id, f"Segue relatório:\n{report_text}")


# ====================== Caso de Uso / Orquestração (alto nível) ======================= #

class TaskService:
    """
    Responsabilidade: regras de negócio/orquestração de tasks.
    (Ele não faz HTTP direto, nem "sabe" como notificar ou reportar.)
    """
    def __init__(
        self,
        repo: TaskApiRepository,
        notifier: NotificationService,
        report_generator: ReportGenerator,
        report_sender: ReportSender,
    ) -> None:
        self._repo = repo
        self._notifier = notifier
        self._report_generator = report_generator
        self._report_sender = report_sender

    def create_task(self, user_id: str, title: str, description: str) -> Dict[str, Any]:
        self._validate_title(title)
        task = self._repo.create(title=title, description=description)
        self._notifier.send(user_id, f"Tarefa criada: {task.get('title', title)}")
        return task

    def update_task(self, user_id: str, task_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        task = self._repo.update(task_id, fields)
        self._notifier.send(user_id, f"Tarefa atualizada: {task_id}")
        return task

    def remove_task(self, user_id: str, task_id: str) -> None:
        self._repo.remove(task_id)
        self._notifier.send(user_id, f"Tarefa removida: {task_id}")

    def send_report(self, user_id: str, tasks: list[Dict[str, Any]]) -> None:
        report = self._report_generator.generate(tasks)
        self._report_sender.send(user_id, report)

    def _validate_title(self, title: str) -> None:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Título inválido")
