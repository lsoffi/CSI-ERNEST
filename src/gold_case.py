"""CSI-005 • Operazione oro. Run: python src/gold_case.py"""
from pathlib import Path
from argparse import ArgumentParser
from xml.sax.saxutils import escape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from pdf_builder import DossierPdf, DARK_BLUE, LIGHT_RULE, YELLOW

TITLE='Operazione oro: il segreto è nel nucleo'
ALICE='https://alice-collaboration.web.cern.ch/2025-alice-lead-to-gold'
PAPER='https://doi.org/10.1103/PhysRevC.111.054906'
class Book(DossierPdf):
    def draw_wrapped(self,text,x,y,w,size=8,leading=10,font='Helvetica'):
        if text==TITLE:
            text='Operazione oro:\nil segreto è nel nucleo';size=20;leading=23
        return super().draw_wrapped(text,x,y,w,size,leading,font)
    def page(self,title):
        self.y=self.new_page(self.case,self.kind)
        self.section(title)
    def section(self,title):
        self.y=self.section_title(title,self.x,self.y,self.w)
    def para(self,text):
        q=Paragraph(escape(text),ParagraphStyle('body',fontName='Helvetica',fontSize=9.5,leading=13,textColor=DARK_BLUE))
        _,h=q.wrap(self.w,700);self.y-=h;q.drawOn(self.c,self.x,self.y);self.y-=3*mm;self.check()
    def lines(self,n):
        for _ in range(n):
            self.y-=6*mm;self.c.setStrokeColor(LIGHT_RULE);self.c.line(self.x,self.y,self.x+self.w,self.y)
        self.y-=3*mm;self.check()
    def table(self,rows,widths):
        t=Table(rows,colWidths=[self.w*w for w in widths],rowHeights=[9*mm]*len(rows))
        t.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'Helvetica',8),('FONT',(0,0),(-1,0),'Helvetica-Bold',8),('BACKGROUND',(0,0),(-1,0),YELLOW),('TEXTCOLOR',(0,0),(-1,-1),DARK_BLUE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),.5,LIGHT_RULE)]))
        _,h=t.wrap(self.w,700);self.y-=h;t.drawOn(self.c,self.x,self.y);self.y-=4*mm;self.check()
    def check(self):
        if self.y<19*mm: raise ValueError(f'Overflow page {self.page_number}')
    def link(self,label,url):
        self.c.setFillColor(DARK_BLUE);self.c.setFont('Helvetica-Bold',9);self.c.drawString(self.x,self.y,label);self.c.linkURL(url,(self.x,self.y-2,self.x+self.w,self.y+10));self.y-=7*mm

def student(b):
    b.page('Aprire il caso')
    b.para('La sfera sul banco rappresenta un solo nucleo: piombo-208. Contiene 82 palline verdi (protoni) e 126 rosse (neutroni). Il contenitore serve solo a tenerle insieme. La sfida: ottenere un nucleo di oro togliendo il minor numero possibile di palline. Per ora non aprire la sfera.')
    b.section('Primo indizio • La tavola periodica')
    b.para('Cerca piombo e oro. Per ciascuno annota simbolo e numero atomico Z: è il numero di protoni. Non confonderlo con il valore, spesso decimale, della massa atomica indicata nella casella.')
    b.table([['Elemento','Simbolo','Numero atomico Z'],['Piombo','',''],['Oro','','']],[.34,.23,.43])
    b.para('Quale conteggio deve cambiare? Scrivi il colore e il numero di palline che toglieresti. Prevedi quale casella della tavola corrisponderà al nucleo rimasto.')
    b.lines(3)
    b.page('Mettere alla prova la previsione')
    b.para('Spiega la tua previsione a chi lavora con te. Ora togli le palline scelte e lasciale bene in vista accanto alla sfera. Per trovare quante ne restano, sottrai quelle sul banco dai conteggi iniziali.')
    b.table([['Nel modello','Protoni','Neutroni','Totale'],['Prima','82','126','208'],['Tolti','','',''],['Rimasti','','','']],[.34,.22,.24,.20])
    b.para('Cerca sulla tavola il numero atomico del nucleo rimasto. Che elemento hai ottenuto? Come lo sai? Se non è oro, rimetti le palline nella sfera e modifica la previsione.')
    b.lines(3)
    b.section('Una prova che potrebbe smentirti')
    b.para('Ripristina il piombo iniziale. Togli lo stesso numero di palline, ma questa volta tutte rosse. Il totale finale è uguale a quello di prima: anche l’elemento è lo stesso? Verifica con Z.')
    b.lines(3)
    b.page('Chiudere il caso')
    b.para('Una persona sostiene: «Basta togliere il numero giusto di palline; il colore non conta». Rispondi usando i due risultati. Indica quale numero identifica l’elemento e quale conta tutte le particelle del nucleo.')
    b.lines(4)
    b.section('Dopo la prova • La traccia al CERN')
    b.para('All’LHC due nuclei di piombo possono passare vicinissimi senza urtarsi frontalmente. L’interazione elettromagnetica può far espellere protoni e neutroni. L’esperimento ALICE ha contato le particelle emesse: anche senza raccogliere il nucleo rimasto, il numero di protoni mancanti permette di identificarne l’elemento.')
    b.para('Immagina un segnale con tre protoni e due neutroni emessi da piombo-208. Quanti protoni e neutroni restano? Qual è il nuovo numero di massa? Che cosa ha in comune questo caso con la tua prima prova, e che cosa cambia?')
    b.lines(3)
    b.para('Ultima domanda: perché il risultato riguarda nuclei di oro e non una pepita?')
    b.lines(2)

