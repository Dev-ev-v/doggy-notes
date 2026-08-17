class TrashNotesUseCase:

    def __init__(self, service, resolver):
        self.service = service
        self.resolver = resolver

    def restore(
        self,
        notes,
    ):   
        for note in notes:
        	self.service.restore_from_trash(note)
        	    
    def delete(
        self,
        notes,
    ):        
        for note in notes:
        	self.service.delete(note)                                                