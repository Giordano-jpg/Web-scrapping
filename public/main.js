async function cargarArticulos() {
  const contenedor = document.getElementById("articulos-container");
  contenedor.innerHTML = "<p>Cargando artículos...</p>";

  try {
    const respuesta = await fetch("/api/articulos");
    const articulos = await respuesta.json();

    if (articulos.length === 0) {
      contenedor.innerHTML = "<p>No hay artículos disponibles</p>";
      return;
    }

    contenedor.innerHTML = "";

    articulos.forEach(articulo => {
      const div = document.createElement("div");
      div.className = "articulo";

      div.innerHTML = `
                <h2>${articulo.titulo || "Sin título"}</h2>
                <p><strong>Fecha:</strong> ${articulo.fecha || "N/A"}</p>
                <p><strong>URL:</strong> ${articulo.url ? `<a href="${articulo.url}" target="_blank">Ver original</a>` : "N/A"}</p>
                <p><strong>Resumen guardado:</strong> ${articulo.resumen || "No disponible"}</p>
                <p><strong>Contenido:</strong> ${articulo.contenido ? articulo.contenido.substring(0, 200) + "..." : "No disponible"}</p>

                <button onclick="generarResumen(${articulo.id})">🤖 Resumir con IA</button>
                <div id="resumen-${articulo.id}" class="resumen-resultado"></div>
                <hr>
            `;

      contenedor.appendChild(div);
    });
  } catch (error) {
    contenedor.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
  }
}

async function generarResumen(idArticulo) {
  const resultadoDiv = document.getElementById(`resumen-${idArticulo}`);
  resultadoDiv.innerHTML = "<p>Generando resumen con IA...</p>";

  try {
    // articulo completo
    const respuestaArticulo = await fetch(`/api/articulos/${idArticulo}`);
    const articulo = await respuestaArticulo.json();

    // Texto a resumir
    const texto = articulo.contenido || articulo.titulo || "";

    if (!texto.trim()) {
      resultadoDiv.innerHTML = "<p style=\"color: red;\">No hay contenido para resumir</p>";
      return;
    }

    // Llamar a la API de resumen
    const respuesta = await fetch("/api/resumir", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto })
    });

    const data = await respuesta.json();

    if (!respuesta.ok) {
      throw new Error(data.error || "Error desconocido");
    }

    resultadoDiv.innerHTML = `
            <div style="background: #f0f8ff; padding: 10px; border-left: 4px solid #2196f3;">
                <strong>✅ Resumen generado:</strong>
                <p>${data.resumen}</p>
            </div>
        `;

  } catch (error) {
    resultadoDiv.innerHTML = `
            <div style="background: #ffebee; padding: 10px; border-left: 4px solid #f44336;">
                <strong>❌ Error:</strong>
                <p>${error.message}</p>
            </div>
        `;
  }
}

// Cargar al iniciar
document.addEventListener("DOMContentLoaded", cargarArticulos);
