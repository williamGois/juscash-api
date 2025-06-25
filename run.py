import os
import click
from app import create_app, db
from app.infrastructure.database.models import PublicacaoModel

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, PublicacaoModel=PublicacaoModel)

@app.cli.command('init-migrations')
def init_migrations():
    """Initialize migration repository"""
    try:
        from flask_migrate import init
        init()
        click.echo('✅ Migration repository initialized!')
    except Exception as e:
        click.echo(f'❌ Error initializing migrations: {str(e)}')

@app.cli.command('create-migration')
def create_migration():
    """Create a new migration"""
    try:
        from flask_migrate import migrate as create_migrate
        create_migrate(message='Initial migration')
        click.echo('✅ Migration created!')
    except Exception as e:
        click.echo(f'❌ Error creating migration: {str(e)}')

@app.cli.command('upgrade-db')
def upgrade_db():
    """Run migrations to upgrade database"""
    try:
        from flask_migrate import upgrade
        upgrade()
        click.echo('✅ Database upgraded successfully!')
    except Exception as e:
        click.echo(f'❌ Error upgrading database: {str(e)}')

@app.cli.command('db-status')
def db_status():
    """Check database connection and tables"""
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        click.echo(f'✅ Database connected: {app.config["SQLALCHEMY_DATABASE_URI"]}')
        click.echo(f'📊 Tables: {", ".join(tables) if tables else "No tables found"}')
        
        if 'publicacoes' in tables:
            # Contar registros
            count = db.session.query(PublicacaoModel).count()
            click.echo(f'📝 Publicações: {count} registros')
    except Exception as e:
        click.echo(f'❌ Database error: {str(e)}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT')
    
    with app.app_context():
        try:
            # Testar conexão com o banco
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print('🎉 Banco PostgreSQL conectado!')
            if not is_railway:
                print('💡 Use "flask upgrade-db" para executar migrações')
        except Exception as e:
            print(f'❌ Erro ao conectar com PostgreSQL: {str(e)}')
            if not is_railway:
                print('💡 Certifique-se de que o PostgreSQL está rodando')
    
    # Configuração para Railway
    if is_railway:
        app.run(host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port) 