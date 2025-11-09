import streamlit as st
from google import genai
from google.genai.errors import APIError

# --- Konfigurasi Gemini API Key ---
# ⚠️ PENTING: Ganti string ini dengan Kunci API Gemini Anda yang sebenarnya.
# Hardcoding Kunci API tidak disarankan untuk aplikasi produksi/publik.
GEMINI_API_KEY = "AIzaSyCV80AVf2cNSEYyIGwGIigPzS2dDeY5v0o" 

# Inisialisasi Klien Gemini
client = None
MODEL_NAME = "gemini-2.5-pro" # Direkomendasikan untuk tugas kompleks

if GEMINI_API_KEY == "ISI_GEMINI_API_KEY_ANDA" or not GEMINI_API_KEY:
    st.error("⚠️ Harap ganti 'ISI_GEMINI_API_KEY_ANDA' di dalam file 'app.py' dengan Kunci API Gemini Anda.")
else:
    try:
        # Pengecekan sederhana apakah kunci API sudah diisi
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Gagal menginisialisasi Gemini Client: {e}")
        client = None

# Daftar 8 Profil Lulusan (Dapat disesuaikan)
PROFIL_LULUSAN = [
    "Komunikatif (Communicative)",
    "Kreatif dan Inovatif (Creative & Innovative)",
    "Berpikir Kritis (Critical Thinking)",
    "Kolaboratif (Collaborative)",
    "Pecinta Lingkungan (Environmental Awareness)",
    "Mandiri dan Bertanggung Jawab (Independent & Responsible)",
    "Literasi Digital (Digital Literacy)",
    "Berkarakter dan Berbudaya (Character & Culture)"
]

# --- Fungsi untuk Memanggil Gemini API ---
def generate_modul_ajar(user_data, phase_data):
    """
    Membuat prompt dan memanggil Gemini API untuk menghasilkan konten Modul Ajar.
    """
    if not client:
        return "Gagal menghasilkan modul ajar karena masalah konfigurasi API Key."

    # Menggabungkan semua data input dari user
    data_str = "\n".join([f"- {k}: {v}" for k, v in user_data.items()])
    
    # Prompt Utama untuk Gemini
    system_prompt = f"""
    Anda adalah asisten yang bertugas membuat Modul Ajar otomatis dengan struktur ketat dalam format Markdown.

    **Data Input User:**
    {data_str}
    
    **Detail Fase dan Model Pembelajaran:**
    {phase_data}
    
    **CATATAN PENTING: Untuk bagian C. Langkah-langkah pembelajaran, saat mengembangkan Tujuan Pembelajaran Harian (TPH), harap integrasikan profil kelulusan yang dipilih oleh pengguna ({user_data.get('8 Profil Lulusan', 'Tidak Ditentukan')}) dan dimensi Profil Pelajar Pancasila (keimanan, kemandirian, gotong royong, kebhinekaan global) yang relevan, serta pastikan Degree diukur dalam penilaian.**

    **Struktur Output Wajib:**
    
    ## B. HASIL PEMETAAN ASESMEN AWAL PESERTA DIDIK
    * Jenis Asesmen Awal
    * Instrumen
    * Hasil Pemetaan (Simulasi 3 kelompok: Mahir, Cakap, Perlu Bantuan)
    
    ---
    
    ## C. LANGKAH-LANGKAH PEMBELAJARAN
    
    ### Tujuan Pembelajaran (TP Utama)
    * Buat 3-5 TP komprehensif.
    
    ### Tujuan Pembelajaran Harian (TPH)
    * Kembangkan TPH (3 ranah) dengan kriteria: **ABCD** (Degree harus terukur dalam penilaian), memuat Profil Lulusan yang dipilih, dan dimensi Profil Pelajar Pancasila yang relevan. TPH harus disusun **HOTS (C4, C5, C6)**, adaptif, dan mengintegrasikan **IT/Media Konkret**.
    
    ### Pemahaman Bermakna
    * 3-5 poin penting.
    
    ### Pertanyaan Pemantik
    * 3-5 pertanyaan yang menarik.
    
    ---
    
    ## D. URUTAN KEGIATAN PEMBELAJARAN
    * Sajikan dalam **tabel Markdown** (4 kolom: Tahap, Kegiatan [termasuk sintaks Model Pembelajaran], Muatan Inovatif, Alokasi Waktu).
    
    ---
    
    ## E. GLOSARIUM
    * Minimal 5 istilah dan definisi.
    
    ---
    
    ## F. DAFTAR PUSTAKA
    * Minimal 3 sumber referensi yang relevan.
    
    ---
    
    ## LAMPIRAN-LAMPIRAN
    
    ### Lampiran 1: LKPD
    * Kerangka minimal 3 tugas.
    
    ### Lampiran 2: Asesmen Penilaian
    * Kerangka Instrumen dan Rubrik untuk Sikap, Pengetahuan, dan Keterampilan, mencerminkan derajat ketercapaian dari TPH.
    
    ### Lampiran 3: Remedial dan Pengayaan
    * Bentuk kegiatan.
    
    ### Lampiran 4: Bahan Bacaan
    * Minimal 3 poin utama bahan bacaan disertai sumber.
    
    Sajikan semua hasil di atas dalam satu output teks Markdown yang rapi.
    """

    # Panggil API
    try:
        with st.spinner(f"🤖 AI ({MODEL_NAME}) sedang menyusun Modul Ajar Anda..."):
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[system_prompt],
                config=genai.types.GenerateContentConfig(
                    temperature=0.7 
                )
            )
        return response.text
    except APIError as e:
        return f"Terjadi kesalahan saat memanggil Gemini API: {e}. Pastikan Kunci API Anda valid."
    except Exception as e:
        return f"Terjadi kesalahan tak terduga: {e}"

