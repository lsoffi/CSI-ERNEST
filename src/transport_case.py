"""CSI-005: package for nursing students, using the repository A5 dossier frame."""
from pathlib import Path
import json,sys
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5,A3
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Flowable,KeepTogether
from reportlab.graphics.shapes import Drawing,Line,String
BLUE=colors.HexColor('#1F2041');YELLOW=colors.HexColor('#FFE548')
BODY=ParagraphStyle('body',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=6,textColor=BLUE)
HEAD=ParagraphStyle('head',parent=BODY,fontName='Helvetica-Bold',fontSize=14,leading=17,spaceAfter=9,keepWithNext=True)
SMALL=ParagraphStyle('small',parent=BODY,fontSize=7.8,leading=10)
def p(t,style=BODY):return Paragraph(escape(t).replace('\n','<br/>'),style)
class Section(Flowable):
 def __init__(self,text):
  super().__init__();self.text=text;self.width=112*mm;self.height=13*mm;self.keepWithNext=True
 def draw(self):
  c=self.canv;c.setFillColor(colors.HexColor('#2B2E63'));c.roundRect(0,3*mm,self.width,9*mm,1.5*mm,fill=1,stroke=0)
  c.setFillColor(YELLOW);c.circle(2*mm,7.5*mm,.9*mm,fill=1,stroke=0)
  st=ParagraphStyle('section',fontName='Helvetica-Bold',fontSize=8.5,leading=10,textColor=colors.white)
  q=p(self.text.upper(),st);_,h=q.wrap(self.width-8*mm,9*mm);q.drawOn(c,5*mm,7.5*mm-h/2)
class Rule(Flowable):
 def __init__(self):super().__init__();self.width=112*mm;self.height=7*mm
 def draw(self):self.canv.setStrokeColor(colors.HexColor('#D8D8E6'));self.canv.line(0,0,self.width,0)
def chart(solved):
 d=Drawing(310,220)
 for i in range(11):
  x=30+26*i;d.add(Line(x,25,x,190,strokeColor=colors.lightgrey));d.add(String(x,12,str(i),fontSize=7,textAnchor='middle'))
 for i in range(16):
  y=25+11*i;d.add(Line(30,y,290,y,strokeColor=colors.lightgrey));d.add(String(25,y-2,f'{i/10:.1f}',fontSize=6,textAnchor='end'))
 d.add(String(30,205,'Velocità (m/s)',fontSize=9));d.add(String(235,0,'Tempo (s)',fontSize=9))
 if solved:
  for pts,col,lab in [([(0,0),(3,1.2),(10,1.2)],BLUE,'A'),([(0,0),(5,1.25),(10,1.25)],colors.HexColor('#BA5B15'),'B')]:
   for (x,y),(xx,yy) in zip(pts,pts[1:]):d.add(Line(30+x*26,25+y*110,30+xx*26,25+yy*110,strokeColor=col,strokeWidth=1.5))
   d.add(String(295,25+pts[-1][1]*110+(5 if lab=='B' else -6),lab,fontSize=8,fillColor=col))
 return d
def full_chart(solved):
 d=Drawing(310,220)
 for i in range(13):
  x=30+i*21;d.add(Line(x,25,x,190,strokeColor=colors.lightgrey))
  if solved:d.add(String(x,12,str(i*5),fontSize=7,textAnchor='middle'))
 for i in range(16):
  y=25+i*11;d.add(Line(30,y,282,y,strokeColor=colors.lightgrey))
  if solved:d.add(String(25,y-2,f'{i/10:.1f}',fontSize=6,textAnchor='end'))
 d.add(Line(30,25,292,25,strokeColor=BLUE));d.add(Line(30,25,30,198,strokeColor=BLUE))
 if solved:
  d.add(String(30,205,'Velocità (m/s)',fontSize=9));d.add(String(235,0,'Tempo (s)',fontSize=9))
  for pts,col in [([(0,0),(3,1.2),(54.1667,1.2),(57.1667,0)],BLUE), ([(0,0),(5,1.25),(52,1.25),(57,0)],colors.HexColor('#BA5B15'))]:
   for (x,y),(xx,yy) in zip(pts,pts[1:]):d.add(Line(30+x*4.2,25+y*110,30+xx*4.2,25+yy*110,strokeColor=col,strokeWidth=1.5))
  d.add(String(90,175,'A: blu    B: arancione',fontSize=8))
 return d
