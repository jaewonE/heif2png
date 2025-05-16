## For MacOS

```
pyinstaller \
  --onefile --windowed \
  --target-architecture arm64 \
  --name "HeicConverter" \
  --icon "assets/heic_converter.icns" \
  --collect-all pillow_heif \
  app.py
```

## For Windows

```
pyinstaller `
  --noconsole --onefile `
  --name "HeicConverter" `
  --icon "C:\path\to\assets\heic_converter.ico" `
  --collect-all pillow_heif `
  app.py
```
