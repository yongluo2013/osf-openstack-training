import webob
from webob import exc
from nova import exception
from nova.api.openstack import extensions
from docutils.nodes import document

documents = {"documents":[{"id":"1001", "name":"docs1"},
                                     {"id":"1002", "name":"docs2"},
                                     {"id":"1003", "name":"docs3"}]}
            
class DocumentsController():
        """the Documents API Controller declearation"""

        def index(self, req):
            '''
            GET v2/{tenant_id}/ os-documents
            '''
            return documents

        def show(self, req, id):
            '''
            GET v2/{tenant_id}/ os-documents/{document_id}

            '''
            document = None
            for docu in  documents["documents"]:
                if docu["id"] == id:
                     document = docu                    
            if document == None:
                 raise webob.exc.HTTPNotFound(explanation="Document not found")
            else:
                 return document
        
        def create(self, req, body):
            '''
            POST v2/{tenant_id}/os-documents 
            '''
            try:
                documents["documents"].append(body["document"])
            except :
                raise webob.exc.HTTPBadRequest(explanation="Document invalid")
            return body["document"]
            

        def update(self, req, body, id):
            '''
            PUT v2/{tenant_id}/os-documents/{document_id}
            '''
            document = None
            for docu in  documents["documents"]:
                if docu["id"] == id:
                    documents["documents"].remove(docu)
                    documents["documents"].append(body["document"])
                    document = body["document"]
            if document == None:
                 raise webob.exc.HTTPNotFound(explanation="Document not found")
            else:               
                return document

        def delete(self, req, id):
            '''
            DELETE v2/{tenant_id}/ os-documents/{document_id}
            '''
            document = None
            for docu in  documents["documents"]:
                if docu["id"] == id:
                     document = docu
                     documents["documents"].remove(docu)
                     return webob.Response(status_int=202)                
            if document == None:
                 raise webob.exc.HTTPNotFound(explanation="Document not found")

                

class Documents(extensions.ExtensionDescriptor):
        """Documents ExtensionDescriptor implementation"""

        name = "documents"
        alias = "os-documents"
        namespace = "www.doc.com"
        updated = "2014-10-19T00:00:00+00:00"

        def get_resources(self):
            """register the new Documents Restful resource"""

            resources = [extensions.ResourceExtension('os-documents',
                DocumentsController())
                ]

            return resources


