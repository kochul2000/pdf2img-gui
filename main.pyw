import os
import platform
import subprocess
import fitz  # PyMuPDF 라이브러리
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image  # Pillow (JPG 저장 시 사용)
from tkinterdnd2 import DND_FILES, TkinterDnD


VERSION = "1.0.0"  # 버전 정보


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

def set_pdf_path(filepath):
    """
    선택한 PDF 파일 경로를 PDF 입력창에 설정하고,
    해당 파일의 디렉토리 내에 파일명(확장자 제외)과 동일한 기본 출력 폴더를 지정합니다.
    PDF가 선택되면 출력 디렉토리 관련 위젯을 활성화합니다.
    """
    pdf_entry.delete(0, tk.END)
    pdf_entry.insert(0, filepath)

    directory = os.path.dirname(filepath)
    filename = os.path.splitext(os.path.basename(filepath))[0]
    default_output_folder = os.path.join(directory, filename)

    output_entry.config(state="normal")
    output_button.config(state="normal")
    output_entry.delete(0, tk.END)
    output_entry.insert(0, default_output_folder)

def drop_pdf(event):
    """
    드래그 앤 드롭된 파일 경로(event.data)를 파싱하여 PDF 입력창에 넣습니다.
    """
    dropped_file = event.data.strip('{}')
    if os.path.isfile(dropped_file) and dropped_file.lower().endswith(".pdf"):
        set_pdf_path(dropped_file)
    else:
        messagebox.showerror("오류", "PDF 파일만 드래그하여 놓으세요.")

def select_pdf():
    """
    PDF 파일 선택 대화상자를 띄워 파일을 선택합니다.
    """
    filepath = filedialog.askopenfilename(filetypes=[("PDF 파일", "*.pdf")])
    if filepath:
        set_pdf_path(filepath)

def select_output_directory():
    """
    출력 디렉토리 선택 대화상자를 띄워 폴더를 선택합니다.
    """
    out_dir = filedialog.askdirectory()
    if out_dir:
        output_entry.config(state="normal")
        output_entry.delete(0, tk.END)
        output_entry.insert(0, out_dir)

def update_quality_widgets(*args):
    """
    export_format_var 값이 변경될 때마다 품질 슬라이더와 라벨의 활성/비활성 상태를 업데이트합니다.
    JPG 선택 시 활성화(슬라이더: normal, 라벨: 검정색), PNG 선택 시 비활성화(슬라이더: disabled, 라벨: 회색)
    """
    if export_format_var.get() == "jpg":
        quality_scale.config(state="normal")
        quality_label.config(fg="black")
    else:
        quality_scale.config(state="disabled")
        quality_label.config(fg="gray")

