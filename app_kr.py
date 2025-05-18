import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QListWidget, QStackedWidget, QSizePolicy,
    QMessageBox, QFrame, QSplitter, QProgressBar, QGridLayout
)
from PyQt6.QtCore import Qt, QMimeData, QUrl, QSettings
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QImage, QPalette, QColor


try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    QMessageBox.critical(
        None, "라이브러리 오류", "pillow-heif 라이브러리를 찾을 수 없습니다. 설치해주세요.")
    sys.exit(1)

from PIL import Image


class HoverLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_normal_style()
        self.setAcceptDrops(True)

    def set_normal_style(self):
        self.setStyleSheet(
            "QLabel { border: 2px dashed #aaa; padding: 20px; background-color: #f0f0f0; }")
        self.setText(
            "HEIC/HEIF 파일이나 폴더를 여기로 드래그하세요.\n\n"
            "옵션을 확인한 후, 아래의 '변환 시작' 버튼을 클릭하세요.")

    def set_hover_style(self):
        self.setStyleSheet(
            "QLabel { border: 3px solid #0078d7; padding: 20px; background-color: #e0e0ff; }")
        self.setText("파일이나 폴더를 여기에 놓으세요!")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.set_hover_style()
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):  # QDragLeaveEvent
        self.set_normal_style()
        event.accept()

    def dropEvent(self, event: QDropEvent):
        self.set_normal_style()
        if self.parentWidget() and hasattr(self.parentWidget(), 'handle_dropped_files'):
            self.parentWidget().handle_dropped_files(event.mimeData())
        else:
            main_window = self.window()
            if isinstance(main_window, HEICConverterApp):
                main_window.process_dropped_urls(event.mimeData().urls())


class FileListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)
        self.setAlternatingRowColors(True)
        self.set_normal_style()

    def set_normal_style(self):
        self.setStyleSheet("QListWidget { border: 1px solid #ccc; }")

    def set_hover_style(self):
        self.setStyleSheet(
            "QListWidget { border: 2px solid #0078d7; background-color: #f5faff; }")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            self.set_hover_style()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragEnterEvent):  # QDragMoveEvent
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):  # QDragLeaveEvent
        self.set_normal_style()
        event.accept()

    def dropEvent(self, event: QDropEvent):
        self.set_normal_style()
        if event.mimeData().hasUrls():
            main_window = self.window()
            if isinstance(main_window, HEICConverterApp):
                main_window.process_dropped_urls(
                    event.mimeData().urls(), append=True)
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()