# --- Interface Streamlit ---

st.set_page_config(
    page_title="Modul Ajar Generator (Gemini-Powered)",
    layout="wide"
)

st.title("📚 Modul Ajar Generator (Gemini-Powered)")
st.caption("Alat bantu untuk guru menyusun Modul Ajar Kumer otomatis.")

# Inisialisasi Session State
if 'modul_content' not in st.session_state:
    st.session_state['modul_content'] = None
if 'file_name' not in st.session_state:
    st.session_state['file_name'] = ""

if GEMINI_API_KEY != "ISI_GEMINI_API_KEY_ANDA":
    # --- Bagian A: Identitas dan Informasi Umum (Input User) ---
    st.header("A. Identitas dan Informasi Umum")

    with st.form("modul_ajar_form"):
        col1, col2, col3 = st.columns(3)

        # Input Column 1
        with col1:
            st.subheader("Data Dasar")
            nama_penyusun = st.text_input("Nama Penyusun", "Nama Guru")
            jenjang_kelas = st.selectbox("Jenjang Sekolah (Kelas)", 
                                         ["VII", "VIII", "IX", "X", "XI", "XII"], index=2, key="kelas")
            
            # Penentuan Fase otomatis berdasarkan Kelas
            if st.session_state.kelas in ["VII", "VIII", "IX"]:
                fase = "D"
            elif st.session_state.kelas in ["X"]:
                fase = "E"
            elif st.session_state.kelas in ["XI", "XII"]:
                fase = "F"
            
            st.text_input("Fase", fase, disabled=True)
            
            mata_pelajaran = st.text_input("Mata Pelajaran", "Informatika", key="mapel")
            elemen_cp = st.text_area("Elemen dan Capaian Pembelajaran (CP)", 
                                     "Elemen: Berpikir Komputasional; CP: Peserta didik mampu mengidentifikasi masalah, mengembangkan prosedur algoritmik, dan mengimplementasikannya dalam kode sederhana.", height=150)

        # Input Column 2
        with col2:
            st.subheader("Detail Teknis")
            kompetensi_awal = st.text_area("Kompetensi Awal", "Peserta didik memahami konsep dasar algoritma dan flowchart.", height=100)
            alokasi_waktu = st.text_input("Alokasi Waktu", "4 x 45 Menit (2 Pertemuan)")
            # --- Perubahan di SINI ---
            profil_lulusan = st.multiselect("8 Profil Lulusan yang Dituju", 
                                            PROFIL_LULUSAN, 
                                            default=["Berpikir Kritis (Critical Thinking)", "Kolaboratif (Collaborative)"])
            # --- Akhir Perubahan ---
            target_siswa = st.selectbox("Target Peserta Didik", 
                                        ["Reguler", "Dengan Hambatan", "Cerdas Istimewa"])
            moda_pembelajaran = st.selectbox("Moda Pembelajaran", 
                                            ["Tatap Muka", "Tatap Maya (Online)", "Blended Learning"])
            
        # Input Column 3
        with col3:
            st.subheader("Metodologi")
            pendekatan_pembelajaran = st.multiselect("Pendekatan Pembelajaran", 
                                                     ["Saintifik", "STEM", "TaRL", "Kontekstual", "Proyek"], 
                                                     default=["Saintifik"])
            model_pembelajaran = st.selectbox("Model Pembelajaran", 
                                              ["Problem Based Learning (PBL)", "Project Based Learning (PjBL)", "Discovery Learning", "Inquiry Learning"], key="model_pembelajaran")
            metode_pembelajaran = st.multiselect("Metode Pembelajaran", 
                                                 ["Diskusi", "Presentasi", "Tanya Jawab", "Demonstrasi", "Praktik Langsung"], 
                                                 default=["Diskusi", "Praktik Langsung"])
            sarana_prasarana = st.text_area("Sarana Prasarana", "Laptop/Komputer, Proyektor, Papan Tulis, Jaringan Internet.")
            sumber_pembelajaran = st.text_area("Sumber Pembelajaran", "Buku Guru dan Siswa, Modul Kemendikbud, Situs Web Edukasi.")
            media_pembelajaran = st.text_area("Media Pembelajaran", "Slide Presentasi (PPT), Video Tutorial, Simulasi Online, LKPD.")

        # Tombol submit harus berada di dalam form
        submitted = st.form_submit_button("🚀 Generate Modul Ajar")

        if submitted:
            # Menyiapkan data untuk dikirim ke Gemini
            user_inputs = {
                "Nama Penyusun": nama_penyusun,
                "Jenjang Sekolah (Kelas)": st.session_state.kelas,
                "Fase": fase,
                "Mata Pelajaran": st.session_state.mapel,
                "Elemen dan CP": elemen_cp,
                "Kompetensi Awal": kompetensi_awal,
                "Alokasi Waktu": alokasi_waktu,
                "8 Profil Lulusan": ", ".join(profil_lulusan), # Data baru
                "Target Peserta Didik": target_siswa,
                "Moda Pembelajaran": moda_pembelajaran,
                "Pendekatan Pembelajaran": ", ".join(pendekatan_pembelajaran),
                "Model Pembelajaran": st.session_state.model_pembelajaran,
                "Metode Pembelajaran": ", ".join(metode_pembelajaran),
                "Sarana Prasarana": sarana_prasarana,
                "Sumber Pembelajaran": sumber_pembelajaran,
                "Media Pembelajaran": media_pembelajaran
            }

            # Data tambahan untuk fase dan model pembelajaran
            phase_details = f"Fase {fase} (Kelas {st.session_state.kelas}). Model Pembelajaran yang harus diintegrasikan sintaksnya ke dalam Urutan Kegiatan Pembelajaran (Bagian D) adalah **{st.session_state.model_pembelajaran}**."

            # Memanggil fungsi generator
            modul_ajar_content = generate_modul_ajar(user_inputs, phase_details)

            # SIMPAN HASIL KE SESSION STATE
            st.session_state['modul_content'] = modul_ajar_content
            st.session_state['file_name'] = f"Modul_Ajar_{st.session_state.mapel.replace(' ', '_')}_{st.session_state.kelas}.md"

            # Menampilkan hasil di dalam form setelah proses selesai
            st.success("✅ Modul Ajar berhasil dibuat!")
            st.divider()
            st.markdown(modul_ajar_content, unsafe_allow_html=True)
            
# --- AKHIR DARI BLOK st.form() ---
# Tombol Download harus berada di LUAR st.form()

if st.session_state['modul_content']:
    st.divider()
    # Tombol Download
    st.download_button(
        label="💾 Download Modul Ajar (Markdown)",
        data=st.session_state['modul_content'],
        file_name=st.session_state['file_name'],
        mime="text/markdown"
    )