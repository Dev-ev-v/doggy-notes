class ReadNotesUseCase:
 
    def __init__(self, service, resolver):
        self.service = service
        self.resolver = resolver
        
    def execute(self, selector):
    	result = self.resolver.resolve(selector)
    	return result