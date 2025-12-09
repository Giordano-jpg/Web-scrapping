import express from "express";
import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";
import { HfInference } from "@huggingface/inference";

const HF_TOKEN = "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";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const hf = new HfInference(HF_TOKEN);
const db = new Database(path.join(__dirname, "hackernews.db"));

// API Routes
app.get("/api/articulos", (req, res) => {
  try {
    const articulos = db.prepare("SELECT * FROM articulos ORDER BY fecha DESC LIMIT 50").all();
    res.json(articulos);
  } catch (error) {
    res.status(500).json({ error: "Error al obtener artículos" });
  }
});

app.get("/api/articulos/:id", (req, res) => {
  try {
    const articulo = db.prepare("SELECT * FROM articulos WHERE id = ?").get(req.params.id);
    res.json(articulo || {});
  } catch (error) {
    res.status(500).json({ error: "Error al obtener artículo" });
  }
});

// Resumen con Hugging Face
app.post("/api/resumir", async (req, res) => {
  try {
    let { texto } = req.body;

    if (!texto) {
      return res.status(400).json({ error: "No se proporcionó texto" });
    }

    texto = texto.trim();

    if (texto.length < 100) {
      return res.status(400).json({
        error: "Texto demasiado corto. Mínimo 100 caracteres.",
        longitud_actual: texto.length
      });
    }

    // Si es muy largo lo recortamos
    const MAX_LENGTH = 1024;
    if (texto.length > MAX_LENGTH) {
      texto = texto.substring(0, MAX_LENGTH);
    }

    console.log(`Enviando a Hugging Face: ${texto.length} caracteres`);

    // Llamada a Hugging Face
    const resultado = await hf.summarization({
      model: "facebook/bart-large-cnn",
      inputs: texto,
      parameters: {
        max_length: 150,
        min_length: 80,
        do_sample: false,
        truncation: true
      }
    });

    res.json({
      resumen: resultado.summary_text,
      longitud_original: texto.length
    });

  } catch (error) {
    console.error("Error de Hugging Face:", error);

    res.status(500).json({
      error: "Error al generar resumen",
      detalle: error.message
    });
  }
});

// Servidor
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`✅ Servidor en http://localhost:${PORT}`);
});
