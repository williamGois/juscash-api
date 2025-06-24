from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Publicacao:
    numero_processo: str
    data_disponibilizacao: datetime
    autores: str
    advogados: str
    conteudo_completo: str
    valor_principal_bruto: Optional[float] = None
    valor_principal_liquido: Optional[float] = None
    valor_juros_moratorios: Optional[float] = None
    honorarios_advocaticios: Optional[float] = None
    reu: str = "Instituto Nacional do Seguro Social - INSS"
    status: str = "nova"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None 