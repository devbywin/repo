# CodeByWin iOS Tweak Repo

Kho lưu trữ Tweak Jailbreak cho iOS (hỗ trợ **Sileo**, **Zebra**, **Cydia**).

## 🚀 Cách thêm Repo vào thiết bị iOS
- Mở **Sileo** > **Sources (Nguồn)** > Nhấn **+** > Dán URL: `https://<username>.github.io/my-repo/`
- Hoặc mở trang web trên Safari của iPhone và bấm **Thêm vào Sileo**.

## 📦 Cách cập nhật hoặc thêm Tweak mới (.deb)
1. Thả file `.deb` mới vào thư mục `debs/`.
2. Mở Terminal / PowerShell tại thư mục này và chạy:
   ```bash
   python update_repo.py
   ```
3. Đẩy lên GitHub:
   ```bash
   git add .
   git commit -m "Add new package"
   git push origin main
   ```
