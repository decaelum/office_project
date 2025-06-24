import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox,
    QProgressBar, QInputDialog, QLineEdit
)
from PySide6.QtCore import QSize, Qt

from services.automation_runner import AutomationThread
from services.mail_service import send_mail_with_attachment, check_for_confirmation
from services.logger_service import log_and_print
from services.excel_services import process_and_save_files, read_excel_file, update_products_from_excel
from services.database_services import get_all_products
from services.farmasi_checker import compare_scraped_links_with_db
from services.cleanup import stop_all_threads_and_kill_chromedrivers

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Office Automation System")
        self.setFixedSize(QSize(400, 600))

        layout = QVBoxLayout()

        buttons = [
            ("Start Automation", self.start_automation),
            ("Manual Check", self.manual_check),
            ("Upload Excel & Process", self.upload_excel),
            ("View Results", self.view_results),
            ("View Logs", self.view_logs),
            ("View Products", self.view_products),
            ("Sync Excel to DB", self.sync_excel_to_db), 
            ("Check %Farmasi Products", self.check_farmasi_products),
            ("Stop Automation", self.stop_automation),
            ("Exit", self.close)
        ]

        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_automation(self):
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        start_index, ok1 = QInputDialog.getInt(self, "Start Index", "Enter start index (default 0):", value=0)
        if not ok1:
            return

        end_index, ok2 = QInputDialog.getInt(self, "End Index", "Enter end index (leave 0 for all):", value=0)
        if not ok2:
            return

        self.automation_thread = AutomationThread(start_index=start_index, end_index=end_index)
        self.automation_thread.progress_updated.connect(self.progress_bar.setValue)
        self.automation_thread.automation_finished.connect(self.automation_complete)
        self.automation_thread.start()

    def automation_complete(self, result_path, duration):
        self.progress_bar.setValue(100)

        if result_path:
            QMessageBox.information(
                self,
                "Automation",
                f"✅ Automation completed.\n\n📄 Report saved to: {result_path}\n🕒 Duration: {duration:.2f} seconds"
            )
        else:
            QMessageBox.warning(self, "Automation", "Automation completed, but no report was saved.")

        log_and_print("📧 Asking for receiver email...")
        email, ok = QInputDialog.getText(self, "Receiver Email", "Enter receiver email address:")
        if ok and email:
            log_and_print(f"📧 Receiver email entered: {email}")
            try:
                self.send_email(email)
                log_and_print("📧 Email sent. Awaiting confirmation...")
                self.ask_for_confirmation()
            except Exception as e:
                log_and_print(f"❌ Failed to send email: {e}", level="error")
        else:
            log_and_print("❌ Email sending cancelled by user.")
            QMessageBox.warning(self, "Cancelled", "E-Mail sending cancelled.")

    def send_email(self, receiver_email):
        try:
            send_mail_with_attachment(
                receiver_email=receiver_email,
                subject="Automation Completed",
                body="Automation process completed successfully. Please find the report attached.",
                attachment_path="results/report.xlsx"
            )
            QMessageBox.information(self, "Email Sent", "Email successfully sent.")
        except Exception as e:
            log_and_print(f"❌ Failed to send email: {e}", level="error")
            QMessageBox.warning(self, "Error", f"Failed to send email: {e}")

    def ask_for_confirmation(self):
        subject_keyword, ok1 = QInputDialog.getText(self, "Confirmation Subject", "Enter email subject keyword to confirm:")
        if not ok1 or not subject_keyword:
            QMessageBox.warning(self, "Cancelled", "Confirmation subject is required.")
            return

        wait_minutes, ok2 = QInputDialog.getInt(self, "Wait Time", "Enter wait time (minutes):", value=5, min=1, max=60)
        if not ok2:
            return

        check_interval, ok3 = QInputDialog.getInt(self, "Check Interval", "Enter check interval (seconds):", value=30, min=5, max=300)
        if not ok3:
            return

        confirmed = check_for_confirmation(
            subject_keyword=subject_keyword,
            wait_minutes=wait_minutes,
            check_interval=check_interval
        )

        if confirmed:
            QMessageBox.information(self, "Confirmation", "Confirmation email received!")
        else:
            QMessageBox.warning(self, "Timeout", "Confirmation email not received in the given time.")

    def manual_check(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            df = read_excel_file(file_path)
            if df.empty:
                QMessageBox.warning(self, "Manual Check", "Selected file is invalid or empty.")
            else:
                process_and_save_files([file_path], db_name="data/products.db")
                QMessageBox.information(self, "Manual Check", "Manual check completed and data processed.")

    def upload_excel(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Excel Files", "", "Excel Files (*.xlsx)")
        if files:
            process_and_save_files(files, db_name="data/products.db")
            QMessageBox.information(self, "Excel Upload", f"{len(files)} file(s) processed successfully.")
        else:
            QMessageBox.warning(self, "Excel Upload", "No files selected.")

    def view_results(self):
        result_dir = "results/"
        if not os.path.exists(result_dir):
            QMessageBox.warning(self, "Results", "No results directory found.")
            return

        files = [f for f in os.listdir(result_dir) if f.endswith(".xlsx")]
        if not files:
            QMessageBox.information(self, "Results", "No result files found.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Select a Result File", result_dir, "Excel Files (*.xlsx)")
        if file_path:
            try:
                if sys.platform == "darwin":
                    subprocess.Popen(['open', file_path])
                elif os.name == "nt":
                    os.startfile(file_path)
                else:
                    subprocess.Popen(['xdg-open', file_path])
            except Exception as e:
                QMessageBox.warning(self, "Results", f"Failed to open file: {e}")

    def view_logs(self):
        log_dir = "logs/"
        if not os.path.exists(log_dir):
            QMessageBox.warning(self, "Logs", "No logs directory found.")
            return

        files = [f for f in os.listdir(log_dir) if f.endswith(".log") or f.endswith(".txt")]
        if not files:
            QMessageBox.information(self, "Logs", "No log files found.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Select a Log File", log_dir, "Log Files (*.log *.txt)")
        if file_path:
            try:
                if sys.platform == "darwin":
                    subprocess.Popen(['open', file_path])
                elif os.name == "nt":
                    os.startfile(file_path)
                else:
                    subprocess.Popen(['xdg-open', file_path])
            except Exception as e:
                QMessageBox.warning(self, "Logs", f"Failed to open log file: {e}")

    def view_products(self):
        products = get_all_products(db_name="data/products.db")
        if not products:
            QMessageBox.information(self, "Products", "No products found in the database.")
            return

        self.product_window = QWidget()
        self.product_window.setWindowTitle("Products in Database")
        self.product_window.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Search by Barcode, Product Name or URL...")
        layout.addWidget(search_input)

        table = QTableWidget()
        table.setRowCount(len(products))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Barcode", "Product Name", "URL", "Last Control"])
        layout.addWidget(table)

        for row_idx, row_data in enumerate(products):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                table.setItem(row_idx, col_idx, item)

        def filter_table():
            query = search_input.text().lower()
            for row in range(table.rowCount()):
                match = False
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item and query in item.text().lower():
                        match = True
                        break
                table.setRowHidden(row, not match)

        search_input.textChanged.connect(filter_table)

        self.product_window.setLayout(layout)
        self.product_window.show()

    def sync_excel_to_db(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel File for Sync", "", "Excel Files (*.xlsx)")
        if file_path:
            try:
                report_path = update_products_from_excel(file_path, db_name="data/products.db")
                if report_path:
                    QMessageBox.information(self, "Sync Completed", f"Update report generated:\n{report_path}")
                else:
                    QMessageBox.information(self, "Sync Completed", "No records required updating.")
            except Exception as e:
                log_and_print(f"❌ Sync failed: {e}", level="error")
                QMessageBox.warning(self, "Error", f"Sync failed: {e}")
        else:
            QMessageBox.information(self, "Cancelled", "No file selected.")

    def check_farmasi_products(self):
        new_path, updated_path = compare_scraped_links_with_db()

        if not new_path and not updated_path:
            QMessageBox.information(self, "Farmasi Check", "No new or updated products found.")
            return

        message = "Farmasi product check completed.\n"
        if new_path:
            message += f"📄 New Products Report: {new_path}\n"
        if updated_path:
            message += f"📄 Updated URLs Report: {updated_path}"
        QMessageBox.information(self, "Farmasi Check", message)

    def stop_automation(self):
        if hasattr(self, 'automation_thread') and self.automation_thread.isRunning():
            self.automation_thread.stop()
            stop_all_threads_and_kill_chromedrivers()
            log_and_print("🚨 Automation stop command issued by user.")
        else:
            log_and_print("⚠️ No running automation thread to stop.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())