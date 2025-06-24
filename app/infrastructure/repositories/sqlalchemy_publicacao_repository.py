from typing import List, Optional
from sqlalchemy import or_, and_, text
from app.domain.entities.publicacao import Publicacao
from app.domain.repositories.publicacao_repository import PublicacaoRepository
from app.infrastructure.database.models import PublicacaoModel
from app import db

class SQLAlchemyPublicacaoRepository(PublicacaoRepository):
    
    def create(self, publicacao: Publicacao) -> Publicacao:
        model = PublicacaoModel(
            numero_processo=publicacao.numero_processo,
            data_disponibilizacao=publicacao.data_disponibilizacao,
            autores=publicacao.autores,
            advogados=publicacao.advogados,
            conteudo_completo=publicacao.conteudo_completo,
            valor_principal_bruto=publicacao.valor_principal_bruto,
            valor_principal_liquido=publicacao.valor_principal_liquido,
            valor_juros_moratorios=publicacao.valor_juros_moratorios,
            honorarios_advocaticios=publicacao.honorarios_advocaticios,
            reu=publicacao.reu,
            status=publicacao.status
        )
        
        db.session.add(model)
        db.session.commit()
        
        return self._model_to_entity(model)
    
    def find_by_id(self, id: int) -> Optional[Publicacao]:
        model = PublicacaoModel.query.get(id)
        return self._model_to_entity(model) if model else None
    
    def find_by_numero_processo(self, numero_processo: str) -> Optional[Publicacao]:
        model = PublicacaoModel.query.filter_by(numero_processo=numero_processo).first()
        return self._model_to_entity(model) if model else None
    
    def find_all(self, limit: int = None, offset: int = None) -> List[Publicacao]:
        query = PublicacaoModel.query.order_by(PublicacaoModel.created_at.desc())
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        models = query.all()
        return [self._model_to_entity(model) for model in models]
    
    def find_by_status(self, status: str, limit: int = None, offset: int = None) -> List[Publicacao]:
        query = PublicacaoModel.query.filter_by(status=status).order_by(PublicacaoModel.created_at.desc())
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        models = query.all()
        return [self._model_to_entity(model) for model in models]
    
    def search_by_content(self, search_term: str, limit: int = 50) -> List[Publicacao]:
        """Busca por termo no conteúdo usando busca textual do PostgreSQL"""
        models = PublicacaoModel.query.filter(
            or_(
                PublicacaoModel.conteudo_completo.ilike(f'%{search_term}%'),
                PublicacaoModel.autores.ilike(f'%{search_term}%'),
                PublicacaoModel.advogados.ilike(f'%{search_term}%'),
                PublicacaoModel.numero_processo.ilike(f'%{search_term}%')
            )
        ).order_by(PublicacaoModel.created_at.desc()).limit(limit).all()
        return [self._model_to_entity(model) for model in models]
    
    def find_by_date_range(self, data_inicio, data_fim, status: str = None) -> List[Publicacao]:
        """Busca publicações por intervalo de datas"""
        query = PublicacaoModel.query.filter(
            and_(
                PublicacaoModel.data_disponibilizacao >= data_inicio,
                PublicacaoModel.data_disponibilizacao <= data_fim
            )
        )
        if status:
            query = query.filter_by(status=status)
        
        models = query.order_by(PublicacaoModel.data_disponibilizacao.desc()).all()
        return [self._model_to_entity(model) for model in models]
    
    def count_by_status(self) -> dict:
        """Retorna contagem de publicações por status"""
        result = db.session.query(
            PublicacaoModel.status,
            db.func.count(PublicacaoModel.id).label('count')
        ).group_by(PublicacaoModel.status).all()
        
        return {status: count for status, count in result}
    
    def update(self, publicacao: Publicacao) -> Publicacao:
        model = PublicacaoModel.query.get(publicacao.id)
        if not model:
            raise ValueError(f"Publicacao with id {publicacao.id} not found")
        
        model.numero_processo = publicacao.numero_processo
        model.data_disponibilizacao = publicacao.data_disponibilizacao
        model.autores = publicacao.autores
        model.advogados = publicacao.advogados
        model.conteudo_completo = publicacao.conteudo_completo
        model.valor_principal_bruto = publicacao.valor_principal_bruto
        model.valor_principal_liquido = publicacao.valor_principal_liquido
        model.valor_juros_moratorios = publicacao.valor_juros_moratorios
        model.honorarios_advocaticios = publicacao.honorarios_advocaticios
        model.reu = publicacao.reu
        model.status = publicacao.status
        
        db.session.commit()
        return self._model_to_entity(model)
    
    def delete(self, id: int) -> bool:
        model = PublicacaoModel.query.get(id)
        if not model:
            return False
        
        db.session.delete(model)
        db.session.commit()
        return True
    
    def _model_to_entity(self, model: PublicacaoModel) -> Publicacao:
        return Publicacao(
            id=model.id,
            numero_processo=model.numero_processo,
            data_disponibilizacao=model.data_disponibilizacao,
            autores=model.autores,
            advogados=model.advogados,
            conteudo_completo=model.conteudo_completo,
            valor_principal_bruto=float(model.valor_principal_bruto) if model.valor_principal_bruto else None,
            valor_principal_liquido=float(model.valor_principal_liquido) if model.valor_principal_liquido else None,
            valor_juros_moratorios=float(model.valor_juros_moratorios) if model.valor_juros_moratorios else None,
            honorarios_advocaticios=float(model.honorarios_advocaticios) if model.honorarios_advocaticios else None,
            reu=model.reu,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at
        ) 