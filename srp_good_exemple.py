# srp_good_example.py
# SRP atendido
# Organização fraca para manutenção
# Escalabilidade ruim

# Mas funciona perfeitamente.

class ApiConnector:
    def connect(self):
        print("Conectando na API...")


class TaskRepository:
    def create(self):
        print("Criando task")

    def update(self):
        print("Atualizando task")

    def remove(self):
        print("Removendo task")


class NotificationService:
    def send(self, message: str):
        print(f"Notificação enviada: {message}")


class ReportGenerator:
    def generate(self):
        print("Gerando relatório")


class ReportSender:
    def send(self):
        print("Enviando relatório")


class TaskService:
    def __init__(
        self,
        repo: TaskRepository,
        notifier: NotificationService,
        report_generator: ReportGenerator,
        report_sender: ReportSender,
    ):
        self.repo = repo
        self.notifier = notifier
        self.report_generator = report_generator
        self.report_sender = report_sender

    def create_task(self):
        self.repo.create()
        self.notifier.send("Task criada")

    def send_report(self):
        self.report_generator.generate()
        self.report_sender.send()
