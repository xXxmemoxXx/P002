from flask import Flask, render_template, jsonify
import mysql.connector
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)

# Función para obtener los datos de MySQL
def obtener_datos():
    conn = mysql.connector.connect(
        host="miaa.mx",
        user="miaamx_telemetria",
        password="eORPvq4.yy@C",
        database="miaamx_telemetria"
    )
    
    cursor = conn.cursor()
    
    query = """
        SELECT FECHA, GATEID, VALUE
        FROM vfitagnumhistory
        WHERE GATEID IN (66482, 66484)
        AND FECHA >= NOW() - INTERVAL 7 DAY
        ORDER BY FECHA ASC
    """
    
    cursor.execute(query)
    datos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    df = pd.DataFrame(datos, columns=["FECHA", "GATEID", "VALUE"])
    df["FECHA"] = pd.to_datetime(df["FECHA"])

    return df

# Ruta para generar el gráfico
@app.route("/")
def index():
    return render_template("index.html")

# Ruta para actualizar los datos cada 5 minutos
@app.route("/datos")
def datos():
    df = obtener_datos()
    
    # Filtrar por GATEID
    df_caudal = df[df["GATEID"] == 66482]
    df_presion = df[df["GATEID"] == 66484]

    # Crear gráfico con Plotly
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_caudal["FECHA"], y=df_caudal["VALUE"], mode="lines+markers",
        name="Caudal (L/s)", line=dict(color="blue"), marker=dict(size=6),
        hovertemplate="Fecha: %{x}<br>Caudal: %{y} L/s"
    ))

    fig.add_trace(go.Scatter(
        x=df_presion["FECHA"], y=df_presion["VALUE"], mode="lines+markers",
        name="Presión (Kg/cm²)", line=dict(color="green"), marker=dict(size=6),
        yaxis="y2", hovertemplate="Fecha: %{x}<br>Presión: %{y} Kg/cm²"
    ))

    fig.update_layout(
        title="P002 Caudal y Presión",
        xaxis=dict(title="Fecha", tickangle=45),
        yaxis=dict(title="Caudal (L/s)", side="left"),
        yaxis2=dict(title="Presión (Kg/cm²)", overlaying="y", side="right"),
        hovermode="x unified",
        template="plotly_dark"
    )

    # Convertir gráfico a HTML
    grafico_html = pio.to_html(fig, full_html=False)
    
    return jsonify({"grafico": grafico_html})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
