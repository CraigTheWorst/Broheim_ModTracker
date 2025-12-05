#!/usr/bin/env python3
"""
Broheim Mod Tracker for Valheim
Extracts mod information from R2MODMAN profiles and creates CSV/ODS spreadsheets
Cross-platform support for Linux distributions
"""

import os
import sys
import yaml
import csv
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

# Try to import ODS library
try:
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.style import Style, TableCellProperties, TextProperties
    from odf.text import P
    from odf.table import Table, TableColumn, TableRow, TableCell
    HAS_ODF = True
except ImportError:
    HAS_ODF = False
    print("Warning: odfpy not installed. ODS export will not be available.")
    print("Install with your package manager or: pip install odfpy")


def find_r2modman_base():
    """
    Find R2MODMAN directory across different Linux distributions.

    R2MODMAN stores its data in different locations depending on how it was installed:
    - Standard installation: ~/.config/r2modmanPlus-local/
    - Alternative location: ~/.local/share/r2modmanPlus-local/
    - Flatpak installation: ~/.var/app/com.github.ebkr.r2modmanPlus/config/r2modmanPlus-local/

    Each installation contains:
    - Valheim/profiles/ directory with all mod profiles
    - Each profile contains a mods.yml file with complete mod information

    Returns:
        Path object pointing to the profiles directory, or None if not found
    """
    # List of possible R2MODMAN installation paths
    # These are checked in order until one is found
    possible_paths = [
        # Standard installation path (most common)
        Path.home() / ".config" / "r2modmanPlus-local" / "Valheim" / "profiles",

        # Alternative installation path (some distributions)
        Path.home() / ".local" / "share" / "r2modmanPlus-local" / "Valheim" / "profiles",

        # Flatpak installation path (sandboxed application)
        Path.home() / ".var" / "app" / "com.github.ebkr.r2modmanPlus" / "config" / "r2modmanPlus-local" / "Valheim" / "profiles",
    ]

    # Check each possible path and return the first one that exists
    for path in possible_paths:
        if path.exists():
            return path

    # No R2MODMAN installation found
    return None


def get_available_profiles():
    """Get list of available R2MODMAN profiles"""
    r2modman_base = find_r2modman_base()

    if not r2modman_base:
        print("Error: R2MODMAN directory not found!")
        print("\nSearched in:")
        print("  - ~/.config/r2modmanPlus-local/Valheim/profiles")
        print("  - ~/.local/share/r2modmanPlus-local/Valheim/profiles")
        print("  - ~/.var/app/com.github.ebkr.r2modmanPlus/config/r2modmanPlus-local/Valheim/profiles (Flatpak)")
        sys.exit(1)

    profiles = [p.name for p in r2modman_base.iterdir() if p.is_dir()]
    return profiles, r2modman_base


