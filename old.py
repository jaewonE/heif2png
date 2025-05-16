import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QListWidget, QStackedWidget, QSizePolicy,
    QMessageBox, QSpacerItem, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QMimeData, QSize, QUrl, QByteArray
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QImage, QPalette, QColor, QIcon

# pillow-heif 오프너 등록
try:
    # HeifImagePlugin 임포트는 Pillow 10.0.0 이상에서 필요할 수 있음
    from pillow_heif import register_heif_opener, HeifImagePlugin
    register_heif_opener()
except ImportError:
    QMessageBox.critical(
        None, "라이브러리 오류", "pillow-heif 라이브러리를 찾을 수 없습니다. 설치해주세요.")
    sys.exit(1)

from PIL import Image

# 애플리케이션 아이콘용 (간단한 Base64 인코딩된 아이콘 데이터)
# 실제 사용 시에는 .ico 또는 .png 파일 경로를 지정하는 것이 좋습니다.
APP_ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAARMSURBVHhe7ZtNbBxlGMf//88c2x3LdlrbStumFClpFSlFBFGPUY8eRKOCHkAMHjRI40EPSk00GgmGBEFNIyhRsA9VgYp4KCgJgkS02oSN2MYYYzu2sWO/M/N4v9vZGZ8d+1EPzP6kZ3ZmZ/b3fd7vfN/3eV4CJGgg6M0g6I0g6I0g6I0g6I0g6I0g6I0g6E0hANBisL29TXNzc0oikaisrq7S2tqa0u12qaurS+np6Y2XjY2NaWNjg4qKihQWFhY0vV6v80EHBwfq6+tTDAZDr2hpaUHbtm0aGBhIvb29NDAwULPZzGtra7R9+3YtLS3N+PjU1RTk5+fHlJeXp7q6OhoaGkqv15u2jo6O3kEqlcr4/v7+A9PT0xkdHS2RSKSRkRG6urqSy+U0NjZWnZycKJfL6evri1arRTAYpNVqzcifnp6mra0tJSUlGZcvX6alpSVKl8tNJBKhlZUVNTU1KTQ0NP0kKysrGRsbS6PRGAkEAnA4HHR0dFAoFCGEkMvlkvH5+fmkv78/xWKxDA4OJiKRaHh5eUlVVVX6+voSTqeber3emJiYyNvbWwoLC9Pc3JzKysoSCARobGyMmzdvUnNzMzk5OdHc3JzS0tLodDqVlZWlXC7XFBcXHwS/v79TPp9Pc3NzjIyMJDc3N51Op0ajUTU1NSGEBgYGNDc3JxKJRBqNRqFQSDQazcjISDIyMsLExARZlpWXl6euri5NTU1pbGyMSqXScDhMIpHI0Ov1KBaLlJaWpnA4XHC5XAgEAjQ2Nqazs7PzfSsrK+np6UnV1dXk5OTExMQEtFotPp+PwMBAWltbk5eXF/Pz8xkaGko0Gm24ublJIpFIuVxuW1tb09LSEg0NDZmamkpNTU0ikUgaGhrSLFuBQQiBQACDwQCpVJpyuRxFUWxtbVFZWZkCAgKMiYlBkqTt7e10d3dnRkYGubm5kZGRgY6ODqZPn47S0lJGR0fR2NiYMjIyGBoawrRp0zA2Nobm5mYaGhrQ3t6OhIQEjI2NwdGjRzE2Nob+/n6Ghobw9vYGd3d3jImJwdjYGADw8PAAQUFBGBsbw4iICNy6dQvV1dXk5eXBxMSEgoICHBycGBkZCR+Ph9DQULhcLrKzsyGEcPXqVXR0dCAQCACQmJhIbm4uISEh6OrqQlpaGuHh4UhPT0cpKSlOnz6NhoYGuru7UVVVhZaWFgQCAQYHB9Hc3IylS5ca3r17l0AgADc3N0RFRQEAoVAIMpkMZWVl8Pl8BAIBuFwuDAYDTExMICAggCAhISEhOXDgALq7u6HVajE0NITe3l5sbGzg4OAAb29vaGlpQUVFBRqNBqOjo/Dx8QFPnjxh/fr1AIDq6moAQElJCQ4dOgSHw4GdnR2ys7MRCARwcHAANzc3AMDZ2RkHBwdsbm5Cc3Nz+p4uLS2NN2/eRKlUyrNnz1IsFuPq1athtVoAgMFgwMrKCg6HwwgGg6Snp0OtVjM+Pj6O7u5uvLy8AADUajWcnJyQl5cXoVCIVqs1jY2NmJmZSTQaZWxsLPX19Ziamlp0U9La2pqu7u709PSkcDhMXV1dmpqaSn19fRqNRuOziMViNDk5mf7+/jQzM6Ouri5NTU3tOWhpacnn5+dUq1VKpVJLS0tjWlpaNDY2JhKJRKFQSFtbW8rn8wkJCTHcEaWlpamqqkokEqGxsTGlpaVx8uTJhgcNGjRAOp2mWCzG4uJiLC0tJRqNkpubm+H5rKyspLOzk0gkQjabJTc3F/f39zgcDrS2tiIsLAyBQAB+fn7Q6/UITU3N9O339nZGRISQjAYpbGxUYSCX6WwB74s1/eHnEwR9EwR9EwR9EwR9EwR9EwR9EwR9k/wHy9hLmh6e3nEAAAAASUVORK5CYII="


class HoverLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_normal_style()
        self.setAcceptDrops(True)  # 드래그 앤 드롭 이벤트를 위젯 자체에서 받도록 설정

    def set_normal_style(self):
        self.setStyleSheet(
            "QLabel { border: 2px dashed #aaa; padding: 20px; background-color: #f0f0f0; }")
        self.setText("여기에 HEIC 파일을 드래그하세요.\n\n옵션 확인 후 하단의 '변환 시작' 버튼을 누르세요.")

    def set_hover_style(self):
        self.setStyleSheet(
            "QLabel { border: 3px solid #0078d7; padding: 20px; background-color: #e0e0ff; }")
        self.setText("여기에 파일을 놓으세요!")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.set_hover_style()
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.set_normal_style()
        event.accept()

    def dropEvent(self, event: QDropEvent):  # HoverLabel에서 drop 이벤트를 직접 처리
        self.set_normal_style()
        # 이벤트를 부모 위젯(HEICConverterApp)으로 전달하여 파일 처리
        if self.parentWidget() and hasattr(self.parentWidget(), 'handle_dropped_files'):
            self.parentWidget().handle_dropped_files(event.mimeData())
        else:
            # 또는 HEICConverterApp의 dropEvent를 직접 호출할 수 있도록 설계
            # 여기서는 MainWindow의 dropEvent를 호출하는 방식으로 가정
            main_window = self.window()  # 최상위 윈도우 찾기
            if isinstance(main_window, HEICConverterApp):
                main_window.process_dropped_urls(event.mimeData().urls())


class FileListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)  # 외부 드롭만 허용
        self.setAlternatingRowColors(True)
        # self.setStyleSheet("QListWidget { border: 1px solid #ccc; }")

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 드래그된 데이터가 URL(파일)인지 확인
        if event.mimeData().hasUrls():
            # 복사 아이콘(+) 표시
            event.setDropAction(Qt.DropAction.CopyAction)
            self.set_hover_style()
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragEnterEvent):
        # 드래그 도중에도 계속 복사 아이콘 표시 & 수락
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        # 드래그가 영역을 벗어나면 스타일 원복
        self.set_normal_style()
        event.accept()

    def dropEvent(self, event: QDropEvent):
        # 드롭 시 스타일 원복
        self.set_normal_style()

        if event.mimeData().hasUrls():
            main_window = self.window()
            if isinstance(main_window, HEICConverterApp):
                # append=True 로 추가
                main_window.process_dropped_urls(
                    event.mimeData().urls(), append=True)
            # 드롭 이벤트 최종 수락 → 파일이 실제로 추가됨
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()


