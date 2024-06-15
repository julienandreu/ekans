import uuid

class with_request_id():
  def __init__(self, app):
        self.app = app
        
  def __call__(self, environ, start_response):
        def new_start_response(status, response_headers, exc_info=None):
            response_headers.append(('Request-Id', uuid.uuid4()))
            return start_response(status, response_headers, exc_info)

        return self.app(environ, new_start_response)