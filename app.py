from flask import Flask, render_template, request, send_file, send_from_directory
from fpdf import FPDF
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SGP_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'SGP-24 | CRONOGRAMA DE PLANTAO', 0, 1, 'C')
        self.ln(5)

    def secao(self, titulo):
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, titulo, 1, 1, 'L', fill=True)
        self.ln(2)

@app.route('/static/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/salvar', methods=['POST'])
def salvar():
    equipe = request.form.get('equipe', 'SGP').upper()
    data_p = request.form.get('data', '')
    
    pdf = SGP_PDF()
    pdf.add_page()
    
    def limpar_texto(txt):
        if not txt: return ""
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    # --- 1. EFETIVO ---
    pdf.secao("RELACAO GERAL DE EFETIVO")
    chefe = request.form.get('chefe_nome', '').upper()
    mat = request.form.get('chefe_mat', '')
    if chefe:
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 7, limpar_texto(f"CHEFE DE EQUIPE: {chefe} | MAT: {mat}"), border='B', ln=1)
    
    pdf.set_font('Arial', '', 9)
    for i in range(1, 13):
        nome = request.form.get(f'p{i}', '').upper()
        status = request.form.get(f's{i}', '')
        if nome:
            pdf.cell(0, 6, limpar_texto(f"{i}. {nome} [{status}]"), border='B', ln=1)

    # --- 2. POSTOS DIA ---
    pdf.ln(5)
    pdf.secao("POSTOS DE SERVICO (DIA)")
    pdf.set_font('Arial', '', 8)
    
    # Recepção e Carceragem (Novos 4 campos)
    rec_nomes = ", ".join([request.form.get(f'rec_p{i}', '').upper() for i in range(1, 5) if request.form.get(f'rec_p{i}')])
    car_nomes = ", ".join([request.form.get(f'car_p{i}', '').upper() for i in range(1, 5) if request.form.get(f'car_p{i}')])
    
    pdf.multi_cell(0, 7, limpar_texto(f"RECEPCAO: {rec_nomes}"), 1)
    pdf.multi_cell(0, 7, limpar_texto(f"CARCERAGEM: {car_nomes}"), 1)
    
    # Monitoramento e Portão (Uso do .get para evitar o erro KeyError)
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 8); pdf.cell(0, 6, "MONITORAMENTO E PORTAO:", ln=1)
    pdf.set_font('Arial', '', 7)
    for i in range(1, 8):
        h_mon = request.form.get(f'mon_camera_{i}', '')
        h_por = request.form.get(f'portao_{i}', '')
        if h_mon or h_por:
            pdf.cell(95, 6, limpar_texto(h_mon), 1)
            pdf.cell(95, 6, limpar_texto(h_por), 1, 1)

    # --- 3. ESCALA NOTURNA ---
    pdf.add_page()
    pdf.secao("ESCALA NOTURNA")
    for i in range(1, 13):
        n = request.form.get(f'qh_p{i}', '').upper()
        h = request.form.get(f'qh_horario{i}', '')
        if n:
            pdf.cell(0, 7, limpar_texto(f"{h} - {n}"), border='B', ln=1)

    # --- 4. MISSÕES E ALMOÇO ---
    pdf.ln(5); pdf.secao("OBSERVACOES E ALMOCO")
    for m in ['defensoria', 'itep', 'ctc', 'atendimento_medico', 'missao_externa', 'missao_interna']:
        conteudo = request.form.get(m, '')
        if conteudo:
            pdf.set_font('Arial', 'B', 8); pdf.cell(0, 6, f"{m.upper()}:", ln=1)
            pdf.set_font('Arial', '', 8); pdf.multi_cell(0, 5, limpar_texto(conteudo), border='B')
    
    alm1 = request.form.get('almoco_1', '')
    alm2 = request.form.get('almoco_2', '')
    if alm1 or alm2:
        pdf.ln(2); pdf.set_font('Arial', 'B', 8); pdf.cell(0, 6, "ALMOCO / REPOUSO:", ln=1)
        pdf.set_font('Arial', '', 8)
        if alm1: pdf.multi_cell(0, 5, limpar_texto(f"1) {alm1}"), border='B')
        if alm2: pdf.multi_cell(0, 5, limpar_texto(f"2) {alm2}"), border='B')

    filename = f"SGP24_{equipe}.pdf"
    path = os.path.join(BASE_DIR, filename)
    pdf.output(path)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
