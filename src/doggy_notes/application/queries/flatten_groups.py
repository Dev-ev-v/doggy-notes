def flatten_groups(groups: dict) -> list:
	items = []
	for value in groups.values():
		if isinstance(value, list):
			items.extend(value)
		elif value is not None:
			items.append(value)
	return items