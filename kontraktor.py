import streamlit as st
from openai import OpenAI
import PyPDF2
from io import BytesIO

# Fungsi untuk mengekstrak teks dari file PDF
def extract_text_from_pdf(pdf_file):
    """
    Mengekstrak teks dari objek file PDF yang diunggah.

    Args:
        pdf_file: Objek file yang diunggah dari st.file_uploader.

    Returns:
        Teks yang diekstrak sebagai string.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file PDF: {e}")
        return None

# Fungsi utama aplikasi Streamlit
def main():
    """
    Fungsi utama untuk menjalankan aplikasi Analisis Dokumen Kontrak.
    """
    st.set_page_config(page_title="Analisis Dokumen Kontrak", layout="wide")
    st.title("Analisis Dokumen Kontrak dengan OpenAI")

    # Sidebar untuk input API Key OpenAI
    st.sidebar.header("Pengaturan")
    api_key = st.sidebar.text_input("Masukkan API Key OpenAI Anda", type="password")

    # Tampilan utama
    st.write("Unggah dokumen kontrak dalam format PDF untuk dianalisis.")
    uploaded_file = st.file_uploader("Pilih file PDF", type="pdf")

    if uploaded_file is not None:
        if not api_key:
            st.warning("Silakan masukkan API Key OpenAI Anda di sidebar untuk melanjutkan.")
        else:
            try:
                client = OpenAI(api_key=api_key)

                # Ekstrak teks dari PDF
                with st.spinner("Mengekstrak teks dari dokumen..."):
                    contract_text = extract_text_from_pdf(uploaded_file)

                if contract_text:
                    st.success("Ekstraksi teks berhasil!")
                    st.text_area("Teks Kontrak", contract_text, height=300)

                    # Opsi Analisis
                    analysis_type = st.selectbox(
                        "Pilih jenis analisis yang ingin Anda lakukan:",
                        [
                            "Ringkasan Umum",
                            "Identifikasi Klausul Penting",
                            "Temukan Potensi Risiko",
                            "Identifikasi Pihak yang Terlibat",
                            "Tanyakan Pertanyaan Spesifik"
                        ]
                    )

                    prompt_template = ""
                    if analysis_type == "Ringkasan Umum":
                        prompt_template = "Berikan ringkasan umum dari kontrak berikut ini:\n\n"
                    elif analysis_type == "Identifikasi Klausul Penting":
                        prompt_template = "Identifikasi dan jelaskan klausul-klausul penting (seperti durasi kontrak, syarat pembayaran, kewajiban utama, dan kondisi pengakhiran) dalam kontrak berikut:\n\n"
                    elif analysis_type == "Temukan Potensi Risiko":
                        prompt_template = "Analisis kontrak berikut dan identifikasi potensi risiko atau area yang mungkin merugikan bagi salah satu pihak:\n\n"
                    elif analysis_type == "Identifikasi Pihak yang Terlibat":
                        prompt_template = "Sebutkan semua pihak yang terlibat dalam kontrak berikut beserta peran mereka:\n\n"
                    
                    user_question = ""
                    if analysis_type == "Tanyakan Pertanyaan Spesifik":
                        user_question = st.text_input("Masukkan pertanyaan Anda mengenai kontrak:")

                    if st.button("Mulai Analisis"):
                        with st.spinner("Menganalisis dokumen... Ini mungkin memakan waktu beberapa saat."):
                            try:
                                full_prompt = ""
                                if analysis_type == "Tanyakan Pertanyaan Spesifik":
                                    if user_question:
                                        full_prompt = f"Berdasarkan konteks dari kontrak berikut:\n\n{contract_text}\n\nJawab pertanyaan ini: {user_question}"
                                    else:
                                        st.warning("Silakan masukkan pertanyaan Anda.")
                                        return
                                else:
                                    full_prompt = prompt_template + contract_text

                                response = client.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "Anda adalah asisten ahli dalam menganalisis dokumen hukum dan kontrak."},
                                        {"role": "user", "content": full_prompt}
                                    ],
                                    temperature=0.5,
                                )
                                
                                analysis_result = response.choices[0].message.content
                                st.subheader("Hasil Analisis")
                                st.write(analysis_result)

                            except Exception as e:
                                st.error(f"Terjadi kesalahan saat berkomunikasi dengan API OpenAI: {e}")

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