class HEICConverterApp(QWidget):
    MIN_WIDTH_FOR_PREVIEW = 750
    PREVIEW_PLACEHOLDER_COLOR = QColor(220, 220, 220)
    SETTINGS_REPLACE_ORIGINAL = "replaceOriginal"
    SETTINGS_MAINTAIN_METADATA = "maintainMetadata"

    def __init__(self):
        super().__init__()
        self.file_paths = []
        self.current_preview_path = None
        # Use your company/app name
        self.settings = QSettings("DevJaewonE", "HEICConverterApp")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('HEIC 변환기')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Top Section (Responsive Controls) ---
        self.top_section_widget = QWidget()  # Container for responsive controls
        self.top_section_layout = QGridLayout(self.top_section_widget)

        # Spacing between controls in the grid
        self.top_section_layout.setSpacing(10)

        self.format_label = QLabel("출력 형식:")
        self.format_dropdown = QComboBox()
        self.format_dropdown.addItems(["PNG", "JPEG", "WEBP"])
        self.format_dropdown.setCurrentText("PNG")
        self.format_dropdown.setToolTip(
            "변환될 이미지의 형식을 선택하세요.")

        self.replace_checkbox = QCheckBox("원본 파일 덮어쓰기")
        self.replace_checkbox.setToolTip(
            "선택하면 원본 파일이 대체됩니다.\n"
            "선택하지 않으면 변환된 파일이 'Converted Files' 폴더에 저장됩니다."
        )
        self.replace_checkbox.setChecked(self.settings.value(
            self.SETTINGS_REPLACE_ORIGINAL, True, type=bool))

        self.metadata_checkbox = QCheckBox("메타데이터 유지")
        self.metadata_checkbox.setToolTip(
            "선택하면 EXIF 및 색상 프로필 메타데이터를 보존하려고 시도합니다.")
        self.metadata_checkbox.setChecked(self.settings.value(
            self.SETTINGS_MAINTAIN_METADATA, True, type=bool))

        self.clear_button = QPushButton("목록 지우기")
        self.clear_button.setToolTip("현재 파일 목록을 지웁니다.")
        self.clear_button.setStyleSheet(
            "QPushButton { background-color: #ffcdd2; color: #b71c1c; border-radius: 6px; padding: 5px; }"
            "QPushButton:hover { background-color: #ef9a9a; }"
            "QPushButton:pressed { background-color: #e57373; }"
        )
        self.clear_button.clicked.connect(self.clear_file_list)

        self.update_top_controls_layout()  # Initial layout based on current width
        main_layout.addWidget(self.top_section_widget)

        # --- Body Section (File List / Preview or Drop Target) ---
        self.body_stack = QStackedWidget()
        main_layout.addWidget(self.body_stack, 1)

        self.no_files_view = HoverLabel(
            "HEIC/HEIF 파일이나 폴더를 여기로 드래그하세요.")
        self.body_stack.addWidget(self.no_files_view)

        self.files_selected_view = QWidget()
        files_selected_layout = QHBoxLayout(self.files_selected_view)
        files_selected_layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.file_list_widget = FileListWidget()
        self.file_list_widget.currentItemChanged.connect(self.update_preview)
        self.file_list_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.splitter.addWidget(self.file_list_widget)

        self.preview_label = QLabel("이미지 미리보기")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.preview_label.setScaledContents(False)
        self.preview_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_label.setMinimumWidth(200)
        self._set_preview_placeholder()
        self.splitter.addWidget(self.preview_label)

        # Initial splitter sizes
        self.splitter.setSizes([self.width() // 3, self.width() * 2 // 3])
        files_selected_layout.addWidget(self.splitter)
        self.body_stack.addWidget(self.files_selected_view)

        # --- Progress Bar and Label ---
        # Use a widget to better manage layout and visibility
        progress_layout_widget = QWidget()
        progress_layout = QHBoxLayout(progress_layout_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("0/0")
        progress_layout.addWidget(self.progress_label)
        main_layout.addWidget(progress_layout_widget)
        self.progress_bar_widget = progress_layout_widget  # Keep a reference to hide/show
        self.progress_bar_widget.setVisible(False)

        # --- Bottom Section (Convert Button) ---
        bottom_section_layout = QHBoxLayout()
        self.convert_button = QPushButton("변환 시작")
        self.convert_button.setFixedHeight(40)
        self.convert_button.setStyleSheet(
            "QPushButton { background-color: #0078d7; color: white; font-weight: bold; border-radius: 5px; } "
            "QPushButton:hover { background-color: #005a9e; } "
            "QPushButton:disabled { background-color: #d0d0d0; color: #808080; }"
        )
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setEnabled(False)

        bottom_section_layout.addWidget(self.convert_button)
        main_layout.addLayout(bottom_section_layout)

        self.setLayout(main_layout)
        self.setAcceptDrops(True)

    def update_top_controls_layout(self):
        # Clear existing items from layout without deleting widgets
        while self.top_section_layout.count():
            child = self.top_section_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)  # Detach widget from layout

        # Reset column stretches
        for i in range(self.top_section_layout.columnCount() + 2):
            self.top_section_layout.setColumnStretch(i, 0)

        if self.width() < self.MIN_WIDTH_FOR_PREVIEW:
            # Narrow layout: 2 rows
            self.top_section_layout.addWidget(self.format_label, 0, 0)
            self.top_section_layout.addWidget(self.format_dropdown, 0, 1)
            self.top_section_layout.addWidget(self.replace_checkbox, 0, 2)
            self.top_section_layout.setColumnStretch(
                3, 1)  # Stretch after items in row 0

            self.top_section_layout.addWidget(self.metadata_checkbox, 1, 0)
            self.top_section_layout.addWidget(self.clear_button, 1, 1)
        else:
            # Wide layout: 1 row
            self.top_section_layout.addWidget(self.format_label, 0, 0)
            self.top_section_layout.addWidget(self.format_dropdown, 0, 1)
            self.top_section_layout.addWidget(self.replace_checkbox, 0, 2)
            self.top_section_layout.addWidget(self.metadata_checkbox, 0, 3)
            self.top_section_layout.addWidget(self.clear_button, 0, 4)
            self.top_section_layout.setColumnStretch(
                5, 1)  # Stretch after last item

        self.top_section_layout.activate()

    def _set_preview_placeholder(self):
        self.preview_label.setText("선택된 파일이 없거나 미리보기를 사용할 수 없습니다.")
        palette = self.preview_label.palette()
        palette.setColor(QPalette.ColorRole.Window,
                         self.PREVIEW_PLACEHOLDER_COLOR)
        self.preview_label.setAutoFillBackground(True)
        self.preview_label.setPalette(palette)
        self.preview_label.setPixmap(QPixmap())

    def handle_dropped_files(self, mime_data: QMimeData):
        if mime_data.hasUrls():
            self.process_dropped_urls(mime_data.urls())

    def dragEnterEvent(self, event: QDragEnterEvent):
        if self.body_stack.currentWidget() != self.no_files_view:
            event.ignore()
            return
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.no_files_view.set_hover_style()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragEnterEvent):  # QDragLeaveEvent
        if self.body_stack.currentWidget() == self.no_files_view:
            self.no_files_view.set_normal_style()
        event.accept()

    def dropEvent(self, event: QDropEvent):
        if self.body_stack.currentWidget() != self.no_files_view:
            event.ignore()
            return
        self.no_files_view.set_normal_style()
        if event.mimeData().hasUrls():
            self.process_dropped_urls(event.mimeData().urls())
            event.acceptProposedAction()
        else:
            event.ignore()

    def process_dropped_urls(self, urls: list[QUrl], append=False):
        new_heic_files_found = False
        if not append:
            self.file_paths = []

        unsupported_files_basenames = []
        # For efficient duplicate checking
        current_file_paths_set = set(self.file_paths)

        for url in urls:
            if url.isLocalFile():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            full_path = os.path.join(root, file)
                            if file.lower().endswith(('.heic', '.heif')):
                                if full_path not in current_file_paths_set:
                                    self.file_paths.append(full_path)
                                    current_file_paths_set.add(full_path)
                                    new_heic_files_found = True
                            else:
                                # Ignore system files
                                if file.startswith(".DS_Store") or file.startswith("Thumbs.db"):
                                    continue
                                unsupported_files_basenames.append(
                                    os.path.basename(full_path))
                elif os.path.isfile(path):
                    if path.lower().endswith(('.heic', '.heif')):
                        if path not in current_file_paths_set:
                            self.file_paths.append(path)
                            current_file_paths_set.add(path)
                            new_heic_files_found = True
                    else:
                        # Ignore system files
                        file = os.path.basename(path)
                        if file.startswith(".DS_Store") or file.startswith("Thumbs.db"):
                            continue
                        unsupported_files_basenames.append(
                            os.path.basename(path))

        if unsupported_files_basenames:
            num_unsupported = len(unsupported_files_basenames)
            # If no HEIC files were found from this drop AND the list was initially empty (or became empty)
            if not new_heic_files_found and not self.file_paths:
                QMessageBox.warning(
                    self, "지원되는 HEIC/HEIF 파일 없음",
                    f"HEIC/HEIF 파일을 찾을 수 없습니다. {num_unsupported}개의 지원되지 않는 파일은 무시되었습니다."
                )
            # Some HEIC files were found/exist, or this drop added some HEIC files along with unsupported ones.
            else:
                message = f"총 {num_unsupported}개의 지원되지 않는 파일이 무시되었습니다:"
                display_limit = 5
                files_to_display = list(set(unsupported_files_basenames))[
                    :display_limit]  # Show unique basenames
                message += "\n - " + "\n - ".join(files_to_display)
                if len(set(unsupported_files_basenames)) > display_limit:  # Check against unique count
                    message += "\n - ..."
                QMessageBox.information(
                    self, "지원되지 않는 파일 무시됨", message)

        if self.file_paths:
            self.update_file_list_widget()
            self.body_stack.setCurrentWidget(self.files_selected_view)
            self.convert_button.setEnabled(True)
            if self.file_list_widget.count() > 0 and not append:  # Select first item only on new drop, not append
                self.file_list_widget.setCurrentRow(0)
            self.update_preview_visibility()
        elif not new_heic_files_found and not unsupported_files_basenames:  # Dropped empty folder or nothing useful
            if self.body_stack.currentWidget() == self.files_selected_view:  # If it was showing files, but now empty
                self.clear_file_list()  # Use clear to reset properly
        # If only unsupported files were dropped and list was already empty, msg shown above, state remains no_files_view

    def update_file_list_widget(self):
        self.file_list_widget.clear()
        for i, path in enumerate(self.file_paths):
            # item = QListWidgetItem(os.path.basename(path)) # PyQt6 style for creating item
            # item.setData(Qt.ItemDataRole.UserRole, path)
            # self.file_list_widget.addItem(item)
            self.file_list_widget.addItem(os.path.basename(path))
            self.file_list_widget.item(i).setData(
                Qt.ItemDataRole.UserRole, path)

    def clear_file_list(self):
        self.file_paths = []
        self.update_file_list_widget()  # Clears QListWidget items
        self.body_stack.setCurrentWidget(self.no_files_view)
        self.convert_button.setEnabled(False)
        self._set_preview_placeholder()
        self.current_preview_path = None
        self.progress_bar_widget.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("0/0")

    def update_preview(self, current_item, previous_item):
        if not current_item:
            self._set_preview_placeholder()
            self.current_preview_path = None
            return

        self.current_preview_path = current_item.data(Qt.ItemDataRole.UserRole)

        if self.current_preview_path and self.preview_label.isVisible():
            try:
                pil_image = Image.open(self.current_preview_path)
                if pil_image.mode == "RGBA":
                    data = pil_image.tobytes("raw", "RGBA")
                    q_image = QImage(data, pil_image.width, pil_image.height,
                                     pil_image.width * 4, QImage.Format.Format_RGBA8888)
                elif pil_image.mode == "RGB":
                    data = pil_image.tobytes("raw", "RGB")
                    q_image = QImage(data, pil_image.width, pil_image.height,
                                     pil_image.width * 3, QImage.Format.Format_RGB888)
                else:
                    pil_image = pil_image.convert("RGB")  # Default conversion
                    data = pil_image.tobytes("raw", "RGB")
                    q_image = QImage(data, pil_image.width, pil_image.height,
                                     pil_image.width * 3, QImage.Format.Format_RGB888)

                pixmap = QPixmap.fromImage(q_image)
                self.preview_label.setAutoFillBackground(False)
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
            except Exception as e:
                self._set_preview_placeholder()
                self.preview_label.setText(
                    f"미리보기 오류:\n{os.path.basename(self.current_preview_path)}\n{type(e).__name__}")
        elif not self.preview_label.isVisible():
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("미리보기 숨김.")
        else:
            self._set_preview_placeholder()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_top_controls_layout()  # Update top controls based on new width
        self.update_preview_visibility()
        if self.current_preview_path and self.preview_label.isVisible():
            current_list_item = self.file_list_widget.currentItem()
            if current_list_item:
                self.update_preview(current_list_item, None)

    def update_preview_visibility(self):
        if self.body_stack.currentWidget() == self.files_selected_view:
            should_show = self.width() >= self.MIN_WIDTH_FOR_PREVIEW
            if should_show != self.preview_label.isVisible():
                self.preview_label.setVisible(should_show)
                if should_show:
                    if self.file_list_widget.currentItem():
                        self.update_preview(
                            self.file_list_widget.currentItem(), None)
                else:
                    self.preview_label.setPixmap(QPixmap())
                    self.preview_label.setText("미리보기 숨김.")

    def start_conversion(self):
        if not self.file_paths:
            QMessageBox.information(
                self, "알림", "변환할 파일이 없습니다.")
            return

        output_format_str = self.format_dropdown.currentText().lower()
        replace_original = self.replace_checkbox.isChecked()
        maintain_metadata = self.metadata_checkbox.isChecked()

        converted_count = 0
        error_count = 0
        output_folders = set()

        total_files = len(self.file_paths)
        self.progress_bar.setMaximum(total_files)
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"0/{total_files}")
        # Ensure the initial 0/n state is rendered before heavy work starts
        QApplication.processEvents()
        self.progress_bar_widget.setVisible(True)

        self.convert_button.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        for i, file_path in enumerate(self.file_paths):
            base_name = os.path.basename(file_path)
            dir_name = os.path.dirname(file_path)
            file_root, _ = os.path.splitext(base_name)
            output_path = ""

            if replace_original:
                output_path = os.path.join(
                    dir_name, f"{file_root}.{output_format_str}")
            else:
                # 사용자가 원하면 이 폴더명도 바꿀 수 있습니다.
                converted_files_dir = os.path.join(dir_name, "Converted Files")
                if not os.path.exists(converted_files_dir):
                    try:
                        os.makedirs(converted_files_dir)
                    except OSError as e:
                        QMessageBox.critical(
                            self, "폴더 생성 오류", f"'{converted_files_dir}' 폴더 생성 중 오류 발생: {e}")
                        error_count += 1
                        self.progress_bar.setValue(i + 1)
                        self.progress_label.setText(f"{i + 1}/{total_files}")
                        QApplication.processEvents()
                        continue
                output_path = os.path.join(
                    converted_files_dir, f"{file_root}.{output_format_str}")
                output_folders.add(converted_files_dir)

            try:
                pil_image = Image.open(file_path)

                save_options = {}
                if maintain_metadata:
                    exif_data = pil_image.info.get('exif')
                    icc_profile = pil_image.info.get('icc_profile')
                    if exif_data:
                        save_options['exif'] = exif_data
                    if icc_profile:
                        save_options['icc_profile'] = icc_profile

                # Format-specific handling
                if output_format_str == "jpeg":
                    if pil_image.mode in ('RGBA', 'P', 'LA'):
                        # Create a new image with a white background if image has alpha
                        if pil_image.mode == 'RGBA' or (pil_image.mode == 'P' and 'transparency' in pil_image.info):
                            alpha = pil_image.split(
                            )[-1] if pil_image.mode == 'RGBA' or pil_image.mode == 'LA' else pil_image.convert("RGBA").split()[-1]
                            background = Image.new(
                                'RGB', pil_image.size, (255, 255, 255))
                            background.paste(pil_image, mask=alpha)
                            pil_image = background
                        else:  # For LA or P without explicit alpha, just convert
                            pil_image = pil_image.convert('RGB')
                    elif pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    save_options['quality'] = 95
                elif output_format_str == "webp":
                    save_options['quality'] = 90  # Good default for lossy WebP
                    # Preserve alpha for WebP if present, otherwise convert to RGB
                    if pil_image.mode not in ('RGB', 'RGBA'):
                        if 'A' in pil_image.mode or 'transparency' in pil_image.info:  # L"A", P with transparency
                            pil_image = pil_image.convert('RGBA')
                        else:
                            pil_image = pil_image.convert('RGB')
                elif output_format_str == "png":
                    # PNG supports transparency by default. If metadata includes icc_profile, it will be used.
                    # No specific quality option for PNG like JPEG/WebP in basic save.
                    # Forcing RGBA if image has alpha but is in P mode might be good for PNG.
                    if pil_image.mode == 'P' and 'transparency' in pil_image.info:
                        pil_image = pil_image.convert('RGBA')

                pil_image.save(
                    output_path, output_format_str.upper(), **save_options)

                if replace_original and output_path.lower() != file_path.lower():
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        print(
                            f"경고: 원본 파일 {file_path}을(를) 삭제할 수 없습니다: {e}")
                converted_count += 1

            except Exception as e:
                error_count += 1
                QMessageBox.critical(
                    self, "변환 오류", f"'{base_name}' 변환 중 오류 발생: {type(e).__name__}: {e}")

            # Update text first so label and bar advance together
            self.progress_label.setText(f"{i + 1}/{total_files}")
            self.progress_bar.setValue(i + 1)
            # Force a repaint so the user sees each step immediately
            QApplication.processEvents()

        QApplication.restoreOverrideCursor()
        self.convert_button.setEnabled(True)  # Re-enable after loop

        summary_message = f"변환 작업이 완료되었습니다.\n총 처리 파일 수: {total_files}\n성공: {converted_count}\n실패: {error_count}\n"
        if not replace_original and output_folders:
            summary_message += "\n변환된 파일은 다음 폴더에 저장되었습니다:\n" + "\n".join(  # 사용자가 원하면 이 폴더명도 바꿀 수 있습니다.
                sorted(list(output_folders)))

        QMessageBox.information(self, "변환 완료", summary_message)

        if replace_original and converted_count > 0:
            self.clear_file_list()
        else:
            if error_count > 0:
                self.progress_bar_widget.setVisible(True)
            else:
                self.progress_bar_widget.setVisible(False)

    def closeEvent(self, event):
        self.settings.setValue(
            self.SETTINGS_REPLACE_ORIGINAL, self.replace_checkbox.isChecked())
        self.settings.setValue(
            self.SETTINGS_MAINTAIN_METADATA, self.metadata_checkbox.isChecked())
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    converter_app = HEICConverterApp()
    converter_app.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