def teacher(b):
    b.page('Preparare una sola postazione')
    b.para('Obiettivo: identificare un elemento dal numero di protoni e distinguere questo numero dal totale di protoni e neutroni. Il gruppo deve giustificare la scelta con due prove, non indovinare un colore.')
    b.para('Materiali: una sfera trasparente apribile e stabile, 82 palline verdi, 126 rosse, una tavola periodica stampata con simboli e numeri atomici, matite e dossier. Preparare in anticipo il piombo-208. Contrassegnare i colori anche con P e N, oppure usare segni tattili. Prevedere un punto del banco dove le palline tolte non rotolino.')
    b.para('Il guscio non è il confine fisico del nucleo. Le palline rappresentano nucleoni, non elettroni né atomi interi. I colori sono convenzioni del modello.')
    b.section('Due modalità')
    b.para('In classe: 25 minuti. Dedicarne 5 a scenario e previsione, 8 alla prima prova, 5 al confronto con soli neutroni e 7 alla restituzione su ALICE. A turno una persona cerca sulla tavola, una manipola, una verifica i conti; scambiare i ruoli nella seconda prova.')
    b.para('Alla Notte della ricerca: 5–7 minuti, senza carte. Dare la tavola e porre la sfida a voce. Prima dell’apertura chiedere una previsione; far eseguire la prova minima e discutere oralmente il controesempio. Mostrare il risultato del poster e raccontare ALICE soltanto dopo la scoperta. Ripristinare 82 verdi e 126 rosse per il gruppo successivo.')
    b.page('Guidare la scoperta')
    b.para('Avvio: «Ti affido un nucleo di piombo. Puoi togliere palline ma non aggiungerle. Come saprai di avere oro prima che te lo dica io?» Lasciare che il gruppo cerchi entrambi gli elementi; non indicare subito le caselle.')
    b.section('Se il gruppo si blocca')
    b.para('1. Se guarda il peso atomico: «Quale numero intero distingue una casella dalla successiva?» 2. Se sa che il totale deve diminuire: «Quale dei due colori conta per scegliere la casella?» 3. Se propone di togliere palline di entrambi i colori: «Potresti ottenere lo stesso elemento togliendone meno?»')
    b.para('Accogliere una proposta non minima: togliere tre verdi e anche alcune rosse può dare comunque oro. Chiedere quali rimozioni sono necessarie per cambiare elemento e quali modificano soltanto l’isotopo. Poi ripristinare il nucleo iniziale.')
    b.section('Che cosa osservare')
    b.para('La prova è conclusa quando il gruppo mostra le palline estratte, ricava il numero di protoni rimasti e ritrova l’elemento sulla tavola. Non basta dire «è oro perché ho tolto tre palline». Il confronto con tre rosse obbliga a precisare il ragionamento.')
    b.page('Soluzioni • Il registro dei nuclei')
    b.para('Z = numero di protoni; N = numero di neutroni; A = Z + N, il numero di massa di un singolo nucleo. Il numero decimale riportato per un elemento in molte tavole non è A.')
    b.table([['Prova da Pb-208','Z','N','A','Esito'],['Inizio','82','126','208','Pb-208'],['Tolti 3 protoni','79','126','205','Au-205'],['Tolti 3 neutroni','82','123','205','Pb-205'],['Tolti 3 p + 2 n','79','124','203','Au-203']],[.35,.11,.12,.12,.30])
    b.para('Prova minima: da 82 a 79 occorre togliere tre protoni, quindi tre palline verdi. Nessuna pallina rossa deve essere rimossa per soddisfare il solo criterio di identità. Con tre rosse si ottiene ancora piombo. I due risultati hanno entrambi A = 205, ma Z diversi: non sono lo stesso elemento.')
    b.para('Nel caso finale Au-203 ha gli stessi 79 protoni di Au-205, ma due neutroni in meno. Sono isotopi dello stesso elemento. Dire «oro» identifica Z; non implica che il nucleo sia stabile o che sia stato prodotto oro metallico.')
    b.section('Verifica individuale')
    b.para('Da Pb-208 tolgo un protone e due neutroni. «È oro, perché mancano tre palline»: vero o falso? Risposta: falso. Restano 81 protoni e 124 neutroni; la tavola identifica tallio-205. Valutare separatamente la lettura di Z, il bilancio dei nucleoni e la giustificazione.')
    b.page('Dal modello alla misura di ALICE')
    b.para('Solo dopo il verdetto, chiedere: «Se non potessimo aprire la sfera e guardare dentro, quali particelle dovremmo contare all’uscita?» È il passaggio dal modello alla misura indiretta.')
    b.para('In incontri ultraperiferici all’LHC i nuclei di piombo passano molto vicini. Il campo elettromagnetico di uno può eccitare l’altro, che emette nucleoni. I calorimetri a zero gradi di ALICE hanno misurato canali con zero, uno, due o tre protoni emessi insieme ad almeno un neutrone. Per il canale con tre protoni, il nucleo residuo ha Z = 79: oro.')
    b.para('Il modello con tre sole palline verdi dà la trasformazione minima. Non riproduce il meccanismo né la distribuzione degli isotopi prodotti. L’esempio con due neutroni emessi illustra un esito possibile, non un numero fisso per ogni evento. Non è fissione in due grandi frammenti. Non si raccolgono pepite: i nuclei prodotti continuano a viaggiare e possono frammentarsi quando incontrano il materiale dell’acceleratore.')
    b.section('Fonti per il debriefing')
    b.para('ALICE Collaboration, risultato divulgativo (2025) e articolo sperimentale in Physical Review C 111, 054906. Collegamenti attivi:')
    b.link('Leggi la spiegazione di ALICE',ALICE)
    b.link('Articolo scientifico • DOI 10.1103/PhysRevC.111.054906',PAPER)

