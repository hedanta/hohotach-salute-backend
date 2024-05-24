from sqlalchemy import select
import sqlalchemy as db 
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
from models import Joke


class JokeLoader:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        
    def _generate_alias(
        self,
        content: str
    ):
        alias = content[:20]
        for i in range(19):
            if alias[i] == '\n':
                if i == 18:
                    alias = alias[:i-1]
                else:
                    alias = alias[:i-1] + ' ' + alias[i+1:]
        alias += "..."
        return alias
    
    def load_data_to_db(self, df: pd.DataFrame):
        ''' Загружает всех клиентов из датафрейма df ''' 
        jokes = df.query('target == 1')['text'].to_list()
        
        for joke in jokes:
            new_joke = Joke(content=joke, alias = self._generate_alias(joke))

            existing_joke_query = select(Joke).filter_by(content=joke)
            result = self.db_session.execute(existing_joke_query)
            existing_joke = result.scalar()

            if not existing_joke:
                self.db_session.add(new_joke)

        self.db_session.flush()  # flush is used here to get the ID if needed immediately after

if __name__ == '__main__':
    engine = db.create_engine("postgresql+psycopg2://user:password@localhost/db",
                              execution_options={"isolation_level": "AUTOCOMMIT"})

    Session = sessionmaker() 
    Session.configure(bind=engine) 
    session = Session()

    df = pd.read_csv('markup_df_v2.csv')

    loader = JokeLoader(session)

    loader.load_data_to_db(df)
