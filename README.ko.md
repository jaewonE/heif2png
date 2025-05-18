# HEIC Converter

[ [English](README.md) | [한국어](README.ko.md) ]

**HEIC/HEIF 이미지를 PNG·JPEG·WEBP로 한 번에 변환하는 데스크톱 애플리케이션**

![데모](https://github.com/jaewonE/heif2png/blob/main/assets/demo.gif?raw=true)

---

## 목차

1. [주요 기능](#주요-기능)
2. [빠른 시작](#빠른-시작)
3. [설치](#설치)
4. [사용법](#사용법)
5. [독립 실행 파일 빌드](#독립-실행-파일-빌드)
6. [로드맵](#로드맵)
7. [기여 방법](#기여-방법)
8. [라이선스](#라이선스)

---

## 주요 기능

- **드래그 앤 드롭**  
  파일·폴더를 통째로 끌어다 놓으면 하위 폴더까지 자동 스캔합니다.
- **PNG·JPEG·WEBP 일괄 변환**  
  포맷별 최적화(알파 채널, 품질 설정)를 적용합니다.
- **메타데이터 보존**  
  EXIF·ICC 프로필을 선택적으로 유지할 수 있습니다.
- **원본 덮어쓰기 / 별도 출력 폴더**  
  원본을 그대로 둘지, _Converted Files_ 폴더에 따로 저장할지 선택합니다.
- **실시간 미리보기 & 진행률 표시**  
  선택한 이미지 썸네일과 변환 진행 상황을 즉시 확인합니다.
- **환경설정 자동 저장**  
  마지막 선택 옵션을 `QSettings`로 보존해 다음 실행 시 그대로 불러옵니다.
- **순수 파이썬 크로스플랫폼 GUI**  
  PyQt 6 기반으로 Windows·macOS·Linux 모두 지원합니다.

---

## 빠른 시작

```bash
# 1) 가상 환경 생성 및 의존성 설치
uv venv --python=3.11.10
uv sync

# 2) GUI 실행
uv run app.py
```

---

## 설치

### 필수 조건

| 소프트웨어         | 최소 버전        |
| ------------------ | ---------------- |
| **Python**         | 3.11 권장        |
| **pip**            | 최신 권장        |
| **libheif**(Linux) | 선택 – 성능 향상 |

### 의존성

```
PyQt6
pillow-heif    # Pillow용 HEIC/HEIF 디코더
pyinstaller    # 독립 실행 파일 빌드용
```

`pyproject.toml`로 한 번에 설치하거나, 위 패키지를 수동 설치하세요.

---

## 사용법

1. **애플리케이션 실행** (`python app.py` 또는 빌드된 실행 파일).
2. 변환할 **.heic / .heif** 파일(또는 폴더)을 드래그해 투하 영역에 놓습니다.
3. 아래 옵션을 설정합니다.

   - **출력 형식**: PNG / JPEG / WEBP
   - **원본 덮어쓰기**: 체크 해제 시 _Converted Files_ 폴더에 저장
   - **메타데이터 유지**: EXIF·ICC 정보 보존 여부

4. **Start Conversion** 버튼 클릭.
5. 진행 바 완료 후 성공·실패·결과 경로가 요약 다이얼로그로 표시됩니다.

---

## 독립 실행 파일 빌드

**PyInstaller**로 바로 패키징할 수 있습니다.

<details>
<summary><strong>Windows (x64)</strong></summary>

```cmd
pyinstaller ^
  --noconsole --onefile ^
  --name "HeicConverter" ^
  --icon "assets\heic_converter.ico" ^
  --collect-all pillow_heif ^
  app.py
```

</details>

<details>
<summary><strong>macOS (Apple Silicon) 예시</strong></summary>

```bash
pyinstaller \
  --onefile --windowed \
  --target-architecture arm64 \
  --name "HeicConverter" \
  --icon "assets/heic_converter.icns" \
  --collect-all pillow_heif \
  app.py
```

</details>

생성된 실행 파일은 Python 설치가 없는 시스템에서도 즉시 실행됩니다.

---

## 로드맵

- 헤드리스 배치 처리를 위한 **CLI 모드**
- 추가 출력 형식 **TIFF·AVIF** 지원
- **다크 모드** 토글
- 설치 프로그램 배포 (\*.msi, \*.dmg, \*.deb)

아이디어가 있다면 [이슈](../../issues)를 열거나 PR을 보내주세요!

---

## 기여 방법

1. 저장소를 포크하고 브랜치 생성: `git checkout -b feature/my-awesome-idea`
2. 명확한 커밋 메시지로 변경 사항을 기록합니다.
3. 원격 브랜치로 푸시하고 Pull Request를 엽니다.

코드는 **PEP 8**을 준수하고 가능하면 테스트를 포함해주세요.

---

## 라이선스

본 프로젝트는 **GNU General Public License v3.0** 하에 배포됩니다.
자세한 내용은 [`LICENSE`](LICENSE) 파일을 참조하세요.

---

빠르고 간편한 HEIC 변환기가 마음에 드셨다면 ⭐️ 한 번 눌러 주세요!
