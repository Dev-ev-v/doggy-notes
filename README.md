# doggy-notes CLI

Fast note-taking in the terminal using SQLite storage.

Create and manage notes quickly without leaving the command line.

## Features

- Create notes
- Delete single or multiple notes
- Confirmation before deletion
- Note search
- SQLite storage
- Tag support
- Creation timestamps
- Read notes in details
- Edit notes

## Installation

Clone the repository:

```bash
git clone https://github.com/Dev-ev-v/doggy-notes.git
cd doggy-notes
```

Install:

```bash
pip install .
```

Or:

```bash
pip install doggy-notes
```

## Quick Start

Create a note:

```bash
doggy add "your text here"
```

List notes

```bash
doggy list
```

Delete a note:

```bash
doggy delete <index>
```

## Command Reference

| Command | Description |
|---------|-------------|
| add     | Create note |
| delete  | Delete note |
| list    | Find notes |
| read  | Show notes details |
| edit  | Edit notes |

## Storage

Notes are stored locally in SQLite.

Example structure:

```note
{
 "content":"Review argparse",
 "title":"Note",
 "description":"How to use argparse + examples"
 "tags":["python","cli"],
 "date":"2026-04-25"
}
```

## Roadmap

Planned:

- Export notes
- Import notes
- Encryption
- Backup support
- README support
- Filter notes dedicated function
- Personalizations

## Why This Project

Built as a lightweight, fast and privacy-friendly terminal note manager.

## Contributing

Issues and suggestions welcome.