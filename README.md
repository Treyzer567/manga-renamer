# Manga Renamer

A Python script that watches a downloads directory, renames `.cbz` manga and webcomic chapter files to a consistent format, and moves them into the correct library folder. Runs on a schedule via Docker using `renamer-compose.yml`. It is meant to be used with Tachidesk to automate the download, renaming and adding to your library of manga and webtoons.

---

## How It Works

1. Scans the `/downloads` directory recursively for `.cbz` files
2. Determines the series name from the parent folder name, cleaning and de-duplicating it using `manga_map.json` for known tricky titles
3. Extracts the chapter number from the filename using pattern matching (`Ch.`, `Chapter`, `Act`, `Episode`, etc.)
4. Renames the file to `Series Name - vChapterNumber.cbz`
5. Routes to `/webcomics` if the source path contains `MangaRead.org (EN)` or `Asura Scans (EN)`, otherwise routes to `/mangas`
6. Skips files that already exist at the destination

---

## Output Format

```
Series Name - v001.cbz
Series Name - v12.5.cbz
Series Name - vUnknown - original-filename.cbz   ← fallback if chapter can't be parsed
```

---

## Files

| File | Description |
|------|-------------|
| `renamer.py` | Main script — scans, renames, and moves `.cbz` files |
| `manga_map.json` | Manual title mapping for series with unusual or duplicated names in their download filenames |
| `renamer-compose.yml` | Docker Compose file — runs the renamer every 10 minutes |

---

## manga_map.json

Used to resolve series names that can't be cleanly parsed from the folder name alone. Keys are the raw folder name (lowercased), values are the clean output name:

```json
{
  "Gachiakuta Gachia Kuta": "Gachiakuta",
  "Nige Jouzu no Wakagimi The Elusive Samurai": "The Elusive Samurai"
}
```

Add entries here whenever a series downloads with a garbled or duplicated name.

---

## Deployment

Runs as a Docker container on a 10-minute loop.

### Volume Mounts

| Host Path | Container Path | Description |
|-----------|---------------|-------------|
| `/path/to/renamer.py` | `/renamer.py` | The script |
| `/path/to/manga_map.json` | `/manga_map.json` | Title mapping file |
| `/path/to/manga-library` | `/mangas` | Manga destination |
| `/path/to/webcomic-library` | `/webcomics` | Webcomic destination |
| `/path/to/downloads` | `/downloads` | Source download directory |

Update paths in `renamer-compose.yml` to match your server's directory layout before deploying.

---

## Related Repos

| Repo | Description |
|------|-------------|
| [scripts](https://github.com/Treyzer567/scripts) | Other standalone media mover scripts |
| [landing-page](https://github.com/Treyzer567/landing-page) | Frontend hub |

---

## External Projects

| Project | Description |
|---------|-------------|
| [Tachidesk (Suwayomi)](https://github.com/Suwayomi/Suwayomi-Server) | Self-hosted Tachiyomi-compatible manga server — source of the downloaded `.cbz` files |
