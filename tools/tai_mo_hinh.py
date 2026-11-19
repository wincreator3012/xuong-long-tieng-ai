#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TẢI VÀ DỌN MÔ HÌNH trên máy chạy mô hình (tools/cai_dat.py gọi, chạy trong môi trường "chung" vì cần huggingface_hub).

    python tools/tai_mo_hinh.py            # tải mô hình của máy đọc đang bật và mô hình gỡ băng; gỡ mô hình không còn dùng
    python tools/tai_mo_hinh.py --xem      # chỉ in: mô hình nào giữ, nào sẽ gỡ, chiếm bao nhiêu
Mô hình nằm ở <môi trường>/hf (HF_HOME), ngoài repo. Đã tải thì bỏ qua, tải dở thì tải tiếp.
Chỉ gỡ mô hình xưởng biết tên (may-doc.json, hai mô hình gỡ băng) mà máy đọc đang bật không cần; kho lạ không đụng tới.
Máy đọc có "tuTai" (VieNeu) tự tải phần nó cần ở lần chạy đầu (bước tự kiểm), nên không tải trước ở đây.
"""
import os
import shutil
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import cau_hinh as CH  # noqa: E402

os.environ.setdefault("HF_HOME", os.path.join(CH.moi_truong(), "hf"))
HUB = os.path.join(os.environ["HF_HOME"], "hub")


def thu_muc(repo):
    return os.path.join(HUB, "models--" + repo.replace("/", "--"))


def bo_nho_dem():
    """{repo: (cỡ GB, [mã bản])} theo huggingface_hub (đúng cả kiểu kho có blobs dùng chung của bản mới)."""
    from huggingface_hub import scan_cache_dir
    if not os.path.isdir(HUB):
        return {}, None
    info = scan_cache_dir(HUB)
    return {r.repo_id: (r.size_on_disk / 1e9, [x.commit_hash for x in r.revisions]) for r in info.repos}, info


def ke_hoach(dem):
    md, dung = CH.may_doc(), CH.may_dung() or []
    asr = CH.asr()
    can = [(asr["moHinh"], "Whisper large-v3-turbo (gỡ băng ngược để kiểm)", 1.6)]
    giu = {asr["moHinh"]}
    biet = set(CH.ASR.values())
    for k, v in md.items():
        kho = [v["moHinh"]] + list(v.get("moHinhPhu", [])) if v.get("loai") == "tai-may" else []
        biet.update(kho)
        if k in dung:
            giu.update(kho)
            if not v.get("tuTai") and v.get("dungLuongGB"):
                can.append((v["moHinh"], v["ten"], v["dungLuongGB"]))
    go = sorted(r for r in biet - giu if r in dem)
    return can, giu, go


def main():
    xem = "--xem" in sys.argv
    dem, info = bo_nho_dem()
    can, giu, go = ke_hoach(dem)
    if go:
        print("Gỡ mô hình không còn dùng:")
        for r in go:
            print(f"  - {r} ({dem[r][0]:.1f} GB)")
        cl = info.delete_revisions(*[h for r in go for h in dem[r][1]])
        print(f"  {'Sẽ giải phóng' if xem else 'Đã giải phóng'} khoảng {cl.expected_freed_size / 1e9:.1f} GB.")
        if not xem:
            cl.execute()
            for r in go:  # phần vỏ còn sót (refs, trees)
                shutil.rmtree(thu_muc(r), ignore_errors=True)
    print("Giữ:", ", ".join(sorted(giu)))
    if xem:
        return 0
    from huggingface_hub import snapshot_download
    trong = shutil.disk_usage(os.path.expanduser("~")).free / 1e9
    print(f"Ổ đĩa còn {trong:.0f} GB.\n", flush=True)
    loi = 0
    for repo, ten, gb in can:
        if repo in dem and dem[repo][0] >= gb * 0.9:
            print(f"-> {ten}: đã có.", flush=True)
            continue
        if gb > trong - 5:
            print(f"-> {ten}: không đủ chỗ ({gb:g} GB, còn {trong:.0f} GB). Dọn ổ đĩa rồi chạy lại trình cài.")
            loi += 1
            continue
        print(f"-> {ten} ({gb:g} GB): {repo}", flush=True)
        try:
            snapshot_download(repo_id=repo)
            sys.stderr.flush()
            print("   xong.", flush=True)
        except Exception as e:
            loi += 1
            print(f"   tải không được: {e}")
        trong = shutil.disk_usage(os.path.expanduser("~")).free / 1e9
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
