class DeleteNotesUseCase:

    def __init__(self, service, resolver):
        self.service = service
        self.resolver = resolver


    def execute(
        self,
        notes,
    ):                
        deleted = []
        seen_ids = set()
        for note in notes:
            if note.id in seen_ids:
                continue
            self.service.add_to_trash(note)
            seen_ids.add(note.id)
            deleted.append(note)

        return deleted