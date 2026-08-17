Doggy Notes Architecture

1. Overview

Doggy Notes is a command-line note-taking application designed around a layered architecture.

The project separates user interaction, application workflows, core domain concepts, persistence, and presentation.

The main architectural areas are:

CLI
 │
 ▼
Application
 │
 ├── Application Services
 ├── Use Cases
 └── Domain abstractions / objects
 │
 ▼
Infrastructure
 │
 ▼
SQLite

Presentation components are used by the CLI to transform application results into human-readable output.

The architecture is intended to keep implementation details isolated while allowing the application to evolve without requiring every layer to change together.

---

2. Project Structure

The main package is organized into the following areas:

src/doggy_notes/
├── cli/
├── application/
├── domain/
├── infra/
├── presentation/
├── main.py
└── _version.py

"cli/"

Responsible for interaction with the user.

cli/
├── commands/
├── parsers/
├── console.py
├── dependencies.py
└── help_messages.py

The CLI:

- Defines commands using Typer.
- Parses command-line input.
- Converts user input into application-level objects.
- Requests application operations through use cases.
- Presents results and errors through the presentation layer.

CLI commands should remain thin. They should translate user interaction into application operations rather than implement application logic themselves.

---

3. Application Layer

The "application" package contains application workflows and orchestration.

application/
├── builders/
├── dto/
├── mappers/
├── queries/
├── services/
├── use_cases/
└── validation/

The application layer coordinates the different parts of Doggy Notes to perform user-requested operations.

It contains:

- Use cases.
- Application services.
- Query and selection logic.
- Application DTOs.
- Mappers.
- Application-level validation.
- Builders and other orchestration components.

The application layer should not depend on CLI-specific interaction details.

---

4. Use Cases

Use cases represent operations that the application can perform.

Current use cases include:

application/use_cases/
├── create_note.py
├── delete_notes.py
├── edit_note.py
├── export_notes.py
├── legacy_importer.py
├── list_notes.py
├── read_notes.py
└── trash_notes.py

A use case coordinates an operation rather than acting as a CLI command.

A typical use case may:

1. Receive already-parsed input.
2. Resolve or validate the requested notes.
3. Call application services.
4. Perform additional application-level processing.
5. Return a result to the caller.

The same application operation should not need to be reimplemented for every CLI command.

---

5. Application Services

Application services coordinate reusable application behavior.

The current application services include:

application/services/
├── note_service.py
├── editor_service.py
└── note_resolver.py

"NoteService"

"NoteService" is the main intermediary between note-related application operations and the note repository.

It is used by most note-related operations.

Its responsibilities include operations such as:

- Creating notes.
- Validating notes.
- Deleting notes.
- Moving notes to the trash.
- Performing note-related persistence operations.

The service hides persistence details from use cases and CLI commands.

"EditorService"

"EditorService" contains application-level logic related to editing notes.

It belongs to the application layer because it coordinates application behavior rather than representing a fundamental domain concept.

"NoteResolver"

"NoteResolver" provides generalized note selection.

Instead of requiring every command to understand all supported selection mechanisms, selection is normalized and resolved centrally.

The general flow is:

CLI input
   │
   ▼
CLI parsers
   │
   ▼
NoteSelector
   │
   ▼
NoteResolver
   │
   ▼
Query strategy
   │
   ▼
QueryResult

"NoteResolver" determines which selection strategy should be used and returns the resulting "QueryResult".

---

6. Dependency Injection and Composition

"cli/dependencies.py" is the composition root of the application.

It is responsible for constructing the application's object graph and providing ready-to-use dependencies to CLI commands.

The dependency structure includes components from multiple layers, such as:

- "SQLiteNoteRepository"
- "NoteService"
- "EditorService"
- "NoteResolver"
- Use cases
- Presenters
- Formatters
- CLI parsers
- Console

The main objects are:

DIContainer
    │
    ├── Infrastructure
    │     └── SQLiteNoteRepository
    │
    ├── Application
    │     ├── NoteService
    │     ├── EditorService
    │     ├── NoteResolver
    │     └── Use Cases
    │
    ├── Presentation
    │     ├── NotePresenter
    │     ├── FilePresenter
    │     ├── ErrorPresenter
    │     └── DateFormatter
    │
    └── CLI
          ├── Parsers
          └── Condole

"DIContainer" constructs these objects and caches them where appropriate.

