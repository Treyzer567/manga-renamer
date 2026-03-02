import os
import re
import shutil
import json
import unicodedata

# --- Configuration ---
DOWNLOADS_DIR = "/downloads"
MANGA_DIR = "/mangas"
WEBCOMIC_DIR = "/webcomics"
MAPPING_FILE = "/manga_map.json"

def load_mappings():
    """Loads the manual name database if it exists."""
    if os.path.exists(MAPPING_FILE):
        try:
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k.strip().lower(): v for k, v in data.items()}
        except Exception as e:
            print(f"Error loading {MAPPING_FILE}: {e}")
    return {}

def clean_text(text):
    if text:
        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r"[_]+", " ", text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\[.*?\]|\(.*?\)", "", text) 
        text = text.strip(" ._-\u200b")
    return text.strip() if text else ""

def refine_series_name(raw_folder_name, mapping_db):
    if not raw_folder_name:
        return ""

    cleaned_name = clean_text(raw_folder_name)
    raw_lower = raw_folder_name.strip().lower()
    cleaned_lower = cleaned_name.lower()

    if raw_lower in mapping_db:
        return mapping_db[raw_lower]
    if cleaned_lower in mapping_db:
        return mapping_db[cleaned_lower]

    parts = re.split(r'\s+|-', cleaned_name)
    unique_parts = []
    for part in parts:
        part_lower = part.lower()
        if not any(part_lower in up.lower() or up.lower() in part_lower for up in unique_parts):
            unique_parts.append(part)
    
    refined = " ".join(unique_parts)
    match = re.search(r"(.*)\s+(the\s+.*|of\s+the\s+.*)", refined, re.IGNORECASE)
    if match:
        return match.group(2).strip().title()

    return refined if refined else cleaned_name

def parse_filename(filepath, mapping_db):
    filename = os.path.basename(filepath)
    # The folder directly containing the file (the series folder)
    series_folder_name = os.path.basename(os.path.dirname(filepath))
    name_without_ext = os.path.splitext(filename)[0]

    match = re.search(
        r"(Ch(?:apter)?|Ep(?:isode)?|Act|Lesson|Mission|Story|Stage|Part|Mob|Punch)[\s._-]*"
        r"(\d+(?:[.\-_a-zA-Z0-9]*))"
        r"(?:[\s._-]*[-:]*[\s._-]*([\w\s'\[\]()!.,&–—‘’“”]+))?",
        name_without_ext,
        re.IGNORECASE
    )

    chapter_num = clean_text(match.group(2).rstrip("_-.")) if match else "Unknown"
    series_name = refine_series_name(series_folder_name, mapping_db)

    if chapter_num == "Unknown":
        new_name = f"{series_name} - vUnknown - {name_without_ext}.cbz"
    else:
        new_name = f"{series_name} - v{chapter_num}.cbz"

    return new_name

def rename_and_move_files(src_dir):
    os.makedirs(MANGA_DIR, exist_ok=True)
    os.makedirs(WEBCOMIC_DIR, exist_ok=True)
    mapping_db = load_mappings()
    renamed_count = 0

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(".cbz"):
                old_path = os.path.join(root, file)
                
                # Determine destination based on path structure: /downloads/Source/Series/Chapter
                # We check if "MangaRead.org (EN)" is part of the directory path
                if "MangaRead.org (EN)" in root:
                    target_base = WEBCOMIC_DIR
                else:
                    target_base = MANGA_DIR

                new_name = parse_filename(old_path, mapping_db)
                new_path = os.path.join(target_base, new_name)

                if new_path.lower().endswith(".cbz.cbz"):
                    new_path = new_path[:-4]

                if os.path.exists(new_path):
                    continue

                try:
                    shutil.move(old_path, new_path)
                    print(f"[{'WEBCOMIC' if target_base == WEBCOMIC_DIR else 'MANGA'}] Moved: {os.path.basename(new_path)}")
                    renamed_count += 1
                except Exception as e:
                    print(f"Error moving {file}: {e}")

    if renamed_count > 0:
        print(f"Total files processed: {renamed_count}")

if __name__ == "__main__":
    rename_and_move_files(DOWNLOADS_DIR)
