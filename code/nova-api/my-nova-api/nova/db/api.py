#数据操作API提供的方法，由Nova API 根据请求进行相应的操作， 由上面的请求控制器进行调用
def document_get(context, document_id):
    """Get a document or raise if it does not exist."""
    return IMPL.document_get(context, document_id)