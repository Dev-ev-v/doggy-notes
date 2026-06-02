# CHANGELOG.md

## [2.2.0] - 2026-05-29

### Added
- Tags are now stored in a dedicated table, making searches faster, more precise, and consistent
- `--mode` option added to commands that use tag filters, supporting `AND` (default) or `OR` search modes
- `info` command now supports reading files and inspecting the directory structure of any doggy-notes path

### Changed
- `info` command now lists all doggy-notes paths for a more transparent view of the system
- `note_errors` refactored — each error now carries a code, message, and optional context, with clearer error names

### Fixed
- During a migration, notes from the previous package were not being deleted. Fixed
- During a migration, notes could be silently deleted if the package name matched an existing doggy-notes package. An explicit confirmation step has been added to prevent data loss
- Wrong field name in the `read` command caused silent failures. A warning is now raised when this occurs
- Tag searches were matching similar tags instead of exact ones. Fixed with the dedicated tags table

---

## [2.1.2] - 2026-05-24

### Added
- `schema_version` table added to automatically handle note structure upgrades in future versions
- `verbose` flag and internal logger added
- Directory structure placeholders created for export, logs and backup features (not yet available)

### Changed
- `read` and `list` commands now emit warnings instead of raising errors for non-critical issues, such as conflicting filter options
- `dependencies.py` is now used as a centralized import for all CLI commands, reducing repetition

### Fixed
- `--sort` with `--desc` now works correctly. Previously, `--desc` was always applied regardless of intent, making it impossible to sort ascending by date
- `--limit 0` is no longer accepted. The limit must now be a positive integer
- Wrong variable name in `delete.py` was producing a misleading error message. Fixed

---

## [2.1.1] - 2026-05-22

### Added
- GitHub release assets now work correctly — doggy-notes can be downloaded without the `.git` directory
- Classifiers and keywords updated in `pyproject.toml`

### Fixed
- Output was displaying times in UTC instead of the local timezone. Fixed

---

## [2.1.0] - 2026-05-20

### Added
- `edit` command added
- `read` command added
- Each command now has a complete help message with description, usage examples, and output samples
- `NoteParser` created to handle and validate user inputs
- `migrations` module added — ensures storage is created if it does not exist and prevents initialization failures
- `note_errors` introduced for structured, descriptive error handling
- Project paths centralized in `paths.py` — scripts no longer rely on hardcoded paths
- `--sort`, `--limit` and `--desc` options added to the `list` command
- `CHANGELOG.md` added

### Changed
- All commands that retrieve a note from storage now receive a unified model, making future API integration easier
- `NotePresenter` refactored — now handles formatting for both notes and error messages using Rich
- `platformdirs` adopted for cross-platform path resolution, replacing manual directory handling
- `service` is now responsible for fetching notes from storage and passing them to commands

### Fixed
- Storage initialization could fail silently in some environments. Fixed via the migrations module
- Duplicate `presenters` file removed
- README and help messages updated to reflect the current version

### Removed
- `storage` file removed — responsibilities absorbed by other modules
- `controller` file removed
- Unused imports cleaned up

## [2.0.1] - 2026-05-17

### Fixed
- App inicialization problem solved
- Nem functions added to improve `console`

---

## [2.0.0] - 2026-05-16

> ⚠️ **Breaking Change:** Storage migrated from JSON to SQLite.
> Existing notes are not automatically migrated yet. Back up your data before upgrading.

### Added
- SQLite storage replacing JSON for better scalability and query support
- `note_repository` created as an abstract layer over `sqlite_note_repository` to prevent implementation errors
- `note_errors` introduced — each error now has a specific message instead of a generic fallback
- `id` field added to the note structure
- Tags support added; notes can now be filtered by tags
- `list` command now accepts tag filters
- `Rich` added for better-formatted and visually cleaner output
- `CACHE_DIR`, `DATA_DIR` and `CONFIG_DIR` defined for future use
- GitHub Actions workflow created to publish automatically to PyPI on release
- `info` command now shows runtime information
- Personal contact email added to `pyproject.toml`
- Documentation and changelog URL added to `pyproject.toml`
- `version` file added to support downloadable GitHub release assets

### Changed
- Storage migrated from JSON to SQLite — better suited for larger datasets and more complex queries
- CLI commands now go through `use_cases` before reaching `services`, improving separation of responsibilities
- `serializer` replaced by `mappers` to reflect the SQLite-based storage model
- Output now goes through `console.py` instead of direct `print` calls
- `app.command()` replaced by `app.add_typer()` for a cleaner and more maintainable CLI structure
- `delete` command now uses note IDs instead of indexes
- Some files relocated for a more organized project structure

### Removed
- Automatic name generation removed from `note.py`
- `serializer` file removed
- Index-based system removed in favor of IDs

---

## [1.1.1] - 2026-05-02

### Added
- First release published to PyPI — the app can now be installed with `pip install doggy-notes`
- Intended audience and topic classifiers added to `pyproject.toml`
- Homepage and issue tracker URLs added to `pyproject.toml`

### Changed
- Version is now read dynamically, keeping the app version in sync with the Git tag and preventing manual versioning errors

### Fixed
- App name corrected in README examples

---

## [1.1.0] - 2026-05-02

### Added
- `--version` option added to display the current app version
- `info` command added with detailed app information
- Basic description added to every command
- `dependencies.py` created to centralize shared imports across commands

### Changed
- CLI restructured: commands moved out of `main.py` into dedicated files for clearer responsibility boundaries
- `argparse` replaced by `Typer` — better help output, automatic type validation, and a more maintainable structure
- Logs changed from Brazilian Portuguese to English as the project's official language

---

## [1.0.0] - 2026-04-28

### Added
- Apache 2.0 license added
- `README.md` added, covering features, usage examples, installation and roadmap
- Project renamed to `doggy-notes` in `pyproject.toml`
- First release published on GitHub

---

## [0.9.0] - 2026-04-21

### Added
- `presenters` file added to format output messages
- `delete` command now accepts multiple indexes at once
- Confirmation prompt added before deleting a note

### Changed
- `serializer` no longer creates storage files — that responsibility moved to `service`
- `timestamp` field renamed to `date` in the note structure
- `list` logic extracted into a separate function for clearer responsibility boundaries

### Fixed
- Import errors fixed

---

## [0.7.0] - 2026-04-20

### Changed
- `note` file split into `storage`, `serializer` and `repository` — the original file had too many responsibilities
- `note` is now an abstract model, not a storage or repository file
- Delete confirmation moved from `main` to the repository layer
- Author name updated in `pyproject.toml` to use account name instead of real name
- Storage directory path updated

### Added
- Notes now persist between sessions. Previously, data was stored only in memory with no persistence

### Removed
- `search` command removed — functionality overlapped with `list`, and the project scope did not justify maintaining both

---

## [0.1.0] - 2026-04-19

### Added
- `pyproject.toml` created
- Project organized into a `src/` directory structure

### Removed
- `edit` command removed due to implementation complexity