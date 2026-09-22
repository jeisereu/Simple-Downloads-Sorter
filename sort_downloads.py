import os
import shutil
from pathlib import Path

# Set the downloads path dynamically across Windows, macOS, and Linux
DOWNLOADS_DIR = Path.home() / "Downloads"

# Category mapping: Maps target relative folder paths to sets of file extensions.
# To add a new category, simply add a new line:
#   "Target Folder/Subfolder": {".ext1", ".ext2"}
FILE_CATEGORIES = {
    # Images
    "Images": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".ico"
    },
    
    # Documents with Subfolders
    "Documents/PDF": {
        ".pdf"
    },
    "Documents/Word Docs": {
        ".doc", ".docx", ".odt", ".rtf"
    },
    "Documents/Spreadsheets": {
        ".xls", ".xlsx", ".csv", ".tsv", ".ods"
    },
    "Documents/Presentations": {
        ".ppt", ".pptx", ".odp"
    },
    "Documents/Other Docs": {
        ".txt", ".md", ".tex", ".epub", ".pages", ".numbers", ".key", ".pub"
    },
    
    # Videos
    "Videos": {
        ".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v"
    },
    
    # Archives / Compressed
    "Compressed Files": {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"
    },
    
    # Installers
    "Installers": {
        ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"
    },
}

# Extensions indicating an in-progress download — these must never be moved
IGNORED_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download"}

# Destination folders managed by this script so it avoids moving or scanning them
TARGET_ROOT_DIRS = {category.split("/")[0] for category in FILE_CATEGORIES.keys()} | {"Miscellaneous Files"}


def get_unique_destination(destination_path: Path) -> Path:
    """
    Prevents data loss by appending an incrementing index if a file
    with the target name already exists (e.g., file (1).ext).
    """
    if not destination_path.exists():
        return destination_path

    stem = destination_path.stem
    suffix = destination_path.suffix
    parent = destination_path.parent
    counter = 1

    while True:
        new_path = parent / f"{stem} ({counter}){suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def get_target_subfolder(file_extension: str) -> str:
    """Finds matching category folder by extension, defaulting to Miscellaneous Files."""
    for folder_name, extensions in FILE_CATEGORIES.items():
        if file_extension in extensions:
            return folder_name
    return "Miscellaneous Files"


def sort_downloads():
    if not DOWNLOADS_DIR.exists():
        print(f"Directory not found: {DOWNLOADS_DIR}")
        return

    print(f"Scanning: {DOWNLOADS_DIR} ...")
    
    # Iterate over immediate files inside Downloads
    for item in DOWNLOADS_DIR.iterdir():
        # Skip subfolders to prevent recursive moves
        if item.is_dir():
            continue

        # Skip temporary/in-progress download files
        ext = item.suffix.lower()
        if ext in IGNORED_EXTENSIONS:
            print(f"Skipping active download: {item.name}")
            continue

        # Determine target category
        rel_folder = get_target_subfolder(ext)
        dest_dir = DOWNLOADS_DIR / rel_folder

        # Create destination directory (and parent directories if nested) safely
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_file_path = get_unique_destination(dest_dir / item.name)

        try:
            # Atomic move within the same filesystem
            shutil.move(str(item), str(dest_file_path))
            print(f"Moved: '{item.name}' -> '{rel_folder}/{dest_file_path.name}'")
        except (PermissionError, OSError) as err:
            # Fallback if a file is open in another program or an interruption happens
            print(f"Could not move '{item.name}': {err}")

    print("Sorting complete.")


if __name__ == "__main__":
    sort_downloads()