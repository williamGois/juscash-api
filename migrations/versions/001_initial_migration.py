"""Initial migration - Create publicacoes table

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Criar extensões PostgreSQL necessárias
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    
    # Criar tabela publicacoes
    op.create_table('publicacoes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('numero_processo', sa.String(length=50), nullable=False),
        sa.Column('data_disponibilizacao', sa.DateTime(), nullable=False),
        sa.Column('autores', sa.Text(), nullable=False),
        sa.Column('advogados', sa.Text(), nullable=False),
        sa.Column('conteudo_completo', sa.Text(), nullable=False),
        sa.Column('valor_principal_bruto', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('valor_principal_liquido', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('valor_juros_moratorios', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('honorarios_advocaticios', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('reu', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices
    op.create_index('idx_publicacoes_uuid', 'publicacoes', ['uuid'], unique=True)
    op.create_index('idx_publicacoes_numero_processo', 'publicacoes', ['numero_processo'], unique=True)
    op.create_index('idx_publicacoes_data_disponibilizacao', 'publicacoes', ['data_disponibilizacao'])
    op.create_index('idx_publicacoes_status', 'publicacoes', ['status'])
    op.create_index('idx_publicacoes_reu', 'publicacoes', ['reu'])
    op.create_index('idx_publicacoes_created_at', 'publicacoes', ['created_at'])
    
    # Índice composto para consultas otimizadas
    op.create_index('idx_publicacoes_status_data', 'publicacoes', ['status', 'data_disponibilizacao'])
    
    # Índices GIN para busca textual
    op.execute('CREATE INDEX idx_publicacoes_conteudo_gin ON publicacoes USING gin (conteudo_completo gin_trgm_ops)')
    op.execute('CREATE INDEX idx_publicacoes_autores_gin ON publicacoes USING gin (autores gin_trgm_ops)')
    op.execute('CREATE INDEX idx_publicacoes_advogados_gin ON publicacoes USING gin (advogados gin_trgm_ops)')
    
    # Adicionar constraints
    op.create_check_constraint('chk_status', 'publicacoes', "status IN ('nova', 'lida', 'processada')")
    
    # Criar função para atualizar updated_at
    op.execute('''
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    ''')
    
    # Criar trigger para atualizar updated_at automaticamente
    op.execute('''
        CREATE TRIGGER update_publicacoes_updated_at 
            BEFORE UPDATE ON publicacoes 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
    ''')
    
    # Adicionar comentários
    op.execute("COMMENT ON TABLE publicacoes IS 'Tabela para armazenar publicações extraídas do DJE'")
    op.execute("COMMENT ON COLUMN publicacoes.uuid IS 'Identificador único universal'")
    op.execute("COMMENT ON COLUMN publicacoes.numero_processo IS 'Número do processo judicial'")
    op.execute("COMMENT ON COLUMN publicacoes.data_disponibilizacao IS 'Data de disponibilização no DJE'")
    op.execute("COMMENT ON COLUMN publicacoes.status IS 'Status do processamento (nova, lida, processada)'")
    op.execute("COMMENT ON COLUMN publicacoes.conteudo_completo IS 'Conteúdo completo da publicação extraída'")


def downgrade():
    # Remover trigger
    op.execute('DROP TRIGGER IF EXISTS update_publicacoes_updated_at ON publicacoes')
    
    # Remover função
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')
    
    # Remover índices GIN
    op.execute('DROP INDEX IF EXISTS idx_publicacoes_conteudo_gin')
    op.execute('DROP INDEX IF EXISTS idx_publicacoes_autores_gin')
    op.execute('DROP INDEX IF EXISTS idx_publicacoes_advogados_gin')
    
    # Remover índices
    op.drop_index('idx_publicacoes_status_data', table_name='publicacoes')
    op.drop_index('idx_publicacoes_created_at', table_name='publicacoes')
    op.drop_index('idx_publicacoes_reu', table_name='publicacoes')
    op.drop_index('idx_publicacoes_status', table_name='publicacoes')
    op.drop_index('idx_publicacoes_data_disponibilizacao', table_name='publicacoes')
    op.drop_index('idx_publicacoes_numero_processo', table_name='publicacoes')
    op.drop_index('idx_publicacoes_uuid', table_name='publicacoes')
    
    # Remover tabela
    op.drop_table('publicacoes') 