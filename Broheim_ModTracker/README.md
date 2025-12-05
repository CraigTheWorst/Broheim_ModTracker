# Broheim Mod Tracker for Valheim

A comprehensive, cross-platform Python tool for managing and tracking Valheim mods installed through R2MODMAN. Export your mod lists to beautifully formatted spreadsheets and track changes over time.

---

## Table of Contents

1. [What This Tool Does](#what-this-tool-does)
2. [Installation](#installation)
3. [How R2MODMAN Stores Mod Data](#how-r2modman-stores-mod-data)
4. [How the Tool Works](#how-the-tool-works)
5. [Usage Guide](#usage-guide)
6. [File Output Format](#file-output-format)
7. [Comparison Feature](#comparison-feature)
8. [Troubleshooting](#troubleshooting)
9. [Technical Details](#technical-details)

---

## What This Tool Does

**Broheim Mod Tracker** helps you:

- ✅ **Export** your complete R2MODMAN mod list to CSV and ODS spreadsheet files
- ✅ **Organize** mods by author and alphabetically with color coding
- ✅ **Analyze** statistics about your mod collection (totals, top authors, newest/oldest mods)
- ✅ **Compare** different exports to track what changed (added, removed, updated mods)
- ✅ **Backup** your mod configurations in a readable format
- ✅ **Share** your mod lists with friends

**Key Features:**
- Cross-platform Linux support (Arch, Debian, Fedora, Ubuntu, etc.)
- Works with standard, alternative, and Flatpak R2MODMAN installations
- Color-coded spreadsheets by author (ODS format)
- Interactive menu system with easy navigation
- Comprehensive statistics at the top of each export
- Detailed comparison mode to track changes

---

## Installation

### Prerequisites

**Required:**
- Python 3.6 or newer (pre-installed on most Linux distributions)
- PyYAML library (usually pre-installed)
- R2MODMAN installed with at least one Valheim profile

**Optional (for ODS support):**
- python-odfpy library (for color-coded spreadsheets)

### Step 1: Verify Python Installation

```bash
python3 --version
```

You should see Python 3.6 or newer. If not, install Python:

**Arch Linux:**
```bash
sudo pacman -S python
```

**Debian/Ubuntu:**
```bash
sudo apt install python3
```

**Fedora:**
```bash
sudo dnf install python3
```

### Step 2: Install Dependencies

#### PyYAML (Required)

Check if installed:
```bash
python3 -c "import yaml; print('PyYAML: OK')"
```

If not installed:

**Arch Linux:**
```bash
sudo pacman -S python-yaml
```

**Debian/Ubuntu:**
```bash
sudo apt install python3-yaml
```

**Fedora:**
```bash
sudo dnf install python3-pyyaml
```

#### python-odfpy (Optional, for ODS files)

Check if installed:
```bash
python3 -c "import odf; print('odfpy: OK')"
```

If not installed:

**Arch Linux:**
```bash
sudo pacman -S python-odfpy
```

**Debian/Ubuntu:**
```bash
sudo apt install python3-odfpy
```

**Fedora:**
```bash
sudo dnf install python3-odfpy
```

### Step 3: Make the Script Executable

```bash
cd ~/Documents/Broheim_ModTracker
chmod +x Broheim_ModTracker.py
```

### Step 4: Run the Tool

```bash
python3 Broheim_ModTracker.py
```

Or, if executable:
```bash
./Broheim_ModTracker.py
```

---

## How R2MODMAN Stores Mod Data

Understanding where R2MODMAN stores its data helps explain how this tool works.

### R2MODMAN Directory Structure

R2MODMAN stores all mod data in one of these locations (the tool checks all of them):

**Standard Installation:**
```
~/.config/r2modmanPlus-local/
└── Valheim/
    ├── profiles/
    │   ├── Default/
    │   │   ├── mods.yml          ← All mod information
    │   │   ├── BepInEx/
    │   │   └── ...
    │   └── MODS-TEST/
    │       ├── mods.yml          ← All mod information
    │       ├── BepInEx/
    │       └── ...
    └── cache/
```

**Alternative Installation:**
```
~/.local/share/r2modmanPlus-local/Valheim/profiles/...
```

**Flatpak Installation:**
```
~/.var/app/com.github.ebkr.r2modmanPlus/config/r2modmanPlus-local/Valheim/profiles/...
```

### The mods.yml File

Each profile contains a `mods.yml` file that stores complete information about every installed mod:

```yaml
- manifestVersion: 1
  name: denikson-BepInExPack_Valheim
  authorName: denikson
  displayName: BepInExPack_Valheim
  description: "BepInEx pack for Valheim..."
  versionNumber:
    major: 5
    minor: 4
    patch: 2333
  enabled: true
  websiteUrl: https://thunderstore.io/c/valheim/p/denikson/BepInExPack_Valheim/
  # ... and many more fields
```

**Key Fields We Extract:**
- `authorName`: Mod creator's name
- `displayName`: User-friendly mod name
- `versionNumber`: Object containing major, minor, and patch version numbers
- `description`: Full description of what the mod does
- `enabled`: Whether the mod is currently active
- `websiteUrl`: Link to the mod's Thunderstore page

---

## How the Tool Works

### Step-by-Step Process

#### 1. Finding R2MODMAN Installation

When you run the tool, it first searches for your R2MODMAN installation:

```python
# Checks these paths in order:
1. ~/.config/r2modmanPlus-local/Valheim/profiles/
2. ~/.local/share/r2modmanPlus-local/Valheim/profiles/
3. ~/.var/app/com.github.ebkr.r2modmanPlus/config/r2modmanPlus-local/Valheim/profiles/
```

The first path that exists is used for all subsequent operations.

#### 2. Reading Profile Data

Once you select a profile, the tool:

1. **Constructs the path** to the profile's `mods.yml` file:
   ```
   {r2modman_base}/{profile_name}/mods.yml
   ```

2. **Parses the YAML** file using Python's `yaml.safe_load()`:
   ```python
   with open(mods_file, 'r', encoding='utf-8') as f:
       mods_data = yaml.safe_load(f)
   ```

3. **Extracts relevant data** from each mod entry:
   - Combines version numbers: `5.4.2333` from `{major: 5, minor: 4, patch: 2333}`
   - Converts boolean `enabled` to "Yes"/"No" for readability
   - Prefers `displayName` over internal `name`

#### 3. Calculating Statistics

The tool analyzes your mod collection to generate insights:

**Counts:**
- Total mods
- Enabled vs disabled mods
- Number of unique authors

**Top Authors:**
Uses Python's `Counter` to count mods per author and finds the top 5:
```python
author_counts = Counter(mod['author'] for mod in mods_list)
top_authors = author_counts.most_common(5)
```

**Newest/Oldest Mods:**
Sorts mods by version number (numerical comparison):
```python
# Convert "5.4.2333" to (5, 4, 2333) for proper sorting
version_tuple = tuple(int(p) for p in version.split('.'))
```

#### 4. Creating Export Files

**CSV File Structure:**
```
PROFILE STATISTICS
<blank line>
Profile Name:,MODS-TEST
Export Date:,Nov-30-2025 06:48PM
Total Mods:,112
Enabled Mods:,112
Disabled Mods:,0
Unique Authors:,39
<blank line>
TOP AUTHORS (by mod count)
blacks7ar,12 mods
Azumatt,11 mods
...
<blank line>
NEWEST MODS (by version)
Mod Name,Author,Version
YamlDotNet,ValheimModding,16.3.1
...
<blank line>
OLDEST MODS (by version)
Mod Name,Author,Version
MarlthonCore,Marlthon,0.0.2
...
<blank line>
COMPLETE MOD LIST
<blank line>
Author,Mod Name,Version,Enabled,Description,Website
Advize,PlantEasily,2.0.3,Yes,"Allows you to plant...",https://...
```

**ODS File Features:**
- Same structure as CSV
- Gray headers for sections
- Blue header for main mod list
- Each author's mods highlighted in a unique color (10 colors that cycle)
- Bold formatting for section titles

#### 5. File Organization

Files are saved to organized subdirectories:

```
Broheim_ModTracker/
├── csv_files/
│   ├── MODS-TEST_Nov-30-2025_06:48PM.csv
│   ├── MODS-TEST_Dec-01-2025_10:23AM.csv
│   └── buttsMD_Nov-30-2025_06:50PM.csv
└── ods_files/
    ├── MODS-TEST_Nov-30-2025_06:48PM.ods
    ├── MODS-TEST_Dec-01-2025_10:23AM.ods
    └── buttsMD_Nov-30-2025_06:50PM.ods
```

**Filename Format:**
```
{ProfileName}_{Month}-{Day}-{Year}_{Hour}:{Minute}{AM/PM}.{ext}
```

Example: `MODS-TEST_Nov-30-2025_06:48PM.csv`

- **ProfileName**: Your R2MODMAN profile name
- **Month**: 3-letter abbreviation (Jan, Feb, Mar, etc.)
- **Day**: 2-digit day (01-31)
- **Year**: 4-digit year
- **Time**: 12-hour format with AM/PM

This format is both human-readable and sortable chronologically.

---

## Usage Guide

### Main Menu

When you run the tool, you'll see:

```
============================================================
  Broheim Mod Tracker for Valheim
============================================================

=== Main Menu ===
  1. Export mod list
  2. Compare two exports
  3. Exit

Select option (1-3):
```

### Option 1: Export Mod List

**What it does:** Creates new CSV and ODS files with your current mod configuration.

**Steps:**

1. Select option `1`
2. Choose your profile from the list (or `0` to go back)
3. Wait for export to complete
4. Screen clears and shows success message with file locations
5. Press Enter to return to main menu

**Example:**
```
=== R2MODMAN Profile Selector ===

Available profiles:
  1. Default
  2. MODS-TEST
  3. buttsMD
  0. Go back

Select profile (0-3): 2

Loading mods from profile: MODS-TEST
Found 112 mods
Mods sorted by author and name

Exporting...
✓ CSV file created: MODS-TEST_Nov-30-2025_06:48PM.csv
✓ ODS file created: MODS-TEST_Nov-30-2025_06:48PM.ods
  Statistics: 112 total, 112 enabled, 39 authors

[Screen clears]

============================================================
  Export complete!
============================================================

Files saved:
  CSV: csv_files/MODS-TEST_Nov-30-2025_06:48PM.csv
  ODS: ods_files/MODS-TEST_Nov-30-2025_06:48PM.ods

Press Enter to return to main menu...
```

### Option 2: Compare Two Exports

**What it does:** Shows what changed between two different exports (mods added, removed, updated, or enabled/disabled).

**Use Cases:**
- Compare before/after mod updates
- See differences between two profiles
- Track changes over time
- Verify mod installations

**Steps:**

1. Select option `2`
2. Choose the first file (newer export)
3. Choose the second file (older export) or `0` to go back
4. View detailed comparison results
5. Press Enter to return to main menu

**Example:**
```
=== Available CSV files ===
  1. MODS-TEST_Dec-01-2025_10:23AM.csv (2025-12-01 10:23:15)
  2. MODS-TEST_Nov-30-2025_06:48PM.csv (2025-11-30 18:48:22)
  3. buttsMD_Nov-30-2025_06:50PM.csv (2025-11-30 18:50:33)
  0. Go back

Select two files to compare (or 0 to go back):
First file (newer): 1
Second file (older): 2

Comparing:
  Newer: MODS-TEST_Dec-01-2025_10:23AM.csv
  Older: MODS-TEST_Nov-30-2025_06:48PM.csv

[Screen clears]

============================================================
  COMPARISON RESULTS
============================================================

✓ ADDED MODS (3):
  + Epic Loot (by RandyKnapp) v0.9.14
  + Sailing (by RandyKnapp) v2.3.1
  + ValheimRAFT (by Spikethecat) v2.0.6

✗ REMOVED MODS (1):
  - OldMod (by SomeAuthor) v1.0.0

↑ VERSION UPDATES (5):
  ↑ Jotunn (by ValheimModding): 2.12.0 → 2.12.5
  ↑ BepInExPack_Valheim (by denikson): 5.4.2200 → 5.4.2333
  ↑ PlantEasily (by Advize): 2.0.2 → 2.0.3
  ↑ WardIsLove (by Azumatt): 3.7.0 → 3.7.1
  ↑ Seasonality (by RustyMods): 3.7.2 → 3.7.3

⚡ ENABLED/DISABLED (2):
  ⚡ SomeMod (by Author): DISABLED
  ⚡ AnotherMod (by Creator): ENABLED

============================================================
Summary: 3 added, 1 removed, 5 updated, 2 status changes
============================================================

Press Enter to return to main menu...
```

**Comparison Logic:**

The tool creates a unique key for each mod: `"Author:ModName"`

- **Added**: Keys in newer file but not in older file
- **Removed**: Keys in older file but not in newer file
- **Updated**: Same key in both, but different version number
- **Enabled/Disabled**: Same key in both, but different enabled status

### Option 3: Exit

Displays goodbye message and closes the program.

```
============================================================
  Thanks for using Broheim Mod Tracker!
============================================================
```

### Navigation Tips

- **Go Back**: Every sub-menu has a `0. Go back` option
- **Ctrl+C**: Returns to main menu gracefully (doesn't crash)
- **Enter**: After each operation, press Enter to return to main menu
- **Clear Screen**: Results are shown on a clean screen for better readability

---

## File Output Format

### CSV File

Standard comma-separated values file that works with any spreadsheet program.

**Advantages:**
- Universal compatibility
- Small file size
- Easy to parse programmatically
- Plain text (can edit with any text editor)

**Opens in:**
- LibreOffice Calc
- Microsoft Excel
- Google Sheets
- Any text editor

### ODS File

OpenDocument Spreadsheet with advanced formatting and color coding.

**Advantages:**
- Color-coded by author
- Beautiful formatting
- Section headers with background colors
- Professional appearance

**Color Coding:**
Each author gets a unique background color:
1. Light Blue (#E6F3FF)
2. Light Red (#FFE6E6)
3. Light Green (#E6FFE6)
4. Light Orange (#FFF4E6)
5. Light Purple (#F0E6FF)
6. Light Yellow (#FFFFE6)
7. Light Pink (#FFE6F0)
8. Light Cyan (#E6FFFF)
9. Light Brown (#F5E6D3)
10. Light Lavender (#E6E6FF)

Colors cycle if you have more than 10 authors.

**Opens in:**
- LibreOffice Calc (native format)
- Microsoft Excel
- Google Sheets
- Most spreadsheet programs

### Statistics Section

Both CSV and ODS files include a comprehensive statistics section at the top:

**Profile Information:**
- Profile name (e.g., "MODS-TEST")
- Export date and time

**Mod Counts:**
- Total number of mods
- How many are enabled
- How many are disabled
- Number of unique authors

**Top Authors:**
Shows the 5 authors with the most mods installed.

Example:
```
blacks7ar - 12 mods
Azumatt - 11 mods
Smoothbrain - 11 mods
OdinPlus - 8 mods
warpalicious - 8 mods
```

**Newest Mods:**
Shows the 5 mods with the highest version numbers.

Example:
```
Mod Name          Author              Version
YamlDotNet        ValheimModding      16.3.1
JsonDotNET        ValheimModding      13.0.4
HoneyPlus         OhhLoz              6.1.0
```

**Oldest Mods:**
Shows the 5 mods with the lowest version numbers.

Example:
```
Mod Name          Author              Version
MarlthonCore      Marlthon            0.0.2
ExplorersVision   Searica             0.1.1
StopChoppyAudio   Neobotics           0.1.2
```

This helps you identify:
- Potentially outdated mods
- Recently updated mods
- Your most-used mod authors

---

## Comparison Feature

### How Comparison Works

1. **Loads both CSV files**
2. **Finds the mod data section** (skips statistics)
3. **Creates unique keys** for each mod: `"Author:ModName"`
4. **Compares the sets** of mod keys
5. **Checks versions and status** for common mods
6. **Displays organized results** by category

### Comparison Categories

**✓ ADDED MODS**
Mods in the newer export that weren't in the older one.

**✗ REMOVED MODS**
Mods in the older export that aren't in the newer one.

**↑ VERSION UPDATES**
Mods that exist in both but have different version numbers.
Shows: `old_version → new_version`

**⚡ ENABLED/DISABLED**
Mods that exist in both but have different enabled status.
Shows whether the mod was ENABLED or DISABLED in the newer export.

### Use Cases

**Before/After Mod Updates:**
```bash
# Export before updating
1. Export mod list → MODS-TEST_Dec-01-2025_09:00AM.csv

# Update mods in R2MODMAN

# Export after updating
2. Export mod list → MODS-TEST_Dec-01-2025_10:00AM.csv

# Compare
3. Compare two exports → See what updated!
```

**Comparing Different Profiles:**
```bash
# Export first profile
1. Export "MODS-TEST" → MODS-TEST_Nov-30-2025_06:48PM.csv

# Export second profile
2. Export "buttsMD" → buttsMD_Nov-30-2025_06:50PM.csv

# Compare profiles
3. Compare exports → See the differences!
```

**Tracking Changes Over Time:**
```bash
# Keep exporting regularly
Monday:    MODS-TEST_Dec-01-2025_09:00AM.csv
Wednesday: MODS-TEST_Dec-03-2025_02:15PM.csv
Friday:    MODS-TEST_Dec-05-2025_05:30PM.csv

# Compare any two to see what changed
```

---

## Troubleshooting

### "R2MODMAN directory not found!"

**Problem:** Tool can't find your R2MODMAN installation.

**Solution:**
1. Make sure R2MODMAN is installed
2. Check if you have any Valheim profiles created in R2MODMAN
3. Verify the installation path:
   ```bash
   ls ~/.config/r2modmanPlus-local/Valheim/profiles/
   # or
   ls ~/.local/share/r2modmanPlus-local/Valheim/profiles/
   # or (Flatpak)
   ls ~/.var/app/com.github.ebkr.r2modmanPlus/config/r2modmanPlus-local/Valheim/profiles/
   ```

### "No profiles found!"

**Problem:** R2MODMAN directory exists but has no profiles.

**Solution:**
1. Open R2MODMAN
2. Make sure you've selected "Valheim" as the game
3. Create at least one profile (or use the Default profile)
4. Install at least one mod
5. Run the tool again

### "ODS export skipped (odfpy not installed)"

**Problem:** ODS files aren't being created.

**Solution:**
Install python-odfpy:
```bash
# Arch
sudo pacman -S python-odfpy

# Debian/Ubuntu
sudo apt install python3-odfpy

# Fedora
sudo dnf install python3-odfpy
```

CSV files will still be created without this dependency.

### "Need at least 2 CSV files to compare!"

**Problem:** You're trying to compare but only have one export.

**Solution:**
1. Export your mod list at least twice
2. Make changes to your mods (add, remove, update)
3. Export again
4. Now you can compare!

### Comparison shows no changes when there should be differences

**Problem:** You're comparing different profiles but seeing "No changes detected."

**Solution:**
This is actually working correctly! The comparison checks if the SAME mods changed between two exports. If you're comparing completely different profiles (like MODS-TEST vs buttsMD), they'll show up as all removed/all added.

To see meaningful comparisons:
- Compare the same profile at different times
- Compare before/after updating mods
- Compare after adding/removing specific mods

### Permission denied errors

**Problem:** Can't read R2MODMAN files or can't write exports.

**Solution:**
1. Make sure you own the Broheim_ModTracker folder:
   ```bash
   ls -la ~/Documents/ | grep Broheim_ModTracker
   ```

2. Fix permissions if needed:
   ```bash
   sudo chown -R $USER:$USER ~/Documents/Broheim_ModTracker
   chmod -R u+rw ~/Documents/Broheim_ModTracker
   ```

### YAML parsing errors

**Problem:** Error reading mods.yml file.

**Solution:**
1. R2MODMAN might have corrupted the file
2. Try exporting a different profile
3. In R2MODMAN, disable all mods, then re-enable them
4. If the problem persists, reinstall the problematic mods in R2MODMAN

---

## Technical Details

### Requirements

**Python Version:** 3.6 or newer

**Required Libraries:**
- `yaml` (PyYAML) - For parsing R2MODMAN's mods.yml files
- `csv` (built-in) - For creating CSV exports
- `pathlib` (built-in) - For cross-platform file path handling
- `datetime` (built-in) - For timestamps
- `collections` (built-in) - For counting and statistics

**Optional Libraries:**
- `odfpy` - For creating ODS (OpenDocument Spreadsheet) files with formatting

### File Locations

**Tool Location:**
```
~/Documents/Broheim_ModTracker/
├── Broheim_ModTracker.py  (main script)
├── README.md               (this file)
├── csv_files/              (CSV exports)
└── ods_files/              (ODS exports)
```

**R2MODMAN Data Location:**

Standard:
```
~/.config/r2modmanPlus-local/Valheim/profiles/{PROFILE_NAME}/mods.yml
```

Alternative:
```
~/.local/share/r2modmanPlus-local/Valheim/profiles/{PROFILE_NAME}/mods.yml
```

Flatpak:
```
~/.var/app/com.github.ebkr.r2modmanPlus/config/r2modmanPlus-local/Valheim/profiles/{PROFILE_NAME}/mods.yml
```

### Code Structure

The script is organized into logical sections:

1. **Imports and Setup** - Load required libraries
2. **R2MODMAN Detection** - Find installation location
3. **Data Loading** - Read and parse mods.yml
4. **Data Processing** - Extract and format mod information
5. **Statistics** - Calculate insights about mod collection
6. **Export Functions** - Create CSV and ODS files
7. **Comparison Functions** - Load and compare exports
8. **User Interface** - Interactive menus
9. **Main Loop** - Program flow control

Each function includes detailed docstrings explaining:
- What it does
- How it works
- What arguments it takes
- What it returns

### Performance

The tool is designed to be fast even with large mod collections:
- **100 mods**: Exports in ~1 second
- **200 mods**: Exports in ~2 seconds
- **500+ mods**: Should still be very quick

Comparison is also fast, even when comparing large exports.

### Safety

The tool is read-only and safe:
- ✅ Never modifies R2MODMAN files
- ✅ Never changes your mod installation
- ✅ Only reads from R2MODMAN directory
- ✅ Only writes to Broheim_ModTracker folder
- ✅ All operations are reversible (just delete exports)

---

## Tips and Best Practices

### Regular Exports

**Export regularly** to track your mod collection over time:
- Before major mod updates
- After installing new mods
- Weekly/monthly for historical tracking

### Naming Your Profiles

Use descriptive names in R2MODMAN:
- ❌ "Default", "Test", "New"
- ✅ "Vanilla-Plus", "Magic-Overhaul", "Building-Focused"

This makes exports easier to identify.

### Backup Strategy

CSV files serve as excellent backups:
1. Export your mod list
2. Save the CSV to cloud storage (Dropbox, Google Drive, etc.)
3. If you need to recreate your setup, use the CSV as reference

### Sharing With Friends

To share your mod list:
1. Export your profile
2. Send the CSV file (smaller than ODS)
3. Your friend can see exactly what mods you're using

Or use the ODS file if you want to show off the nice formatting!

### Comparison Workflow

**Best practice for tracking updates:**
```bash
# Weekly routine:
Monday: Export baseline
    → MODS-TEST_Dec-01-2025_09:00AM.csv

Friday: Update mods in R2MODMAN

Friday: Export after updates
    → MODS-TEST_Dec-05-2025_05:00PM.csv

Friday: Compare to see what updated
    → View all version changes
```

---

## Contributing

Found a bug? Have a feature request? Want to contribute?

The tool is designed to be easily extensible. The code is well-commented and organized into logical functions.

---

## Credits

**Created for managing Valheim mods with R2MODMAN across all Linux platforms.**

Built with:
- Python 3
- PyYAML
- python-odfpy (optional)

---

## License

Free to use and modify for personal use.

---

## Version History

**v1.0** - Initial release
- Export to CSV and ODS
- Statistics section
- Comparison mode
- Cross-platform Linux support
- Interactive menu system

---

**Happy modding! 🎮**
