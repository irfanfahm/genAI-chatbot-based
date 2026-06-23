import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import pdfplumber

# 1. Konfigurasi Environment & API
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY tidak ditemukan!")

# 2. Inisialisasi Aplikasi (Tahap 7: Standardization Aktif)
app = FastAPI(title="Kemenperin BI Dashboard & EV Agent")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# 3. Setup Embedding Lokal & Vector Database
print("Memuat mesin analitik dan embedding lokal (all-MiniLM-L6-v2)...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

qdrant = QdrantClient(":memory:")
COLLECTION_NAME = "kemenperin_knowledge"
qdrant.recreate_collection(
    collection_name=COLLECTION_NAME, vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

genai.configure(api_key=GEMINI_API_KEY)
chat_model = genai.GenerativeModel('gemini-2.5-flash')

DOCS_DIR = "development"

# --- PIPELINE ETL: AUTO-EKSTRAKSI PDF/PPT ---
@app.on_event("startup")
async def load_knowledge_base():
    if not os.path.exists(DOCS_DIR): os.makedirs(DOCS_DIR)
    files = [f for f in os.listdir(DOCS_DIR) if f.endswith('.pdf')]
    
    if not files:
        print(f"⚠️ Menunggu dokumen PDF di folder '{DOCS_DIR}'.")
        return

    print("Memulai proses ekstraksi ETL...")
    total_chunks = 0
    for filename in files:
        filepath = os.path.join(DOCS_DIR, filename)
        try:
            with pdfplumber.open(filepath) as pdf:
                points = []
                for page_num, page in enumerate(pdf.pages, start=1):
                    slide_text = page.extract_text(layout=False)
                    if not slide_text or not slide_text.strip(): continue
                    
                    chunk = f"--- SLIDE {page_num} ---\n{slide_text}\n--- END SLIDE {page_num} ---"
                    vector = embedder.encode(chunk).tolist()
                    points.append(PointStruct(
                        id=str(uuid.uuid4()), vector=vector, payload={"text": chunk, "source": f"{filename} (Slide {page_num})"}
                    ))
                
                if points:
                    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
                    total_chunks += len(points)
                    print(f"  ✓ {filename} terkalibrasi ({len(points)} Slide).")
        except Exception as e:
            print(f"  ❌ Error pada {filename}: {e}")
            
    print(f"✅ RAG Pipeline Siap. Total matriks: {total_chunks}")

# --- ENDPOINT 1: DATA JSON UNTUK DASHBOARD VISUAL ---
@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Menyajikan metrik kolektif KBLBB dari slide Kemenperin"""
    return JSONResponse(content={
        "kpi": {
            "total_ev_pop": "333.561",
            "cagr_growth": "143.1%",
            "r4_bev_share": "12.93%",
            "investasi_baterai": "Rp 96.04 T"
        },
        "charts": {
            "ev_growth": {
                "labels": ["2020", "2021", "2022", "2023", "2024", "2025"],
                "data": [3894, 15883, 41743, 116439, 207478, 333561]
            },
            "r4_market_share": {
                "labels": ["ICE (Bensin)", "HEV (Hybrid)", "BEV (Listrik)", "PHEV"],
                "data": [78.29, 8.13, 12.93, 0.65]
            }
        }
    })

# --- ENDPOINT 2: RAG AI COPILOT ---
class ChatRequest(BaseModel): message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        query_vector = embedder.encode(request.message).tolist()
        search_results = qdrant.search(collection_name=COLLECTION_NAME, query_vector=query_vector, limit=4)
        
        context_text = "\n\n========\n\n".join([f"(Sumber: {hit.payload['source']})\n{hit.payload['text']}" for hit in search_results])
        if not context_text.strip(): context_text = "Data tidak tersedia di slide."

        prompt = prompt = f"""Kamu adalah AI Analytics Copilot Kemenperin.
Tugasmu adalah mengekstrak data dari [KNOWLEDGE BASE] dan memberikan jawaban analitik yang mutlak, padat, dan langsung.

STANDARISASI OUTPUT:
1. ZERO FILLER: Dilarang keras menggunakan kalimat pembuka/penutup (seperti "Baik, berikut adalah datanya..." atau "Semoga informasi ini membantu").
2. DIRECT ANSWER: Kalimat pertama harus langsung menjawab inti pertanyaan.
3. STRUCTURED DATA: Gunakan bullet points (-) untuk menjabarkan lebih dari 2 metrik atau tahapan.
4. SITASI TEGAS: Wajib menyertakan nomor referensi di akhir kalimat yang mengandung metrik [Slide X].
5. OUT OF SCOPE: Jika data tidak ada di [KNOWLEDGE BASE], outputkan tepat: "N/A: Data tidak tersedia dalam laporan referensi."

[KNOWLEDGE BASE]:
{context_text}

[PERTANYAAN USER]:
{request.message}

OUTPUT ANALITIK:"""

        response = chat_model.generate_content(prompt, stream=True)
        
        def stream_generator():
            for chunk in response:
                if chunk.text: yield chunk.text

        return StreamingResponse(stream_generator(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)