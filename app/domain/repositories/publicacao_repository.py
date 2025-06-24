from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.publicacao import Publicacao

class PublicacaoRepository(ABC):
    
    @abstractmethod
    def create(self, publicacao: Publicacao) -> Publicacao:
        pass
    
    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Publicacao]:
        pass
    
    @abstractmethod
    def find_by_numero_processo(self, numero_processo: str) -> Optional[Publicacao]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Publicacao]:
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[Publicacao]:
        pass
    
    @abstractmethod
    def update(self, publicacao: Publicacao) -> Publicacao:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass 