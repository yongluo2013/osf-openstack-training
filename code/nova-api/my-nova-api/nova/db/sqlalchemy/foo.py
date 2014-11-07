from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean

sql_connection = "mysql://root:root@localhost/test?charset=utf8" 
engine = create_engine(sql_connection, echo=True) 
Session = sessionmaker(bind=engine)
session = Session()

class NovaBase():
    pass

BASE = declarative_base() 

class InstanceTypes(BASE, NovaBase):
    __tablename__ = "instance_types" 
    id = Column(Integer, primary_key=True) 
    name = Column(String(255))
    memory_mb = Column(Integer)
    vcpus = Column(Integer)
    root_gb = Column(Integer)
    ephemeral_gb = Column(Integer)
    flavorid = Column(String(255))
    swap = Column(Integer, nullable=False, default=0)
    rxtx_factor = Column(Float, nullable=False, default=1)
    vcpu_weight = Column(Integer, nullable=True)
    disabled = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)

flavors = session.query(InstanceTypes).all()
for flavor in flavors:
    print flavor.id, flavor.name