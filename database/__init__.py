from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database import settings

engine = create_engine('sqlite:///db/bcs-db.db3', convert_unicode=True)
#engine = create_engine(settings.db_path, convert_unicode=settings.convert_unicode)
session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Model = declarative_base()
Model.query = session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from database.schema import Event ,Storage
    from sqlalchemy_utils import database_exists, create_database
    if not database_exists(engine.url):
        create_database(engine.url)

    Model.metadata.create_all(bind=engine)

