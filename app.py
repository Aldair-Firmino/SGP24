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

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, 'Powered by Soluções Inteligentes', 0, 0, 'R')
        self.set_x(10)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'L')

    def secao(self, titulo):
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, str(titulo).upper(), 1, 1, 'L', fill=True)
        self.ln(2)

def limpar_texto(txt):
    if not txt: return ""
    return str(txt).upper().encode('latin-1', 'replace').decode('latin-1')

@app.route('/static/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/salvar', methods=['POST'])
def salvar():
    equipe = request.form.get('equipe', 'ALFA').upper()
    data_p = request.form.get('data', '')
    
    pdf = SGP_PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # 1. EFETIVO
    pdf.secao("RELACAO GERAL DE EFETIVO")
    chefe = request.form.get('chefe_nome', '')
    mat = request.form.get('chefe_mat', '')
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 7, limpar_texto(f"CHEFE DE EQUIPE: {chefe} | MAT: {mat}"), border='B', ln=1)
    
    pdf.set_font('Arial', '', 9)
    for i in range(1, 13):
        nome = request.form.get(f'p{i}', '')
        status = request.form.get(f's{i}', '24H')
        if nome:
            pdf.cell(0, 6, limpar_texto(f"{i}. {nome} [{status}]"), border='B', ln=1)

    # 2. MONITORAMENTO MANHÃ (RESTAURADO)
    pdf.ln(5)
    pdf.secao("MONITORAMENTO MANHA (06:00 AS 08:00)")
    pdf.set_font('Arial', '', 8)
    h_manha = ['06:00 - 06:30','06:30 - 07:00','07:00 - 07:30','07:30 - 08:00']
    for i, h in enumerate(h_manha, 1):
        pol = request.form.get(f'mon_manha_{i}', '')
        if pol:
            pdf.cell(0, 7, limpar_texto(f"{h} - {pol}"), border='B', ln=1)

    # 3. POSTOS DIA
    pdf.ln(5)
    pdf.secao("POSTOS DE SERVICO (DIA)")
    
    # Recepção e Carceragem
    pdf.set_font('Arial', 'B', 8)
    rec = ", ".join([request.form.get(f'rec_p{i}', '') for i in range(1, 5) if request.form.get(f'rec_p{i}', '')])
    car = ", ".join([request.form.get(f'car_p{i}', '') for i in range(1, 5) if request.form.get(f'car_p{i}', '')])
    if rec: pdf.multi_cell(0, 6, limpar_texto(f"RECEPCAO: {rec}"), border='B')
    if car: pdf.multi_cell(0, 6, limpar_texto(f"CARCERAGEM: {car}"), border='B')
    pdf.ln(2)

    # Monitoramento e Portão
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(95, 7, "MONITORAMENTO (CAMERAS)", 1, 0, 'C', fill=True)
    pdf.cell(95, 7, "ABERTURA DE PORTAO", 1, 1, 'C', fill=True)
    pdf.set_font('Arial', '', 8)
    for i in range(1, 8):
        h_dia = request.form.get(f'mon_camera_horario{i}', '')
        p_mon = request.form.get(f'mon_camera_{i}', '')
        p_por = request.form.get(f'portao_{i}', '')
        if p_mon or p_por:
            pdf.cell(95, 7, limpar_texto(f"{h_dia} - {p_mon}"), 1, 0, 'L')
            pdf.cell(95, 7, limpar_texto(f"{h_dia} - {p_por}"), 1, 1, 'L')

    # 4. ESCALA NOTURNA
    pdf.ln(5)
    pdf.secao("ESCALA NOTURNA")
    
    # Pré-Quarto
    pdf.set_font('Arial', 'B', 9); pdf.cell(0, 8, "PRE-QUARTO (18:00 AS 22:00)", ln=1)
    pdf.set_font('Arial', '', 9)
    for i in range(1, 8):
        h_pre = request.form.get(f'pre_horario{i}', '')
        n_pre = request.form.get(f'pre_p{i}', '')
        if n_pre:
            pdf.cell(0, 7, limpar_texto(f"{h_pre} - {n_pre}"), border='B', ln=1)

    pdf.ln(3)
    # Quarto de Hora
    pdf.set_font('Arial', 'B', 9); pdf.cell(0, 8, "QUARTO DE HORA (22:00 AS 06:00)", ln=1)
    pdf.set_font('Arial', '', 9)
    for i in range(1, 13):
        h_qh = request.form.get(f'qh_horario{i}', '')
        n_qh = request.form.get(f'qh_p{i}', '')
        if n_qh:
            pdf.cell(0, 7, limpar_texto(f"{h_qh} - {n_qh}"), border='B', ln=1)

    # 5. MISSÕES E ALMOÇO
    pdf.ln(5)
    pdf.secao("OBSERVACOES E MISSOES")
    for label, field in [('DEFENSORIA','defensoria'),('ITEP','itep'),('CTC','ctc'),('MEDICO','atendimento_medico'),('EXTERNA','missao_externa'),('INTERNA','missao_interna'),('ALMOCO / REPOUSO','almoco_repouso')]:
        cont = request.form.get(field, '')
        if cont:
            pdf.set_font('Arial', 'B', 8); pdf.cell(0, 6, limpar_texto(label), ln=1)
            pdf.set_font('Arial', '', 8); pdf.multi_cell(0, 5, limpar_texto(cont), border='B')

    filename = f"SGP24_{equipe}_{data_p}.pdf"
    path = os.path.join(BASE_DIR, filename)
    pdf.output(path)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