"CommandDependencies" exposes the dependencies required by commands without requiring commands to construct them.

The intended command-side usage is conceptually:

Command
   │
   ▼
get_dependencies()
   │
   ▼
CommandDependencies
   │
   ├── use cases
   ├── parsers
   ├── presenters
   └── other CLI dependencies

This prevents commands from becoming responsible for constructing repositories, services, presenters, or other dependencies.

Why this exists

Without the composition root, a command could gradually become responsible for creating its entire dependency graph:

Command
 ├── creates repository
 ├── creates service
 ├── creates resolver
 ├── creates presenter
 └── creates use case

That would tightly couple the CLI to implementation details.

Instead:

Composition Root
 └── constructs application

Command
 └── consumes application

"dependencies.py" may grow as the application grows. Its responsibility is specifically to construct and connect components, not to contain business logic.

---

7. Domain Layer

The "domain" package contains concepts that define the identity of Doggy Notes.

domain/
├── config.py
├── dto/
├── entities/
├── enums/
├── exceptions/
├── repositories/
└── value_objects/

The domain should contain concepts that remain meaningful even if the application's interface or infrastructure is substantially refactored.

Entities

domain/entities/
├── node.py
└── note.py

"Note" is the primary domain entity.

Value Objects

domain/value_objects/
├── criterion.py
└── note_selector.py

Value objects represent structured concepts whose meaning is determined by their values.

Enums

Domain enums define concepts shared by the application, such as:

- File formats.
- Selection modes.
- Note fields.
- Sorting fields.
- Sort directions.

Repository Abstraction

domain/repositories/
└── note_repository.py

The domain defines the abstraction required to persist and retrieve notes.

The concrete SQLite implementation is kept outside the domain.

---

8. Note Selection

Note selection is centralized through "Criterion", "NoteSelector", "NoteResolver", and query strategies.

"Criterion"

A "Criterion" represents a selection criterion.

It contains:

value
exclude

The "exclude" flag allows a criterion to represent negative selection.

For example:

'!archived'

can represent a request to select notes that do not match the "archived" criterion.

The "!" prefix is parsed before reaching the application layer.

When using this syntax from a shell, the criterion should normally be enclosed in single quotes so that the shell does not interpret the value unexpectedly.

"NoteSelector"

"NoteSelector" provides a normalized representation of selection input.

It currently supports:

- ID selection.
- Tag selection.
- Title selection.
- AND/OR selection modes where supported.

A selector may contain only one selection category at a time:

IDs
OR
Tags
OR
Titles

This invariant is enforced by "NoteSelector".

Query Strategies

Query implementations are located under:

application/queries/
├── all_notes.py
├── by_ids.py
├── by_tags.py
├── by_titles.py
├── flatten_groups.py
└── strategies.py

The resolver selects the appropriate strategy rather than implementing every query directly.

---

9. Query Results

"QueryResult" represents the result of resolving a note selection.

Conceptually:

QueryResult
├── items
├── groups
└── filters

"items"

The notes returned by the query.

"groups"

Grouping information associated with the query.

For example, tag-based selection may require grouping information.

"filters"

Information about the criteria used to produce the result.

This can also be useful when reporting errors or explaining the result of a selection.

A "QueryResult" therefore carries more context than a simple list of notes.

---

10. Persistence and Infrastructure

The "infra" package contains concrete implementations and external concerns.

infra/
├── database/
├── logging/
├── persistence/
├── path_resolver.py
└── paths.py

Infrastructure is responsible for things such as:

- SQLite persistence.
- Database initialization.
- Database migrations.
- Filesystem paths.
- Logging.
- Concrete repository implementations.

SQLite

The current persistence mechanism is SQLite.

infra/database/
├── database_bootstrap.py
├── migrations.py
├── paths_migrations.py
└── schema.py

The database layer handles database initialization and schema evolution.

Repository Implementation

infra/persistence/
├── sqlite_note_repository.py
└── mappers/
    └── note_mapper.py

"SQLiteNoteRepository" implements the repository abstraction defined by the domain.

Its responsibility is to translate application/domain operations into SQLite operations.

The mapper handles conversion between persisted database representations and domain "Note" objects.

The relationship is:

Domain
  │
  │ repository abstraction
  ▼
NoteRepository
  ▲
  │ implementation
  │
SQLiteNoteRepository
  │
  ▼
