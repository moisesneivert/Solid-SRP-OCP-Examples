from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Dict, Type, runtime_checkable


# ================================================== DOMAIN ================================================== #

@runtime_checkable
class Exame(Protocol):
    """Contrato mínimo de um Exame no domínio."""
    @property
    def tipo(self) -> str: ...


class ValidadorExame(Protocol):
    """Policy: regra de aprovação para um exame específico."""
    def aprovar(self, exame: Exame) -> bool: ...
    def motivo_reprovacao(self, exame: Exame) -> str: ...


@dataclass(frozen=True)
class ExameSangue:
    hemacias: int
    leucocitos: int

    @property
    def tipo(self) -> str:
        return "sangue"


@dataclass(frozen=True)
class ExameRaioX:
    regiao: str
    tem_fratura: bool

    @property
    def tipo(self) -> str:
        return "raio-x"


class ValidadorSangue:
    def aprovar(self, exame: Exame) -> bool:
        assert isinstance(exame, ExameSangue)  # segurança em runtime
        return 5000 <= exame.leucocitos <= 17000 and exame.hemacias >= 3500000

    def motivo_reprovacao(self, exame: Exame) -> str:
        assert isinstance(exame, ExameSangue)
        problemas = []
        if not (5000 <= exame.leucocitos <= 17000):
            problemas.append("leucócitos fora da faixa")
        if exame.hemacias < 3500000:
            problemas.append("hemácias baixas")
        return ", ".join(problemas) if problemas else ""


class ValidadorRaioX:
    def aprovar(self, exame: Exame) -> bool:
        assert isinstance(exame, ExameRaioX)
        return not exame.tem_fratura

    def motivo_reprovacao(self, exame: Exame) -> str:
        assert isinstance(exame, ExameRaioX)
        return "fratura detectada" if exame.tem_fratura else ""


# ========================================== APPLICATION (USE CASE) ========================================== #

class ValidadorRegistry:
    """
    Resolve o validador baseado no *tipo* do exame, sem if/elif no use case.
    Extensão: basta registrar um novo validador.
    """
    def __init__(self) -> None:
        self._por_tipo: Dict[str, ValidadorExame] = {}

    def registrar(self, tipo: str, validador: ValidadorExame) -> None:
        self._por_tipo[tipo] = validador

    def obter(self, tipo: str) -> ValidadorExame:
        try:
            return self._por_tipo[tipo]
        except KeyError:
            raise ValueError(f"Não há validador registrado para o tipo: {tipo!r}")


class Auditoria(Protocol):
    def registrar_evento(self, mensagem: str) -> None: ...


class AuditoriaConsole:
    def registrar_evento(self, mensagem: str) -> None:
        print(f"[AUDITORIA] {mensagem}")


@dataclass(frozen=True)
class ResultadoAprovacao:
    aprovado: bool
    motivo: str = ""


class AprovacaoExameService:
    """
    Caso de uso: aprovar solicitação de exame.
    Depende de abstrações (registry + auditoria), não de tipos concretos.
    """
    def __init__(self, registry: ValidadorRegistry, auditoria: Auditoria) -> None:
        self._registry = registry
        self._auditoria = auditoria

    def aprovar(self, exame: Exame) -> ResultadoAprovacao:
        self._auditoria.registrar_evento(f"Início da análise do exame tipo={exame.tipo}")

        validador = self._registry.obter(exame.tipo)
        aprovado = validador.aprovar(exame)

        if aprovado:
            self._auditoria.registrar_evento(f"Exame tipo={exame.tipo} aprovado")
            return ResultadoAprovacao(aprovado=True)

        motivo = validador.motivo_reprovacao(exame)
        self._auditoria.registrar_evento(f"Exame tipo={exame.tipo} reprovado: {motivo}")
        return ResultadoAprovacao(aprovado=False, motivo=motivo)


# ============================== COMPOSITION ROOT (onde você “monta” o sistema) ============================== #

def montar_servico_aprovacao() -> AprovacaoExameService:
    registry = ValidadorRegistry()
    registry.registrar("sangue", ValidadorSangue())
    registry.registrar("raio-x", ValidadorRaioX())

    auditoria = AuditoriaConsole()
    return AprovacaoExameService(registry=registry, auditoria=auditoria)


# =============================== USO ==========

service = montar_servico_aprovacao()

r1 = service.aprovar(ExameSangue(hemacias=4200000, leucocitos=9000))
print("Resultado:", r1)

r2 = service.aprovar(ExameRaioX(regiao="tórax", tem_fratura=True))
print("Resultado:", r2)


# =============================== EXTENSÃO (NOVO EXAME) sem alterar o service =============================== #

@dataclass(frozen=True)
class ExameUltrassom:
    orgao: str
    achado_critico: bool

    @property
    def tipo(self) -> str:
        return "ultrassom"


class ValidadorUltrassom:
    def aprovar(self, exame: Exame) -> bool:
        assert isinstance(exame, ExameUltrassom)
        return not exame.achado_critico

    def motivo_reprovacao(self, exame: Exame) -> str:
        assert isinstance(exame, ExameUltrassom)
        return "achado crítico" if exame.achado_critico else ""


###### Só registra no composition root (ou via config/DI container) ######
service2 = montar_servico_aprovacao()
service2._registry.registrar("ultrassom", ValidadorUltrassom())  # em app real, evite acessar atributo "privado"

r3 = service2.aprovar(ExameUltrassom(orgao="fígado", achado_critico=True))
print("Resultado:", r3)