def select_profile(profiles):
    """Interactive profile selection"""
    print("\n=== R2MODMAN Profile Selector ===")
    print("\nAvailable profiles:")
    for i, profile in enumerate(profiles, 1):
        print(f"  {i}. {profile}")
    print(f"  0. Go back")

    while True:
        try:
            choice = input(f"\nSelect profile (0-{len(profiles)}): ").strip()
            idx = int(choice)
            if idx == 0:
                return None  # Go back to main menu
            elif 1 <= idx <= len(profiles):
                return profiles[idx - 1]
            else:
                print(f"Please enter a number between 0 and {len(profiles)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            return None


def select_mode():
    """Select operation mode"""
    print("\n=== Main Menu ===")
    print("  1. Export mod list")
    print("  2. Compare two exports")
    print("  3. Exit")

    while True:
        try:
            choice = input("\nSelect option (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            else:
                print("Please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\nExiting...")
            return 3


def load_mods(profile_name, r2modman_base):
    """
    Load mods from profile's mods.yml file.

    R2MODMAN stores all mod information in a YAML file located at:
    ~/.config/r2modmanPlus-local/Valheim/profiles/{PROFILE_NAME}/mods.yml

    The mods.yml file contains a list of all installed mods with their complete metadata:
    - name: Internal mod name (e.g., "denikson-BepInExPack_Valheim")
    - displayName: User-friendly name
    - authorName: Mod author
    - versionNumber: Object with major, minor, patch version numbers
    - description: Full mod description
    - enabled: Boolean indicating if mod is active
    - websiteUrl: Link to mod's Thunderstore page
    - And many other metadata fields

    Args:
        profile_name: Name of the R2MODMAN profile (e.g., "Default", "MODS-TEST")
        r2modman_base: Path to the R2MODMAN profiles directory

    Returns:
        List of dictionaries, each containing complete mod information
    """
    # Construct full path to the profile's mods.yml file
    # Example: ~/.config/r2modmanPlus-local/Valheim/profiles/MODS-TEST/mods.yml
    mods_file = r2modman_base / profile_name / "mods.yml"

    # Check if the file exists
    if not mods_file.exists():
        print(f"Error: mods.yml not found for profile '{profile_name}'")
        sys.exit(1)

    # Read and parse the YAML file
    # This contains the complete list of all mods installed in the profile
    with open(mods_file, 'r', encoding='utf-8') as f:
        mods_data = yaml.safe_load(f)

    return mods_data


def parse_mod_info(mod):
    """
    Extract and format relevant information from a mod entry.

    The mods.yml file contains extensive metadata for each mod. This function
    extracts the essential information we want to display in our exports.

    Version numbers in R2MODMAN are stored as objects with separate fields:
    - versionNumber.major (e.g., 5)
    - versionNumber.minor (e.g., 4)
    - versionNumber.patch (e.g., 2333)
    These are combined into a readable format: "5.4.2333"

    Args:
        mod: Dictionary containing raw mod data from mods.yml

    Returns:
        Dictionary with formatted mod information ready for export
    """
    # Extract version number object and format it as "major.minor.patch"
    version = mod.get('versionNumber', {})
    version_str = f"{version.get('major', 0)}.{version.get('minor', 0)}.{version.get('patch', 0)}"

    # Return cleaned and formatted mod information
    return {
        'name': mod.get('displayName', mod.get('name', 'Unknown')),  # Prefer displayName over internal name
        'author': mod.get('authorName', 'Unknown'),
        'version': version_str,
        'description': mod.get('description', ''),
        'enabled': 'Yes' if mod.get('enabled', False) else 'No',  # Convert boolean to readable text
        'website': mod.get('websiteUrl', ''),  # Usually Thunderstore link
    }


def sort_mods(mods_list):
    """Sort mods by author, then alphabetically by name"""
    return sorted(mods_list, key=lambda x: (x['author'].lower(), x['name'].lower()))


def calculate_statistics(mods_list, profile_name):
    """
    Calculate comprehensive statistics from the mod list.

    This generates useful insights about the mod collection that are displayed
    at the top of exported files:
    - Total/enabled/disabled counts
    - Number of unique mod authors
    - Top 5 authors by mod count
    - 5 newest mods (by version number)
    - 5 oldest mods (by version number)

    Args:
        mods_list: List of parsed mod dictionaries
        profile_name: Name of the profile being exported

    Returns:
        Dictionary containing all calculated statistics
    """
    # Count total mods and enabled/disabled breakdown
    total_mods = len(mods_list)
    enabled_mods = sum(1 for mod in mods_list if mod['enabled'] == 'Yes')
    disabled_mods = total_mods - enabled_mods

    # Count how many mods each author has contributed
    # Counter creates a dictionary: {'AuthorName': count, ...}
    author_counts = Counter(mod['author'] for mod in mods_list)
    unique_authors = len(author_counts)

    # Get the top 5 authors by mod count
    # Returns list of tuples: [('AuthorName', count), ...]
    top_authors = author_counts.most_common(5)

    # Sort mods by version number to find newest/oldest
    # Version comparison: "5.4.2333" > "1.2.0"
    def version_key(mod):
        """Convert version string to tuple for proper numerical comparison"""
        try:
            # Split "5.4.2333" into ["5", "4", "2333"]
            parts = mod['version'].split('.')
            # Convert to tuple of integers: (5, 4, 2333)
            return tuple(int(p) for p in parts)
        except:
            # If version format is invalid, return (0, 0, 0)
            return (0, 0, 0)

    # Sort by version (highest first) and get top 5
    sorted_by_version = sorted(mods_list, key=version_key, reverse=True)
    newest_mods = sorted_by_version[:5]  # First 5 = newest
    oldest_mods = sorted_by_version[-5:][::-1]  # Last 5, reversed = oldest first

    # Compile all statistics into a dictionary
    stats = {
        'profile_name': profile_name,
        'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_mods': total_mods,
        'enabled_mods': enabled_mods,
        'disabled_mods': disabled_mods,
        'unique_authors': unique_authors,
        'top_authors': top_authors,
        'newest_mods': newest_mods,
        'oldest_mods': oldest_mods,
    }

    return stats


def generate_colors(num_authors):
    """Generate distinct colors for authors"""
    colors = [
        '#E6F3FF',  # Light Blue
        '#FFE6E6',  # Light Red
        '#E6FFE6',  # Light Green
        '#FFF4E6',  # Light Orange
        '#F0E6FF',  # Light Purple
        '#FFFFE6',  # Light Yellow
        '#FFE6F0',  # Light Pink
        '#E6FFFF',  # Light Cyan
        '#F5E6D3',  # Light Brown
        '#E6E6FF',  # Light Lavender
    ]
    return [colors[i % len(colors)] for i in range(num_authors)]


def ensure_output_dirs(base_dir):
    """Ensure csv_files and ods_files directories exist"""
    csv_dir = base_dir / "csv_files"
    ods_dir = base_dir / "ods_files"

    csv_dir.mkdir(exist_ok=True)
    ods_dir.mkdir(exist_ok=True)

    return csv_dir, ods_dir


def export_to_csv(mods_list, output_file, stats):
    """Export mods to CSV file with statistics section"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write statistics section
        writer.writerow(['PROFILE STATISTICS'])
        writer.writerow([''])
        writer.writerow(['Profile Name:', stats['profile_name']])
        writer.writerow(['Export Date:', stats['export_date']])
        writer.writerow(['Total Mods:', stats['total_mods']])
        writer.writerow(['Enabled Mods:', stats['enabled_mods']])
        writer.writerow(['Disabled Mods:', stats['disabled_mods']])
        writer.writerow(['Unique Authors:', stats['unique_authors']])
        writer.writerow([''])

        # Top authors
        writer.writerow(['TOP AUTHORS (by mod count)'])
        for author, count in stats['top_authors']:
            writer.writerow([author, f"{count} mods"])
        writer.writerow([''])

        # Newest mods
        writer.writerow(['NEWEST MODS (by version)'])
        writer.writerow(['Mod Name', 'Author', 'Version'])
        for mod in stats['newest_mods']:
            writer.writerow([mod['name'], mod['author'], mod['version']])
        writer.writerow([''])

        # Oldest mods
        writer.writerow(['OLDEST MODS (by version)'])
        writer.writerow(['Mod Name', 'Author', 'Version'])
        for mod in stats['oldest_mods']:
            writer.writerow([mod['name'], mod['author'], mod['version']])
        writer.writerow([''])
        writer.writerow([''])

        # Write main mod list header
        writer.writerow(['COMPLETE MOD LIST'])
        writer.writerow([''])
        headers = ['Author', 'Mod Name', 'Version', 'Enabled', 'Description', 'Website']
        writer.writerow(headers)

        # Write mod data
        for mod in mods_list:
            writer.writerow([
                mod['author'],
                mod['name'],
                mod['version'],
                mod['enabled'],
                mod['description'],
                mod['website'],
            ])

    print(f"✓ CSV file created: {output_file.name}")


def export_to_ods(mods_list, output_file, stats):
    """Export mods to ODS file with color coding and statistics"""
    if not HAS_ODF:
        print("✗ ODS export skipped (odfpy not installed)")
        return

    doc = OpenDocumentSpreadsheet()

    # Create styles
    # Bold style for headers
    bold_style = Style(name="bold", family="table-cell")
    bold_style.addElement(TextProperties(fontweight="bold"))
    doc.automaticstyles.addElement(bold_style)

    # Stats header style (bold + light gray background)
    stats_header_style = Style(name="stats_header", family="table-cell")
    stats_header_style.addElement(TableCellProperties(backgroundcolor="#E0E0E0"))
    stats_header_style.addElement(TextProperties(fontweight="bold", fontsize="12pt"))
    doc.automaticstyles.addElement(stats_header_style)

    # Section header style (bold + darker gray)
    section_header_style = Style(name="section_header", family="table-cell")
    section_header_style.addElement(TableCellProperties(backgroundcolor="#CCCCCC"))
    section_header_style.addElement(TextProperties(fontweight="bold"))
    doc.automaticstyles.addElement(section_header_style)

    # Main table header style
    header_style = Style(name="header", family="table-cell")
    header_style.addElement(TableCellProperties(backgroundcolor="#4A90E2"))
    header_style.addElement(TextProperties(fontweight="bold", color="#FFFFFF"))
    doc.automaticstyles.addElement(header_style)

    # Get unique authors and assign colors
    authors = list(dict.fromkeys([mod['author'] for mod in mods_list]))
    author_colors = dict(zip(authors, generate_colors(len(authors))))

    # Create styles for each author
    author_styles = {}
    for author, color in author_colors.items():
        style = Style(name=f"author_{author.replace(' ', '_').replace('-', '_')}", family="table-cell")
        style.addElement(TableCellProperties(backgroundcolor=color))
        doc.automaticstyles.addElement(style)
        author_styles[author] = style

    # Create table
    table = Table(name="Mods")

    # Add columns (6 for main data)
    for _ in range(6):
        table.addElement(TableColumn())

    # Add statistics section
    def add_row(cells, style=None):
        row = TableRow()
        for cell_text in cells:
            cell = TableCell(stylename=style) if style else TableCell()
            cell.addElement(P(text=str(cell_text)))
            row.addElement(cell)
        table.addElement(row)
        return row

    # Statistics header
    add_row(['PROFILE STATISTICS', '', '', '', '', ''], stats_header_style)
    add_row(['', '', '', '', '', ''])
    add_row(['Profile Name:', stats['profile_name'], '', '', '', ''], bold_style)
    add_row(['Export Date:', stats['export_date'], '', '', '', ''])
    add_row(['Total Mods:', stats['total_mods'], '', '', '', ''])
    add_row(['Enabled Mods:', stats['enabled_mods'], '', '', '', ''])
    add_row(['Disabled Mods:', stats['disabled_mods'], '', '', '', ''])
    add_row(['Unique Authors:', stats['unique_authors'], '', '', '', ''])
    add_row(['', '', '', '', '', ''])

    # Top authors
    add_row(['TOP AUTHORS (by mod count)', '', '', '', '', ''], section_header_style)
    for author, count in stats['top_authors']:
        add_row([author, f"{count} mods", '', '', '', ''])
    add_row(['', '', '', '', '', ''])

    # Newest mods
    add_row(['NEWEST MODS (by version)', '', '', '', '', ''], section_header_style)
    add_row(['Mod Name', 'Author', 'Version', '', '', ''], bold_style)
    for mod in stats['newest_mods']:
        add_row([mod['name'], mod['author'], mod['version'], '', '', ''])
    add_row(['', '', '', '', '', ''])

    # Oldest mods
    add_row(['OLDEST MODS (by version)', '', '', '', '', ''], section_header_style)
    add_row(['Mod Name', 'Author', 'Version', '', '', ''], bold_style)
    for mod in stats['oldest_mods']:
        add_row([mod['name'], mod['author'], mod['version'], '', '', ''])
    add_row(['', '', '', '', '', ''])
    add_row(['', '', '', '', '', ''])

    # Main mod list header
    add_row(['COMPLETE MOD LIST', '', '', '', '', ''], stats_header_style)
    add_row(['', '', '', '', '', ''])

    # Add main table header row
    headers = ['Author', 'Mod Name', 'Version', 'Enabled', 'Description', 'Website']
    header_row = TableRow()
    for header_text in headers:
        cell = TableCell(stylename=header_style)
        cell.addElement(P(text=header_text))
        header_row.addElement(cell)
    table.addElement(header_row)

    # Add mod data rows with color coding
    for mod in mods_list:
        row = TableRow()
        style = author_styles[mod['author']]

        for field in ['author', 'name', 'version', 'enabled', 'description', 'website']:
            cell = TableCell(stylename=style)
            cell.addElement(P(text=str(mod[field])))
            row.addElement(cell)

        table.addElement(row)

    doc.spreadsheet.addElement(table)
    doc.save(output_file)

    print(f"✓ ODS file created: {output_file.name}")
    print(f"  Statistics: {stats['total_mods']} total, {stats['enabled_mods']} enabled, {stats['unique_authors']} authors")


def load_csv_for_comparison(csv_file):
    """
    Load a CSV export file and extract mod data for comparison.

    Our CSV files have a specific structure:
    1. Statistics section (multiple rows)
    2. Top Authors section
    3. Newest/Oldest Mods sections
    4. Blank rows
    5. "COMPLETE MOD LIST" header
    6. Actual CSV header: "Author,Mod Name,Version,Enabled,Description,Website"
    7. Mod data rows

    This function needs to skip all the statistics and find the actual mod data
    starting from the "Author,Mod Name,Version" header line.

    Args:
        csv_file: Path object pointing to the CSV file to load

    Returns:
        Dictionary with keys as "Author:ModName" and values as row dictionaries
        Example: {"Azumatt:WardIsLove": {"Author": "Azumatt", "Mod Name": "WardIsLove", ...}}
    """
    mods = {}

    with open(csv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

        # Scan through the file to find the actual mod data header
        # We're looking for the line that starts with "Author,Mod Name,Version"
        # This appears after all the statistics sections
        header_line_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith('Author,Mod Name,Version'):
                header_line_idx = i
                break

        if header_line_idx is None:
            # If we can't find the header, the file format might be wrong
            print(f"Warning: Could not find mod data header in {csv_file.name}")
            return mods

        # Create a new CSV reader starting from the header line
        # This skips all the statistics sections above
        import io
        csv_data = io.StringIO(''.join(lines[header_line_idx:]))
        reader = csv.DictReader(csv_data)

        # Read each mod entry and store it with a unique key
        for row in reader:
            # Only process rows that have valid data (skip empty rows)
            if row.get('Author') and row.get('Mod Name'):
                # Create unique key: "Author:ModName"
                # This allows us to match mods across different exports
                key = f"{row['Author']}:{row['Mod Name']}"
                mods[key] = row

    return mods


def compare_exports(csv_dir):
    """Compare two CSV exports to show changes"""
    csv_files = sorted(csv_dir.glob("*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)

    if len(csv_files) < 2:
        print("\nError: Need at least 2 CSV files to compare!")
        print(f"Found only {len(csv_files)} file(s) in csv_files/")
        input("\nPress Enter to return to main menu...")
        return

    print("\n=== Available CSV files ===")
    for i, f in enumerate(csv_files[:10], 1):
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {i}. {f.name} ({mtime})")
    print("  0. Go back")

    print("\nSelect two files to compare (or 0 to go back):")
    try:
        choice1 = input("First file (newer): ").strip()
        if choice1 == '0':
            return
        idx1 = int(choice1) - 1

        choice2 = input("Second file (older): ").strip()
        if choice2 == '0':
            return
        idx2 = int(choice2) - 1

        if idx1 < 0 or idx1 >= len(csv_files) or idx2 < 0 or idx2 >= len(csv_files):
            print("Invalid selection!")
            input("\nPress Enter to return to main menu...")
            return

        file1 = csv_files[idx1]
        file2 = csv_files[idx2]

    except (ValueError, KeyboardInterrupt):
        print("\nReturning to main menu...")
        return

    print(f"\nComparing:")
    print(f"  Newer: {file1.name}")
    print(f"  Older: {file2.name}")
    print()

    mods1 = load_csv_for_comparison(file1)
    mods2 = load_csv_for_comparison(file2)

    keys1 = set(mods1.keys())
    keys2 = set(mods2.keys())

    added = keys1 - keys2
    removed = keys2 - keys1
    common = keys1 & keys2

    # Check for version/status changes
    updated = []
    enabled_changes = []
    for key in common:
        if mods1[key]['Version'] != mods2[key]['Version']:
            updated.append((key, mods2[key]['Version'], mods1[key]['Version']))
        if mods1[key]['Enabled'] != mods2[key]['Enabled']:
            enabled_changes.append((key, mods2[key]['Enabled'], mods1[key]['Enabled']))

    # Clear screen for clean results display
    os.system('clear')

    # Display results
    print("="*60)
    print("  COMPARISON RESULTS")
    print("="*60)

    if added:
        print(f"\n✓ ADDED MODS ({len(added)}):")
        for key in sorted(added):
            author, name = key.split(':', 1)
            print(f"  + {name} (by {author}) v{mods1[key]['Version']}")

    if removed:
        print(f"\n✗ REMOVED MODS ({len(removed)}):")
        for key in sorted(removed):
            author, name = key.split(':', 1)
            print(f"  - {name} (by {author}) v{mods2[key]['Version']}")

    if updated:
        print(f"\n↑ VERSION UPDATES ({len(updated)}):")
        for key, old_ver, new_ver in sorted(updated):
            author, name = key.split(':', 1)
            print(f"  ↑ {name} (by {author}): {old_ver} → {new_ver}")

    if enabled_changes:
        print(f"\n⚡ ENABLED/DISABLED ({len(enabled_changes)}):")
        for key, old_status, new_status in sorted(enabled_changes):
            author, name = key.split(':', 1)
            status = "ENABLED" if new_status == "Yes" else "DISABLED"
            print(f"  ⚡ {name} (by {author}): {status}")

    if not (added or removed or updated or enabled_changes):
        print("\n✓ No changes detected!")

    print("\n" + "="*60)
    print(f"Summary: {len(added)} added, {len(removed)} removed, {len(updated)} updated, {len(enabled_changes)} status changes")
    print("="*60 + "\n")

    input("Press Enter to return to main menu...")


def export_mode(profiles, r2modman_base):
    """Export mode - create new CSV/ODS files"""
    profile_name = select_profile(profiles)

    if profile_name is None:
        # User chose to go back
        return

    print(f"\nLoading mods from profile: {profile_name}")

    mods_data = load_mods(profile_name, r2modman_base)

    if not mods_data:
        print("Error: No mods found in profile!")
        input("\nPress Enter to return to main menu...")
        return

    print(f"Found {len(mods_data)} mods")

    mods_list = [parse_mod_info(mod) for mod in mods_data]
    mods_list = sort_mods(mods_list)
    print("Mods sorted by author and name")

    # Calculate statistics
    stats = calculate_statistics(mods_list, profile_name)

    # Setup output directories
    output_dir = Path(__file__).parent
    csv_dir, ods_dir = ensure_output_dirs(output_dir)

    # Generate filenames with readable timestamp
    now = datetime.now()
    timestamp = now.strftime("%b-%d-%Y_%I:%M%p")
    csv_file = csv_dir / f"{profile_name}_{timestamp}.csv"
    ods_file = ods_dir / f"{profile_name}_{timestamp}.ods"

    # Export
    print("\nExporting...")
    export_to_csv(mods_list, csv_file, stats)
    export_to_ods(mods_list, ods_file, stats)

    # Clear screen for clean results display
    os.system('clear')

    print("\n" + "="*60)
    print("  Export complete!")
    print("="*60)
    print(f"\nFiles saved:")
    print(f"  CSV: csv_files/{csv_file.name}")
    if HAS_ODF:
        print(f"  ODS: ods_files/{ods_file.name}")
    print()

    input("Press Enter to return to main menu...")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("  Broheim Mod Tracker for Valheim")
    print("="*60)

    profiles, r2modman_base = get_available_profiles()

    if not profiles:
        print("Error: No profiles found!")
        sys.exit(1)

    # Main loop - continue until user exits
    while True:
        mode = select_mode()

        if mode == 1:
            export_mode(profiles, r2modman_base)
        elif mode == 2:
            output_dir = Path(__file__).parent
            csv_dir, _ = ensure_output_dirs(output_dir)
            compare_exports(csv_dir)
        elif mode == 3:
            print("\n" + "="*60)
            print("  Thanks for using Broheim Mod Tracker!")
            print("="*60 + "\n")
            break


if __name__ == "__main__":
    main()
