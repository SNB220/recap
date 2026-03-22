# Recap

A lightweight CLI tool for saving and organizing quick reference notes for tools and utilities. Save tool-specific snippets by tool name and tags, search across all notes, and export your knowledge base.

## Features

- 💾 **Save notes** associated with specific tools and tags
- 🏷️ **Organize by tags** - Create categories like "basic", "advanced", "stealth_scans"
- 🔍 **Search** across all saved notes by keyword
- 📋 **List & View** all tags for a tool or display specific notes
- ✏️ **Interactive mode** - Save notes via prompts or use CLI flags
- 📤 **Export** your notes to Markdown or plain text files
- 🗑️ **Delete** tags and notes you no longer need
- 🔄 **Merge or replace** when updating existing tags

## Installation

```bash
# Clone or download this repository
cd recap

# No external dependencies required! Uses Python standard library only.
# Optional: Install for enhanced UI (future versions)
# pip install -r requirements.txt
```

## Setup: Run `recap` Without `python` Prefix

By default, you need to type `python main.py` before each command. Follow these platform-specific steps to use just `recap`:

### Option 1: Add to PATH (Recommended for all platforms)

#### Linux / macOS

1. **Make main.py executable:**
   ```bash
   chmod +x main.py
   ```

2. **Add the recap directory to your PATH:**
   
   Get the full path to your recap directory:
   ```bash
   pwd  # Copy this output
   ```
   
   Add to `~/.bashrc` or `~/.zshrc` (depending on your shell):
   ```bash
   export PATH="$PATH:/path/to/recap"
   ```
   
   Example (if your recap folder is at `/home/user/recap`):
   ```bash
   export PATH="$PATH:/home/user/recap"
   ```
   
   Then reload your shell:
   ```bash
   source ~/.bashrc   # or source ~/.zshrc
   ```

3. **Test it works:**
   ```bash
   recap --version
   recap save nmap -t basic -c "test"
   recap list nmap
   ```

#### Windows (PowerShell / CMD)

##### Method 1: Add to System PATH (Permanent)

1. Find your recap folder full path:
   ```cmd
   cd recap
   cd
   ```
   Copy the output (e.g., `C:\Users\YourName\Downloads\recap`)

2. **Add Python script to PATH (Admin privileges required):**
   - Press `Win + X` → Select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "User variables" or "System variables", click "New"
   - Variable name: `PATH`
   - Variable value: `C:\Python39` (or your Python installation path)
   - Click OK

3. **Create a batch wrapper (easier method):**
   
   Create a file called `recap.bat` in your recap folder:
   ```batch
   @echo off
   python "%~dp0main.py" %*
   ```
   
   Then add the recap folder to your PATH (steps above).
   
   Now you can use: `recap save nmap -t basic`

##### Method 2: Create Command Alias (Quick, per-session)

**PowerShell:**
```powershell
# Add to your PowerShell profile (opens it):
notepad $PROFILE

# Add this line:
Set-Alias -Name recap -Value "python C:\path\to\recap\main.py"

# Save and reload PowerShell
. $PROFILE
```

**CMD (Command Prompt):**
```cmd
# One-time per session:
doskey recap=python C:\path\to\recap\main.py $*

# Or create a DOSKEY macro file (more permanent)
```

##### Method 3: Use .py File Association (Simplest)

Windows can execute `.py` files directly if Python is in PATH:

```cmd
# Test from recap folder:
main.py save nmap -t basic

# If this works, create an alias:
doskey recap=main.py $*
```

### Option 2: Create Shell Alias (Quick Setup)

#### Linux / macOS

Add to your `~/.bashrc` or `~/.zshrc`:
```bash
alias recap='python /path/to/recap/main.py'
```

Reload your shell:
```bash
source ~/.bashrc
```

Then use:
```bash
recap save nmap -t basic
```

### Kali Linux / Python PEP 668 Restrictions

**Issue:** If you get `error: externally-managed-environment` when trying to install, your system prevents pip installations.

**Solution:** Create a virtual environment and wrapper script:

