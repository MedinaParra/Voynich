#!/usr/bin/env python3
"""Render the exploratory inventory as a visually reviewable Spanish atlas."""
import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from PIL import Image

W, H = A4
M = 43
INK = colors.HexColor("#152C3A")
TEAL = colors.HexColor("#087A8E")
MUTED = colors.HexColor("#526672")


def build(data, spec_path, output):
    for name, file in [("DV", "DejaVuSans.ttf"), ("DVB", "DejaVuSans-Bold.ttf")]:
        pdfmetrics.registerFont(TTFont(name, "/usr/share/fonts/truetype/dejavu/" + file))
    result = json.loads((data / "result.json").read_text())
    spec = json.loads(spec_path.read_text())
    cases = {c["id"]: c for c in json.loads((data / "catalog.json").read_text())}
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=A4, pageCompression=1)
    c.setTitle("Voynich | Primer atlas de números y contexto")
    c.setAuthor("Proyecto Voynich - Exe Medina / análisis asistido")
    body = ParagraphStyle("body", fontName="DV", fontSize=10.3, leading=15, textColor=INK)
    small = ParagraphStyle("small", parent=body, fontSize=8.1, leading=11.7)
    cell = ParagraphStyle("cell", parent=small, fontSize=8.0, leading=11)

    def p(text, x, top, width, style=body):
        a = Paragraph(text, style)
        _, h = a.wrap(width, H)
        if top - h < 48:
            raise ValueError("Text exceeds page: " + text[:60])
        a.drawOn(c, x, top - h)
        return top - h - 10

    def page(title, subtitle):
        c.setFillColor(TEAL); c.rect(0, H - 15, W, 15, fill=1, stroke=0)
        c.setFillColor(MUTED); c.setFont("DVB", 8)
        c.drawString(M, H - 44, "VOYNICH  /  INVENTARIO EXPLORATORIO  /  26 OCT 2026")
        c.setFillColor(INK); c.setFont("DVB", 21)
        c.drawString(M, H - 78, title)
        return p(subtitle, M, H - 96, W - 2 * M, small) - 7

    def finish():
        c.setStrokeColor(colors.HexColor("#D5E0E5")); c.line(M, 40, W - M, 40)
        c.setFont("DV", 7); c.setFillColor(MUTED)
        c.drawString(M, 26, "Imágenes: Yale University Library, Beinecke MS 408. Anotaciones modernas identificadas.")
        c.drawRightString(W - M, 26, str(c.getPageNumber()))
        c.showPage()

    def picture(path, x, top, width, maxheight, border=True):
        im = Image.open(path)
        scale = min(width / im.width, maxheight / im.height)
        ww, hh = im.width * scale, im.height * scale
        xx = x + (width - ww) / 2
        c.drawImage(str(path), xx, top - hh, ww, hh)
        if border:
            c.setStrokeColor(colors.HexColor("#D5E0E5")); c.rect(xx, top - hh, ww, hh, stroke=1, fill=0)
        return top - hh - 8

    def table(headers, rows, top, widths):
        data_rows = [[Paragraph(escape(str(a)), cell) for a in row] for row in [headers] + rows]
        t = Table(data_rows, colWidths=widths, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEFF2")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LINEBELOW", (0, 0), (-1, 0), .6, TEAL),
            ("LINEBELOW", (0, 1), (-1, -1), .3, colors.HexColor("#DFE7EB")),
        ]))
        _, hh = t.wrap(W - 2 * M, H)
        if top - hh < 50:
            raise ValueError("Table exceeds page")
        t.drawOn(c, M, top - hh)
        return top - hh - 14

    y = page("Números: qué sabemos leer", "Primer inventario dirigido: 20 casos y 12 diagramas zodiacales. No es un censo completo ni una traducción del manuscrito.")
    y = p("<b>La pista principal está en f49v:</b> cifras 1-5 junto a una columna de signos. Es una asociación verificable en la imagen, pero su función sigue abierta.", M, y, W - 2 * M)
    y = table(["Evidencia", "Ejemplos", "Función probable"], [
        ["Cifras legibles", "26, 42, 71, 103", "Identificar hojas; no describen cantidades de las plantas o del texto."],
        ["Orden del libro", "Pmus en f8v; 20 en f103r", "Marcas del primer cuaderno y del cuaderno 20."],
        ["Cifras junto a signos", "1-5 en f49v", "Enumeración parcial, comparación de signos o anotación de lector."],
        ["Cantidades contables", "15 + 15 figuras de Aries", "Dos mitades de una serie de 30 unidades."],
        ["Formas ambiguas", "Marca inferior de f57v", "Posible numeral u ordinal; lectura sin confirmar."],
    ], y, [126, 133, W - 2 * M - 259])
    y = p("<b>Regla de trabajo.</b> Registramos por separado la forma que se ve, su ubicación, la lectura propuesta y la función inferida. Una cifra de foliación no fecha el texto. Un conteo de 30 objetos no equivale a encontrar escrito el número 30.", M, y, W - 2 * M)
    y = p("<b>Resultado actual.</b> La organización en 30 unidades es una hipótesis útil para los diagramas zodiacales. Todavía no hay un signo voynichés cuyo valor numérico se haya demostrado mediante predicciones en otras hojas.", M, y, W - 2 * M)
    p("Las páginas siguientes permiten revisar las observaciones en recortes originales. Confianza cualitativa; una lectura por asistente, pendiente de revisión paleográfica experta.", M, y, W - 2 * M, small)
    finish()

    y = page("f49v: la asociación más directa", "Página botánica. A la izquierda del texto hay 26 signos aislados; cinco cifras occidentales acompañan los renglones 2-6.")
    y = picture(data / "figures/f49v_alignment.jpg", M, y, W - 2 * M, 269)
    y = p("Recorte sin realce: cifra occidental, signo aislado y renglón de texto. Las denominaciones EVA de la tabla son códigos modernos, no pronunciaciones ni traducciones.", M, y, W - 2 * M, small)
    y = table(["Cifra visible", "Renglón", "Signo en ZL/EVA", "Palabras transcritas"], [[r["visible_arabic_digit"], r["physical_line"], r["marginal_sign"], r["tokens_dot"]] for r in result["f49v"]["digit_rows"]], y, [95, 90, 155, W - 2 * M - 340])
    y = p("<b>Interpretación provisional:</b> numeración parcial de elementos de una lista, quizá realizada por un lector. Empieza junto al segundo renglón; no coincide con la numeración absoluta 1-5 de los renglones ni con su cantidad de palabras.", M, y, W - 2 * M)
    p("<b>Límite decisivo:</b> no se concluye o = 1, r = 2, y = 3, e = 4. La misma forma o reaparece junto a los renglones 10 y 17. Una correspondencia numérica general requiere pruebas en otros contextos. Fuentes: Q7, S, ZL.", M, y, W - 2 * M, small)
    finish()

    y = page("El libro tiene varios niveles", "Una misma hoja puede llevar un número de folio y otro de cuaderno. Su posición ayuda a reconocer la función.")
    y0 = y
    for row, ids in enumerate([["N01", "N02"], ["N04", "N05"], ["N06", "N07"]]):
        for col, key in enumerate(ids):
            x = M + col * 264
            case = cases[key]
            top = y0 - row * 174
            p(f"<b>{case['folio']} | {escape(case['reading'])}</b>", x, top, 245, small)
            yy = picture(data / case["crop_file"], x, top - 24, 245, 99)
            short = {"N01": "26: identificador de hoja.", "N02": "42: cifra dentro de una hoja pintada.", "N04": "71: identifica la hoja con Aries.", "N05": "103: número de hoja.", "N06": "Pmus: primer cuaderno; no termina en un nueve numérico.", "N07": "20: número de cuaderno, en el margen inferior izquierdo."}[key]
            p(short, x, yy, 245, small)
    y = y0 - 531
    p("McCrone analizó la cifra 26 y una marca de cuaderno. Identificó formulaciones de tinta diferentes de la del texto, sin fechar su aplicación. Ni la lectura de las cifras ni su química demuestran el año en que se escribieron. Fuentes: M, Q1, Q20, O.", M, y, W - 2 * M, small)
    finish()

    y = page("f57v: repetición y ambigüedad", "La geometría hace contable una estructura, aunque todavía desconozcamos qué representan sus signos.")
    ringbottom = picture(data / "crops/N14.jpg", M, y, 329, 335)
    yy = picture(data / "crops/N13.jpg", M + 350, y, 159, 150)
    p("Marca inferior: lectura indeterminada. Zandbergen propone tentativamente un ordinal 17th. No se adopta esa lectura como dato seguro.", M + 350, yy, 159, small)
    y = ringbottom - 4
    y = p("<b>Lo que sí reproduce la transcripción:</b> el anillo f57v.3 contiene 68 grupos delimitados, que pueden organizarse como cuatro bloques de 17. Catorce posiciones se mantienen iguales entre los cuatro bloques; tres presentan variaciones.", M, y, W - 2 * M)
    y = p("<b>Qué podría indicar:</b> un repertorio ordenado de signos o una serie cíclica. La repetición justifica estudiar la estructura. No basta para establecer una base 17, una tabla aritmética o una secuencia de cantidades.", M, y, W - 2 * M)
    p("68 es un conteo editorial, no un numeral leído en el pergamino. La separación de componentes modifica cuántos glifos se consideran individuales. La marca marginal y el anillo se registran por separado para evitar que una lectura incierta confirme a la otra. Fuentes: Q8, S, ZL.", M, y, W - 2 * M, small)
    finish()

    y = page("Aries: dos grupos de quince", "Recuento visual de las figuras humanas en f70v1 y f71r: cinco en el anillo interior y diez en el exterior, en cada dibujo.")
    for j, folio in enumerate(["70v1", "71r"]):
        x = M + j * 264
        p(f"<b>f{folio}: 5 + 10 = 15 figuras</b>", x, y, 245, small)
        picture(data / "figures" / (folio + "_counted.jpg"), x, y - 25, 245, 394)
    y -= 438
    y = p("Los círculos y números azul verdoso son <b>anotaciones modernas de revisión</b>. Señalan las cabezas contadas; no forman parte del manuscrito. Este recuento es una primera lectura, no una anotación experta independiente.", M, y, W - 2 * M, small)
    y = p("<b>Interpretación con mejor apoyo contextual:</b> ambas imágenes forman una serie de 30 unidades para Aries. La división puede representar dos mitades de un signo. Los 30 grados de cada signo zodiacal son una hipótesis histórica pertinente.", M, y, W - 2 * M)
    p("También sigue siendo posible una organización calendárica esquemática u otra clasificación de 30 elementos. El número de figuras no traduce sus etiquetas ni identifica por sí solo días, grados o nombres de estrellas. Fuentes: Q10, Q11; cotejo visual de imágenes de Yale.", M, y, W - 2 * M, small)
    finish()

    y = page("Zodiaco: contar sin forzar", "Doce diagramas representan diez signos: Aries y Tauro aparecen divididos. Capricornio y Acuario no se conservan en la serie.")
    zr = spec["zodiac"]
    y = table(["Hoja", "Signo", "Figuras (catálogo)", "Etiquetas ZL"], [["f" + r["folio"], r["sign"], r["figures_reported"], r["labels_reported"]] for r in zr], y, [95, 136, 143, W - 2 * M - 374])
    y = p("<b>Conservar las excepciones:</b> Piscis tiene 29 figuras y 30 etiquetas. Géminis tiene 30 figuras y 29 etiquetas. En el catálogo se describen además casos de estrella o etiqueta ausente en Géminis. Figuras, estrellas y etiquetas no son intercambiables.", M, y, W - 2 * M)
    y = p("Al reunir las mitades de Aries y Tauro, nueve de los diez signos tienen 30 etiquetas; nueve tienen 30 figuras. Una lectura estricta de un objeto por día del mes civil no encaja con todos los meses anotados. Un calendario de 30 unidades sí permanece abierto.", M, y, W - 2 * M)
    p("La transcripción ZL reproduce los 12 conteos de etiquetas del catálogo. Esto verifica consistencia, no independencia: ambas fuentes comparten autoría e historia de datos. Solo los dos recuentos de Aries se documentan aquí con puntos de revisión individual. Fuentes: Q10-Q12, W, ZL.", M, y, W - 2 * M, small)
    finish()

    y = page("Dos cautelas que importan", "Una cantidad del dibujo y una forma parecida a una cifra deben pasar comprobaciones diferentes.")
    yy = picture(data / "crops/N17.jpg", M, y, 270, 260)
    t = y
    t = p("<b>Piscis, f70v2</b>", M + 291, t, 218)
    t = p("29 figuras humanas y 30 etiquetas según la descripción y la transcripción. Una etiqueta se encuentra junto a una estrella central, fuera de las figuras del anillo.", M + 291, t, 218)
    p("Es un caso de control: si un método exige exactamente una persona por etiqueta, debe explicar esta excepción antes de proponer una traducción.", M + 291, t, 218, small)
    y = min(yy, t) - 26
    yy = picture(data / "crops/N20.jpg", M, y, 205, 174)
    t = p("<b>Marca roja de f1r</b>", M + 230, y, 279)
    t = p("Algunas descripciones señalan su parecido con 29. La imagen no permite adoptar esa lectura numérica. Se registra como forma ambigua, sin valor asignado.", M + 230, t, 279)
    y = min(yy, t) - 23
    p("<b>Orden de prioridad:</b> estudiar primero la columna y las cifras de f49v; después, comprobar relaciones entre cantidades y etiquetas en el zodiaco. Las formas ambiguas se conservan en el inventario y no se convierten en pruebas favorables por semejanza visual.", M, y, W - 2 * M)
    finish()

    y = page("Fuentes y alcance de la prueba", "Referencias para comprobar el inventario. Código, coordenadas de recorte, tablas y resultados se conservan en el repositorio.")
    refs = [
        ("Y", "Yale University Library: imágenes de Beinecke MS 408. Los enlaces IIIF y huellas de cada captura están en el catálogo de casos."),
        ("M", "Joseph G. Barabe / McCrone Associates. Materials Analysis of the Voynich Manuscript, 1 abril 2009, proyecto MA47613; especialmente pp. 3 y 5 y tabla I."),
        ("Q1, Q7, Q8, Q10-Q12, Q20", "René Zandbergen. Descripciones de los cuadernos y folios en voynich.nu. Se distingue observación del catálogo de interpretación tentativa."),
        ("S", "Jorge Stolfi. Note 034: The key-like sequences collected, 1999. Antecedente explícito de la columna de f49v y del anillo de f57v."),
        ("W, O", "René Zandbergen. The Writing System y Special Topics: Origin of the MS. Contexto de foliación, marcas, meses y orden de producción."),
        ("ZL", "Transcripción ZL, versión 3b, 13 mayo 2025. Copia fijada por SHA-256 y commit de origen; no es una traducción."),
    ]
    for key, text in refs:
        y = p(f"<b>{key}</b> {escape(text)}", M, y, W - 2 * M, small)
    y = p("<b>Enlaces principales</b>", M, y - 6, W - 2 * M)
    for key in ["Y", "M", "Q7", "Q8", "Q10", "Q11", "Q12", "S"]:
        url = spec["sources"][key]
        y = p(f'<link href="{escape(url)}" color="#087A8E">{escape(url)}</link>', M, y, W - 2 * M, small)
    y = p("<b>Estado:</b> inventario descriptivo. No se ha identificado una clave numérica validada ni una traducción. Las hipótesis anteriores sobre estas páginas se citan como antecedentes, sin reivindicar novedad.", M, y - 4, W - 2 * M, small)
    p("Repositorio: github.com/MedinaParra/Voynich<br/>Rama: experiment/kraken-voynich<br/>Informe: research_gpt6/55_numeral_context_inventory.md", M, y, W - 2 * M, small)
    finish()
    c.save()
    return {"pages": 8, "path": str(output), "case_count": result["case_count"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(build(a.data, a.spec, a.output), ensure_ascii=False))
