"""Configuration and constants for Recap Tool."""

import os
from pathlib import Path

# Database configuration
DB_DIR = Path.home() / ".recap"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "recap.db"

# Application metadata
APP_NAME = "Recap"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Save and organize quick reference notes for tools by tool name and tags"

# UI Messages
MESSAGES = {
    "welcome": f"Welcome to {APP_NAME} v{APP_VERSION}",
    "help": f"""
{APP_NAME} v{APP_VERSION}
{APP_DESCRIPTION}

USAGE:
    recap save <tool_name> -t <tag_name>        Save a new note for a tool with a tag
    recap list <tool_name>                      List all tags for a tool
    recap notes <tool_name> -t <tag_name>       Display notes for a tool and tag
    recap tags <tool_name>                      Show all tags for a tool
    recap delete <tool_name> -t <tag_name>      Delete a tag and its notes
    recap search <keyword>                      Search all notes by keyword
    recap --help                                Show this help message

FLAGS:
    -t, --tag <name>        Tag name for organizing notes
    -c, --content <text>    Direct content (non-interactive save)
    -q, --quick             Quick view mode
    --help                  Show help

EXAMPLES:
    recap save nmap -t basic
    recap list nmap
    recap notes nmap -t basic
    recap search "syn"
""",
}

# Database schema
DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_id INTEGER NOT NULL,
    tag_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools(id),
    UNIQUE(tool_id, tag_name)
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
"""
