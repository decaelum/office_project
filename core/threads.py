import threading
from core.core import kontrol_ve_kaydet

def baslat_tekli(dosya_yolu, progress_callback, islem_adi):
    """
    Tek bir Excel dosyası için URL kontrolünü ayrı bir thread içinde başlatır.
    """
    thread = threading.Thread(
        target=kontrol_ve_kaydet,
        kwargs={
            "dosya_yolu": dosya_yolu,
            "progress_callback": progress_callback,
            "islem_adi": islem_adi
        }
    )
    thread.start()

def baslat_toplu(df, progress_callback, islem_adi):
    """
    Birden fazla dosya birleştirilmişse doğrudan DataFrame üzerinden çalışır.
    """
    thread = threading.Thread(
        target=kontrol_ve_kaydet,
        kwargs={
            "df": df,
            "progress_callback": progress_callback,
            "islem_adi": islem_adi
        }
    )
    thread.start()