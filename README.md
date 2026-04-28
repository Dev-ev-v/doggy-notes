# doggy-notes CLI

Fast note-taking in the terminal using JSON storage.

Create and manage notes quickly without leaving the command line.

## Features

- Create notes
- Delete single or multiple notes
- JSON storage
- Tag support
- Creation timestamps

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
doggy add
```

List notes

```bash
doggy list
```

Delete a note:

```bash
doggy delete 3
```

## Command Reference

| Command | Description |
|---------|-------------|
| add     | Create note |
| delete  | Delete note |
| list    | Show notes |

## Storage

Notes are stored locally in JSON.

Example structure:

```json
{
 "content":"Review argparse",
 "title":"Note",
 "description":"How to use argparse + examples"
 "tags":["python","cli"],
 "data":"2026-04-25"
}
```

## Roadmap

Planned:

- SQLite backend
- Search notes
- Edit notes
- Export notes
- Encryption
- Backup support
<Up>
## Why This Project

Built as a lightweight, fast and privacy-friendly terminal note manager.

## Contributing

Issues and suggestions welcome.
