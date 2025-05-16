import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PIL import Image
from pillow_heif import register_heif_opener

# HEIF 오프너 등록 (HEIC/HEIF 파일을 Pillow에서 인식하도록 함)
register_heif_opener()


class HEICConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.output_format = "PNG"  # 기본 변환 형식 (PNG 또는 JPEG)
        self.init_ui()

    def init_ui(self):
        self.setAcceptDrops(True)  # 드래그 앤 드롭 활성화

        layout = QVBoxLayout()
        self.info_label = QLabel(
            f"여기에 HEIC 파일을 드래그하세요.\n파일은 {self.output_format}로 변환 후 원본을 대치합니다.", self)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(
            "QLabel { border: 2px dashed #aaa; padding: 20px; }")
        layout.addWidget(self.info_label)

        self.setLayout(layout)
        self.setWindowTitle(f'HEIC to {self.output_format} Converter')
        self.setGeometry(300, 300, 400, 200)  # 창 크기 및 위치 설정

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 드래그된 데이터에 URL(파일 경로)이 있는지 확인
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # 드롭 허용
        else:
            event.ignore()  # 드롭 거부

    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            file_paths = [url.toLocalFile() for url in mime_data.urls()]
            heic_files_found = False
            for file_path in file_paths:
                if file_path.lower().endswith(('.heic', '.heif')):
                    heic_files_found = True
                    self.convert_and_replace(file_path)

            if not heic_files_found:
                QMessageBox.warning(
                    self, "파일 형식 오류", "HEIC 또는 HEIF 파일만 처리할 수 있습니다.")
                self.info_label.setText(
                    f"여기에 HEIC 파일을 드래그하세요.\n파일은 {self.output_format}로 변환 후 원본을 대치합니다.")
        else:
            event.ignore()

    def convert_and_replace(self, heic_file_path):
        try:
            self.info_label.setText(
                f"'{os.path.basename(heic_file_path)}' 변환 중...")
            QApplication.processEvents()  # UI 업데이트 강제

            # HEIC 파일 열기
            image = Image.open(heic_file_path)

            # 출력 파일 경로 설정 (원본 파일명 + 새 확장자)
            base, ext = os.path.splitext(heic_file_path)
            output_file_path = f"{base}.{self.output_format.lower()}"

            # 이미지 저장 (PNG 또는 JPEG)
            if self.output_format.upper() == "PNG":
                image.save(output_file_path, "PNG")
            elif self.output_format.upper() == "JPEG":
                # JPEG의 경우 RGB로 변환 필요할 수 있음 (Pillow가 처리)
                # HEIC는 종종 알파 채널을 포함할 수 있으므로, JPEG로 저장 시 주의
                if image.mode == 'RGBA' or image.mode == 'P':  # 알파 채널이 있거나 팔레트 모드인 경우
                    image = image.convert('RGB')
                image.save(output_file_path, "JPEG",
                           quality=95)  # quality는 0-100
            else:
                raise ValueError(f"지원하지 않는 출력 형식: {self.output_format}")

            # 원본 HEIC 파일 삭제
            os.remove(heic_file_path)

            self.info_label.setText(
                f"'{os.path.basename(heic_file_path)}'이(가)\n'{os.path.basename(output_file_path)}'(으)로 변환 및 대치되었습니다.")
            QMessageBox.information(self, "변환 완료",
                                    f"파일이 성공적으로 변환 및 대치되었습니다:\n{output_file_path}")

        except Exception as e:
            self.info_label.setText(
                f"오류 발생: {os.path.basename(heic_file_path)}\n다시 시도하세요.")
            QMessageBox.critical(
                self, "변환 오류", f"파일 변환 중 오류가 발생했습니다:\n{str(e)}")
        finally:
            # 다음 드롭을 위해 메시지 초기화 (선택 사항)
            # self.info_label.setText(f"여기에 HEIC 파일을 드래그하세요.\n파일은 {self.output_format}로 변환 후 원본을 대치합니다.")
            pass


def main():
    app = QApplication(sys.argv)
    converter_app = HEICConverterApp()
    converter_app.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