1. **Create and activate a virtual environment:**
   ```bash
   cd /home/kali/recap  # or your recap path
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install the package in the virtual environment:**
   ```bash
   pip install -e .
   deactivate
   ```

3. **Create a global wrapper script:**
   ```bash
   sudo nano /usr/local/bin/recap
   ```

   Paste this content:
   ```bash
   #!/bin/bash
   /home/kali/recap/venv/bin/python /home/kali/recap/main.py "$@"
   ```

   Save and exit (`Ctrl+X`, then `Y`, then `Enter`)

4. **Make it executable:**
   ```bash
   sudo chmod +x /usr/local/bin/recap
   ```

5. **Test it:**
   ```bash
   recap -h
   recap --version
   ```

Now you can use `recap` from anywhere without activating the venv!

#### Windows PowerShell

Add to your PowerShell profile:
```powershell
Set-Alias -Name recap -Value "python C:\path\to\recap\main.py" -Scope Global
```

### Option 3: Install as Global Command (Advanced)

Create `setup.py` in your recap folder and run `pip install -e .`:

1. **Create setup.py:**
   ```python
   from setuptools import setup
   
   setup(
       name='recap',
       version='1.0.0',
       py_modules=['main', 'cli', 'db', 'config'],
       entry_points={
           'console_scripts': [
               'recap=main:main',
           ],
       },
   )
   ```

2. **Install:**
   ```bash
   pip install -e .
   ```

3. **Now use globally:**
   ```bash
   recap save nmap -t basic
   ```

### Verify Your Setup

After any method above, test:
```bash
recap --version
recap --help
recap save test_tool -t verify -c "Setup successful!"
recap list test_tool
```

---

## Quick Start

### Save a note (interactive mode)
```bash
recap save nmap -t basic
# Prompts you to enter note content
```

### Save a note directly
```bash
recap save nmap -t basic -c "nmap -sV target.com  # Service version scan"
```

### List all tags for a tool
```bash
recap list nmap
```

### View notes for a specific tag
```bash
recap notes nmap -t basic
```

### Search across all notes
```bash
recap search "syn"
```

### Delete a tag
```bash
recap delete nmap -t basic
```

### Export all notes
```bash
recap export -f md -o my_notes.md
```

### Export notes for a specific tool
```bash
recap export nmap -f md -o nmap_notes.md
```

## Commands

### `save` - Save a note

```bash
recap save <tool_name> -t <tag_name> [-c <content>]
```

**Options:**
- `-t, --tag` (required): Tag name for organizing notes
- `-c, --content`: Note content (if not provided, interactive mode)

**Examples:**
```bash
# Interactive mode - you'll be prompted for content
recap save wireshark -t filters

# Direct mode - save content as argument
recap save wireshark -t filters -c "tcp.port==443  # HTTPS traffic"

# Append to existing tag
recap save nmap -t basic
# Will show: append/replace/cancel option
```

### `list` - List all tags for a tool

```bash
recap list <tool_name>
```

**Examples:**
```bash
recap list nmap
# Output:
# Tags for 'nmap':
#   1. advanced
#   2. basic
#   3. stealth_scans
```

### `notes` - Display notes for a specific tag

```bash
recap notes <tool_name> -t <tag_name>
```

**Examples:**
```bash
recap notes nmap -t basic
```

### `tags` - Show all tags for a tool (alternative to list)

```bash
recap tags <tool_name>
```

### `delete` - Delete a tag and all its notes

```bash
recap delete <tool_name> -t <tag_name>
```

**Examples:**
```bash
recap delete nmap -t old_notes
# Prompts for confirmation
```

### `search` - Search notes by keyword

```bash
recap search <keyword>
```

**Examples:**
```bash
recap search "UDP"
```

### `export` - Export notes to file

```bash
recap export [tool_name] [-f {md,txt}] [-o <output_file>]
```

**Options:**
- `-f, --format`: Export format - `md` (markdown) or `txt` (plain text). Default: md
- `-o, --output`: Output file path. Default: `recap_export.md`
- `tool_name` (optional): Specific tool to export; if omitted, exports all tools

**Examples:**
```bash
# Export all notes to markdown
recap export -o all_notes.md

