# CHANGELOG.md

## [2.1.1] - 2026-05-22

### Added

- You can now download doggy-notes without the .git file. Assets are now working
- Classifiers and keywords updated

### Fixed

- Previously, the UTC time zone was used as the default in the output, resulting in incorrect times. This issue has been resolved by using the local time zone

## [2.1.0] - 2026-05-20

### Added

- Edit function
- Read function
- Commands usage examples 
- Changelog.md added to help organize the project
- NoteParser created
- query_result created, useful to centralize the get function in services
- migrations created to create storage if it don't exist, be a more secure option to control the storage a ensure it will not close or show any problems
- note_errors created to resolve problems with personalized instructions
- Now the project paths are centralized in paths

### Changed

- Now every command that takes a note from storage receives a universal model, making it easier to use in future APIs or expand
- Basic help messages changed by complete help messages, with examples, output models and a better explanation 
- Better responsability control in NotePresenter

### Fixed

- Possible storage inicialization problem solved with migrations
- README updated to the actual version
- Help messages updated to the actual version

### Removed

- Unused storage file
- Some unused imports