def render(case,path,kind,root):
 sys.path.insert(0,str(root/'src'));from pdf_builder import DossierPdf
 def frame(c,doc):
  obj=DossierPdf.__new__(DossierPdf);obj.c=c;obj.logo_path=root/'assets/ERNEST-logo.svg';obj.page_number=doc.page+(1 if kind=='student' else 0)
  obj.page_frame();obj.footer_mark(case);obj.header(case,'Scheda studenti' if kind=='student' else 'Guida docente')
 story=[]
 for idx,item in enumerate(case[kind]):
  if kind=='student' and idx<2:continue
  t=item.get('text','')
  if item['type']=='break':story.append(PageBreak()) if kind=='student' else story.append(Spacer(1,4*mm))
  elif item['type']=='chart_full':story.append(full_chart(item['solved']))
  elif item['type']=='chart':story.append(chart(item['solved']))
  elif item['type']=='table':
   rows=[[p(c,SMALL) for c in row] for row in item['rows']];n=len(rows[0]);width=112*mm
   widths=([width*.44,width*.28,width*.28] if n==3 else [width/n]*n)
   tb=Table(rows,colWidths=widths,repeatRows=1,splitByRow=0,minRowHeights=[8*mm]*len(rows))
   tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),YELLOW),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D8D8E6')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.extend([tb,Spacer(1,3*mm)])
  elif t and set(t)=={'_'}:story.append(Rule())
  else:
   # Long writing lines wrap poorly on A5; retain short prompts and add ruled space.
   if '_' in t:
    import re
    t=re.sub(r'_{20,}', '_________________', t)
   story.append(Section(t) if item['type']=='heading' else p(t,BODY))
 doc=SimpleDocTemplate(str(path),pagesize=A5,leftMargin=18*mm,rightMargin=18*mm,topMargin=35*mm,bottomMargin=30*mm)
 doc.build(story,onFirstPage=frame,onLaterPages=frame)
 if kind=='student':
  import tempfile
  from pypdf import PdfReader,PdfWriter
  class Cover(DossierPdf):
   def cover_mystery(self,case,x,y,w,h):
    y+=10*mm;h=90*mm
    self.box(x,y,w,h)
    self.c.setFillColor(BLUE);self.c.setFont('Helvetica-Bold',9);self.c.drawString(x+3*mm,y-5*mm,'Scenario')
    st=ParagraphStyle('covertext',fontName='Helvetica',fontSize=7.7,leading=8.9,textColor=BLUE)
    text=case['mystery']+'\n\n'+case['story_intro']
    q=p(text,st);_,hh=q.wrap(w-6*mm,h)
    while hh>h-15*mm:
     st.fontSize-=.1;st.leading-=.1;q=p(text,st);_,hh=q.wrap(w-6*mm,h)
    q.drawOn(self.c,x+3*mm,y-12*mm-hh)
    return y-h
   def field_box(self,*args):pass
  with tempfile.TemporaryDirectory() as td:
   coverpath=Path(td)/'cover.pdf';cover=Cover(coverpath,root/'assets/ERNEST-logo.svg');cover.cover(case);cover.save()
   writer=PdfWriter()
   for source in [coverpath,path]:
    for page in PdfReader(str(source)).pages:writer.add_page(page)
   with open(path,'wb') as f:writer.write(f)
def poster(case,path,root):
 from reportlab.pdfgen import canvas
 c=canvas.Canvas(str(path),pagesize=A3);w,h=A3
 c.setFillColor(colors.HexColor('#FFFBED'));c.rect(0,0,w,h,fill=1,stroke=0)
 def text(t,y,size=20,bold=False):
  st=ParagraphStyle('poster',fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=size*1.25,textColor=BLUE)
  pp=p(t,st);_,hh=pp.wrap(w-44*mm,h);pp.drawOn(c,22*mm,y-hh);return y-hh-10*mm
 y=h-22*mm
 y=text('CSI-005 | Classroom Science Investigation',y,19,True)
 y=text('Trasporto del paziente\ne studio del movimento',y,34,True)
 y=text('Indagine per studenti di infermieristica',y,18)
 for title,body in [('Scenario','Un paziente riferisce nausea durante gli spostamenti. Il percorso verso la sala esami misura circa 100 passi. A accompagna il paziente alla sala esami, B lo riporta nella stanza. Chi rispetta la regola?'),('Il banco di indagine','Metro da 5 m, fogli a quadretti, matite, righello e calcolatrice. Gruppi fino a 10 persone. Lavoro su carta e brevi misure del passo; nessuna prova di trasporto su persone.'),('La missione','Misurate cinque passi per persona, tre volte. Stimate il percorso. Confrontate velocità e accelerazioni, disegnate i primi 10 secondi e il moto completo. Individuate chi rispetta la regola.'),('Gli indizi','A: da fermo a 72 m/min in 3 s; frenata in 3 s.\nB: da fermo a 4,5 km/h in 5 s; frenata in 5 s.\nTra le due fasi, velocità costante. Le variazioni sono uniformi.'),('La regola del caso','Accelerazione in valore assoluto non superiore a 0,30 m/s². È una soglia inventata per il gioco, non un limite clinico.'),('La domanda finale','Si può essere in movimento con accelerazione nulla? La risposta deve essere sostenuta dalle vostre prove.')]:
  y=text(title,y,18,True);y=text(body,y,15)
 assert y>25*mm,y
 c.drawImage(str(root/'assets/eu-funded-logo.png'),22*mm,7*mm,width=48*mm,height=13*mm,preserveAspectRatio=True,mask='auto');c.save()
def generate(input_path,output,root):
 case=json.loads(Path(input_path).read_text());out=Path(output);out.mkdir(parents=True,exist_ok=True)
 for kind,suffix in [('student','student'),('teacher','teacher-guide')]:render(case,out/f'csi-005-trasporto-del-paziente-{suffix}.pdf',kind,Path(root))
 poster(case,out/'csi-005-poster-a3.pdf',Path(root))
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--input',required=True);a.add_argument('--output',required=True);a.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));v=a.parse_args();generate(v.input,v.output,v.root)
