import chainlit as cl
import google.generativeai as genai
import random

# Ganti dengan API key kamu (gunakan API key yang valid dan aman)
GOOGLE_API_KEY = "AIzaSyBYmVZA6nnetMjeWcnosX639-glZoCJAyU" # Pastikan ini adalah API key yang valid dan aman!
genai.configure(api_key=GOOGLE_API_KEY)

# Daftar soal pemrograman dasar
PROGRAMMING_QUESTIONS = [
    {
        "id": 1,
        "question": "Buatlah fungsi Python yang menerima sebuah angka dan mengembalikan 'Genap' jika angka tersebut genap, dan 'Ganjil' jika angka tersebut ganjil.",
        "expected_output_hint": "Fungsi Anda harus mengembalikan string 'Genap' atau 'Ganjil'."
    },
    {
        "id": 2,
        "question": "Tulisklah kode python untuk menampilkan nilai pertama dari sebuah array/list.",
        "expected_output_hint": "Fungsi atau kode Anda harus menghasilkan nilai pertama array."
    },
    {
        "id": 3,
        "question": "Buatlah kode python untuk menghitung kembalian pada sebuah transaksi.",
        "expected_output_hint": "Program anda harus dapat menghitung kembalian."
    },
    {
        "id": 4,
        "question": "Buatlah program python untuk menghitung luas sebidang lahan.",
        "expected_output_hint": "Fungsi Anda harus mengembalikan luas yang dihitung dari panjang dan lebar lahan."
    },
    {
        "id": 5,
        "question": "Buatlah fungsi python untuk menentukan sebuah kendaraan boleh masuk toll atau tidak. Dengan syarat jumlah roda harus lebih dari atau sama dengan 4.",
        "expected_output_hint": "Return true jika boleh, return false jika tidak boleh."
    }
]

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

@cl.on_chat_start
async def on_chat_start():
    print("User session object:", cl.user_session)

    user = cl.user_session.get("user")
    model = genai.GenerativeModel("gemini-1.5-flash") # Menggunakan gemini-1.5-flash untuk performa lebih baik

    cl.user_session.set("chat", model.start_chat(history=[]))

    # Pilih soal secara acak
    selected_question = random.choice(PROGRAMMING_QUESTIONS)
    cl.user_session.set("current_question", selected_question)

    welcome_message = f"Hello {user.identifier}👋! Saya Ak()de. Ayo ngoding!\n\n"
    question_message = f"**Soal:**\n{selected_question['question']}\n\n"
    instruction_message = "Silakan tulis jawaban Python Anda di bawah ini:"

    await cl.Message(content=welcome_message + question_message + instruction_message).send()


@cl.on_message
async def on_message(message: cl.Message):
    chat = cl.user_session.get("chat")
    current_question = cl.user_session.get("current_question")

    if chat is None or current_question is None:
        await cl.Message(content="❌ Sesi atau soal tidak ditemukan. Silakan muat ulang.").send()
        return

    user_code = message.content

    review_prompt = (
        f"Saya telah diberikan soal pemrograman dasar berikut:\n\n"
        f"**Soal:** {current_question['question']}\n\n"
        f"Dan saya telah mencoba menjawabnya dengan kode Python ini:\n\n"
        f"```python\n{user_code}\n```\n\n"
        f"Jika ada kesalahan atau error atau tidak ada kodenya, jangan berikan kode yang benar. Jika kodenya ada, berikan review yang komprehensif terhadap kode saya. Fokus pada aspek-aspek berikut:\n"
        f"1. **Kebenaran**\n"
        f"2. **Efisiensi**\n"
        # f"3. **Keterbacaan**\n"
        f"Berikan _review_ Anda dalam format yang terstruktur, cukup singkat dan mudah dipahami."
        f"Jika jawaban user sudah benar, perintahkan untuk membuat chat baru."
    )

    try:
        # Kirim pesan loading (tidak disimpan karena tidak bisa diupdate)
        await cl.Message(content="⏳ Sedang mereview jawaban Anda...").send()

        # Kirim prompt ke Gemini
        response = chat.send_message(review_prompt)

        # Kirim pesan baru dengan hasil review
        await cl.Message(content=f"**Review Jawaban Anda:**\n\n{response.text}").send()

    except Exception as e:
        await cl.Message(content=f"❌ Terjadi kesalahan saat me-review: {str(e)}").send()