def convert_pdf_to_images():
    """
    선택된 PDF의 각 페이지를 지정한 형식(png 또는 jpg)으로 고해상도로 변환하여,
    선택한 출력 디렉토리에 {원본파일명}_{페이지번호}.{확장자} 형식으로 저장합니다.
    JPG 선택 시 Pillow를 이용해 품질(quality) 옵션을 적용합니다.
    변환 후 출력 폴더 열기 여부를 사용자에게 묻습니다.
    """
    pdf_path = pdf_entry.get()
    output_dir = output_entry.get()
    export_format = export_format_var.get()  # "png" 또는 "jpg"
    quality = quality_scale.get()

    if not pdf_path:
        messagebox.showerror("오류", "PDF 파일을 선택해주세요.")
        return
    if not output_dir:
        messagebox.showerror("오류", "출력 디렉토리를 선택해주세요.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        doc = fitz.open(pdf_path)
        total_pages = doc.page_count
        original_filename = os.path.splitext(os.path.basename(pdf_path))[0]

        zoom_matrix = fitz.Matrix(2, 2)  # 2배 확대
        for page_number in range(total_pages):
            page = doc.load_page(page_number)
            pix = page.get_pixmap(matrix=zoom_matrix)
            img_filename = os.path.join(
                output_dir, f"{original_filename}_{page_number+1}.{export_format}"
            )
            if export_format.lower() == "jpg":
                if pix.alpha:  # 투명 채널 처리
                    img = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                else:
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                img.save(img_filename, quality=quality)
            else:
                pix.save(img_filename)

        if messagebox.askyesno("성공", f"{total_pages} 페이지가 변환되었습니다.\n출력 폴더를 열겠습니까?"):
            open_folder(output_dir)

    except Exception as e:
        messagebox.showerror("오류", str(e))

###############################################################################
#                               GUI 구성 시작                                 #
###############################################################################
root = TkinterDnD.Tk()
root.title(f"PDF -> Image 변환기 (PyMuPDF) - v{VERSION}")

# 전체 창 너비 확장을 위한 설정
root.columnconfigure(0, weight=1)

frame = tk.Frame(root, padx=10, pady=10)
frame.grid(sticky="nsew")
frame.columnconfigure(0, weight=0)
frame.columnconfigure(1, weight=1)
frame.columnconfigure(2, weight=0)

###############################################################################
# 드래그 드랍 존 (최상단에 배치)
###############################################################################
drop_zone = tk.Label(
    frame,
    text="여기에 PDF 파일을 드래그하세요.",
    relief="groove",
    bg="#f0f0f0",
    height=4
)
drop_zone.grid(row=0, column=0, columnspan=3, pady=(0,10), sticky="ew")
drop_zone.drop_target_register(DND_FILES)
drop_zone.dnd_bind("<<Drop>>", drop_pdf)

###############################################################################
# PDF 파일 선택
###############################################################################
pdf_label = tk.Label(frame, text="PDF 파일:")
pdf_label.grid(row=1, column=0, sticky="w")

pdf_entry = tk.Entry(frame, width=50)
pdf_entry.grid(row=1, column=1, padx=5, sticky="ew")

pdf_button = tk.Button(frame, text="찾아보기", command=select_pdf)
pdf_button.grid(row=1, column=2)

###############################################################################
# 출력 디렉토리 선택 (초기엔 비활성화)
###############################################################################
output_label = tk.Label(frame, text="출력 디렉토리:")
output_label.grid(row=2, column=0, sticky="w")

output_entry = tk.Entry(frame, width=50, state="disabled")
output_entry.grid(row=2, column=1, padx=5, sticky="ew")

output_button = tk.Button(frame, text="찾아보기", command=select_output_directory, state="disabled")
output_button.grid(row=2, column=2)

###############################################################################
# 출력 형식 선택
###############################################################################
format_label = tk.Label(frame, text="출력 형식:")
format_label.grid(row=3, column=0, sticky="w")

export_format_var = tk.StringVar(value="png")
format_frame = tk.Frame(frame)
format_frame.grid(row=3, column=1, columnspan=2, sticky="w")

png_radio = tk.Radiobutton(format_frame, text="PNG", variable=export_format_var, value="png")
png_radio.pack(side=tk.LEFT, padx=5)

jpg_radio = tk.Radiobutton(format_frame, text="JPG", variable=export_format_var, value="jpg")
jpg_radio.pack(side=tk.LEFT, padx=5)

###############################################################################
# 품질 슬라이더 (PNG 선택 시 비활성화 및 라벨 회색 처리)
###############################################################################
quality_label = tk.Label(frame, text="JPG 품질 (1-100):")
quality_label.grid(row=4, column=0, sticky="w")

quality_scale = tk.Scale(frame, from_=1, to=100, orient=tk.HORIZONTAL)
quality_scale.set(95)
quality_scale.grid(row=4, column=1, columnspan=2, sticky="w", padx=5)

export_format_var.trace("w", update_quality_widgets)
update_quality_widgets()  # 초기 상태 반영

###############################################################################
# 변환 시작 버튼
###############################################################################
convert_button = tk.Button(frame, text="변환 시작", command=convert_pdf_to_images)
convert_button.grid(row=5, column=1, pady=10)

# 전체 창 크기 조정 허용
root.rowconfigure(0, weight=1)
root.mainloop()
