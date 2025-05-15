from PySide6.QtCore import QThread, Signal
from services.manual_check_service import manual_check_logic
from services.excel_services import save_results_to_excel
import time
import os

class ManualCheckWorker(QThread):
    progress_updated = Signal(int)
    finished = Signal(str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        results = manual_check_logic(
            self.file_path,
            progress_callback=self.progress_updated.emit
        )

        if results:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            result_file = f"results/manual_check_{timestamp}.xlsx"
            save_results_to_excel(results, result_file)
            self.finished.emit(result_file)
        else:
            self.finished.emit("no_changes")