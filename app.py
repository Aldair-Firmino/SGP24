from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
import webbrowser
from threading import Timer

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

def abrir_navegador():
    webbrowser.open_new("http://127.0.0.1:5000")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/salvar', methods=['POST'])
def salvar():
    equipe = request.form.get('equipe', 'SGP').upper()
    data_p = request.form.get('data', '')
    
    pdf = SGP_PDF()
    pdf.add_page()
    
    # Função para limpar caracteres que travam o PDF (como o traço longo)
    def limpar_texto(txt):
        if not txt: return ""
        return txt.encode('latin-1', 'replace').decode('latin-1')

    # 1. EFETIVO
    pdf.secao("RELACAO GERAL DE EFETIVO")
    chefe = request.form.get('chefe_nome', '').upper()
    chefe_mat = request.form.get('chefe_mat', '')
    if chefe:
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 7, limpar_texto(f"CHEFE DE EQUIPE: {chefe} - MAT: {chefe_mat}"), border='B', ln=1)
    
    pdf.set_font('Arial', '', 9)
    for i in range(1, 11):
        nome = request.form.get(f'p{i}', '').upper()
        if nome:
            pdf.cell(0, 6, limpar_texto(f"{i}. {nome} - MAT: {request.form.get('m'+str(i), '')} [{request.form.get('s'+str(i), '')}]"), border='B', ln=1)

    # 2. POSTOS DIA
    pdf.ln(5)
    pdf.secao("POSTOS DE SERVICO (DIA - 08:00 AS 18:00)")
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(95, 6, "RECEPCAO", 1); pdf.cell(95, 6, "CARCERAGEM", 1, 1)
    pdf.set_font('Arial', '', 8)
    for i in range(1, 5):
        p_rec = request.form.get(f'rec_p{i}', '').upper()
        p_car = request.form.get(f'car_p{i}', '').upper()
        pdf.cell(95, 7, limpar_texto(f"{i}. {p_rec}"), 1)
        pdf.cell(95, 7, limpar_texto(f"{i}. {p_car}"), 1, 1)

    # MONITORAMENTO E PORTÃO
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(95, 6, "MONITORAMENTO: CAMERAS", 1); pdf.cell(95, 6, "ABERTURA DE PORTAO", 1, 1)
    pdf.set_font('Arial', '', 8)
    h_lista = ['08:00 AS 10:00','10:00 AS 12:00','12:00 AS 14:00','14:00 AS 16:00','16:00 AS 18:00']
    for i, h in enumerate(h_lista, 1):
        p_mon = request.form.get(f'mon_camera_{i}', '').upper()
        p_por = request.form.get(f'portao_{i}', '').upper()
        pdf.cell(95, 7, limpar_texto(f"{h} - {p_mon}"), 1)
        pdf.cell(95, 7, limpar_texto(f"{h} - {p_por}"), 1, 1)

    # 3. ESCALA NOITE
    pdf.add_page()
    pdf.secao("ESCALA NOTURNA")
    
    # Pré-Quarto
    pdf.set_font('Arial', 'B', 9); pdf.cell(0, 8, "1. PRE-QUARTO (18:00 AS 22:00)", ln=1)
    pdf.set_font('Arial', '', 8)
    pre_h = ['18:00 AS 18:48','18:48 AS 19:36','19:36 AS 20:24','20:24 AS 21:12','21:12 AS 22:00']
    for i, h in enumerate(pre_h, 1):
        p_pre = request.form.get(f'pre_p{i}', '').upper()
        pdf.cell(0, 7, limpar_texto(f"{h} - {p_pre}"), border='B', ln=1)

    # Quarto de Hora Dinâmico
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 9); pdf.cell(0, 8, "2. QUARTO DE HORA (22:00 AS 06:00)", ln=1)
    pdf.set_font('Arial', '', 9)
    for i in range(1, 12):
        nome_qh = request.form.get(f'qh_p{i}', '').upper()
        horario_qh = request.form.get(f'qh_horario{i}', '')
        if nome_qh and horario_qh:
            pdf.cell(0, 8, limpar_texto(f"{horario_qh} {nome_qh}"), border='B', ln=1)

    # Café da Manhã
    pdf.ln(5)
    pdf.secao("3. QUARTO DE HORA CAFE DA MANHA (MONITORAMENTO)")
    cafe_h = ["06:00 AS 06:30", "06:30 AS 07:00", "07:00 AS 07:30", "07:30 AS 08:00"]
    for i, h in enumerate(cafe_h, 1):
        p_mon = request.form.get(f'cafe_mon_{i}', '').upper()
        pdf.cell(0, 8, limpar_texto(f"{h} {p_mon}"), border='B', ln=1)

    # 4. MISSÕES
    pdf.ln(5); pdf.secao("OBSERVACOES E MISSOES")
    for m in ['defensoria', 'itep', 'ctc', 'atendimento_medico', 'missao_externa', 'missao_interna']:
        conteudo = request.form.get(m, '')
        if conteudo:
            pdf.set_font('Arial', 'B', 8); pdf.cell(0, 6, f"{m.upper().replace('_', ' ')}:", ln=1)
            pdf.set_font('Arial', '', 8); pdf.multi_cell(0, 5, limpar_texto(conteudo), border='B')

    filename = f"SGP24_{equipe}_{data_p}.pdf"
    path = os.path.join(BASE_DIR, filename)
    pdf.output(path)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    Timer(1, abrir_navegador).start()
    app.run(debug=False, port=5000)