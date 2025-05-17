# HEIC Converter

## 소개

HEIC Converter는 HEIC/HEIF 이미지 파일을 PNG, JPEG, 또는 WEBP 형식으로 변환하는 데스크톱 애플리케이션입니다. 사용자 친화적인 그래픽 인터페이스(GUI)를 제공하여 파일을 쉽게 드래그 앤 드롭하고 변환 설정을 선택할 수 있습니다.

## 주요 기능

- **HEIC/HEIF 파일 변환**: 고효율 이미지 파일 포맷인 HEIC 및 HEIF 파일을 널리 사용되는 형식으로 변환합니다.
- **다양한 출력 포맷 지원**: PNG, JPEG, WEBP 중 원하는 포맷으로 변환할 수 있습니다.
- **드래그 앤 드롭**: 변환할 파일을 프로그램 창으로 직접 끌어다 놓아 쉽게 추가할 수 있습니다.
- **파일 목록 표시**: 추가된 파일의 목록을 보여주어 변환 대상을 명확히 확인할 수 있습니다.
- **이미지 미리보기**: 선택한 HEIC 파일의 내용을 변환 전에 미리 볼 수 있습니다. 창 크기가 작을 경우 미리보기는 자동으로 숨겨집니다.
- **변환 옵션**:
  - **파일 대치**: 원본 HEIC 파일을 변환된 파일로 대치할 수 있습니다.
  - **새 폴더에 저장**: 원본 파일과 동일한 경로의 '변환된 파일' 폴더에 변환된 파일을 저장할 수 있습니다. (파일 대치 옵션 해제 시)
- **변환 상태 알림**: 변환 진행 상황 및 완료 후 성공/실패 요약을 제공합니다.
- **오류 처리**: 지원하지 않는 파일 형식이나 변환 중 발생하는 오류에 대한 알림을 표시합니다.

## 사용 방법

1.  애플리케이션을 실행합니다.
2.  변환하고자 하는 HEIC 또는 HEIF 파일을 프로그램 창의 "여기에 HEIC 파일을 드래그하세요." 영역으로 드래그 앤 드롭하거나, 파일이 이미 목록에 있는 경우 파일 목록 영역으로 드래그 앤 드롭하여 추가합니다.
3.  상단의 "변환 포맷" 드롭다운 메뉴에서 원하는 출력 포맷(PNG, JPEG, WEBP)을 선택합니다.
4.  "파일을 대치합니다" 체크박스를 사용하여 원본 파일을 대치할지, 아니면 '변환된 파일' 폴더에 저장할지를 결정합니다.
5.  파일 목록에서 파일을 선택하면 오른쪽에 이미지 미리보기가 표시됩니다 (창 너비가 충분할 경우).
6.  하단의 "변환 시작" 버튼을 클릭하여 변환을 시작합니다.
7.  변환이 완료되면 결과 알림창이 표시됩니다.

## 의존성

이 애플리케이션을 소스 코드에서 직접 실행하려면 다음 라이브러리가 필요합니다:

- PyQt6
- Pillow
- pillow-heif

<!-- end list -->

```bash
pip install PyQt6 Pillow pillow-heif
```

## 빌드 방법 (PyInstaller 사용)

애플리케이션을 독립 실행형 파일로 빌드할 수 있습니다.

### macOS용

```bash
pyinstaller \
  --onefile --windowed \
  --target-architecture arm64 \
  --name "HeicConverter" \
  --icon "assets/heic_converter.icns" \
  --collect-all pillow_heif \
  app.py
```

### Windows용

```bash
pyinstaller `
  --noconsole --onefile `
  --name "HeicConverter" `
  --icon "C:\path\to\assets\heic_converter.ico" `
  --collect-all pillow_heif `
  app.py
```

**참고**: `assets/heic_converter.icns` (macOS) 및 `C:\path\to\assets\heic_converter.ico` (Windows)는 실제 아이콘 파일 경로로 수정해야 합니다. 애플리케이션 코드 내에는 Base64로 인코딩된 기본 아이콘이 포함되어 있어, 별도 아이콘 파일 없이 빌드해도 작동합니다.