class HEICConverterApp(QWidget):
    MIN_WIDTH_FOR_PREVIEW = 750  # 미리보기가 보이는 최소 창 너비
    PREVIEW_PLACEHOLDER_COLOR = QColor(220, 220, 220)  # 회색

    def __init__(self):
        super().__init__()
        self.file_paths = []
        self.current_preview_path = None
        self.init_ui()

        # 애플리케이션 아이콘 설정
        try:
            from PyQt6.QtGui import QImageReader
            img_reader = QImageReader.imageFormat(
                QByteArray.fromBase64(APP_ICON_B64.encode()))
            if img_reader:
                icon_img = QImage.fromData(
                    QByteArray.fromBase64(APP_ICON_B64.encode()))
                self.setWindowIcon(QIcon(QPixmap.fromImage(icon_img)))
        except Exception as e:
            print(f"아이콘 로드 실패: {e}")  # 실제로는 로깅 사용

    def init_ui(self):
        self.setWindowTitle('HEIC 변환기')
        self.setGeometry(100, 100, 800, 600)  # 초기 크기

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # 창 전체 마진
        main_layout.setSpacing(10)

        # --- 상단 섹션 ---
        top_section_layout = QHBoxLayout()
        top_section_layout.setSpacing(15)

        self.format_label = QLabel("변환 포맷:")
        self.format_dropdown = QComboBox()
        self.format_dropdown.addItems(["PNG", "JPEG", "WEBP"])
        self.format_dropdown.setCurrentText("PNG")
        self.format_dropdown.setToolTip("이미지를 변환할 포맷을 선택합니다.")

        self.replace_checkbox = QCheckBox("파일을 대치합니다")
        self.replace_checkbox.setChecked(True)
        self.replace_checkbox.setToolTip(
            "체크 시 원본 파일을 변환된 파일로 대치합니다.\n"
            "체크 해제 시 원본 파일과 동일한 경로의 '변환된 파일' 폴더에 저장합니다."
        )

        top_section_layout.addWidget(self.format_label)
        top_section_layout.addWidget(self.format_dropdown)
        top_section_layout.addWidget(self.replace_checkbox)
        top_section_layout.addStretch(1)  # 오른쪽으로 밀기

        main_layout.addLayout(top_section_layout)

        # --- 본문 섹션 (QStackedWidget 사용) ---
        self.body_stack = QStackedWidget()
        # Stretch factor 1 to take available space
        main_layout.addWidget(self.body_stack, 1)

        # 본문 1: 파일 없을 때
        self.no_files_view = HoverLabel("여기에 HEIC 파일을 드래그하세요.")
        # HoverLabel이 drop 이벤트를 직접 처리하도록 수정했으므로, 여기서 setAcceptDrops는 필요 없음
        # self.no_files_view.setAcceptDrops(True)
        # self.no_files_view.dragEnterEvent = self.no_files_drag_enter_event
        # self.no_files_view.dragLeaveEvent = self.no_files_drag_leave_event
        # self.no_files_view.dropEvent = self.no_files_drop_event
        self.body_stack.addWidget(self.no_files_view)

        # 본문 2: 파일 있을 때 (QSplitter 사용)
        self.files_selected_view = QWidget()
        files_selected_layout = QHBoxLayout(self.files_selected_view)
        files_selected_layout.setContentsMargins(
            0, 0, 0, 0)  # No margins for the splitter to fill

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # 좌측: 파일명 리스트
        self.file_list_widget = FileListWidget()
        self.file_list_widget.currentItemChanged.connect(self.update_preview)
        self.file_list_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.file_list_widget.setMinimumHeight(200) # 최소 높이 설정
        self.splitter.addWidget(self.file_list_widget)

        # 우측: 이미지 미리보기
        self.preview_label = QLabel("이미지 미리보기")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_label.setMinimumWidth(200)  # 미리보기 최소 너비
        self._set_preview_placeholder()
        self.splitter.addWidget(self.preview_label)

        self.splitter.setSizes([300, 500])  # 초기 크기 비율 설정
        files_selected_layout.addWidget(self.splitter)

        self.body_stack.addWidget(self.files_selected_view)

        # --- 하단 섹션 ---
        bottom_section_layout = QHBoxLayout()
        self.convert_button = QPushButton("변환 시작")
        self.convert_button.setFixedHeight(40)  # 버튼 높이 고정
        self.convert_button.setStyleSheet(
            "QPushButton { background-color: #0078d7; color: white; font-weight: bold; border-radius: 5px; } QPushButton:hover { background-color: #005a9e; }")
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setEnabled(False)  # 초기에는 비활성화

        bottom_section_layout.addWidget(self.convert_button)
        main_layout.addLayout(bottom_section_layout)

        self.setLayout(main_layout)
        self.setAcceptDrops(True)  # 메인 윈도우도 드롭을 받을 수 있도록

    def _set_preview_placeholder(self):
        self.preview_label.setText("선택된 파일 없음")
        palette = self.preview_label.palette()
        palette.setColor(QPalette.ColorRole.Window,
                         self.PREVIEW_PLACEHOLDER_COLOR)
        self.preview_label.setAutoFillBackground(True)
        self.preview_label.setPalette(palette)
        self.preview_label.setPixmap(QPixmap())  # 이전 이미지 제거

    def handle_dropped_files(self, mime_data: QMimeData):  # HoverLabel에서 호출됨
        if mime_data.hasUrls():
            self.process_dropped_urls(mime_data.urls())

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 이 이벤트는 body_stack의 현재 위젯이 드롭을 처리하지 않을 때 (예: QStackedWidget 자체 영역) 발생 가능
        # 또는 HoverLabel을 사용하지 않고 메인 윈도우에서 직접 드롭 처리할 때
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # 만약 no_files_view가 현재 보이고 있다면, 여기서도 호버 효과를 줄 수 있음
            if self.body_stack.currentWidget() == self.no_files_view:
                self.no_files_view.set_hover_style()  # HoverLabel의 dragEnterEvent가 우선함
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragEnterEvent):
        if self.body_stack.currentWidget() == self.no_files_view:
            self.no_files_view.set_normal_style()  # HoverLabel의 dragLeaveEvent가 우선함
        event.accept()

    def dropEvent(self, event: QDropEvent):
        # 이 이벤트는 body_stack의 현재 위젯이 드롭을 처리하지 않을 때 발생
        if self.body_stack.currentWidget() == self.no_files_view:
            self.no_files_view.set_normal_style()  # HoverLabel의 dropEvent가 우선함

        if event.mimeData().hasUrls():
            self.process_dropped_urls(event.mimeData().urls())
            event.acceptProposedAction()
        else:
            event.ignore()

    def process_dropped_urls(self, urls, append=False):
        new_files_added = False
        if not append:
            # 새로 드롭하면 기존 목록 초기화 (파일 리스트 위젯으로 드롭 시에는 append=True)
            self.file_paths = []

        for url in urls:
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.heic', '.heif')):
                    if file_path not in self.file_paths:  # 중복 방지
                        self.file_paths.append(file_path)
                        new_files_added = True
                else:
                    QMessageBox.warning(
                        self, "파일 형식 오류", f"지원하지 않는 파일 형식입니다: {os.path.basename(file_path)}")

        # 새 파일이 추가되었거나, 초기 드롭으로 파일이 있는 경우
        if new_files_added or (not append and self.file_paths):
            self.update_file_list_widget()
            self.body_stack.setCurrentWidget(self.files_selected_view)
            self.convert_button.setEnabled(True)
            if self.file_list_widget.count() > 0:
                self.file_list_widget.setCurrentRow(0)  # 첫 번째 아이템 자동 선택
            self.update_preview_visibility()  # 창 크기에 따라 미리보기 업데이트
        elif not self.file_paths:  # 파일이 하나도 없는 경우 (모두 필터링 되었거나, 비었거나)
            self.body_stack.setCurrentWidget(self.no_files_view)
            self.convert_button.setEnabled(False)

    def update_file_list_widget(self):
        self.file_list_widget.clear()
        for path in self.file_paths:
            self.file_list_widget.addItem(os.path.basename(path))

    def update_preview(self, current_item, previous_item):
        if not current_item:
            self._set_preview_placeholder()
            self.current_preview_path = None
            return

        selected_filename = current_item.text()
        # 전체 경로 찾기 (self.file_paths에 저장된 원본 경로 사용)
        # QListWidget에는 basename만 표시하므로, 전체 경로를 찾아야 함
        # 여러 폴더에서 온 파일이 같은 이름을 가질 수 있으므로, 인덱스를 사용하는 것이 더 안전할 수 있으나,
        # 현재는 basename으로 간단히 매칭
        # 더 견고한 방법: QListWidgetItem에 UserRole로 전체 경로 저장
        self.current_preview_path = None
        for path in self.file_paths:
            if os.path.basename(path) == selected_filename:
                # 만약 같은 이름의 파일이 여러개면 첫번째 것을 사용.
                # self.file_list_widget.currentRow()를 사용하여 self.file_paths의 인덱스와 매칭하는 것이 더 정확
                try:
                    idx = self.file_list_widget.row(current_item)
                    if 0 <= idx < len(self.file_paths):
                        self.current_preview_path = self.file_paths[idx]
                        break
                except Exception:  # 만약을 대비한 예외처리
                    pass

        if not self.current_preview_path:  # 혹시 경로를 못찾으면
            for path in self.file_paths:  # 단순 이름으로 다시 한번 시도
                if os.path.basename(path) == selected_filename:
                    self.current_preview_path = path
                    break

        if self.current_preview_path:
            try:
                # pillow_heif가 등록되었으므로 Pillow의 Image.open 사용 가능
                pil_image = Image.open(self.current_preview_path)

                # Pillow 이미지를 QImage로 변환
                # RGBA, RGB 등 다양한 모드 처리
                if pil_image.mode == "RGBA":
                    q_image = QImage(pil_image.tobytes(
                        "raw", "RGBA"), pil_image.width, pil_image.height, QImage.Format.Format_RGBA8888)
                elif pil_image.mode == "RGB":
                    q_image = QImage(pil_image.tobytes(
                        "raw", "RGB"), pil_image.width, pil_image.height, QImage.Format.Format_RGB888)
                else:  # 다른 모드(예: L, P)는 RGB로 변환
                    pil_image = pil_image.convert("RGB")
                    q_image = QImage(pil_image.tobytes(
                        "raw", "RGB"), pil_image.width, pil_image.height, QImage.Format.Format_RGB888)

                pixmap = QPixmap.fromImage(q_image)
                self.preview_label.setAutoFillBackground(False)  # 배경색 칠하기 해제
                self.preview_label.setPixmap(pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            except Exception as e:
                self._set_preview_placeholder()
                self.preview_label.setText(
                    f"미리보기 오류:\n{os.path.basename(self.current_preview_path)}\n{e}")
                QMessageBox.warning(
                    self, "미리보기 오류", f"'{os.path.basename(self.current_preview_path)}' 파일 미리보기 중 오류: {e}")
        else:
            self._set_preview_placeholder()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_preview_visibility()
        # 현재 선택된 이미지가 있다면 미리보기 크기 업데이트
        if self.current_preview_path and self.preview_label.isVisible():
            self.update_preview(self.file_list_widget.currentItem(), None)

    def update_preview_visibility(self):
        if self.body_stack.currentWidget() == self.files_selected_view:
            if self.width() < self.MIN_WIDTH_FOR_PREVIEW:
                self.preview_label.hide()
            else:
                self.preview_label.show()
                # QSplitter의 크기 재조정 (예: 리스트와 미리보기가 대략 1:2 비율 유지)
                # 단, 사용자가 조절한 크기를 존중하는 것이 좋을 수 있음. 여기서는 단순 show/hide만.
                # self.splitter.setSizes([self.width() // 3, self.width() * 2 // 3])

    def start_conversion(self):
        if not self.file_paths:
            QMessageBox.information(self, "알림", "변환할 파일이 없습니다.")
            return

        output_format_str = self.format_dropdown.currentText().lower()
        replace_original = self.replace_checkbox.isChecked()

        converted_count = 0
        error_count = 0
        output_folders = set()  # 생성된 '변환된 파일' 폴더 경로 저장 (알림용)

        self.convert_button.setEnabled(False)  # 변환 중 버튼 비활성화
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        for file_path in self.file_paths:
            base_name = os.path.basename(file_path)
            dir_name = os.path.dirname(file_path)
            file_root, _ = os.path.splitext(base_name)

            output_path = ""

            if replace_original:
                output_path = os.path.join(
                    dir_name, f"{os.path.splitext(file_path)[0]}.{output_format_str}")
            else:
                converted_files_dir = os.path.join(dir_name, "변환된 파일")
                if not os.path.exists(converted_files_dir):
                    try:
                        os.makedirs(converted_files_dir)
                    except OSError as e:
                        QMessageBox.critical(
                            self, "폴더 생성 오류", f"'{converted_files_dir}' 폴더 생성 중 오류: {e}")
                        error_count += 1
                        continue  # 다음 파일로
                output_path = os.path.join(
                    converted_files_dir, f"{file_root}.{output_format_str}")
                output_folders.add(converted_files_dir)

            try:
                image = Image.open(file_path)
                save_options = {}
                if output_format_str == "jpeg":
                    # HEIC는 알파 채널을 가질 수 있으므로 JPEG 저장 시 RGB로 변환
                    if image.mode in ('RGBA', 'P', 'LA'):
                        image = image.convert('RGB')
                    save_options['quality'] = 95  # 기본 JPEG 품질
                elif output_format_str == "webp":
                    save_options['quality'] = 90  # WebP 품질
                    if image.mode in ('P', 'LA') and 'transparency' in image.info:  # WebP는 알파채널 지원
                        image = image.convert('RGBA')
                    elif image.mode not in ('RGB', 'RGBA'):
                        image = image.convert('RGB')

                image.save(output_path, output_format_str.upper(),
                           **save_options)

                # 확장자가 달라졌을 경우 (항상 그럴 것)
                if replace_original and output_path != file_path:
                    os.remove(file_path)
                converted_count += 1

            except Exception as e:
                error_count += 1
                QMessageBox.critical(
                    self, "변환 오류", f"'{base_name}' 파일 변환 중 오류: {e}")

        QApplication.restoreOverrideCursor()
        self.convert_button.setEnabled(True)

        summary_message = f"총 {len(self.file_paths)}개 파일 중:\n성공: {converted_count}개\n실패: {error_count}개\n"
        if not replace_original and output_folders:
            summary_message += "\n변환된 파일은 다음 폴더(들)에 저장되었습니다:\n" + \
                "\n".join(list(output_folders))

        QMessageBox.information(self, "변환 완료", summary_message)

        # 변환 후 파일 목록 초기화 또는 유지 선택 가능 (여기서는 유지)
        # self.file_paths = []
        # self.update_file_list_widget()
        # self.body_stack.setCurrentWidget(self.no_files_view)
        # self.convert_button.setEnabled(False)
        # self._set_preview_placeholder()


def main():
    app = QApplication(sys.argv)

    converter_app = HEICConverterApp()
    converter_app.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
