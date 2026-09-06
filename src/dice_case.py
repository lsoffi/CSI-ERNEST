"""Fascicoli e poster specifici per CSI-004, senza modificare gli altri casi."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5, A3
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

BLUE=colors.HexColor('#1F2041'); YELLOW=colors.HexColor('#FFE548'); LIGHT=colors.HexColor('#E6E6EF')
STYLE=ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=14,textColor=BLUE,spaceAfter=8)
H=ParagraphStyle('heading',parent=STYLE,fontName='Helvetica-Bold',fontSize=17,leading=20,spaceAfter=14)
SMALL=ParagraphStyle('small',parent=STYLE,fontSize=8,leading=11)

def p(text, style=STYLE): return Paragraph(escape(text).replace('\n','<br/>'),style)
def title(text): return p(text,H)
def grid(headers, rows, widths=None, height=8*mm):
    t=Table([headers]+rows,colWidths=widths,rowHeights=[height]*(len(rows)+1))
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),YELLOW),('TEXTCOLOR',(0,0),(-1,-1),BLUE),('GRID',(0,0),(-1,-1),.5,BLUE),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    return t

def lines(question,n=3):
    return [p(question),grid([''],[[''] for _ in range(n-1)],[112*mm],6*mm),Spacer(1,3*mm)]

def matrix(filled=False):
    return grid(['A / B']+list(range(1,7)),[[a]+[a+b if filled else '' for b in range(1,7)] for a in range(1,7)],[16*mm]*7,9*mm)

def frame(c,doc):
    w,h=doc.pagesize; c.setStrokeColor(BLUE); c.setLineWidth(1)
    c.rect(12*mm,17*mm,w-24*mm,h-22*mm)
    c.setFont('Helvetica-Bold',8); c.setFillColor(BLUE)
    c.drawString(18*mm,h-14*mm,'ERNEST | CLASSROOM SCIENCE INVESTIGATION')
    c.setStrokeColor(YELLOW);c.setLineWidth(2);c.line(18*mm,h-19*mm,w-18*mm,h-19*mm)
    c.setFont('Helvetica',8);c.drawString(18*mm,21*mm,'CSI-004 | I dadi nascondono un segreto');c.drawRightString(w-18*mm,21*mm,str(doc.page))
    assets=Path(__file__).resolve().parents[1]/'assets'
    eu=assets/'eu-funded-logo.png'
    if eu.exists(): c.drawImage(str(eu),18*mm,4*mm,width=37*mm,height=10*mm,preserveAspectRatio=True,mask='auto')

def document(path,pages):
    doc=SimpleDocTemplate(str(path),pagesize=A5,leftMargin=18*mm,rightMargin=18*mm,topMargin=27*mm,bottomMargin=30*mm)
    story=[]
    for i,page in enumerate(pages):
        if i: story.append(PageBreak())
        while page and isinstance(page[-1], Spacer):
            page = page[:-1]
        story.extend(page)
    doc.build(story,onFirstPage=frame,onLaterPages=frame)

def cover(case,kind):
    return [p('CASE FILE / '+case['case_id']),Spacer(1,8*mm),title(case['title']),p(kind),Spacer(1,5*mm),p(case['mystery']),p(case['story_intro']),Spacer(1,5*mm),p('LA MISSIONE',H),p(case['mission'])]

def build_student_pdf(case,path,logo_path=None):
    pages=[cover(case,'Fascicolo investigatori | Notte Europea dei Ricercatori')]
    pages.append([title('Le voci della piazza'),p(case['scene_evidence']),p(case['witness_1']),p(case['witness_2']),p(case['witness_3']),*lines('La nostra previsione: quali somme compariranno più spesso? Perché?',4),p('Squadra: ________________________')])
    pages.append([title('Il protocollo dei lanci'),p('1. Assegnate i ruoli: due lanciatori, lettore, addetto al pannello. Identificate i dadi come A e B.'),p('2. Lanciate entrambi i dadi nella zona indicata. Attendete che siano fermi e leggete le facce superiori.'),p('3. Se un dado è inclinato o fuori area, ripetete entrambi. Annotate la ripetizione, senza inserire quel tentativo nel grafico.'),p('4. Scrivete un solo post-it per ogni lancio valido: A = __, B = __, somma = __.'),p('5. Attaccatelo nella colonna della somma, subito sopra il precedente, senza spazi né sovrapposizioni.'),p('6. Dopo 10 lanci fermatevi a osservare. Poi proseguite: registrate tutti i risultati, anche quelli inattesi.'),*lines('Dopo 10 lanci: cosa vediamo? È già una prova sufficiente?',3)])
    pages.append([title('Registro della squadra'),p('Continuate sul pannello o su altre copie. Un solo post-it per lancio: il registro non è un secondo evento.',SMALL),grid(['N.','Dado A','Dado B','Somma'],[[i,'','',''] for i in range(1,16)],[14*mm,32*mm,32*mm,34*mm],7*mm),Spacer(1,5*mm),p('Tentativi da ripetere e motivo: __________________\nLanci validi registrati: ______',SMALL)])
    pages.append([title('Leggere il pannello'),p('Trascrivete i conteggi. Le prime 10 prove sono incluse nel totale finale. La somma di ogni colonna di conteggi deve dare il rispettivo totale.',SMALL),grid(['Somma','Primi 10','Totale finale'],[[i,'',''] for i in range(2,13)],[28*mm,42*mm,42*mm],7*mm),Spacer(1,4*mm),p('Totale lanci finali N = ______\nFrequenza relativa = conteggio / N.',SMALL),*lines('La forma è cambiata? Per confrontare 10 lanci con N lanci, perché le sole altezze non bastano?',2)])
    from reportlab.graphics.shapes import Drawing, Line, String
    chart=Drawing(305,245)
    for j in range(11):
        x=25+j*25
        chart.add(String(x+12,5,str(j+2),fontSize=9,textAnchor='middle'))
        chart.add(Line(x,22,x,222,strokeColor=LIGHT))
    chart.add(Line(300,22,300,222,strokeColor=LIGHT))
    for j in range(11):
        chart.add(Line(25,22+j*20,300,22+j*20,strokeColor=LIGHT))
        chart.add(String(18,19+j*20,str(j*2),fontSize=7,textAnchor='end'))
    chart.add(String(25,235,'Numero di lanci',fontSize=9))
    pages.append([title('Il nostro istogramma'),p('Riportate i conteggi finali del pannello. Colorate una barra per ogni somma: una riga della griglia vale 2 lanci. Se serve una scala maggiore, concordatela e correggete tutte le etichette.',SMALL),chart,p('Somma dei dadi A + B',SMALL),*lines('Quale forma osserviamo?',3)])
    pages.append([title('La prova delle 36 coppie'),p('APRIRE DOPO LA RACCOLTA',SMALL),p('Scrivete in ogni casella la somma di A e B. A = 1, B = 6 e A = 6, B = 1 sono due coppie distinte.'),matrix(),Spacer(1,5*mm),p('Quante caselle danno 2? ____  7? ____  12? ____'),*lines('Le somme hanno tutte lo stesso numero di modi per comparire?',3)])
    pages.append([title('Rapporto conclusivo'),*lines('Quale spiegazione proponiamo per la forma del grafico?',4),*lines('Quali conteggi e quali combinazioni la sostengono?',3),*lines('Le previsioni corrispondono ai dati? Che cosa resta da verificare?',3),p('La nostra scoperta in una frase:\n________________________________',SMALL)])
    document(path,pages)

def build_teacher_pdf(case,path,logo_path=None):
    pages=[cover(case,'Guida docente e facilitatore | 20-30 minuti')]
    pages.append([title('Preparare la piazza'),p(case['materials']),p('Etichettare i dadi A e B senza coprire le facce numerate. Usare una superficie piana, lontana dal passaggio del pubblico. Delimitare lo spazio in base alla dimensione dei dadi; solo i lanciatori entrano quando l’area è libera.'),p('Disegnare 11 colonne da 2 a 12, con base comune. Scrivere: asse x = somma; asse y = numero di lanci. Un post-it = un lancio valido. Prevedere una persona al pannello per evitare errori e code.'),p('Con post-it da 7,5 cm, riservare circa 95 cm di larghezza e 150 cm di altezza utile, più titoli. È una scelta di allestimento, non una garanzia contro colonne troppo alte.'),p('Se una colonna si riempie, annotare tutti i conteggi e iniziare un nuovo blocco di raccolta per tutte le colonne. Conservare i subtotali. Non comprimere soltanto una colonna.'),p('Fissare pannello e fogli; rinforzare i post-it con nastro. Non usare i dadi con vento che ne impedisca il controllo. Tenere libera l’area di atterraggio.',SMALL)])
    pages.append([title('Conduzione in 30 minuti'),p('0-4 min | Leggere il mistero e le tre testimonianze. Presentare l’esperimento collettivo: lanciare due dadi, sommare e cercare una regolarità.'),p('4-7 min | Raccogliere le previsioni prima dei lanci. Non mostrare ancora la griglia delle combinazioni e non anticipare il 7.'),p('7-20 min | Lanciare, registrare e aggiornare il grafico insieme. Dopo 10 lanci salvare i conteggi e discutere brevemente. Obiettivo pratico: 60-100 lanci; se il flusso è lento, usare quelli disponibili o proseguire con il pubblico successivo.'),p('20-25 min | Compilare la griglia 6 × 6. Contare le combinazioni, distinguendo A e B. Collegare il conteggio alla forma prevista.'),p('25-30 min | Confrontare modello e osservazioni. Scrivere la conclusione citando i dati e un limite dell’indagine.'),p('Partecipazione libera: ogni coppia compie un lancio e lascia un post-it. Fare brevi restituzioni periodiche. Chi non lancia può leggere, sommare o gestire il pannello.'),p('Validità: facce superiori leggibili, dadi fermi e dentro l’area. Se un dado è inclinato o fuori area, ripetere entrambi. Stabilire la regola prima e applicarla sempre.',SMALL)])
    pages.append([title('La soluzione del caso'),p('Il modello assume due dadi equi e indipendenti. Le 36 coppie ordinate sono equiprobabili, le 11 somme no.'),matrix(True),Spacer(1,5*mm),p('Somme: 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12.\nModi: 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1.',SMALL),p('Probabilità di una somma = modi / 36.\nConteggio atteso in N lanci = N × modi / 36.',SMALL),p('In 72 lanci, i conteggi attesi sono 2, 4, 6, 8, 10, 12, 10, 8, 6, 4, 2. Sono una previsione media, non dati da inserire sul pannello.',SMALL)])
    pages.append([title('Interpretare senza forzare'),p(case['teacher_solution']),p('La conclusione sostenibile: le somme centrali sono più probabili perché si ottengono con più coppie di risultati. Non chiedere agli studenti di certificare che i dadi siano equi.'),p('Se il grafico è irregolare, conservarlo. Non rilanciare per ottenere una forma migliore. Con pochi eventi sono normali oscillazioni; più lanci non garantiscono un avvicinamento regolare a ogni passo.'),p('Per confrontare 10 lanci e il campione finale usare conteggio/N. Per approfondire, contare separatamente le sei facce di A e di B; controllare superficie, gonfiaggio e modalità di lancio. Anche questi controlli non costituiscono una certificazione.'),p('Il dado non ricorda: l’assenza recente di un risultato non lo rende “dovuto” al lancio successivo, nel modello indipendente.',SMALL)])
    pages.append([title('Domande e restituzione'),p('• Perché 1 non può essere una somma?\n• Quanti modi producono 2, 7 e 12?\n• Perché scambiare A e B può creare una coppia diversa?\n• Una somma mai uscita è impossibile?\n• Se il 7 non è la colonna più alta, il modello è smentito?\n• Quali dati raccogliereste ancora?'),p('Obiettivi: distinguere esito, somma e frequenza; registrare dati senza selezionarli; costruire un istogramma; contare coppie ordinate; distinguere probabilità teorica e frequenza osservata.'),p('Collegamento alla ricerca',H),p(case['real_world_connection']),p('Frase finale',H),p(case['educational_message'])])
    document(path,pages)

def build_poster_pdf(case,path):
    from reportlab.pdfgen import canvas
    from reportlab.platypus import KeepInFrame
    c=canvas.Canvas(str(path),pagesize=A3);w,h=A3
    c.setFillColor(BLUE);c.rect(0,0,w,h,fill=1,stroke=0)
    c.setFillColor(YELLOW);c.setFont('Helvetica-Bold',20);c.drawString(22*mm,h-28*mm,'ERNEST / CSI-004')
    ps=ParagraphStyle('poster',fontName='Helvetica-Bold',fontSize=43,leading=48,textColor=colors.white)
    text=p('I DADI NASCONDONO\nUN SEGRETO',ps);text.wrap(w-44*mm,150*mm);text.drawOn(c,22*mm,h-83*mm)
    sub=ParagraphStyle('sub',fontName='Helvetica',fontSize=20,leading=27,textColor=colors.white)
    blocks=[('QUALI SOMME USCIRANNO PIÙ SPESSO?', 'Fai una previsione, lancia i dadi e cerca la regolarità.'),('01  LANCIA', 'Lancia i due dadi giganti, A e B.'),('02  SOMMA', 'Scrivi A, B e la loro somma su un post-it.'),('03  LASCIA LA TUA PROVA', 'Attacca il post-it nella colonna della somma. Un lancio = un post-it.'),('04  INDAGA', 'Quale forma compare? Le somme hanno tutte le stesse possibilità?')]
    y=h-111*mm
    for head,body in blocks:
        c.setFillColor(YELLOW);c.setFont('Helvetica-Bold',17);c.drawString(22*mm,y,head);y-=10*mm
        q=p(body,sub);_,qh=q.wrap(w-44*mm,100*mm);q.drawOn(c,22*mm,y-qh);y-=qh+14*mm
    for dx,spots,label in [(24*mm,[(1,1),(2,2),(3,3)],'A'),(85*mm,[(1,1),(1,3),(3,1),(3,3)],'B')]:
        dy=56*mm; side=43*mm
        c.setFillColor(colors.white);c.roundRect(dx,dy,side,side,5*mm,fill=1,stroke=0)
        c.setFillColor(BLUE)
        for a,b in spots:c.circle(dx+a*side/4,dy+b*side/4,2.6*mm,fill=1,stroke=0)
        c.setFillColor(YELLOW);c.setFont('Helvetica-Bold',14);c.drawCentredString(dx+side/2,dy-7*mm,label)
    c.setFillColor(YELLOW);c.setFont('Helvetica-Bold',14);c.drawString(22*mm,26*mm,'NOTTE EUROPEA DEI RICERCATORI')
    c.setFillColor(colors.white);c.setFont('Helvetica',12);c.drawString(22*mm,18*mm,'Partecipa a un lancio o segui tutta l’indagine.')
    c.save()
