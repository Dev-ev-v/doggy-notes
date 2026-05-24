# CHANGELOG.md

## [2.1.2] - 2026-05-24

### Added

- Export, logs and backup paths structure for future updates
- schema_version table created to update automatically older notes. Not useful now in the first version, but this will keep the storage working when I change the note structure for example.  A essencial feature in this project

### Changed

- Non dangerous commands (read and list) now warn the user instead of raise errors when something bad happens but not important, such as choosing two selection types at the same time for example
- dependencies.py used as a centralized import to cli commands.  This change remove desnecessary and repetitive import lines and make tests and changes easier

### Fixed

- Sort list works correctly in list command.  The sorting was broken because --desc was treated as a synonym for reverse, and since there was no --asc option, when sorting by date we always got the most recent entries at the top, there was no way to reverse that
- Previously, the limit could be equal to 0, resulting in a warning message.  Now limit must be higher than 0
- Variable "delete_all" confuded to "all" in delete.py file solved.  This problem was raising a wrong error message

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