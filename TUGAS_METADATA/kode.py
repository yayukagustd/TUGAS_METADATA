import PyPDF2
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io


def create_page_with_logo_and_blank(logo_path, page_size=letter):
    """Membuat PDF dengan logo yang disembunyikan oleh halaman kosong."""
    # Buat halaman dengan logo
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=page_size)
    
    # Tambahkan logo yang memenuhi seluruh halaman
    can.drawImage(logo_path, 0, 0, width=page_size[0], height=page_size[1])
    
    # Tambahkan lapisan putih untuk menutupi logo
    can.setFillColorRGB(1, 1, 1)  # Warna putih
    can.rect(0, 0, page_size[0], page_size[1], fill=1, stroke=0)  # Menutupi logo dengan lapisan putih
    
    can.showPage()
    can.save()

    packet.seek(0)  # Kembali ke awal data
    new_pdf = PyPDF2.PdfReader(packet)
    
    return new_pdf.pages[0]


def hide_old_metadata(input_pdf, new_pdf_writer):
    """Menyembunyikan metadata lama dari PDF."""
    old_metadata = input_pdf.metadata
    for key, value in old_metadata.items():
        encoded_value = base64.b64encode(value.encode()).decode()
        new_key = f"/O={key}/S"
        new_pdf_writer.add_metadata({new_key: encoded_value})

def edit_pdf_with_modifications(input_pdf, output_pdf, new_metadata, logo_path):
    """Mengedit PDF dengan halaman tersembunyi di awal, halaman kosong di akhir,
    dan metadata baru ditambahkan."""
    # Baca PDF asli
    with open(input_pdf, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_writer = PyPDF2.PdfWriter()

        # Tambahkan halaman dengan logo yang disembunyikan
        hidden_logo_page = create_page_with_logo_and_blank(logo_path)
        pdf_writer.add_page(hidden_logo_page)

        # Tambahkan semua halaman dari input PDF
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        # Tambahkan halaman kosong di akhir
        pdf_writer.add_page(create_page_with_logo_and_blank(logo_path))

        # Sembunyikan metadata lama
        hide_old_metadata(pdf_reader, pdf_writer)

        # Encode metadata baru dengan Base64
        encoded_metadata = {}
        for key, value in new_metadata.items():
            encoded_str = base64.b64encode(value.encode()).decode()
            encoded_metadata[key] = encoded_str

        # Tambahkan metadata baru
        pdf_writer.add_metadata(encoded_metadata)

        # Tulis ke file output
        with open(output_pdf, 'wb') as output_file:
            pdf_writer.write(output_file)



def reverse_caesar_cipher(text, shift):
    """Mengembalikan teks berdasarkan pergeseran tertentu (Caesar cipher)."""
    result = []
    for char in text:
        if char.isalpha():
            start = ord('A') if char.isupper() else ord('a')
            new_char = chr(start + (ord(char) - start - shift + 26) % 26)
            result.append(new_char)
        else:
            result.append(char)
    return ''.join(result)


def decode_metadata_base64(metadata):
    """Dekode metadata dari Base64 dan Caesar cipher."""
    decoded_metadata = {}
    for key, value in metadata.items():
        base64_decoded = base64.b64decode(value).decode()
        original_text = reverse_caesar_cipher(base64_decoded, 4)
        decoded_metadata[key] = original_text
    return decoded_metadata


def create_pdf_without_hidden_logo(input_pdf, output_pdf):
    """Membuat PDF tanpa halaman dengan logo yang disembunyikan dan halaman kosong di akhir."""
    with open(input_pdf, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_writer = PyPDF2.PdfWriter()

        # Tambahkan semua halaman kecuali yang pertama dan terakhir
        for page in pdf_reader.pages[1:-1]:
            pdf_writer.add_page(page)

        # Tulis ke file output
        with open(output_pdf, 'wb') as output_file:
            pdf_writer.write(output_file)

    # Dapatkan metadata dan dekode
    decoded_metadata = decode_metadata_base64(pdf_reader.metadata)

    print("Metadata terdekode:", decoded_metadata)


# Contoh penggunaan
input_pdf = 'JURNAL.pdf'
output_pdf = 'output.pdf'
logo_path = 'logo.png'  # Ganti dengan path ke file logo Anda
new_metadata = {'/Title': 'Sejarah Digital Forensik', '/Author': 'Tejo', '/Subject': 'New Subject'}

edit_pdf_with_modifications(input_pdf, output_pdf, new_metadata, logo_path)
