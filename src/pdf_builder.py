from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
except Exception:  # pragma: no cover - optional dependency fallback
    svg2rlg = None
    renderPDF = None


DARK_BLUE = colors.HexColor("#1F2041")
SECONDARY_BLUE = colors.HexColor("#2B2E63")
CREAM = colors.HexColor("#FFFFFF")
YELLOW = colors.HexColor("#FFE548")
ORANGE = colors.HexColor("#FFB300")
INK = colors.HexColor("#222222")
LIGHT_RULE = colors.HexColor("#D8D8E6")

PAGE_W, PAGE_H = A5
MARGIN = 12 * mm
FRAME_X = MARGIN
FRAME_BOTTOM = 17 * mm
FRAME_TOP_GAP = 5 * mm
FRAME_W = PAGE_W - 2 * FRAME_X
FRAME_H = PAGE_H - FRAME_BOTTOM - FRAME_TOP_GAP
CONTENT_PAD = 6 * mm
CONTENT_X = FRAME_X + CONTENT_PAD
CONTENT_W = FRAME_W - 2 * CONTENT_PAD
UNICODE_FONT = "DejaVuSansERNEST"

try:
    pdfmetrics.registerFont(TTFont(UNICODE_FONT, "/Users/ls/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/fonts/DejaVuSans.ttf"))
except Exception:  # pragma: no cover - fallback for systems without bundled font
    UNICODE_FONT = "Helvetica"


