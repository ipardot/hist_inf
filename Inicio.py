import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas

Expert=" "
profile_imgenh=" "

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""
    
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# Streamlit
st.set_page_config(page_title='Cuentos para dormir', page_icon='🌙')

# ------------------------------------------------------------------
# TEMA "CUENTOS PARA DORMIR" (solo estilos CSS; la lógica y los inputs no cambian)
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Nunito:wght@400;600;700&display=swap');

:root{
  --noche:#0f1533;
  --noche-media:#23306b;
  --luna:#f6e7b4;
  --oro:#e9c46a;
  --lavanda:#f1eefa;
  --almohada:#fffaf0;
  --tinta:#1a1a2e;
}

/* Fondo: cielo de noche con estrellas */
.stApp{
  background:
    radial-gradient(1.5px 1.5px at 25px 35px, #ffffff 50%, transparent 51%) 0 0 / 170px 170px,
    radial-gradient(1px 1px at 110px 80px, #ffffffcc 50%, transparent 51%) 0 0 / 170px 170px,
    radial-gradient(2px 2px at 60px 140px, var(--luna) 50%, transparent 51%) 0 0 / 230px 230px,
    radial-gradient(1px 1px at 180px 30px, #ffffffaa 50%, transparent 51%) 0 0 / 230px 230px,
    linear-gradient(180deg, var(--noche) 0%, var(--noche-media) 100%);
  background-attachment: fixed;
}
header[data-testid="stHeader"]{ background: transparent; }
header[data-testid="stHeader"] *{ color: var(--luna); }

/* Panel central: tarjeta clara donde se lee el cuento */
[data-testid="stMainBlockContainer"], .block-container{
  background:var(--almohada);
  border-radius:24px;
  box-shadow:0 0 0 1px rgba(233,196,106,.45), 0 24px 60px rgba(0,0,0,.35);
  margin-top:2rem;
  margin-bottom:4rem;
  padding:1.6rem 2.2rem 2.4rem !important;
  max-width:780px;
}
@media (max-width:640px){
  [data-testid="stMainBlockContainer"], .block-container{
    padding:1.1rem 1rem 1.8rem !important;
  }
}

/* Encabezado: ventana a la noche */
.noche-hero{
  position:relative; overflow:hidden;
  border-radius:18px;
  padding:1.8rem 1.8rem 1.6rem;
  margin-bottom:1.4rem;
  background:
    radial-gradient(1.5px 1.5px at 30px 40px, #ffffff 50%, transparent 51%) 0 0 / 120px 120px,
    radial-gradient(1px 1px at 90px 90px, #ffffffbb 50%, transparent 51%) 0 0 / 120px 120px,
    linear-gradient(135deg, var(--noche) 0%, var(--noche-media) 100%);
}
.noche-luna{
  position:absolute; top:1.3rem; right:1.6rem;
  width:58px; height:58px; border-radius:50%;
  box-shadow: inset -14px 9px 0 0 var(--luna);
  transform: rotate(-20deg);
}
.noche-tag{
  display:inline-block;
  font-family:'Nunito', sans-serif;
  font-weight:700; font-size:.78rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--noche);
  background:var(--oro);
  padding:.3rem .8rem; border-radius:999px;
}
.noche-title{
  font-family:'Fraunces', serif;
  font-weight:700; font-size:2.6rem; line-height:1.1;
  color:var(--luna);
  margin:.8rem 0 .5rem;
  padding-right:70px;
}
.noche-sub{
  font-family:'Nunito', sans-serif;
  font-size:1.05rem; line-height:1.55;
  color:#e4e7f6;
  max-width:520px;
}
.noche-pasos{ display:flex; flex-wrap:wrap; gap:.5rem; margin-top:1.1rem; }
.noche-pasos span{
  font-family:'Nunito', sans-serif; font-weight:700; font-size:.9rem;
  color:#ffffff;
  background:rgba(255,255,255,.12);
  border:1px solid rgba(246,231,180,.35);
  padding:.35rem .8rem; border-radius:999px;
}
@media (max-width:640px){
  .noche-title{ font-size:1.9rem; }
  .noche-luna{ width:42px; height:42px; top:1rem; right:1rem; box-shadow: inset -10px 7px 0 0 var(--luna); }
}

/* Títulos y textos del contenido */
h2, h3{
  font-family:'Fraunces', serif !important;
  font-weight:700 !important;
  color:var(--noche-media) !important;
}
h1 a, h2 a, h3 a{ display:none !important; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li{
  font-family:'Nunito', sans-serif;
  font-size:1.05rem;
  line-height:1.7;
}
.stApp hr{ border-color: rgba(35,48,107,.18); }

/* Barra lateral: lavanda suave */
section[data-testid="stSidebar"]{
  background:var(--lavanda);
  border-right:3px solid var(--oro);
}
section[data-testid="stSidebar"] h3{ font-size:1.1rem !important; }

/* Textos sobre fondos claros: siempre en negro (también si Streamlit usa el tema oscuro) */
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stWidgetLabel"] label,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="caption"],
.stApp [data-testid="stSliderThumbValue"],
.stApp [data-testid="stSliderTickBarMin"],
.stApp [data-testid="stSliderTickBarMax"],
.stApp [data-testid="stAlert"] [data-testid="stMarkdownContainer"] *{
  color:#1a1a1a !important;
}

/* Botones: conservan los colores originales de Streamlit (contraste) */
.stApp button [data-testid="stMarkdownContainer"],
.stApp button [data-testid="stMarkdownContainer"] *,
.stApp button [data-testid="stMarkdownContainer"] p{
  color:inherit !important;
  font-family:inherit !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="noche-hero">
  <div class="noche-luna"></div>
  <span class="noche-tag">🌙 Cuentos con IA</span>
  <div class="noche-title">Cuentos para dormir</div>
  <div class="noche-sub">Dibuja al protagonista de tu cuento y, cuando se apaguen las luces, la IA te contará su historia.</div>
  <div class="noche-pasos"><span>1 · Dibuja</span><span>2 · Conoce a tu personaje</span><span>3 · Escucha tu cuento</span></div>
</div>
""", unsafe_allow_html=True)
with st.sidebar:
    st.subheader("🌙 ¿Cómo funciona?")
    st.subheader("Dibuja a tu personaje, la IA lo conocerá y después te contará un cuento para dormir sobre él.")
st.subheader("✏️ Dibuja al protagonista de tu cuento")

# Add canvas component
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Grosor del lápiz', 1, 30, 5)
stroke_color = "#000000" 
bg_color = '#FFFFFF'

# Create a canvas component
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

ke = st.text_input('🔑 Ingresa tu clave de OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke

# Retrieve the OpenAI API Key
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

analyze_button = st.button("🔭 Conocer a mi personaje", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("🌙 Mirando tu dibujo con calma..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')
        
        # Codificar la imagen en base64
        base64_image = encode_image_to_base64("img.png")
        st.session_state.base64_image = base64_image
            
        prompt_text = (f"Describe in spanish briefly the image")
    
        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
              model= "gpt-4o-mini",
              messages=[
                {
                   "role": "user",
                   "content": [
                     {"type": "text", "text": prompt_text},
                     {
                       "type": "image_url",
                       "image_url": {
                         "url": f"data:image/png;base64,{base64_image}",
                       },
                     },
                   ],
                  }
                ],
              max_tokens=500,
              )
            
            if response.choices[0].message.content is not None:
                    full_response += response.choices[0].message.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
            
            # Guardar en session_state
            st.session_state.full_response = full_response
            st.session_state.analysis_done = True
            
            if Expert== profile_imgenh:
               st.session_state.mi_respuesta= response.choices[0].message.content
    
        except Exception as e:
            st.error(f"Ups, no pudimos ver tu dibujo esta noche: {e}")

# Mostrar la funcionalidad de crear historia si ya se hizo el análisis
if st.session_state.analysis_done:
    st.divider()
    st.subheader("📚 ¿Listo para tu cuento?")
    
    if st.button("✨ Cuéntame un cuento"):
        with st.spinner("✨ Escribiendo tu cuento entre las estrellas..."):
            story_prompt = f"Basándote en esta descripción: '{st.session_state.full_response}', crea una historia infantil breve y entretenida. La historia debe ser creativa y apropiada para niños."
            
            story_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_prompt}],
                max_tokens=500,
            )
            
            st.markdown("**📖 Tu cuento para dormir:**")
            st.write(story_response.choices[0].message.content)

# Warnings for user action required
if not api_key:
    st.warning("🔑 Ingresa tu clave de OpenAI para empezar el cuento.")
