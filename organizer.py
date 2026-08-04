import os
import shutil
from pathlib import Path

# 1. Tentukan path folder Downloads (Otomatis mendeteksi user OS saat ini)
DOWNLOADS_DIR = Path.home() / "Downloads"

# 2. Pemetaan kategori folder dan ekstensi filenya
CATEGORIES = {
    "Images": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".webp",
        ".bmp",
        ".ico",
        ".jfif",
        ".cr2",
        ".heic",
    ],
    "Adobe Creative Suite": [
        ".psd",
        ".psb",
        ".ai",
        ".eps",
        ".prproj",
        ".aep",
        ".indd",
        ".xd",
        ".lrcat",
    ],
    "Figure & Design": [".fig"],
    "Network (Cisco Packet Tracer)": [".pkt", ".pka"],
    "Markdown": [".md", ".markdown"],
    "Code & Data": [
        ".c",
        ".cpp",
        ".java",
        ".class",
        ".jar",
        ".py",
        ".js",
        ".css",
        ".json",
        ".xml",
        ".sql",
        ".ipynb",
    ],
    "Link Web": [".url", ".htm", ".html", ".mhtml"],
    "Documents (Office)": [
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".txt",
        ".csv",
    ],
    "Installers & Apps": [".exe", ".msi", ".dmg", ".pkg", ".apk"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
    "Audio & Video": [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".mp3",
        ".wav",
        ".flac",
    ],
}

# Ekstensi yang diabaikan (misal: file yang sedang proses download)
IGNORE_EXTENSIONS = [".crdownload", ".tmp", ".part"]

# 3. Daftar nama folder sistem/kategori yang dikelola skrip
SYSTEM_FOLDERS = list(CATEGORIES.keys()) + ["Others", "Folders & Projects"]


def get_category(extension):
    """Menentukan nama folder berdasarkan ekstensi file."""
    for category, extensions in CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return "Others"


def get_unique_path(destination_path):
    """Mencegah overwrite: jika nama file/folder sudah ada, tambahkan angka (1), (2), dst."""
    counter = 1
    new_path = destination_path
    while new_path.exists():
        new_path = destination_path.with_name(
            f"{destination_path.stem} ({counter}){destination_path.suffix}"
        )
        counter += 1
    return new_path


def reset_existing_categories():
    """FITUR REORGANIZE: Mengeluarkan semua file dari folder kategori lama

    ke Downloads utama agar bisa diklasifikasikan ulang dengan aturan baru.
    """
    print("Memeriksa dan menata ulang folder kategori yang sudah ada...")
    for folder_name in list(CATEGORIES.keys()) + ["Others"]:
        cat_dir = DOWNLOADS_DIR / folder_name
        if cat_dir.exists() and cat_dir.is_dir():
            # Pindahkan semua file dari dalam subfolder keluar ke Downloads
            for file_item in cat_dir.iterdir():
                if file_item.is_file():
                    dest_path = get_unique_path(DOWNLOADS_DIR / file_item.name)
                    try:
                        shutil.move(str(file_item), str(dest_path))
                    except Exception as e:
                        print(
                            f"[!] Gagal mengeluarkan {file_item.name} dari {folder_name}: {e}"
                        )

            # Hapus folder kategori jika sudah kosong
            try:
                cat_dir.rmdir()
            except OSError:
                pass  # Abaikan jika folder masih berisi item lain (misal subfolder)


def organize_downloads():
    if not DOWNLOADS_DIR.exists():
        print(f"Folder tidak ditemukan: {DOWNLOADS_DIR}")
        return

    print(f"Memulai perapihan di: {DOWNLOADS_DIR}\n" + "-" * 40)

    # 1. Tarik keluar dulu semua file dari folder kategori lama (Reorganize All)
    reset_existing_categories()

    moved_count = 0

    # 2. Iterasi dan klasifikasikan ulang semua item di folder Downloads
    for item in list(DOWNLOADS_DIR.iterdir()):
        # Lewati file skrip ini sendiri jika disimpan di folder Downloads
        if item.name == Path(__file__).name:
            continue

        # --- PENANGANAN FOLDER ---
        if item.is_dir():
            # Lewati folder kategori/sistem buatan skrip ini
            if item.name in SYSTEM_FOLDERS:
                continue
            category = "Folders & Projects"

        # --- PENANGANAN FILE ---
        else:
            # Lewati file yang sedang proses download
            if item.suffix.lower() in IGNORE_EXTENSIONS:
                continue
            category = get_category(item.suffix)

        # Tentukan lokasi folder tujuan & buat foldernya jika belum ada
        target_dir = DOWNLOADS_DIR / category
        target_dir.mkdir(exist_ok=True)

        # Siapkan path tujuan (dengan proteksi nama ganda)
        target_path = get_unique_path(target_dir / item.name)

        try:
            shutil.move(str(item), str(target_path))
            print(f"[✔] {item.name} -> {category}/")
            moved_count += 1
        except Exception as e:
            print(f"[X] Gagal memindahkan {item.name}: {e}")

    print("-" * 40)
    print(f"Selesai! {moved_count} item berhasil dirapikan ulang.")


if __name__ == "__main__":
    organize_downloads()