import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QListWidget, QStackedWidget, QSizePolicy,
    QMessageBox, QSpacerItem, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QMimeData, QSize, QUrl, QByteArray
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QImage, QPalette, QColor, QIcon

# Register pillow‑heif opener
try:
    # Importing HeifImagePlugin may be required for Pillow ≥ 10.0.0
    from pillow_heif import register_heif_opener, HeifImagePlugin
    register_heif_opener()
except ImportError:
    QMessageBox.critical(
        None, "Library Error", "Could not find the pillow‑heif library. Please install it.")
    sys.exit(1)

from PIL import Image


class HoverLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_normal_style()
        # Accept drag‑and‑drop events directly on this widget
        self.setAcceptDrops(True)

    def set_normal_style(self):
        self.setStyleSheet(
            "QLabel { border: 2px dashed #aaa; padding: 20px; background-color: #f0f0f0; }")
        self.setText(
            "Drag HEIC files here.\n\nAfter checking the options, click the 'Start Conversion' button below.")

    def set_hover_style(self):
        self.setStyleSheet(
            "QLabel { border: 3px solid #0078d7; padding: 20px; background-color: #e0e0ff; }")
        self.setText("Drop files here!")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.set_hover_style()
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.set_normal_style()
        event.accept()

    def dropEvent(self, event: QDropEvent):  # Handle the drop event directly in HoverLabel
        self.set_normal_style()
        # Forward the event to the parent widget (HEICConverterApp) to process files
        if self.parentWidget() and hasattr(self.parentWidget(), 'handle_dropped_files'):
            self.parentWidget().handle_dropped_files(event.mimeData())
        else:
            # Alternatively, you can design this to call HEICConverterApp.dropEvent directly
            # Here we assume calling the main window’s dropEvent
            main_window = self.window()  # Find the top-level window
            if isinstance(main_window, HEICConverterApp):
                main_window.process_dropped_urls(event.mimeData().urls())


class FileListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        # Only allow external drops
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)
        self.setAlternatingRowColors(True)
        self.set_normal_style()

    def set_normal_style(self):
        self.setStyleSheet("QListWidget { border: 1px solid #ccc; }")

    def set_hover_style(self):
        self.setStyleSheet(
            "QListWidget { border: 2px solid #0078d7; background-color: #f5faff; }")

    # ---------- DnD events ----------
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Called when files enter the list area."""
        if event.mimeData().hasUrls():
            # Show a ➕ cursor icon
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            self.set_hover_style()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragEnterEvent):
        """Keep accepting the drag while it moves inside the list area."""
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Restore the style when the drag leaves the list area."""
        self.set_normal_style()
        event.accept()

    def dropEvent(self, event: QDropEvent):
        """Handle files after the drop is completed."""
        self.set_normal_style()

        if event.mimeData().hasUrls():
            main_window = self.window()
            if isinstance(main_window, HEICConverterApp):
                # append=True to add to the bottom of the list
                main_window.process_dropped_urls(
                    event.mimeData().urls(), append=True)
            # Finally accept the event & keep the copy cursor
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()


