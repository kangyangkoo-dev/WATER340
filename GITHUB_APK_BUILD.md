# GitHub에서 WATER340 APK 자동 만들기

이 프로젝트는 `.github/workflows/build-apk.yml` 파일이 포함되어 있어 GitHub Actions에서 APK를 자동으로 빌드합니다.

## 처음 한 번만 하기

1. GitHub에 로그인합니다.
2. 우측 상단 `+` → `New repository`를 선택합니다.
3. 저장소 이름을 예: `WATER340`으로 입력합니다.
4. Public/Private 중 원하는 것을 선택하고 저장소를 만듭니다.
5. 이 압축파일의 `WATER340_Kivy` 폴더 안 **내용 전체**를 저장소 최상위에 업로드합니다.
   - `main.py`
   - `water340.kv`
   - `buildozer.spec`
   - `.github` 폴더
   - `assets` 폴더
   - 기타 파일
6. `Commit changes`를 누릅니다.

## APK 만들기

main/master 브랜치에 파일을 올리거나 수정하면 자동 빌드가 시작됩니다.
수동으로 만들고 싶으면:

1. 저장소 상단 `Actions` 클릭
2. 왼쪽 `Build WATER340 APK` 클릭
3. `Run workflow` 클릭
4. 실행이 성공(초록색 체크)한 항목을 엽니다.
5. 화면 아래 `Artifacts`에서 `WATER340-APK`를 클릭합니다.
6. ZIP을 내려받아 압축을 풀면 `.apk` 파일이 있습니다.

## 소스 수정 후 다시 APK 만들기

`main.py` 또는 `water340.kv` 등을 수정한 뒤 GitHub에 Commit하면 다시 자동 빌드됩니다.

## 한글 폰트 참고

현재 `main.py`는 Windows에서는 맑은 고딕을 찾고, Android에서는 Android 시스템의 Noto 계열 한글 폰트를 찾도록 되어 있습니다.
특정 Android 기기에서 한글이 깨지면 프로젝트에 사용 권한이 있는 한글 TTF/OTF 폰트를 직접 추가하고 `main.py`의 폰트 경로를 그 파일로 지정하는 방법이 가장 확실합니다.

## 오류가 날 경우

GitHub `Actions` → 실패한 실행 → `Build debug APK` 단계를 열어 빨간색 오류 부분을 복사해 ChatGPT에 보내면 됩니다.
