'''
Created on 2014-11-3

@author: eluoyng
'''
# 完成通过由SQLAlchemy操作数据库
@require_admin_context
def document_get(context, document_id): 
    session = get_session()
    with session.begin():
        query = model_query(context, models.Document, session=session, read_deleted="yes").filter_by(id=document_id)
        result = query.first()
        if not result or not query:
            raise Exception()
        return result