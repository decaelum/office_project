import threading
from core import kontrol_ve_kaydet

def baslat_tekli(dosya_yolu, log_path, progress_callback, islem_adi):
    threading.Thread(
        target=kontrol_ve_kaydet,
        args=(dosya_yolu, log_path),
        kwargs={"progress_callback": progress_callback, "islem_adi": islem_adi}
    ).start()

def baslat_toplu(df, log_path, progress_callback, islem_adi):
    threading.Thread(
        target=kontrol_ve_kaydet,
        kwargs={"df": df, "log_path": log_path, "progress_callback": progress_callback, "islem_adi": islem_adi}
    ).start()