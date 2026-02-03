from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


# 1) Interface (abstração): qualquer exame aprovável precisa expor estes métodos #
class ExameAprovavel(Protocol):
    def nome(self) -> str: ...
    def aprovar(self) -> bool: ...


# 2) Implementações (extensões): cada tipo de exame implementa a interface #
@dataclass(frozen=True)
class ExameSangue:
    hemacias: int
    leucocitos: int

    def nome(self) -> str:
        return "Exame de Sangue"

    def aprovar(self) -> bool:
        # regra exemplo: leucócitos dentro de uma faixa e hemácias não baixas #
        return 5000 <= self.leucocitos <= 17000 and self.hemacias >= 3500000


@dataclass(frozen=True)
class ExameRaioX:
    regiao: str
    tem_fratura: bool

    def nome(self) -> str:
        return "Raio-X"

    def aprovar(self) -> bool:
        # regra exemplo: aprova se não houver fratura #
        return not self.tem_fratura


# 3) “Aprovador” depende da abstração, não de if/elif por tipo #
class AprovadorExames:
    def aprovar_solicitacao(self, exame: ExameAprovavel) -> None:
        # lógica antes do approve (logs, auditoria, etc.) #
        print(f"Iniciando análise: {exame.nome()}")

        if exame.aprovar():
            print(f"{exame.nome()} aprovado!\n")
        else:
            print(f"{exame.nome()} reprovado.\n")


# 4) Uso #
aprovador = AprovadorExames()

exame_sangue = ExameSangue(hemacias=4200000, leucocitos=9000)
exame_raiox = ExameRaioX(regiao="tórax", tem_fratura=False)

aprovador.aprovar_solicitacao(exame_sangue)
aprovador.aprovar_solicitacao(exame_raiox)


# 5) Extensão (NOVO EXAME) — sem alterar AprovadorExames #
@dataclass(frozen=True)
class ExameUltrassom:
    orgao: str
    achado_critico: bool

    def nome(self) -> str:
        return "Ultrassom"

    def aprovar(self) -> bool:
        # regra exemplo: reprova se houver achado crítico #
        return not self.achado_critico


exame_ultrassom = ExameUltrassom(orgao="fígado", achado_critico=True)
aprovador.aprovar_solicitacao(exame_ultrassom)
