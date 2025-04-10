import fitz  # PyMuPDF 라이브러리
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import platform
import subprocess
from PIL import Image  # Pillow 라이브러리 (jpg 저장 시 사용)


# 버전 정보
VERSION = "1.0.0"


def open_folder(path):
    """
    주어진 경로의 폴더를 OS에 맞춰 엽니다.
    """
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("오류", f"폴더 열기에 실패했습니다: {e}")


def select_pdf():
    """
    PDF 파일 선택 대화상자를 띄워 사용자가 파일을 선택할 수 있도록 합니다.
    선택한 파일의 디렉토리 내에, 파일명과 동일한 폴더명을 기본 출력 디렉토리로 설정하고
    출력 디렉토리 입력창을 활성화합니다.
    """
    filepath = filedialog.askopenfilename(filetypes=[("PDF 파일", "*.pdf")])
    if filepath:
        pdf_entry.delete(0, tk.END)
        pdf_entry.insert(0, filepath)
        # 선택한 파일의 폴더와 파일명(확장자 제외)을 기본 출력 폴더로 지정
        directory = os.path.dirname(filepath)
        filename = os.path.splitext(os.path.basename(filepath))[0]
        default_output_folder = os.path.join(directory, filename)
        output_entry.config(state="normal")
        output_entry.delete(0, tk.END)
        output_entry.insert(0, default_output_folder)


def select_output_directory():
    """
    출력 디렉토리 선택 대화상자를 띄워 저장할 폴더를 선택합니다.
    """
    out_dir = filedialog.askdirectory()
    if out_dir:
        output_entry.config(state="normal")
        output_entry.delete(0, tk.END)
        output_entry.insert(0, out_dir)


def convert_pdf_to_images():
    """
    선택된 PDF 파일의 각 페이지를 지정된 형식(png 또는 jpg)으로 고해상도로 변환하여,
    선택된 출력 디렉토리에 `{원본파일명}_{페이지번호}.{확장자}` 형식으로 저장합니다.
    jpg 형식 선택 시, Pillow를 이용해 설정한 품질(quality)로 저장합니다.
    변환 후, 출력 폴더 열기 여부를 사용자에게 묻습니다.
    """
    pdf_path = pdf_entry.get()
    output_dir = output_entry.get()
    export_format = export_format_var.get()  # "png" 또는 "jpg"
    quality = quality_scale.get()  # 슬라이더에서 선택한 품질 값

    if not pdf_path:
        messagebox.showerror("오류", "PDF 파일을 선택해주세요.")
        return
    if not output_dir:
        messagebox.showerror("오류", "출력 디렉토리를 선택해주세요.")
        return

    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        doc = fitz.open(pdf_path)
        total_pages = doc.page_count
        original_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        # 해상도 향상을 위해 2배 확대 행렬 사용
        zoom_matrix = fitz.Matrix(2, 2)
        for page_number in range(total_pages):
            page = doc.load_page(page_number)
            pix = page.get_pixmap(matrix=zoom_matrix)

            # 파일명: {원본파일명}_{페이지번호}.{export_format}
            img_filename = os.path.join(output_dir, f"{original_filename}_{page_number + 1}.{export_format}")

            if export_format.lower() == "jpg":
                # pixmap을 Pillow Image로 변환하여 quality 옵션과 함께 저장
                if pix.alpha:  # 투명 채널이 있는 경우, 흰색 배경으로 변환
                    img = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                else:
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                img.save(img_filename, quality=quality)
            else:
                pix.save(img_filename)
        # 변환 성공 후 출력 폴더 열기 여부 확인
        if messagebox.askyesno("성공", f"{total_pages} 페이지가 성공적으로 변환되었습니다.\n출력 폴더를 열겠습니까?"):
            open_folder(output_dir)
    except Exception as e:
        messagebox.showerror("오류", str(e))


# Tkinter GUI 기본 창 설정 (타이틀에 VERSION 추가)
root = tk.Tk()
root.title(f"PDF -> Image 변환기 (PyMuPDF) - VERSION={VERSION}")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# PDF 파일 선택 위젯
pdf_label = tk.Label(frame, text="PDF 파일:")
pdf_label.grid(row=0, column=0, sticky="w")
pdf_entry = tk.Entry(frame, width=50)
pdf_entry.grid(row=0, column=1, padx=5)
pdf_button = tk.Button(frame, text="찾아보기", command=select_pdf)
pdf_button.grid(row=0, column=2)

# 출력 디렉토리 선택 위젯 (초기에는 비활성화)
output_label = tk.Label(frame, text="출력 디렉토리:")
output_label.grid(row=1, column=0, sticky="w")
output_entry = tk.Entry(frame, width=50, state="disabled")
output_entry.grid(row=1, column=1, padx=5)
output_button = tk.Button(frame, text="찾아보기", command=select_output_directory)
output_button.grid(row=1, column=2)

# 출력 형식 선택 위젯
format_label = tk.Label(frame, text="출력 형식:")
format_label.grid(row=2, column=0, sticky="w")
export_format_var = tk.StringVar(value="png")
format_frame = tk.Frame(frame)
format_frame.grid(row=2, column=1, columnspan=2, sticky="w")
png_radio = tk.Radiobutton(format_frame, text="PNG", variable=export_format_var, value="png")
png_radio.pack(side=tk.LEFT, padx=5)
jpg_radio = tk.Radiobutton(format_frame, text="JPG", variable=export_format_var, value="jpg")
jpg_radio.pack(side=tk.LEFT, padx=5)

# JPG 품질 선택 컨트롤러 (PNG일 경우 사용되지 않음)
quality_label = tk.Label(frame, text="JPG 품질 (1-100):")
quality_label.grid(row=3, column=0, sticky="w")
quality_scale = tk.Scale(frame, from_=1, to=100, orient=tk.HORIZONTAL)
quality_scale.set(95)
quality_scale.grid(row=3, column=1, columnspan=2, sticky="w", padx=5)

# 변환 시작 버튼
convert_button = tk.Button(frame, text="변환 시작", command=convert_pdf_to_images)
convert_button.grid(row=4, column=1, pady=10)

root.mainloop()