SQLite database

SQLite-specific details should remain in infrastructure.

---

11. Trash and Permanent Deletion

Doggy Notes uses a database-backed trash system.

The trash is not a separate directory or database.

Instead, notes remain in the same SQLite database while being marked as trashed.

Conceptually:

SQLite database
├── active notes
└── trashed notes

Moving a note to the trash therefore does not immediately destroy its data.

The trash acts as a safety barrier before permanent deletion.

Permanent deletion is intentionally more restrictive than ordinary note operations:

- It requires explicit user intent.
- Notes must be identified by IDs.
- Confirmation is performed more strictly than for ordinary operations.
- The operation is treated as destructive and irreversible.

The trash is not automatically emptied.

This separation allows the normal "delete" operation to remain recoverable while reserving permanent deletion for an explicit user action.

---

12. User Feedback for Note Operations

Operations that affect notes are designed to provide explicit feedback to the user.

When notes are created, edited, moved, deleted, or otherwise affected, the application presents the affected notes and the number of affected notes whenever appropriate.

Conceptually:

Operation
   │
   ▼
Affected notes
   │
   ├── note information
   └── affected count
         │
         ▼
     Presenter
         │
         ▼
       User

This is an intentional UX decision rather than merely a formatting detail.

The goal is to make potentially important data operations observable and reduce ambiguity about what an operation actually affected.

---

13. Import and Export

Doggy Notes supports importing and exporting notes using multiple file formats.

Export

Supported export formats:

- JSON
- Markdown
- Plain text

The default export format is JSON.

The user can also choose the output path.

Import

Supported import formats:

- JSON
- Markdown

Plain text is currently export-only.

This distinction is important because exported ".txt" files cannot currently be imported back into Doggy Notes.

Import and export are application-level workflows rather than database operations.

Conceptually:

Export:

Notes
  │
  ▼
Export Use Case
  │
  ▼
Export Mapper
  │
  ▼
Selected format
  │
  ▼
Output file

Import:

Input file
  │
  ▼
Legacy / Import Use Case
  │
  ▼
Parsed notes
  │
  ▼
Application services
  │
  ▼
Repository
  │
  ▼
SQLite

Future changes may improve the user experience around destructive operations when the available export format cannot be imported.

---

14. Backup

Backups are stored separately from the main database under the application's backup directory.

The current backup system is not automatic.

Automatic backup support is planned for a future update.

The architecture should therefore treat backups as a separate persistence-safety mechanism rather than as part of normal note storage.

---

15. Application Paths

Doggy Notes uses "platformdirs" to determine platform-appropriate application directories.

Paths are resolved through the infrastructure layer rather than hardcoded into the application.

The logical path categories are:

config_dir
data_dir
cache_dir
backups_dir
exports_dir

The current data layout is conceptually:

data_dir/
├── doggy_notes.db
└── backups/

cache_dir/
└── doggy-notes.log

exports_dir/
└── exported files

The actual filesystem locations vary by operating system and environment.

For example, the application may use different locations on Linux, Windows, macOS, or Termux.

The "doggy path" command exposes the resolved paths and their contents to the user.

---

16. Logging

Doggy Notes has a logging subsystem under:

infra/logging/
└── logger.py

The logger records significant application events, particularly operations that can affect user data.

Examples include:

- Note creation.
- Note deletion.
- Other important persistence operations.
- Relevant database events.

Logging is intended to provide operational visibility and aid troubleshooting without replacing user-facing feedback.

The log is stored under the application's cache directory.

---

17. Presentation Layer

The "presentation" package handles human-readable output.

presentation/
├── formatters/
│   └── date_formatter.py
└── presenters/
    ├── error_presenter.py
    ├── file_presenter.py
    └── note_presenter.py

Presenters transform application results into output appropriate for the CLI.

Formatters handle focused presentation transformations, such as date formatting.

Presentation code should not contain application business logic.

The CLI's Rich-based console is responsible for terminal interaction, while presenters determine what information should be shown.

---

18. Error Handling

Doggy Notes uses "AppError" as the common application error abstraction.

The purpose is to prevent CLI commands from needing to import and understand every concrete error that may originate deeper in the application.

Conceptually:

AppError
   │
   └── specific application errors

Note-specific errors are defined in:

domain/exceptions/note_errors.py

These errors provide more precise information than generic exceptions such as "ValueError".

