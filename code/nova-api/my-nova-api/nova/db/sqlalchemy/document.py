class Document(BASE, NovaBase):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
