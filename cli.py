"""CLI command handling for Recap."""

import argparse
import sys
from typing import Optional
from db import Database
from config import MESSAGES, APP_VERSION


class RecapCLI:
    """Command-line interface for Panmen Tool Recap."""

    def __init__(self):
        """Initialize CLI with database."""
        self.db = Database()
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser."""
        parser = argparse.ArgumentParser(
            prog="recap",
            description=MESSAGES["help"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument("--version", action="version", version=f"%(prog)s {APP_VERSION}")

        subparsers = parser.add_subparsers(dest="command", help="Commands")

        # Save command
        save_parser = subparsers.add_parser("save", help="Save a note for a tool")
        save_parser.add_argument("tool", help="Tool name (e.g., nmap, wireshark)")
        save_parser.add_argument("-t", "--tag", required=True, help="Tag name for organizing notes")
        save_parser.add_argument(
            "-c", "--content", help="Note content (if not provided, interactive mode)"
        )

        # List command
        list_parser = subparsers.add_parser("list", help="List all tags for a tool")
        list_parser.add_argument("tool", help="Tool name")
        list_parser.add_argument(
            "-q", "--quick", action="store_true", help="Quick view mode"
        )

        # Notes command
        notes_parser = subparsers.add_parser("notes", help="Display notes for a tool and tag")
        notes_parser.add_argument("tool", help="Tool name")
        notes_parser.add_argument("-t", "--tag", required=True, help="Tag name")

        # Tags command
        tags_parser = subparsers.add_parser("tags", help="Show all tags for a tool")
        tags_parser.add_argument("tool", help="Tool name")

        # Delete command
        delete_parser = subparsers.add_parser("delete", help="Delete a tag and its notes")
        delete_parser.add_argument("tool", help="Tool name")
        delete_parser.add_argument("-t", "--tag", required=True, help="Tag name to delete")

        # Search command
        search_parser = subparsers.add_parser("search", help="Search all notes by keyword")
        search_parser.add_argument("keyword", help="Keyword to search for")

        # Export command
        export_parser = subparsers.add_parser("export", help="Export notes to a file")
        export_parser.add_argument(
            "tool", nargs="?", help="Tool name (optional; exports all if not specified)"
        )
        export_parser.add_argument("-f", "--format", choices=["md", "txt"], default="md", help="Export format")
        export_parser.add_argument("-o", "--output", help="Output file path")

        return parser

    def run(self, args: list = None) -> int:
        """Run CLI with given arguments. Returns exit code."""
        try:
            parsed_args = self.parser.parse_args(args)

            if not parsed_args.command:
                self.parser.print_help()
                return 0

            command = parsed_args.command
            if hasattr(self, f"cmd_{command}"):
                return getattr(self, f"cmd_{command}")(parsed_args)
            else:
                print(f"Unknown command: {command}")
                return 1

        except KeyboardInterrupt:
            print("\nAborted.")
            return 130
        except Exception as e:
            print(f"Error: {e}")
            return 1
        finally:
            self.db.close()

    # Command implementations
    def cmd_save(self, args) -> int:
        """Handle save command."""
        tool_name = args.tool.strip()
        tag_name = args.tag.strip()
        content = args.content

        if not tool_name or not tag_name:
            print("Error: Tool and tag names cannot be empty.")
            return 1

        # Get or create tool
        tool_id = self.db.get_or_create_tool(tool_name)

        # Check if tag exists
        tag_exists = self.db.tag_exists(tool_id, tag_name)

        if tag_exists and not content:
            # Prompt user for merge/replace
            choice = input(
                f"Tag '{tag_name}' already exists for '{tool_name}'. "
                "[a]ppend/[r]eplace/[c]ancel? "
            ).strip().lower()
            if choice == "c":
                print("Cancelled.")
                return 0
        elif not content:
            choice = "a"  # Default to append for new tags
        else:
            choice = "a"  # Append if content provided via CLI

        # Get or create tag
        tag_id = self.db.get_or_create_tag(tool_id, tag_name)

        # Get content if not provided
        if not content:
            print(f"Enter note content for {tool_name} / {tag_name} (press Enter twice to finish):")
            lines = []
            empty_count = 0
            while True:
                line = input()
                if line == "":
                    empty_count += 1
                    if empty_count >= 2:
                        break
                    lines.append(line)
                else:
                    empty_count = 0
                    lines.append(line)
            content = "\n".join(lines).rstrip()

        if not content:
            print("Error: Content cannot be empty.")
            return 1

        # Save or update note
        if tag_exists and choice == "a":
            # Append to existing notes
            existing = self.db.get_latest_note(tag_id) or ""
            combined = existing + "\n---\n" + content if existing else content
            self.db.update_note(tag_id, combined)
            print(f"✓ Appended note to {tool_name}/{tag_name}")
        elif tag_exists and choice == "r":
            # Replace existing notes
            self.db.update_note(tag_id, content)
            print(f"✓ Replaced note for {tool_name}/{tag_name}")
        else:
            # New tag
            self.db.save_note(tag_id, content)
            print(f"✓ Saved note to {tool_name}/{tag_name}")

        return 0

    def cmd_list(self, args) -> int:
        """Handle list command."""
        tool_name = args.tool.strip()

        if not self.db.tool_exists(tool_name):
            print(f"No notes found for tool '{tool_name}'.")
            return 0

        tool_id = self.db.get_or_create_tool(tool_name)
        tags = self.db.get_tags_for_tool(tool_id)

        if not tags:
            print(f"No tags found for tool '{tool_name}'.")
            return 0

        print(f"Tags for '{tool_name}':")
        for i, tag in enumerate(tags, 1):
            print(f"  {i}. {tag}")

        return 0

    def cmd_notes(self, args) -> int:
        """Handle notes command."""
        tool_name = args.tool.strip()
        tag_name = args.tag.strip()

        if not self.db.tool_exists(tool_name):
            print(f"Tool '{tool_name}' not found.")
            return 1

        tool_id = self.db.get_or_create_tool(tool_name)

        if not self.db.tag_exists(tool_id, tag_name):
            print(f"Tag '{tag_name}' not found for tool '{tool_name}'.")
            return 1

        cursor = self.db.execute(
            "SELECT id FROM tags WHERE tool_id = ? AND tag_name = ?",
            (tool_id, tag_name),
        )
        tag_id = cursor.fetchone()[0]

        notes = self.db.get_notes_for_tag(tag_id)

        if not notes:
            print(f"No notes found for {tool_name}/{tag_name}.")
            return 0

        print(f"\n{'='*60}")
        print(f"Notes: {tool_name} / {tag_name}")
        print(f"{'='*60}")
        for note in notes:
            print(note)
        print(f"{'='*60}\n")

        return 0

    def cmd_tags(self, args) -> int:
        """Handle tags command."""
        tool_name = args.tool.strip()

        if not self.db.tool_exists(tool_name):
            print(f"Tool '{tool_name}' not found.")
            return 1

        tool_id = self.db.get_or_create_tool(tool_name)
        tags = self.db.get_tags_for_tool(tool_id)

        if not tags:
            print(f"No tags found for tool '{tool_name}'.")
            return 0

        print(f"Tags for '{tool_name}':")
        for tag in tags:
            print(f"  • {tag}")

        return 0

    def cmd_delete(self, args) -> int:
        """Handle delete command."""
        tool_name = args.tool.strip()
        tag_name = args.tag.strip()

        if not self.db.tool_exists(tool_name):
            print(f"Tool '{tool_name}' not found.")
            return 1

        tool_id = self.db.get_or_create_tool(tool_name)

        if not self.db.tag_exists(tool_id, tag_name):
            print(f"Tag '{tag_name}' not found for tool '{tool_name}'.")
            return 1

        confirm = input(f"Delete '{tag_name}' from '{tool_name}'? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Cancelled.")
            return 0

        if self.db.delete_tag(tool_id, tag_name):
            print(f"✓ Deleted {tool_name}/{tag_name}")
            return 0
        else:
            print("Error: Failed to delete tag.")
            return 1

    def cmd_search(self, args) -> int:
        """Handle search command."""
        keyword = args.keyword.strip()

        if not keyword:
            print("Error: Keyword cannot be empty.")
            return 1

        results = self.db.search_notes(keyword)

        if not results:
            print(f"No notes found matching '{keyword}'.")
            return 0

        print(f"Search results for '{keyword}':")
        print(f"{'='*60}")

        for tool_name, tag_name, content in results:
            print(f"\n{tool_name} / {tag_name}:")
            print(f"{content[:200]}{'...' if len(content) > 200 else ''}")

        print(f"{'='*60}\n")
        return 0

    def cmd_export(self, args) -> int:
        """Handle export command."""
        tool_name = args.tool
        export_format = args.format
        output_file = args.output

        if not output_file:
            output_file = f"recap_export.{export_format}"

        try:
            with open(output_file, "w") as f:
                if export_format == "md":
                    self._export_markdown(f, tool_name)
                elif export_format == "txt":
                    self._export_text(f, tool_name)

            print(f"✓ Exported to {output_file}")
            return 0
        except Exception as e:
            print(f"Error exporting: {e}")
            return 1

    def _export_markdown(self, f, tool_name: Optional[str]):
        """Export notes to markdown format."""
        f.write("# Panmen Tool Recap Export\n\n")

        if tool_name:
            if not self.db.tool_exists(tool_name):
                f.write(f"Tool '{tool_name}' not found.\n")
                return

            tool_id = self.db.get_or_create_tool(tool_name)
            tags = self.db.get_tags_for_tool(tool_id)

            f.write(f"## {tool_name}\n\n")
            for tag in tags:
                cursor = self.db.execute(
                    "SELECT id FROM tags WHERE tool_id = ? AND tag_name = ?",
                    (tool_id, tag),
                )
                tag_id = cursor.fetchone()[0]
                notes = self.db.get_notes_for_tag(tag_id)

                f.write(f"### {tag}\n\n")
                for note in notes:
                    f.write(f"```\n{note}\n```\n\n")
        else:
            all_notes = self.db.get_all_notes_by_tag()
            current_tool = None

            for tool, tag, content in all_notes:
                if tool != current_tool:
                    current_tool = tool
                    f.write(f"## {tool}\n\n")

                f.write(f"### {tag}\n\n")
                f.write(f"```\n{content}\n```\n\n")

    def _export_text(self, f, tool_name: Optional[str]):
        """Export notes to text format."""
        f.write("RECAP EXPORT\n")
        f.write("=" * 60 + "\n\n")

        if tool_name:
            if not self.db.tool_exists(tool_name):
                f.write(f"Tool '{tool_name}' not found.\n")
                return

            tool_id = self.db.get_or_create_tool(tool_name)
            tags = self.db.get_tags_for_tool(tool_id)

            f.write(f"TOOL: {tool_name}\n")
            f.write("-" * 60 + "\n\n")

            for tag in tags:
                cursor = self.db.execute(
                    "SELECT id FROM tags WHERE tool_id = ? AND tag_name = ?",
                    (tool_id, tag),
                )
                tag_id = cursor.fetchone()[0]
                notes = self.db.get_notes_for_tag(tag_id)

                f.write(f"TAG: {tag}\n")
                for note in notes:
                    f.write(f"{note}\n")
                f.write("\n")
        else:
            all_notes = self.db.get_all_notes_by_tag()
            current_tool = None

            for tool, tag, content in all_notes:
                if tool != current_tool:
                    current_tool = tool
                    f.write(f"TOOL: {tool}\n")
                    f.write("-" * 60 + "\n\n")

                f.write(f"TAG: {tag}\n")
                f.write(f"{content}\n\n")