def generate(root,out):
    out.mkdir(parents=True,exist_ok=True)
    for method,role,suffix in [(student,'Scheda studenti','student'),(teacher,'Guida docente','teacher-guide')]:
        f=out/f'csi-005-operazione-oro-{suffix}.pdf';b=Book(f,root/'assets/ERNEST-logo.svg');b.kind=role;b.x,b.w=b.content_bounds()
        b.case={'case_id':'CSI-005','title':TITLE,'mystery':'Davanti a te c’è una sfera piena di palline: è un modello di nucleo di piombo. La sfida è trasformarlo in oro togliendo alcune palline. Quali? La tavola periodica custodisce l’indizio decisivo.','story_intro':role+' • '+('Prima di aprire la sfera, scegli una trasformazione e prevedi quale elemento resterà. Poi cerca una prova che distingua la tua spiegazione da una semplice coincidenza.' if suffix=='student' else 'Preparazione della postazione, conduzione dell’indagine, soluzioni e collegamento con la misura di ALICE.')};b.c.setTitle('CSI-005 | '+TITLE+' | '+role);b.cover(b.case);method(b);b.save()
if __name__=='__main__':
    a=ArgumentParser();a.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a.add_argument('--output',type=Path);v=a.parse_args();generate(v.root,v.output or v.root/'output')
