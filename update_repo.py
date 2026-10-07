import os
import sys
import io
import bz2
import gzip
import lzma
import hashlib
import tarfile

# Hỗ trợ UTF-8 cho Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DEBS_DIR = os.path.join(REPO_DIR, "debs")

RELEASE_HEADER = """Origin: DevByWin Repo
Label: DevByWin Repo
Suite: stable
Version: 1.0
Codename: ios
Architectures: iphoneos-arm iphoneos-arm64 iphoneos-arm64e
Components: main
Description: Kho tweak jailbreak của DevByWin dành cho Sileo và Zebra
"""

def parse_ar(deb_path):
    """Đọc file .deb (chuẩn ar archive) bằng Python thuần"""
    with open(deb_path, 'rb') as f:
        magic = f.read(8)
        if magic != b'!<arch>\n':
            raise ValueError(f"Không phải định dạng file deb hợp lệ: {deb_path}")
        
        while True:
            header = f.read(60)
            if not header or len(header) < 60:
                break
            name = header[0:16].strip().decode('ascii', errors='ignore')
            size = int(header[48:58].strip())
            file_data = f.read(size)
            if size % 2 != 0:
                f.read(1)  # Bỏ qua ký tự pad chẵn byte của ar
            
            if name.startswith('control.tar'):
                return file_data, name
    return None, None

def get_control_content(deb_path):
    """Trích xuất file control từ deb"""
    data, name = parse_ar(deb_path)
    if not data:
        return ""
    
    tar_stream = io.BytesIO(data)
    with tarfile.open(fileobj=tar_stream, mode='r:*') as tar:
        for member in tar.getmembers():
            if member.name in ('./control', 'control'):
                f = tar.extractfile(member)
                if f:
                    return f.read().decode('utf-8', errors='ignore').strip()
    return ""

def get_hashes_and_size(file_bytes):
    size = len(file_bytes)
    md5 = hashlib.md5(file_bytes).hexdigest()
    sha1 = hashlib.sha1(file_bytes).hexdigest()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    return size, md5, sha1, sha256

def main():
    if not os.path.exists(DEBS_DIR):
        os.makedirs(DEBS_DIR, exist_ok=True)
        print(f"Đã tạo thư mục: {DEBS_DIR}")

    deb_files = [f for f in os.listdir(DEBS_DIR) if f.endswith('.deb')]
    if not deb_files:
        print("Không tìm thấy file .deb nào trong thư mục debs/!")
        return

    print(f"Tìm thấy {len(deb_files)} file .deb:")
    packages_entries = []

    for deb in sorted(deb_files):
        deb_path = os.path.join(DEBS_DIR, deb)
        with open(deb_path, 'rb') as f:
            deb_bytes = f.read()

        size, md5, sha1, sha256 = get_hashes_and_size(deb_bytes)
        control = get_control_content(deb_path)
        if not control:
            print(f"  [BỎ QUA] Không thể đọc control của {deb}")
            continue

        # Đảm bảo đường dẫn dạng debs/ten_file.deb (dùng / thay vì \\)
        rel_path = f"debs/{deb}"
        entry = (
            f"{control}\n"
            f"Filename: {rel_path}\n"
            f"Size: {size}\n"
            f"MD5sum: {md5}\n"
            f"SHA1: {sha1}\n"
            f"SHA256: {sha256}"
        )
        packages_entries.append(entry)
        print(f"  + {deb} ({size:,} bytes)")

    # Nội dung Packages (ngăn cách nhau bởi 2 dấu xuống dòng)
    packages_text = "\n\n".join(packages_entries) + "\n"
    packages_bytes = packages_text.encode('utf-8')

    # 1. Ghi file Packages
    with open(os.path.join(REPO_DIR, 'Packages'), 'wb') as f:
        f.write(packages_bytes)

    # 2. Ghi file Packages.bz2
    bz2_bytes = bz2.compress(packages_bytes)
    with open(os.path.join(REPO_DIR, 'Packages.bz2'), 'wb') as f:
        f.write(bz2_bytes)

    # 3. Ghi file Packages.xz
    xz_bytes = lzma.compress(packages_bytes)
    with open(os.path.join(REPO_DIR, 'Packages.xz'), 'wb') as f:
        f.write(xz_bytes)

    # 4. Ghi file Packages.gz
    gz_bytes = gzip.compress(packages_bytes)
    with open(os.path.join(REPO_DIR, 'Packages.gz'), 'wb') as f:
        f.write(gz_bytes)

    # 5. Cập nhật file Release kèm thông tin hash
    meta_files = [
        ('Packages', packages_bytes),
        ('Packages.bz2', bz2_bytes),
        ('Packages.xz', xz_bytes),
        ('Packages.gz', gz_bytes),
    ]

    release_content = RELEASE_HEADER.strip() + "\n"
    release_content += "MD5Sum:\n"
    for name, data in meta_files:
        sz, md5, _, _ = get_hashes_and_size(data)
        release_content += f" {md5} {sz:16d} {name}\n"

    release_content += "SHA1:\n"
    for name, data in meta_files:
        sz, _, sha1, _ = get_hashes_and_size(data)
        release_content += f" {sha1} {sz:16d} {name}\n"

    release_content += "SHA256:\n"
    for name, data in meta_files:
        sz, _, _, sha256 = get_hashes_and_size(data)
        release_content += f" {sha256} {sz:16d} {name}\n"

    with open(os.path.join(REPO_DIR, 'Release'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(release_content)

    print("\n=> Cập nhật thành công các file:")
    print("   - Packages")
    print("   - Packages.bz2")
    print("   - Packages.xz")
    print("   - Packages.gz")
    print("   - Release")

if __name__ == '__main__':
    main()
