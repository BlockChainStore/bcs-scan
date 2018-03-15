from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Model

class Event(Model):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50))
    tx_hash = Column(String(120), unique=True)
    block_number = Column(Integer,default=0)
    method = Column(String(50))
    param1 = Column(String(150))
    param2 = Column(String(120))
    param3 = Column(String(120))
    param4 = Column(String(120))
    param5 = Column(String(120))
    execution_success = Column(Boolean)
    timestamp = Column(DateTime)

    def __repr__(self):
        return '<Event %r, Method %r>' % (self.event_type, self.method)

class Storage(Model):
    __tablename__ = 'storage'
    id = Column(Integer, primary_key=True)
    key = Column(String(200), unique=True)
    data = Column(String(500))
    last_changed = Column(DateTime)

    def __repr__(self):
        return '<Key %r, Data %r>' % (self.key, self.data)
