import os
from datetime import datetime
from docx import Document
from docx.shared import Cm
from PIL import Image
import streamlit as st
import tempfile

def reduzir_imagem(imagem_bytes, largura_cm, altura_cm):
    with Image.open(imagem_bytes) as img:
        dpi = img.info.get("dpi", (96, 96))[0]
        largura_px = int((largura_cm / 2.54) * dpi)
        altura_px = int((altura_cm / 2.54) * dpi)
        img = img.resize((largura_px, altura_px), Image.LANCZOS)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        img.save(temp_file.name)
        return temp_file.name

def inserir_bloco_imagens(doc, titulo, imagens, largura_cm=5, altura_cm=4):
    doc.add_paragraph("------------------------------------------")
    doc.add_heading(titulo, level=2)
    par = doc.add_paragraph()
    for imagem in imagens:
        img_path = reduzir_imagem(imagem, largura_cm, altura_cm)
        par.add_run().add_picture(img_path, width=Cm(largura_cm), height=Cm(altura_cm))
        os.remove(img_path)

st.title("Relatório Fotográfico de Zeladoria")

with st.form("relatorio_form"):
    site_id = st.text_input("ID do site")
    data_execucao = st.date_input("Data da execução")
    localizacao = st.text_input("Localização (cidade - estado)")

    fotos_antes = st.file_uploader("Fotos do ANTES", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    fotos_depois = st.file_uploader("Fotos do DEPOIS", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    foto_placa = st.file_uploader("Foto da PLACA DE IDENTIFICAÇÃO", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Gerar Relatório")

if submitted:
    doc = Document()
    doc.add_heading("RELATÓRIO FOTOGRÁFICO DE ZELADORIA", level=1)
    doc.add_paragraph(f"Site ID: {site_id}")
    doc.add_paragraph(f"Data da Execução: {data_execucao.strftime('%d/%m/%Y')}")
    doc.add_paragraph(f"Localização: {localizacao.upper()}")

    if fotos_antes:
        inserir_bloco_imagens(doc, "FOTOS - ANTES", fotos_antes)
    if fotos_depois:
        inserir_bloco_imagens(doc, "FOTOS - DEPOIS", fotos_depois)
    if foto_placa:
        inserir_bloco_imagens(doc, "PLACA DE IDENTIFICAÇÃO", [foto_placa])

    nome_arquivo = f"RLT. ZELADORIA - {site_id} - {data_execucao.strftime('%Y-%m-%d')}.docx"
    temp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(temp_docx.name)

    with open(temp_docx.name, "rb") as file:
        st.success("✅ Relatório gerado com sucesso!")
        st.download_button("Baixar Relatório", file, file_name=nome_arquivo)
