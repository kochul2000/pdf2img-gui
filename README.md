# pdf2img-gui
## 소개
* pdf2img-gui는 PDF 파일을 이미지로 변환하는 윈도우용 GUI 프로그램입니다.
* 이 것은 토이 프로젝트이며, 대부분의 코드는 GPT 를 사용하여 작성 되었습니다.
* PDF -> [PNG, JPG] 변환을 지원합니다.

## 사용법
1. `pip install -r requirements.txt`로 필요한 라이브러리를 설치합니다.
2. `build.bat`를 실행하여 exe 파일을 생성합니다.
3. `dist/pdf2img-gui.exe`를 실행합니다.

## 사용 라이브러리
|             라이브러리             | GitHub                                                     |
|:-----------------------------:|:-----------------------------------------------------------|
|         **altgraph**          | [https://github.com/ronaldoussoren/altgraph](https://github.com/ronaldoussoren/altgraph) |
|         **packaging**         | [https://github.com/pypa/packaging](https://github.com/pypa/packaging)                     |
|          **pefile**           | [https://github.com/erocarrera/pefile](https://github.com/erocarrera/pefile)               |
|          **pillow**           | [https://github.com/python-pillow/Pillow](https://github.com/python-pillow/Pillow)         |
|        **pyinstaller**        | [https://github.com/pyinstaller/pyinstaller](https://github.com/pyinstaller/pyinstaller)   |
| **pyinstaller-hooks-contrib** | [https://github.com/pyinstaller/pyinstaller-hooks-contrib](https://github.com/pyinstaller/pyinstaller-hooks-contrib) |
|          **PyMuPDF**          | [https://github.com/pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF)                   |
|      **pywin32-ctypes**       | [https://github.com/enthought/pywin32-ctypes](https://github.com/enthought/pywin32-ctypes) |
|        **setuptools**         | [https://github.com/pypa/setuptools](https://github.com/pypa/setuptools)                   |
|        **tkinterdnd2**        | [https://github.com/cranmer/tkinterdnd2](https://github.com/cranmer/tkinterdnd2)           |


## 라이센스
* MIT License
* 단, 각 사용 라이브러리의 라이센스 조항이 우선됩니다.