# Export specific tool to text
recap export nmap -f txt -o nmap_ref.txt
```

## Use Cases

### Security Testing Reference
```bash
# Save common nmap commands
recap save nmap -t basic -c "nmap -sV -sC target.com"
recap save nmap -t stealth -c "nmap -sS -f -D decoy1 target.com"

# Save Wireshark filters
recap save wireshark -t filters -c "tcp.flags.syn==1 && tcp.flags.ack==0"

# View all your nmap notes
recap notes nmap -t basic
```

### Tool Documentation
```bash
# Build a personal reference library
recap save curl -t auth -c "curl -H 'Authorization: Bearer TOKEN' https://api"
recap save ffmpeg -t video -c "ffmpeg -i input.mp4 -vf scale=1280:-1 output.mp4"

# Export for sharing
recap export -o team_reference.md
```

### Quick Lookups
```bash
# Search for a specific technique
recap search "stealth"

# View all available tools
recap list all

# Compare your various tool tags
recap tags nmap
recap tags metasploit
```

## Database Location

Notes are stored in a SQLite database at `~/.recap/recap.db` (user's home directory).

**Example locations:**
- Windows: `C:\Users\YourUsername\.recap\recap.db`
- macOS/Linux: `/home/username/.recap/recap.db`

## Project Structure

```
recap/
├── main.py              # Entry point
├── cli.py               # Command parsing & execution
├── db.py                # Database operations
├── config.py            # Constants & configuration
├── requirements.txt     # Dependencies (optional)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## How It Works

### Database Schema

The tool uses SQLite with three tables:

- **tools**: Stores tool names (e.g., nmap, wireshark)
- **tags**: Stores tags per tool (e.g., "basic", "advanced")
- **notes**: Stores actual note content

```
tools
├── id
├── tool_name
└── created_at

tags
├── id
├── tool_id (→ tools.id)
├── tag_name
└── created_at

notes
├── id
├── tag_id (→ tags.id)
├── content
├── created_at
└── updated_at
```

### Workflow

1. **Save**: Create tool → Create tag → Store note content
2. **List**: Show all tags for a tool
3. **View**: Retrieve and display notes for tool+tag combo
4. **Search**: Find notes matching keyword across all tools
5. **Delete**: Remove tag and associated notes
6. **Export**: Generate markdown/text file from database

## Examples - Real Usage

### Example 1: Building a Nmap Reference

```bash
# Session 1: Save basic commands
recap save nmap -t basic
# Enter content:
# nmap -sV host.com           # Service version detection
# nmap -sC host.com           # Default scripts
# nmap -A host.com            # Aggressive scan

# Session 2: Save advanced techniques
recap save nmap -t advanced
# Enter content:
# nmap -sS -T3 host.com       # Stealth SYN scan
# nmap -O host.com            # OS detection
# nmap --script vuln host.com # Vulnerability scanning

# View your notes
recap list nmap
recap notes nmap -t advanced

# Search across all notes
recap search "SYN"
```

### Example 2: Team Knowledge Base

```bash
# Each team member saves their tool tips
recap save wireshark -t filters -c "tcp.port==443 && tcp.flags.syn==1"
recap save burp -t proxy -c "Set upstream proxy: Project Options > Connections"
recap save metasploit -t basics -c "use exploit/windows/smb/ms17_010_eternalblue"

# Export for sharing
recap export -o team_kb.md

# Share team_kb.md with team
```

### Example 3: Quick Lookup During Assessment

```bash
# Mid-assessment: "What's the syntax for nmap again?"
recap notes nmap -t basic

# "Let me search for UDP scan"
recap search "UDP"

# "Export my current notes for the report"
recap export nmap -f md -o assessment_notes.md
```

## Contributing

Have ideas for improvements? Future enhancements planned:

- Interactive UI with arrow key navigation
- Colored terminal output with `colorama`
- Fuzzy search with `fuzzywuzzy`
- Schema versioning & migrations
- Sync between machines (optional cloud backend)
- Multi-user support

## License

MIT

## Author

Created by SNB - A tool for quick reference note management during security assessments and tool learning.

---

**Happy learning!** 📚