class DossierPdf:
    def __init__(self, path: Path, logo_path: Path | None = None):
        self.path = path
        self.logo_path = logo_path
        self.c = canvas.Canvas(str(path), pagesize=A5)
        self.page_number = 0

    def save(self) -> None:
        self.c.save()

    def new_page(self, case: dict[str, str], title: str, show_header: bool = True) -> float:
        if self.page_number:
            self.c.showPage()
        self.page_number += 1
        self.c.setFillColor(colors.white)
        self.c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        self.page_frame()
        self.footer_mark(case)
        if show_header:
            self.header(case, title)
            return PAGE_H - 34 * mm
        return PAGE_H - MARGIN

    def page_frame(self) -> None:
        self.c.setStrokeColor(DARK_BLUE)
        self.c.setLineWidth(1.2)
        self.c.rect(FRAME_X, FRAME_BOTTOM, FRAME_W, FRAME_H, stroke=1, fill=0)

    def content_bounds(self) -> tuple[float, float]:
        return CONTENT_X, CONTENT_W

    def header(self, case: dict[str, str], title: str) -> None:
        self.c.setFillColor(colors.white)
        self.c.rect(CONTENT_X, PAGE_H - 24 * mm, CONTENT_W, 17 * mm, stroke=0, fill=1)
        self.draw_logo(CONTENT_X, PAGE_H - 19 * mm, 31 * mm, 14 * mm)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawString(CONTENT_X + 36 * mm, PAGE_H - 9 * mm, "CLASSROOM SCIENCE INVESTIGATION")
        self.c.setFont("Helvetica-Bold", 12.5)
        self.c.drawString(CONTENT_X + 36 * mm, PAGE_H - 16 * mm, title)
        self.c.setFont("Helvetica", 7.5)
        self.c.drawRightString(CONTENT_X + CONTENT_W, PAGE_H - 9 * mm, case["case_id"])
        self.c.drawRightString(CONTENT_X + CONTENT_W, PAGE_H - 16 * mm, f"pag. {self.page_number}")
        self.c.setStrokeColor(YELLOW)
        self.c.setLineWidth(1.4)
        self.c.line(CONTENT_X, PAGE_H - 24 * mm, CONTENT_X + CONTENT_W, PAGE_H - 24 * mm)

    def cover(self, case: dict[str, str]) -> None:
        self.new_page(case, "Classroom Science Investigation", show_header=False)
        self.cover_watermark()
        self.page_frame()
        self.footer_mark(case)
        top_y = PAGE_H - 18 * mm
        self.draw_logo(MARGIN + 8 * mm, top_y - 10 * mm, 42 * mm, 19 * mm)
        self.c.setFillColor(DARK_BLUE)
        right_x = PAGE_W - MARGIN - 8 * mm
        self.c.setFont("Helvetica-Bold", 8.2)
        self.c.drawRightString(right_x, top_y - 1 * mm, "CLASSROOM SCIENCE INVESTIGATION")
        self.c.setFont("Helvetica", 6.2)
        self.c.drawRightString(right_x, top_y - 7 * mm, "What if the classroom became a crime lab?")
        self.c.setStrokeColor(ORANGE)
        self.c.setLineWidth(1)
        self.c.line(MARGIN + 8 * mm, PAGE_H - 39 * mm, PAGE_W - MARGIN - 8 * mm, PAGE_H - 39 * mm)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 18)
        self.c.drawString(MARGIN + 8 * mm, PAGE_H - 51 * mm, "CASE FILE")
        self.stamp(case["case_id"], PAGE_W - MARGIN - 43 * mm, PAGE_H - 52 * mm, 34 * mm, 10 * mm)
        self.c.setFont("Helvetica-Bold", 8.5)
        self.c.drawString(MARGIN + 8 * mm, PAGE_H - 59 * mm, "CSI = Classroom Science Investigation")
        self.c.setFont("Helvetica", 7.2)
        self.draw_wrapped(
            "Indagine scientifica in classe: osservare, ipotizzare, testare, analizzare, concludere.",
            MARGIN + 8 * mm,
            PAGE_H - 65 * mm,
            PAGE_W - 50 * mm,
            7.2,
            8.5,
        )
        self.c.setFont("Helvetica-Bold", 24)
        self.draw_wrapped(case["title"], MARGIN + 8 * mm, PAGE_H - 82 * mm, PAGE_W - 38 * mm, 24, 26, "Helvetica-Bold")
        y = PAGE_H - 102 * mm
        self.cover_mystery(case, MARGIN + 8 * mm, y, PAGE_W - 40 * mm, 70 * mm)
        self.field_box("Nome partecipante/i", MARGIN + 8 * mm, 30 * mm, PAGE_W - 40 * mm, 8 * mm)
        self.footer_mark(case)

    def draw_logo(self, x: float, y: float, w: float, h: float) -> None:
        logo_image = self.logo_image_path()
        if logo_image:
            self.c.drawImage(str(logo_image), x, y, width=w, height=h, preserveAspectRatio=True, mask="auto")
            return
        if self.logo_path and self.logo_path.exists() and self.logo_path.suffix.lower() == ".svg" and svg2rlg:
            drawing = svg2rlg(str(self.logo_path))
            if drawing:
                scale = min(w / drawing.width, h / drawing.height)
                drawing.scale(scale, scale)
                renderPDF.draw(drawing, self.c, x, y)
                return
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 18)
        self.c.drawString(x, y + 4 * mm, "ERNEST")
        self.c.setFillColor(ORANGE)
        self.c.setFont("Helvetica-Bold", 6)
        self.c.drawString(x, y, "QUANTUM CAT SCIENCE TEAM")

    def watermark(self) -> None:
        if not self.logo_path:
            return
        watermark_path = self.logo_path.with_name("ERNEST-watermark.png")
        if not watermark_path.exists():
            return
        self.c.drawImage(
            str(watermark_path),
            PAGE_W / 2 - 55 * mm,
            PAGE_H / 2 - 55 * mm,
            width=110 * mm,
            height=110 * mm,
            preserveAspectRatio=True,
            mask="auto",
        )

    def cover_watermark(self) -> None:
        if not self.logo_path:
            return
        watermark_path = self.logo_path.with_name("ERNEST-watermark.png")
        if not watermark_path.exists():
            return
        self.c.drawImage(
            str(watermark_path),
            PAGE_W / 2 - 43 * mm,
            29 * mm,
            width=86 * mm,
            height=86 * mm,
            preserveAspectRatio=True,
            mask="auto",
        )

    def cover_mystery(self, case: dict[str, str], x: float, y: float, w: float, h: float) -> float:
        self.box(x, y, w, h)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 9)
        self.c.drawString(x + 3 * mm, y - 5 * mm, "Scenario")
        body = f"{case['mystery']}\n\n{case['story_intro']}"
        self.draw_wrapped(body, x + 3 * mm, y - 12 * mm, w - 6 * mm, 7.7, 8.9)
        return y - h - 4 * mm

    def cover_image(self, case: dict[str, str], x: float, y: float, w: float, h: float) -> float:
        self.c.setStrokeColor(DARK_BLUE)
        self.c.setLineWidth(0.75)
        self.c.setFillColor(colors.white)
        self.c.rect(x, y - h, w, h, stroke=1, fill=1)
        self.c.setStrokeColor(colors.HexColor("#E7E7F1"))
        self.c.setLineWidth(0.35)
        step = 5 * mm
        gx = x + step
        while gx < x + w:
            self.c.line(gx, y - h, gx, y)
            gx += step
        gy = y - step
        while gy > y - h:
            self.c.line(x, gy, x + w, gy)
            gy -= step
        self.c.setFillColor(SECONDARY_BLUE)
        self.c.setFont("Helvetica-Bold", 7.2)
        self.c.drawString(x + 3 * mm, y - 5 * mm, "Usa questo spazio per realizzare un disegno schematico del caso in esame")
        return y - h - 4 * mm

    def resolve_asset(self, value: str) -> Path | None:
        if not value:
            return None
        path = Path(value)
        if not path.is_absolute():
            base = self.logo_path.parent if self.logo_path else Path.cwd()
            path = base / value
        return path if path.exists() else None

    def logo_image_path(self) -> Path | None:
        if not self.logo_path:
            return None
        candidates = []
        if self.logo_path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            candidates.append(self.logo_path)
        candidates.append(self.logo_path.with_name("ERNEST-logo-transparent.png"))
        candidates.append(self.logo_path.with_suffix(self.logo_path.suffix + ".png"))
        candidates.append(self.logo_path.with_suffix(".png"))
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def footer_mark(self, case: dict[str, str]) -> None:
        y = 4.8 * mm
        h = 8.0 * mm
        self.c.setFillColor(colors.white)
        self.c.rect(CONTENT_X, y - 0.4 * mm, CONTENT_W, h + 0.8 * mm, stroke=0, fill=1)
        self.c.setStrokeColor(LIGHT_RULE)
        self.c.setLineWidth(0.45)
        self.c.line(CONTENT_X, y + h + 0.25 * mm, CONTENT_X + CONTENT_W, y + h + 0.25 * mm)
        eu_logo = self.eu_logo_path()
        logo_w = 22 * mm
        logo_h = 5.3 * mm
        if eu_logo:
            self.c.drawImage(str(eu_logo), CONTENT_X, y + 1.1 * mm, width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto")
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont(UNICODE_FONT, 4.75)
        text_x = CONTENT_X + logo_w + 8 * mm
        text_w = CONTENT_X + CONTENT_W - text_x
        disclaimer = (
            "ERNEST is a European Researchers' Night project funded by the European Commission under "
            "the Marie Skłodowska-Curie Actions. GA 101305138"
        )
        self.draw_wrapped(disclaimer, text_x, y + 5.15 * mm, text_w, 4.75, 5.2, UNICODE_FONT)

    def eu_logo_path(self) -> Path | None:
        if not self.logo_path:
            return None
        path = self.logo_path.with_name("eu-funded-logo.png")
        return path if path.exists() else None

    def callout(self, text: str, x: float, y: float, w: float, h: float) -> float:
        self.c.setFillColor(colors.HexColor("#FFF8C7"))
        self.c.setStrokeColor(ORANGE)
        self.c.roundRect(x, y - h, w, h, 2 * mm, stroke=1, fill=1)
        self.draw_wrapped(text, x + 3 * mm, y - 5 * mm, w - 6 * mm, 8.2, 9.4)
        return y - h - 4 * mm

    def meta_line(self, label: str, value: str, y: float) -> None:
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawString(MARGIN + 9 * mm, y, f"{label}:")
        self.c.setFont("Helvetica", 8)
        self.c.drawString(MARGIN + 34 * mm, y, value)

    def science_track(self, value: str, x: float, y: float, w: float, h: float) -> None:
        self.box(x, y, w, h)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 7.5)
        self.c.drawString(x + 3 * mm, y - 5 * mm, "Pista scientifica")
        self.draw_wrapped(value, x + 3 * mm, y - 10 * mm, w - 6 * mm, 6.4, 7.3)

    def badge(self, text: str, x: float, y: float, w: float, h: float) -> None:
        self.c.setFillColor(YELLOW)
        self.c.setStrokeColor(DARK_BLUE)
        self.c.rect(x, y, w, h, stroke=1, fill=1)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawCentredString(x + w / 2, y + h / 2 - 3, text)

    def stamp(self, text: str, x: float, y: float, w: float, h: float) -> None:
        self.c.setFillColor(colors.white)
        self.c.setStrokeColor(DARK_BLUE)
        self.c.setLineWidth(1)
        self.c.rect(x, y, w, h, stroke=1, fill=1)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 9)
        self.c.drawCentredString(x + w / 2, y + h / 2 - 3, text)

    def section_title(self, text: str, x: float, y: float, w: float) -> float:
        self.c.setFillColor(SECONDARY_BLUE)
        self.c.roundRect(x, y - 7 * mm, w, 7 * mm, 1.5 * mm, stroke=0, fill=1)
        self.c.setFillColor(YELLOW)
        self.c.circle(x + 2 * mm, y - 3.5 * mm, 0.9 * mm, stroke=0, fill=1)
        self.c.setFillColor(colors.white)
        self.c.setFont("Helvetica-Bold", 8.5)
        self.c.drawString(x + 5 * mm, y - 5 * mm, text.upper())
        return y - 10 * mm

    def box(self, x: float, y: float, w: float, h: float, fill=None) -> None:
        self.c.setStrokeColor(DARK_BLUE)
        self.c.setLineWidth(0.6)
        if fill:
            self.c.setFillColor(fill)
            self.c.rect(x, y - h, w, h, stroke=1, fill=1)
        else:
            self.c.rect(x, y - h, w, h, stroke=1, fill=0)

    def text_box(self, title: str, body: str, x: float, y: float, w: float, h: float) -> float:
        self.box(x, y, w, h)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawString(x + 3 * mm, y - 5 * mm, title)
        self.draw_wrapped(body, x + 3 * mm, y - 10 * mm, w - 6 * mm, 7.4, 9)
        return y - h - 4 * mm

    def writing_box(self, title: str, x: float, y: float, w: float, h: float, lines: int = 4) -> float:
        self.box(x, y, w, h)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawString(x + 3 * mm, y - 5 * mm, title)
        gap = (h - 11 * mm) / max(lines, 1)
        self.c.setStrokeColor(LIGHT_RULE)
        for i in range(lines):
            ly = y - 11 * mm - i * gap
            self.c.line(x + 4 * mm, ly, x + w - 4 * mm, ly)
        return y - h - 4 * mm

    def draw_wrapped(self, text: str, x: float, y: float, w: float, size: float = 8, leading: float = 10, font: str = "Helvetica") -> float:
        self.c.setFillColor(INK)
        self.c.setFont(font, size)
        max_chars = max(18, int(w / (size * 0.48)))
        for paragraph in str(text).splitlines() or [""]:
            for line in wrap(paragraph, max_chars) or [""]:
                self.c.drawString(x, y, line)
                y -= leading
        return y

    def checkbox_row(self, labels: list[str], x: float, y: float) -> None:
        cx = x
        for label in labels:
            self.c.setStrokeColor(DARK_BLUE)
            self.c.rect(cx, y, 4 * mm, 4 * mm, stroke=1, fill=0)
            self.c.setFillColor(INK)
            self.c.setFont("Helvetica", 7.5)
            self.c.drawString(cx + 6 * mm, y + 0.7 * mm, label)
            cx += max(33 * mm, len(label) * 2.1 * mm)

    def field_box(self, label: str, x: float, y: float, w: float, h: float) -> None:
        self.box(x, y, w, h)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 7.5)
        self.c.drawString(x + 3 * mm, y - 5 * mm, label)

    def incident_report(self, case: dict[str, str]) -> None:
        y = self.new_page(case, "Schema e indizi")
        x, w = self.content_bounds()
        y = self.cover_image(case, x, y, w, 42 * mm)
        y = self.section_title("Indizi", x, y, w)
        body = "\n".join([
            f"Sulla scena: {case['scene_evidence']}",
            f"Voce 1: {case['witness_1']}",
            f"Voce 2: {case['witness_2']}",
            f"Voce 3: {case['witness_3']}",
        ])
        y = self.text_box("Indizi raccolti", body, x, y, w, 58 * mm)
        self.text_box("La vostra missione", case["mission"], x, y, w, 24 * mm)

    def evidence_log(self, case: dict[str, str]) -> None:
        y = self.new_page(case, "Taccuino degli indizi")
        x, w = self.content_bounds()
        y = self.section_title("Taccuino degli indizi", x, y, w)
        y = self.writing_box("Quali indizi vi sembrano piu' importanti? Perche'?", x, y, w, 28 * mm, 3)
        y = self.writing_box("Osservazioni dalla scena", x, y, w, 38 * mm, 5)
        y = self.section_title("Ipotesi possibili", x, y, w)
        self.hypothesis_lines(x, y, w, 3)
        self.writing_box("Appunti liberi", x, y - 30 * mm, w, 32 * mm, 5)

    def investigation_plan(self, case: dict[str, str]) -> None:
        for experiment_number in range(1, 4):
            self.experiment_sheet(case, experiment_number)

    def experiment_sheet(self, case: dict[str, str], experiment_number: int) -> None:
        y = self.new_page(case, f"Esperimento {experiment_number}")
        x, w = self.content_bounds()
        y = self.section_title(f"Esperimento {experiment_number}", x, y, w)
        half = (w - 4 * mm) / 2
        self.field_box("Titolo dell'esperimento", x, y, w, 10 * mm)
        y -= 15 * mm
        self.writing_box("Che cosa vogliamo capire?", x, y, w, 18 * mm, 2)
        y -= 22 * mm
        self.field_box("x = cosa cambiamo / confrontiamo", x, y, half, 10 * mm)
        self.field_box("y = cosa misuriamo / osserviamo", x + half + 4 * mm, y, half, 10 * mm)
        y -= 16 * mm
        y = self.section_title("Dati raccolti (x, y)", x, y, w)
        self.xy_table(x, y, half, 52 * mm)
        self.small_graph(x + half + 4 * mm, y, half, 52 * mm)
        y -= 58 * mm
        self.writing_box("Che cosa mostra questo esperimento?", x, y, w, 24 * mm, 3)

    def hypothesis_lines(self, x: float, y: float, w: float, count: int) -> None:
        row_h = 8.5 * mm
        self.c.setStrokeColor(DARK_BLUE)
        self.c.setFillColor(INK)
        self.c.setFont("Helvetica", 8)
        for i in range(count):
            yy = y - i * row_h
            self.c.drawString(x + 1 * mm, yy - 5.5 * mm, f"{i + 1}.")
            self.c.line(x + 8 * mm, yy - 5.8 * mm, x + w - 2 * mm, yy - 5.8 * mm)

    def table(self, x: float, y: float, w: float, h: float, headers: list[str], rows: int = 7) -> None:
        cols = len(headers)
        row_h = h / rows
        col_w = w / cols
        self.box(x, y, w, h)
        self.c.setFillColor(YELLOW)
        self.c.rect(x, y - row_h, w, row_h, stroke=0, fill=1)
        self.c.setStrokeColor(DARK_BLUE)
        for i in range(1, cols):
            self.c.line(x + i * col_w, y, x + i * col_w, y - h)
        for i in range(1, rows):
            self.c.line(x, y - i * row_h, x + w, y - i * row_h)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 7)
        for i, header in enumerate(headers):
            self.c.drawCentredString(x + i * col_w + col_w / 2, y - row_h + 4, header[:24])

    def xy_table(self, x: float, y: float, w: float, h: float) -> None:
        self.table(x, y, w, h, ["#", "x", "y"], rows=7)

    def small_graph(self, x: float, y: float, w: float, h: float) -> None:
        self.box(x, y, w, h)
        self.c.setFillColor(DARK_BLUE)
        self.c.setFont("Helvetica-Bold", 7)
        self.c.drawString(x + 3 * mm, y - 5 * mm, "Grafico")
        gx = x + 9 * mm
        gy = y - h + 9 * mm
        gw = w - 15 * mm
        gh = h - 18 * mm
        self.c.setStrokeColor(DARK_BLUE)
        self.c.line(gx, gy, gx, gy + gh)
        self.c.line(gx, gy, gx + gw, gy)
        self.c.setStrokeColor(LIGHT_RULE)
        for i in range(1, 5):
            self.c.line(gx, gy + i * gh / 5, gx + gw, gy + i * gh / 5)
            self.c.line(gx + i * gw / 5, gy, gx + i * gw / 5, gy + gh)
        self.c.setFillColor(INK)
        self.c.setFont("Helvetica", 5.8)
        self.c.drawCentredString(gx + gw / 2, y - h + 3 * mm, "x")
        self.c.drawString(x + 2 * mm, gy + gh / 2, "y")

    def evidence_analysis(self, case: dict[str, str]) -> None:
        y = self.new_page(case, "Analisi degli indizi")
        x, w = self.content_bounds()
        y = self.section_title("Analisi degli indizi", x, y, w)
        y = self.writing_box("Quale dei 3 grafici e' piu' utile per risolvere il caso?", x, y, w, 28 * mm, 3)
        y = self.writing_box("Che cosa cambia tra Esperimento 1, Esperimento 2 e Esperimento 3?", x, y, w, 30 * mm, 3)
        y = self.section_title("Leggete i risultati", x, y, w)
        prompts = [
            "Che schema vedete nei dati?",
            "Quale ipotesi e' piu' forte?",
            "Che cosa testereste ancora per essere piu' sicuri?",
        ]
        for prompt in prompts:
            y = self.writing_box(prompt, x, y, w, 18 * mm, 2)

    def graph_area(self, x: float, y: float, w: float, h: float, case: dict[str, str]) -> None:
        self.box(x, y, w, h)
        gx, gy = x + 12 * mm, y - h + 12 * mm
        gw, gh = w - 22 * mm, h - 23 * mm
        self.c.setStrokeColor(DARK_BLUE)
        self.c.line(gx, gy, gx, gy + gh)
        self.c.line(gx, gy, gx + gw, gy)
        self.c.setStrokeColor(LIGHT_RULE)
        for i in range(1, 6):
            self.c.line(gx, gy + i * gh / 6, gx + gw, gy + i * gh / 6)
            self.c.line(gx + i * gw / 6, gy, gx + i * gw / 6, gy + gh)
        self.c.setFillColor(INK)
        self.c.setFont("Helvetica", 6.5)
        self.c.drawCentredString(gx + gw / 2, y - h + 4 * mm, "Asse x: ______________________________")
        self.c.drawString(gx, y - 8 * mm, "Asse y:")
        self.c.line(gx + 13 * mm, y - 8 * mm, gx + 70 * mm, y - 8 * mm)

    def final_report(self, case: dict[str, str]) -> None:
        y = self.new_page(case, "Conclusione scientifica")
        x, w = self.content_bounds()
        y = self.section_title("Conclusione scientifica", x, y, w)
        y = self.writing_box("Che cosa avete scoperto?", x, y, w, 30 * mm, 4)
        y = self.writing_box("Quali dati o indizi lo mostrano?", x, y, w, 38 * mm, 5)
        y = self.writing_box("Che cosa cambiereste se rifaceste l'indagine?", x, y, w, 26 * mm, 3)
        self.writing_box("La scoperta in una frase", x, y, w, 22 * mm, 2)

    def teacher_guide(self, case: dict[str, str]) -> None:
        y = self.new_page(case, "Guida docente")
        x, w = self.content_bounds()
        sections = [
            ("Panoramica del caso", f"{case['case_id']} - {case['title']}\nEta': {case['age_group']}\nTema: {case['physics_topic']}\nMistero: {case['mystery']}"),
            ("Obiettivi di apprendimento", self.objectives(case)),
            ("Spiegazione del fenomeno", self.phenomenon_text(case)),
            ("Misure da fare", self.measurement_text(case)),
            ("Risultati attesi e interpretazione", self.expected_results_text(case)),
            ("Materiali", case["materials"]),
            ("Preparazione", self.setup_text(case)),
            ("Timeline da 30 minuti", self.timeline_text(case)),
            ("Risultato atteso / soluzione", case["teacher_solution"]),
            ("Domande per il debriefing", self.debrief_text(case)),
            ("Connessione con la ricerca reale", case["real_world_connection"]),
            ("Note di sicurezza", "Usare solo materiali sicuri per la classe. Tenere piccoli e leggeri gli oggetti oscillanti. Chiedere agli studenti di restare a distanza dal pendolo in movimento."),
        ]
        for title, body in sections:
            needed = self.estimate_height(body) + 14 * mm
            if y - needed < FRAME_BOTTOM + 6 * mm:
                y = self.new_page(case, "Guida docente")
            y = self.section_title(title, x, y, w)
            y = self.text_box(title, body, x, y, w, max(22 * mm, needed - 8 * mm))

    def objectives(self, case: dict[str, str]) -> str:
        return "\n".join([
            f"Riconoscere la variabile modificata: {case['variable_changed']}.",
            f"Misurare e confrontare: {case['quantity_measured']}.",
            "Usare tabella e grafico per sostenere una conclusione scientifica.",
            "Collegare una piccola indagine di classe a un contesto di ricerca reale.",
        ])

    def phenomenon_text(self, case: dict[str, str]) -> str:
        topic = f"{case['physics_topic']} {case['title']}".lower()
        if "pendolo" in topic:
            return "\n".join([
                "Un pendolo e' un sistema oscillante: se viene spostato dalla posizione di equilibrio e lasciato andare, la gravita' lo riporta verso il basso e il moto si ripete.",
                "Per piccole oscillazioni, il tempo di una oscillazione completa dipende soprattutto dalla lunghezza del filo. Un pendolo piu' lungo oscilla piu' lentamente; un pendolo piu' corto oscilla piu' rapidamente.",
                "La massa del peso, se non cambia la lunghezza effettiva del pendolo e se l'attrito resta piccolo, ha un effetto molto minore sul periodo. Per questo e' importante cambiare una sola variabile alla volta.",
                "La relazione ideale e' T = 2*pi*sqrt(L/g), dove T e' il periodo, L la lunghezza del pendolo e g l'accelerazione di gravita'. In classe non serve usare la formula per calcolare tutto, ma e' utile sapere che aumentando la lunghezza aumenta anche il tempo di oscillazione.",
                f"Nel caso investigativo, la domanda scientifica e': una modifica a {case['variable_changed'].lower()} puo' spiegare il ritardo dell'orologio?",
            ])
        return "\n".join([
            f"Il fenomeno centrale del caso riguarda: {case['physics_topic']}.",
            f"La variabile da isolare e' {case['variable_changed']}; la grandezza da osservare o misurare e' {case['quantity_measured']}.",
            "La guida della discussione deve aiutare la classe a distinguere tra indizi narrativi, ipotesi plausibili e prove sperimentali.",
            "Il punto chiave e' far cambiare una sola variabile alla volta, mantenendo costanti le altre condizioni.",
        ])

    def measurement_text(self, case: dict[str, str]) -> str:
        topic = f"{case['physics_topic']} {case['title']}".lower()
        if "pendolo" in topic:
            return "\n".join([
                "Preparare materiali che permettano scelte sperimentali diverse: filo regolabile, pesi intercambiabili, righello, cronometro e riferimenti visivi per piccoli angoli.",
                "Per ogni confronto, misurare il tempo necessario per 10 oscillazioni complete. Una oscillazione completa va da un lato, torna indietro e ritorna al lato di partenza.",
                "Ricavare il periodo dividendo il tempo totale per 10. Ripetere ogni misura almeno 2 volte, meglio 3, e calcolare una media.",
                "Invitare la classe a decidere quale variabile cambiare e quali condizioni lasciare uguali. Le variabili disponibili nella scena devono permettere confronti su massa del peso, angolo iniziale e lunghezza del filo, senza imporre un ordine unico.",
                "Quando si confrontano i risultati con il modello semplice del pendolo, usare angoli piccoli, circa 5-15 gradi, e lasciare andare il pendolo senza spingerlo.",
                "Possibili errori da discutere: partenza data con una spinta, conteggio sbagliato delle oscillazioni, lunghezza misurata dal punto di aggancio al centro del peso, reazione umana nel cronometro.",
            ])
        return "\n".join([
            f"Variabile indipendente: {case['variable_changed']}.",
            f"Variabile dipendente: {case['quantity_measured']}.",
            "Eseguire piu' prove per ogni valore o condizione, registrare tutti i dati e usare una media quando ha senso.",
            "Prima dell'esperimento concordare quali condizioni devono restare costanti.",
            f"Grafico consigliato: {case['expected_graph']}.",
        ])

    def expected_results_text(self, case: dict[str, str]) -> str:
        topic = f"{case['physics_topic']} {case['title']}".lower()
        if "pendolo" in topic:
            return "\n".join([
                f"Risultato atteso: {case['graph_shape']}.",
                "Se la classe confronta pesi diversi mantenendo uguali lunghezza e piccolo angolo iniziale, il periodo dovrebbe restare quasi uguale.",
                "Se la classe confronta piccoli angoli iniziali mantenendo uguali lunghezza e peso, il periodo dovrebbe restare quasi uguale. Per angoli grandi questa semplificazione non e' piu' cosi' buona.",
                "Se la classe confronta lunghezze diverse mantenendo uguali peso e piccolo angolo iniziale, il periodo aumenta con la lunghezza. Valori indicativi per 10 oscillazioni: 20 cm circa 9 s; 30 cm circa 11 s; 40 cm circa 13 s; 50 cm circa 14 s.",
                "Interpretazione: se aumentando la lunghezza aumenta il tempo di oscillazione, allora un pendolo reso piu' lungo puo' far rallentare il ritmo dell'orologio.",
                "Conclusione attesa per il caso: l'ipotesi piu' forte e' che il pendolo sia diventato piu' lungo. L'ipotesi del pendolo piu' corto non spiega un ritardo; l'ipotesi delle lancette spostate resta narrativa ma non e' sostenuta dall'esperimento sul moto.",
                "Durante il debrief, chiedere alla classe di distinguere tra prova diretta, indizio coerente e supposizione. Il grafico e' la prova piu' forte per collegare la modifica fisica al mistero.",
            ])
        return "\n".join([
            f"Grafico atteso: {case['expected_graph']}.",
            f"Andamento atteso: {case['graph_shape']}.",
            f"Soluzione attesa: {case['teacher_solution']}.",
            "La conclusione degli studenti dovrebbe citare almeno un dato o un andamento del grafico, non solo un'impressione.",
            "Se i dati non seguono l'andamento atteso, usare il momento per discutere errori di misura, variabili non controllate e necessita' di ripetere le prove.",
        ])

    def setup_text(self, case: dict[str, str]) -> str:
        return "\n".join([
            "Preparare una postazione semplice per gruppo o una postazione dimostrativa.",
            "Mettere i materiali in una vaschetta o busta degli indizi.",
            f"Gli studenti devono modificare solo: {case['variable_changed']}.",
            f"Gli studenti devono misurare: {case['quantity_measured']}.",
        ])

    def timeline_text(self, case: dict[str, str]) -> str:
        return "\n".join([
            f"0-5 min: Osservare - {case['step_1_observe']}",
            f"5-8 min: Ipotizzare - {case['step_2_hypothesize']}",
            f"8-18 min: Sperimentare - {case['step_3_experiment']}",
            f"18-22 min: Registrare i dati - {case['step_4_record_data']}",
            f"22-26 min: Costruire il grafico - {case['step_5_build_graph']}",
            f"26-30 min: Concludere - {case['step_6_conclusion']}",
        ])

    def debrief_text(self, case: dict[str, str]) -> str:
        return "\n".join([
            f"Che cosa mostra il grafico su {case['variable_changed']}?",
            "Quale indizio della storia e' diventato piu' importante dopo l'esperimento?",
            "Quale variabile testereste se aveste piu' tempo?",
            f"Come si collega alla ricerca reale? {case['real_world_connection']}",
        ])

    def estimate_height(self, text: str) -> float:
        lines = 0
        for paragraph in str(text).splitlines() or [""]:
            lines += max(1, len(paragraph) // 62 + 1)
        return (lines * 4.2 + 8) * mm


def build_student_pdf(case: dict[str, str], path: Path, logo_path: Path | None = None) -> None:
    pdf = DossierPdf(path, logo_path)
    pdf.cover(case)
    pdf.incident_report(case)
    pdf.evidence_log(case)
    pdf.investigation_plan(case)
    pdf.evidence_analysis(case)
    pdf.final_report(case)
    pdf.save()


def build_teacher_pdf(case: dict[str, str], path: Path, logo_path: Path | None = None) -> None:
    pdf = DossierPdf(path, logo_path)
    pdf.cover(case)
    pdf.teacher_guide(case)
    pdf.save()
