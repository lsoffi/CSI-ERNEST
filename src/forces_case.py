"""Generate the CSI-009 forces package using the shared ERNEST visual system."""
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
from pdf_builder import DossierPdf, UNICODE_FONT
from xml.sax.saxutils import escape
from reportlab.platypus import Paragraph

BODY = ParagraphStyle('ramps_body', parent=BODY, fontSize=8.7, leading=11.3, spaceAfter=5)

def p(text, style=None):
    content = escape(text).replace('\n', '<br/>')
    for char in ('Δ', 'θ', 'μ'):
        content = content.replace(char, f'<font name="{UNICODE_FONT}">{char}</font>')
    return Paragraph(content, style or BODY)

ROOT = Path(__file__).resolve().parents[1]

from reportlab.graphics.shapes import Drawing, Line, String, Rect, Polygon

def visual(item):
    width=112*mm
    typ=item['type']
    if typ=='sketch':
        height=item.get('height',42)*mm
        d=Drawing(width,height)
        for i in range(0,113,5): d.add(Line(i*mm,0,i*mm,height,strokeColor=colors.HexColor('#E6E6EE'),strokeWidth=.3))
        for j in range(0,item.get('height',42)+1,5):d.add(Line(0,j*mm,width,j*mm,strokeColor=colors.HexColor('#E6E6EE'),strokeWidth=.3))
        return d
    if typ=='ramps':
        d=Drawing(width,43*mm)
        for x,base,label in [(8,30,'Corta'),(48,60,'Lunga')]:
            xx=x*mm;b=base*mm;y=9*mm;hh=21*mm
            d.add(Polygon([xx,y,xx+b,y,xx+b,y+hh],strokeColor=BLUE,fillColor=colors.HexColor('#FFF5B0'),strokeWidth=1))
            d.add(String(xx+b/2,y-4*mm,label,fontName='Helvetica',fontSize=8,textAnchor='middle',fillColor=BLUE))
            d.add(String(xx+b+2*mm,y+hh/2,'h',fontSize=8,fillColor=BLUE))
            d.add(String(xx+b/2,y+hh/2+3*mm,'s',fontSize=8,fillColor=BLUE))
        d.add(String(0,38*mm,'Stesso dislivello, lunghezze diverse (schema non in scala)',fontSize=7,fillColor=BLUE))
        return d
    d=Drawing(width,46*mm)
    d.add(String(0,41*mm,item['label'],fontName='Helvetica-Bold',fontSize=8,fillColor=BLUE))
    left=16*mm;bottom=9*mm;right=108*mm;top=35*mm
    for j in range(6):
        y=bottom+(top-bottom)*j/5
        d.add(Line(left,y,right,y,strokeColor=colors.HexColor('#D8D8E6'),strokeWidth=.4))
        d.add(Line(left-3*mm,y,left-1*mm,y,strokeColor=BLUE,strokeWidth=.5))
    d.add(Line(left,bottom,right,bottom,strokeColor=BLUE))
    d.add(Line(left,bottom,left,top,strokeColor=BLUE))
    for i,label in enumerate(['V','C','L']):
        x=left+(i+.5)*(right-left)/3
        d.add(String(x,bottom-5*mm,label,textAnchor='middle',fontSize=8,fillColor=BLUE))
    return d

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
        c.drawRightString(130*mm, 188*mm, f"CSI-009 | pag. {doc.page + 1}")
        c.setStrokeColor(YELLOW)
        c.line(18*mm,186*mm,130*mm,186*mm)
    story=[]
    items=case[kind]
    for item in items:
        typ=item['type']; text=item.get('text','')
        if typ=='break': story.append(PageBreak())
        elif typ=='heading': story.append(Section(text))
        elif typ in ('sketch','ramps','bar_grid'): story.append(visual(item))
        elif typ=='table':
            rows=[[p(str(cell),SMALL) for cell in row] for row in item['rows']]
            widths=[112*mm*w for w in item.get('widths',[.44,.28,.28])]
            tb=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),YELLOW),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D8D8E6')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            story.extend([tb,Spacer(1,3*mm)])
        elif text and set(text)=={'_'}:
            rule=Rule(); rule.height=5.5*mm; story.append(rule)
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
        if kind=='teacher': cc['story_intro']='Guida docente • Preparazione del banco, risultati attesi, esempi numerici e criteri per la discussione.'
        cover.cover(cc)
        cover.save()
        writer=PdfWriter()
        for source in [cp,path]:
            for pg in PdfReader(source).pages: writer.add_page(pg)
        writer.add_metadata({'/Title':f"CSI-009 - {case['title']} - {kind}",'/Author':'ERNEST'})
        with path.open('wb') as f: writer.write(f)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',default=str(ROOT/'data/csi009.json'))
    parser.add_argument('--output',default=str(ROOT/'output'))
    args=parser.parse_args(); case=json.loads(Path(args.input).read_text())
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    for k,f in [('student','student'),('teacher','teacher-guide')]:
        render(case,out/f'csi-009-una-scatola-da-sistemare-{f}.pdf',k)