The CLI can handle the common error abstraction and delegate user-facing formatting to "ErrorPresenter".

Generic exceptions such as "ValueError" and "typer.Exit()" may still be used for small, local cases where a dedicated application error would add unnecessary complexity.

---

19. Dependency Direction

The project follows a dependency direction intended to prevent infrastructure and presentation details from leaking into core application concepts.

The general relationship is:

                Composition Root
                dependencies.py
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
       CLI       Presentation     Application
                                      │
                                      ▼
                                    Domain
                                      ▲
                                      │
                              Infrastructure

In practical terms:

- CLI commands depend on application operations and CLI-facing dependencies.
- The application layer coordinates use cases and services.
- Application code may use domain concepts and abstractions.
- Infrastructure provides concrete implementations of external concerns and repository abstractions.
- Domain code should not depend on Typer, Rich, SQLite, or CLI implementation details.
- Presentation should not implement application business rules.
- SQLite-specific behavior should remain in infrastructure.
- Dependency construction is centralized in "dependencies.py".

The exact dependency graph may evolve, but these boundaries are intended to remain stable.

---

20. Typical Command Flow

A normal note operation generally follows this structure:

User
 │
 ▼
Typer CLI command
 │
 ▼
CLI parser / input handling
 │
 ▼
Use case
 │
 ├── NoteResolver
 │      │
 │      └── Query strategy
 │              │
 │              └── QueryResult
 │
 └── Application Service
        │
        ▼
   NoteRepository
        │
        ▼
SQLiteNoteRepository
        │
        ▼
     SQLite

The resulting data then travels back through the application and presentation layers:

SQLite
  │
  ▼
Repository
  │
  ▼
Application result
  │
  ▼
Presenter / Formatter
  │
  ▼
Rich Console
  │
  ▼
User

Not every command uses every component. This diagram represents the general architecture rather than a mandatory execution path.

---

21. Architectural Principles

Keep commands thin

CLI commands should translate user interaction into application operations.

Centralize dependency construction

Objects required by commands should be assembled by the composition root rather than constructed independently inside each command.

Centralize note selection

Commands should not independently implement ID, tag, title, exclusion, and query-selection logic.

Hide persistence details

Application code should use repository abstractions instead of depending directly on SQLite.

Keep domain concepts independent

Core concepts should not depend on CLI, Rich, Typer, or SQLite.

Separate application workflows from domain concepts

Application services and use cases coordinate operations. Domain entities and value objects represent the core concepts of Doggy Notes.

Make destructive operations explicit

Operations that can permanently affect user data should have stronger safeguards than ordinary operations.

Make data operations observable

Operations affecting notes should provide clear user-facing feedback and relevant logging.

Keep external formats at the boundaries

Import and export formats should be handled at application/infrastructure boundaries rather than becoming part of the internal representation of notes.

---

22. What This File Does Not Document

This file describes the architecture, not every implementation detail.

The following should generally be documented elsewhere or kept close to the code:

- Installation instructions.
- Complete CLI command reference.
- Function-level documentation.
- Complete database schema details.
- Migration-by-migration history.
- Full import/export file specifications.
- Changelog entries.
- Individual parser implementation details.
- Internal helper functions.
- Exact logging statements.
- Detailed backup procedures.

"README.md" should primarily explain how users use and install Doggy Notes.

"CHANGELOG.md" should describe historical changes.

The source code should remain the authoritative source for implementation details.

---

23. Architectural Mental Model

When navigating the project, the following mental model should be sufficient:

"What did the user ask for?"
          │
          ▼
         CLI
          │
          ▼
"What operation should happen?"
          │
          ▼
      Use Case
          │
          ▼
"What application logic coordinates it?"
          │
          ├── NoteService
          ├── EditorService
          └── NoteResolver
                    │
                    ▼
              Query Strategy
                    │
                    ▼
               QueryResult
          │
          ▼
"What are the core concepts?"
          │
          ▼
        Domain
          │
          ▼
"How does the application interact with storage?"
          │
          ▼
     Infrastructure
          │
          ▼
        SQLite

When adding new functionality, the first architectural question should be:

«Which layer owns this responsibility?»

Only after that should implementation details be considered.

The goal is not to maximize the number of layers or abstractions. The goal is to keep responsibilities clear enough that the application can continue to evolve without every change propagating through the entire codebase.