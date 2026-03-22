"""Database operations for Recap."""

import sqlite3
from typing import List, Optional, Tuple
from config import DB_PATH, DB_SCHEMA


class Database:
    """SQLite database manager for tools, tags, and notes."""

    def __init__(self):
        """Initialize database connection and schema."""
        self.db_path = DB_PATH
        self.connection = None
        self.init_db()

    def connect(self):
        """Create or return database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def init_db(self):
        """Initialize database schema."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executescript(DB_SCHEMA)
        conn.commit()
        cursor.close()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        """Commit database changes."""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """Rollback database changes."""
        if self.connection:
            self.connection.rollback()

    # Tool operations
    def get_or_create_tool(self, tool_name: str) -> int:
        """Get tool ID or create if doesn't exist. Returns tool_id."""
        cursor = self.execute(
            "SELECT id FROM tools WHERE tool_name = ?", (tool_name,)
        )
        row = cursor.fetchone()

        if row:
            return row[0]

        cursor = self.execute("INSERT INTO tools (tool_name) VALUES (?)", (tool_name,))
        self.commit()
        return cursor.lastrowid

    def tool_exists(self, tool_name: str) -> bool:
        """Check if a tool exists."""
        cursor = self.execute(
            "SELECT id FROM tools WHERE tool_name = ?", (tool_name,)
        )
        return cursor.fetchone() is not None

    def get_all_tools(self) -> List[str]:
        """Get all tool names."""
        cursor = self.execute("SELECT tool_name FROM tools ORDER BY tool_name")
        return [row[0] for row in cursor.fetchall()]

    # Tag operations
    def get_or_create_tag(self, tool_id: int, tag_name: str) -> int:
        """Get tag ID or create if doesn't exist. Returns tag_id."""
        cursor = self.execute(
            "SELECT id FROM tags WHERE tool_id = ? AND tag_name = ?",
            (tool_id, tag_name),
        )
        row = cursor.fetchone()

        if row:
            return row[0]

        cursor = self.execute(
            "INSERT INTO tags (tool_id, tag_name) VALUES (?, ?)",
            (tool_id, tag_name),
        )
        self.commit()
        return cursor.lastrowid

    def tag_exists(self, tool_id: int, tag_name: str) -> bool:
        """Check if a tag exists for a tool."""
        cursor = self.execute(
            "SELECT id FROM tags WHERE tool_id = ? AND tag_name = ?",
            (tool_id, tag_name),
        )
        return cursor.fetchone() is not None

    def get_tags_for_tool(self, tool_id: int) -> List[str]:
        """Get all tag names for a tool."""
        cursor = self.execute(
            "SELECT tag_name FROM tags WHERE tool_id = ? ORDER BY tag_name",
            (tool_id,),
        )
        return [row[0] for row in cursor.fetchall()]

    def delete_tag(self, tool_id: int, tag_name: str) -> bool:
        """Delete a tag and all its notes. Returns True if successful."""
        cursor = self.execute(
            "SELECT id FROM tags WHERE tool_id = ? AND tag_name = ?",
            (tool_id, tag_name),
        )
        tag_row = cursor.fetchone()

        if not tag_row:
            return False

        tag_id = tag_row[0]
        self.execute("DELETE FROM notes WHERE tag_id = ?", (tag_id,))
        self.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        self.commit()
        return True

    # Note operations
    def save_note(self, tag_id: int, content: str) -> int:
        """Save a note for a tag. Returns note_id."""
        cursor = self.execute(
            "INSERT INTO notes (tag_id, content) VALUES (?, ?)", (tag_id, content)
        )
        self.commit()
        return cursor.lastrowid

    def get_notes_for_tag(self, tag_id: int) -> List[str]:
        """Get all note contents for a tag."""
        cursor = self.execute(
            "SELECT content FROM notes WHERE tag_id = ? ORDER BY created_at",
            (tag_id,),
        )
        return [row[0] for row in cursor.fetchall()]

    def get_latest_note(self, tag_id: int) -> Optional[str]:
        """Get the most recent note for a tag."""
        cursor = self.execute(
            "SELECT content FROM notes WHERE tag_id = ? ORDER BY created_at DESC LIMIT 1",
            (tag_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all_notes_by_tag(self) -> List[Tuple[str, str, str]]:
        """Get all notes grouped by tool and tag. Returns list of (tool_name, tag_name, content)."""
        cursor = self.execute(
            """
            SELECT tools.tool_name, tags.tag_name, notes.content
            FROM notes
            JOIN tags ON notes.tag_id = tags.id
            JOIN tools ON tags.tool_id = tools.id
            ORDER BY tools.tool_name, tags.tag_name
        """
        )
        return cursor.fetchall()

    def search_notes(self, keyword: str) -> List[Tuple[str, str, str]]:
        """Search notes by keyword. Returns list of (tool_name, tag_name, content)."""
        cursor = self.execute(
            """
            SELECT tools.tool_name, tags.tag_name, notes.content
            FROM notes
            JOIN tags ON notes.tag_id = tags.id
            JOIN tools ON tags.tool_id = tools.id
            WHERE notes.content LIKE ? OR tags.tag_name LIKE ?
            ORDER BY tools.tool_name, tags.tag_name
        """,
            (f"%{keyword}%", f"%{keyword}%"),
        )
        return cursor.fetchall()

    def update_note(self, tag_id: int, content: str) -> int:
        """Update a note's content. If multiple notes exist, updates the latest."""
        cursor = self.execute(
            "SELECT id FROM notes WHERE tag_id = ? ORDER BY created_at DESC LIMIT 1",
            (tag_id,),
        )
        row = cursor.fetchone()

        if row:
            note_id = row[0]
            self.execute(
                "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (content, note_id),
            )
            self.commit()
            return note_id

        # If no note exists, create one
        return self.save_note(tag_id, content)
