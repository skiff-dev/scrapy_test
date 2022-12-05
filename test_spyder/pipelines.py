from datetime import datetime
from itemadapter import ItemAdapter
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from .models import Author, Keyword, Quote, init_db


def get_session():
    init_db()
    engine = create_engine('sqlite:///test.db')
    return sessionmaker(bind=engine)


class RemoveQuotePipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'quote' in adapter.keys():
            adapter['quote'] = adapter['quote'].replace('“','').replace('”','').replace('\n','').strip()
        return item


class AddAuthorToDB():

    def process_item(self, item, spider):
        Session = get_session()
        adapter = ItemAdapter(item)
        if 'name' in adapter.keys():
            session = Session()
            a = Author(name= adapter['name'], birthday= datetime.strptime(adapter['birthdate'], '%B %d, %Y' ).date(), bio= adapter['bio'][:149])
            try:
                session.add(a)
                session.commit()
                session.close()
            except:
                session.close()
        return item


class AddKeywordToDB():

    def process_item(self, item, spider):
        Session = get_session()
        adapter = ItemAdapter(item)
        if 'keywords' in adapter.keys():
            session = Session()
            for word in adapter['keywords']:
                kw = Keyword(word = word)
                try:
                    session.add(kw)
                    session.commit()
                    session.close()
                except:
                    session.close()
        return item


class AddQuoteToDB():

    def process_item(self, item, spider):
        Session = get_session()
        adapter = ItemAdapter(item)
        if 'quote' in adapter.keys():
            session = Session()
            for author in adapter['author']:
                try:
                    a = session.execute(select(Author).where(Author.name == author)).scalar_one()
                    q = Quote(quote= adapter['quote'], author_id = a.id)
                    # for word in adapter['keywords']:
                    kws = session.execute(select(Keyword).where(Keyword.word.in_(adapter['keywords']))).all()
                    # print([kw[0] for kw in kws])
                    q.keywords = [kw[0] for kw in kws]
                    session.add(q)
                    session.commit()
                    session.close()
                except Exception as e:
                    print('Error in AddQuoteDB', e, item)
                    session.close()
        return item