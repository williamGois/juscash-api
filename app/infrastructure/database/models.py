from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text
import uuid
import os

class PublicacaoModel(db.Model):
    __tablename__ = 'publicacoes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True)
    numero_processo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    data_disponibilizacao = db.Column(db.DateTime, nullable=False, index=True)
    autores = db.Column(db.Text, nullable=False)
    advogados = db.Column(db.Text, nullable=False)
    conteudo_completo = db.Column(db.Text, nullable=False)
    valor_principal_bruto = db.Column(db.Numeric(12, 2), nullable=True)
    valor_principal_liquido = db.Column(db.Numeric(12, 2), nullable=True)
    valor_juros_moratorios = db.Column(db.Numeric(12, 2), nullable=True)
    honorarios_advocaticios = db.Column(db.Numeric(12, 2), nullable=True)
    reu = db.Column(db.String(255), nullable=False, default="Instituto Nacional do Seguro Social - INSS", index=True)
    status = db.Column(db.String(20), nullable=False, default="nova", index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Apenas índices básicos no modelo - GIN será criado separadamente pelo create-tables.py
    __table_args__ = (
        db.Index('idx_publicacoes_status_data', 'status', 'data_disponibilizacao'),
        db.CheckConstraint("status IN ('nova', 'lida', 'processada')", name='chk_status'),
    )
    
    def __repr__(self):
        return f'<Publicacao {self.numero_processo}>'
    
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'numero_processo': self.numero_processo,
            'data_disponibilizacao': self.data_disponibilizacao.isoformat(),
            'autores': self.autores,
            'advogados': self.advogados,
            'conteudo_completo': self.conteudo_completo,
            'valor_principal_bruto': float(self.valor_principal_bruto) if self.valor_principal_bruto else None,
            'valor_principal_liquido': float(self.valor_principal_liquido) if self.valor_principal_liquido else None,
            'valor_juros_moratorios': float(self.valor_juros_moratorios) if self.valor_juros_moratorios else None,
            'honorarios_advocaticios': float(self.honorarios_advocaticios) if self.honorarios_advocaticios else None,
            'reu': self.reu,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 