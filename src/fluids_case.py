"""Generate the CSI-007 fluids package using the shared ERNEST visual system."""
from pathlib import Path
import argparse
import json
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, A5
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, PageBreak
from reportlab.pdfgen import canvas
from transport_case import p, Section, Rule, BODY, SMALL, BLUE, YELLOW
from pdf_builder import DossierPdf

ROOT = Path(__file__).resolve().parents[1]

def render(case, path, kind):
    def frame(c, doc):
        obj = DossierPdf.__new__(DossierPdf)
        obj.c, obj.logo_path, obj.page_number = c, ROOT/'assets/ERNEST-logo.svg', doc.page + 1
        obj.page_frame()
        obj.footer_mark(case)
        # Keep the case identifier distinct from the long header strapline.
        obj.draw_logo(18*mm, 191*mm, 31*mm, 14*mm)
        c.setFillColor(BLUE)
        c.setFont('Helvetica-Bold', 7)
        c.drawString(54*mm, 201*mm, 'CLASSROOM SCIENCE INVESTIGATION')
        c.setFont('Helvetica-Bold', 11)
        c.drawString(54*mm, 194*mm, 'Scheda studenti' if kind == 'student' else 'Guida docente')
        c.setFont('Helvetica', 7)
        c.drawRightString(130*mm, 188*mm, f"CSI-007 | pag. {doc.page + 1}")
        c.setStrokeColor(YELLOW)
        c.line(18*mm,186*mm,130*mm,186*mm)
    story=[]
    items=case[kind][2:] if kind=='student' else case[kind]
    for item in items:
        typ=item['type']; text=item.get('text','')
        if typ=='break': story.append(PageBreak())
        elif typ=='heading': story.append(Section(text))
        elif typ=='table':
            rows=[[p(str(cell),SMALL) for cell in row] for row in item['rows']]
            widths=[112*mm*.44,112*mm*.28,112*mm*.28]
            tb=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),YELLOW),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D8D8E6')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
            story.extend([tb,Spacer(1,3*mm)])
        elif text and set(text)=={'_'}:
            rule=Rule(); rule.height=6*mm; story.append(rule)
        else: story.append(p(text,BODY))
    doc=SimpleDocTemplate(str(path),pagesize=A5,leftMargin=18*mm,rightMargin=18*mm,topMargin=32*mm,bottomMargin=25*mm)
    doc.build(story,onFirstPage=frame,onLaterPages=frame)
    import tempfile
    from pypdf import PdfReader, PdfWriter
    with tempfile.TemporaryDirectory() as td:
        cp=Path(td)/'cover.pdf'
        cover=DossierPdf(cp,ROOT/'assets/ERNEST-logo.svg')
        cc=dict(case)
        cc['mystery']=case['mystery']
        cover.cover(cc)
        cover.save()
        writer=PdfWriter()
        for source in [cp,path]:
            for pg in PdfReader(source).pages: writer.add_page(pg)
        writer.add_metadata({'/Title':f"CSI-007 - {case['title']} - {kind}",'/Author':'ERNEST'})
        with path.open('wb') as f: writer.write(f)

def poster(case,path):
    c=canvas.Canvas(str(path),pagesize=A3)
    w,h=A3
    c.setTitle('CSI-007 - Il livello fa la differenza')
    c.setFillColor(colors.HexColor('#FFFBED'));c.rect(0,0,w,h,fill=1,stroke=0)
    c.drawImage(str(ROOT/'assets/ERNEST-logo-transparent.png'),22*mm,h-42*mm,width=62*mm,height=25*mm,preserveAspectRatio=True,mask='auto')
    def text(txt,y,size,bold=False):
        st=ParagraphStyle('poster',fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=size*1.25,textColor=BLUE)
        pp=p(txt,st);_,height=pp.wrap(w-44*mm,h);pp.drawOn(c,22*mm,y-height)
        return y-height-6*mm
    y=text('CSI-007 | Classroom Science Investigation',h-49*mm,18,True)
    y=text(case['title'],y,34,True)
    y=text('Fluidi, pressione e portata\nCorso di Studi in Infermieristica - Fisica Applicata',y,17)
    for title,body in case['poster']:
        y=text(title,y,18,True);y=text(body,y,15)
    assert y>25*mm, y
    c.drawImage(str(ROOT/'assets/eu-funded-logo.png'),22*mm,7*mm,width=48*mm,height=13*mm,preserveAspectRatio=True,mask='auto')
    c.save()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',default=str(ROOT/'data/csi007.json'))
    parser.add_argument('--output',default=str(ROOT/'output'))
    args=parser.parse_args()
    case=json.loads(Path(args.input).read_text()); out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    for kind,suffix in [('student','student'),('teacher','teacher-guide')]:
        path=out/f'csi-007-il-livello-fa-la-differenza-{suffix}.pdf'
        render(case,path,kind);print(path)
    poster(case,out/'csi-007-poster-a3.pdf')
if __name__=='__main__': main()