class HEICConverterApp(QWidget):
    MIN_WIDTH_FOR_PREVIEW = 750  # Minimum window width to show the preview.
    PREVIEW_PLACEHOLDER_COLOR = QColor(220, 220, 220)  # Gray.

    def __init__(self):
        super().__init__()
        self.file_paths = []
        self.current_preview_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('HEIC Converter')
        self.setGeometry(100, 100, 800, 600)  # 초기 크기

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # 창 전체 마진
        main_layout.setSpacing(10)

        # --- 상단 섹션 ---
        top_section_layout = QHBoxLayout()
        top_section_layout.setSpacing(15)

        self.format_label = QLabel("Output format:")
        self.format_dropdown = QComboBox()
        self.format_dropdown.addItems(["PNG", "JPEG", "WEBP"])
        self.format_dropdown.setCurrentText("PNG")
        self.format_dropdown.setToolTip("이미지를 변환할 포맷을 선택합니다.")

        self.replace_checkbox = QCheckBox("Overwrite original files")
        self.replace_checkbox.setChecked(True)
        self.replace_checkbox.setToolTip(
            "If checked, the original file will be replaced with the converted file.\n"
            "If unchecked, converted files will be saved in a 'Converted Files' folder next to the original."
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
        self.no_files_view = HoverLabel("Drag HEIC files here.")
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
        self.preview_label = QLabel("Image Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 이미지가 커도 QLabel이 스스로 크기를 키우지 않도록 함
        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.preview_label.setScaledContents(False)
        self.preview_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_label.setMinimumWidth(200)  # 미리보기 최소 너비
        self._set_preview_placeholder()
        self.splitter.addWidget(self.preview_label)

        self.splitter.setSizes([300, 500])  # 초기 크기 비율 설정
        files_selected_layout.addWidget(self.splitter)

        self.body_stack.addWidget(self.files_selected_view)

        # --- 하단 섹션 ---
        bottom_section_layout = QHBoxLayout()
        self.convert_button = QPushButton("Start Conversion")
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
        self.preview_label.setText("No file selected")
        palette = self.preview_label.palette()
        palette.setColor(QPalette.ColorRole.Window,
                         self.PREVIEW_PLACEHOLDER_COLOR)
        self.preview_label.setAutoFillBackground(True)
        self.preview_label.setPalette(palette)
        self.preview_label.setPixmap(QPixmap())  # Remove previous image

    def handle_dropped_files(self, mime_data: QMimeData):  # HoverLabel에서 호출됨
        if mime_data.hasUrls():
            self.process_dropped_urls(mime_data.urls())

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 파일이 이미 선택된 상태라면 메인 윈도우에서의 드롭은 무시하고
        # FileListWidget 자체에서만 드롭을 허용한다.
        if self.body_stack.currentWidget() != self.no_files_view:
            event.ignore()
            return

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Hover 효과
            self.no_files_view.set_hover_style()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragEnterEvent):
        if self.body_stack.currentWidget() == self.no_files_view:
            self.no_files_view.set_normal_style()  # HoverLabel의 dragLeaveEvent가 우선함
        event.accept()

    def dropEvent(self, event: QDropEvent):
        # 파일 목록이 이미 있을 때는 메인 윈도우가 드롭을 처리하지 않는다.
        if self.body_stack.currentWidget() != self.no_files_view:
            event.ignore()
            return

        self.no_files_view.set_normal_style()

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
                    if file_path not in self.file_paths:  # Avoid duplicates
                        self.file_paths.append(file_path)
                        new_files_added = True
                else:
                    QMessageBox.warning(
                        self, "File Type Error", f"Unsupported file format: {os.path.basename(file_path)}")

        # If new files were added, or if files exist after initial drop
        if new_files_added or (not append and self.file_paths):
            self.update_file_list_widget()
            self.body_stack.setCurrentWidget(self.files_selected_view)
            self.convert_button.setEnabled(True)
            if self.file_list_widget.count() > 0:
                self.file_list_widget.setCurrentRow(
                    0)  # Auto-select first item
            self.update_preview_visibility()  # Update preview according to window size
        elif not self.file_paths:  # No files at all (all filtered or empty)
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
        # Find the full path (use original path from self.file_paths)
        # Only basename is shown in QListWidget, so need to match
        # Multiple files from different folders could have the same name; using index is safer,
        # but for now, simple basename matching
        # More robust: store the full path in QListWidgetItem UserRole
        self.current_preview_path = None
        for path in self.file_paths:
            if os.path.basename(path) == selected_filename:
                # If multiple files have the same name, use the first one.
                # More accurate: match index using self.file_list_widget.currentRow()
                try:
                    idx = self.file_list_widget.row(current_item)
                    if 0 <= idx < len(self.file_paths):
                        self.current_preview_path = self.file_paths[idx]
                        break
                except Exception:
                    pass

        if not self.current_preview_path:  # If not found by index, try simple name match
            for path in self.file_paths:
                if os.path.basename(path) == selected_filename:
                    self.current_preview_path = path
                    break

        if self.current_preview_path:
            try:
                # pillow_heif is registered, so Pillow's Image.open works
                pil_image = Image.open(self.current_preview_path)

                # Convert Pillow image to QImage (handle RGBA, RGB, etc.)
                if pil_image.mode == "RGBA":
                    data = pil_image.tobytes("raw", "RGBA")
                    bytes_per_line = pil_image.width * 4
                    q_image = QImage(data, pil_image.width, pil_image.height,
                                     bytes_per_line, QImage.Format.Format_RGBA8888)
                elif pil_image.mode == "RGB":
                    data = pil_image.tobytes("raw", "RGB")
                    bytes_per_line = pil_image.width * 3
                    q_image = QImage(data, pil_image.width, pil_image.height,
                                     bytes_per_line, QImage.Format.Format_RGB888)
                else:  # Other modes (e.g. L, P): convert to RGB
                    pil_image = pil_image.convert("RGB")
                    data = pil_image.tobytes("raw", "RGB")
                    bytes_per_line = pil_image.width * 3
                    q_image = QImage(data, pil_image.width, pil_image.height,
                                     bytes_per_line, QImage.Format.Format_RGB888)

                pixmap = QPixmap.fromImage(q_image)
                self.preview_label.setAutoFillBackground(
                    False)  # Disable background fill
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
            except Exception as e:
                self._set_preview_placeholder()
                self.preview_label.setText(
                    f"Preview Error:\n{os.path.basename(self.current_preview_path)}\n{e}")
                QMessageBox.warning(
                    self, "Preview Error", f"Error previewing '{os.path.basename(self.current_preview_path)}': {e}")
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
                # Optionally resize QSplitter to maintain a 1:2 ratio between list and preview.
                # However, it's better to respect user-adjusted sizes; here we simply show/hide.
                # self.splitter.setSizes([self.width() // 3, self.width() * 2 // 3])

    def start_conversion(self):
        if not self.file_paths:
            QMessageBox.information(
                self, "Notice", "There are no files to convert.")
            return

        output_format_str = self.format_dropdown.currentText().lower()
        replace_original = self.replace_checkbox.isChecked()

        converted_count = 0
        error_count = 0
        output_folders = set()  # Store created 'Converted Files' folder paths (for info)

        # Disable button during conversion
        self.convert_button.setEnabled(False)
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
                converted_files_dir = os.path.join(dir_name, "Converted Files")
                if not os.path.exists(converted_files_dir):
                    try:
                        os.makedirs(converted_files_dir)
                    except OSError as e:
                        QMessageBox.critical(
                            self, "Folder Creation Error", f"Error creating folder '{converted_files_dir}': {e}")
                        error_count += 1
                        continue  # Continue to next file
                output_path = os.path.join(
                    converted_files_dir, f"{file_root}.{output_format_str}")
                output_folders.add(converted_files_dir)

            try:
                image = Image.open(file_path)
                save_options = {}
                if output_format_str == "jpeg":
                    # HEIC may have alpha channel; convert to RGB for JPEG
                    if image.mode in ('RGBA', 'P', 'LA'):
                        image = image.convert('RGB')
                    save_options['quality'] = 95  # Default JPEG quality
                elif output_format_str == "webp":
                    save_options['quality'] = 90  # WebP quality
                    # WebP supports alpha
                    if image.mode in ('P', 'LA') and 'transparency' in image.info:
                        image = image.convert('RGBA')
                    elif image.mode not in ('RGB', 'RGBA'):
                        image = image.convert('RGB')

                image.save(output_path, output_format_str.upper(),
                           **save_options)

                # If extension changed (which it always will)
                if replace_original and output_path != file_path:
                    os.remove(file_path)
                converted_count += 1

            except Exception as e:
                error_count += 1
                QMessageBox.critical(
                    self, "Conversion Error", f"Error converting '{base_name}': {e}")

        QApplication.restoreOverrideCursor()
        self.convert_button.setEnabled(True)

        summary_message = f"Out of {len(self.file_paths)} files:\nSuccess: {converted_count}\nFailed: {error_count}\n"
        if not replace_original and output_folders:
            summary_message += "\nConverted files have been saved to the following folder(s):\n" + \
                "\n".join(list(output_folders))

        QMessageBox.information(self, "Conversion Completed", summary_message)

        # Optionally clear or retain file list after conversion (here we retain it)
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
