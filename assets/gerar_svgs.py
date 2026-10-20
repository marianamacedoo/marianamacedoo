"""Gera os SVGs animados do README do perfil (mesma paleta do portfólio).

Uso: python3 assets/gerar_svgs.py
"""
import base64
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent

SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

P = {
    "lilac": "#c9b6ff", "peach": "#ffd3b8", "mint": "#bdebd7",
    "sky": "#bfe0ff", "butter": "#fff0b3", "rose": "#ffc8dd",
}

# classes de cor com modo escuro, iguais às variáveis do site
STYLE = f"""<style>
  .bg {{ fill: #fdfbf7; }} .surface {{ fill: #ffffff; }} .line {{ stroke: #ece6f2; }}
  .ink {{ fill: #2f2a3d; }} .muted {{ fill: #6f6880; }} .accent {{ fill: #7a5cd6; }}
  .chiptxt {{ fill: #2f2a3d; }} .blob {{ opacity: .55; }}
  .serif {{ font-family: {SERIF}; }} .sans {{ font-family: {SANS}; }} .mono {{ font-family: {MONO}; }}
  .fade {{ opacity: 0; animation: fade .8s ease forwards; }}
  @keyframes fade {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
  @media (prefers-color-scheme: dark) {{
    .bg {{ fill: #1c1a24; }} .surface {{ fill: #252231; }} .line {{ stroke: #36324a; }}
    .ink {{ fill: #f2eefb; }} .muted {{ fill: #b2abc4; }} .accent {{ fill: #c9b6ff; }}
    .blob {{ opacity: .2; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} .fade {{ opacity: 1; }} }}
</style>"""


def svg(w, h, body, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{STYLE}\n<defs>{extra_defs}</defs>\n{body}\n</svg>\n')


def text_w(s, size, kind="sans"):
    """Largura aproximada do texto (não dá para carregar fontes num SVG usado como imagem)."""
    if kind == "mono":
        return len(s) * size * 0.6
    narrow = sum(1 for c in s if c in "ilIjtf.,:;'| ")
    return (len(s) - narrow) * size * 0.56 + narrow * size * 0.3


def wrap(s, maxc):
    lines, cur = [], ""
    for word in s.split():
        if cur and len(cur) + 1 + len(word) > maxc:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur] if cur else lines


def blobs(w, h, clip_id):
    specs = [(P["lilac"], 0.08, 0.05, 150, "0 0; 40 50; -30 20; 0 0"),
             (P["peach"], 0.92, 0.45, 130, "0 0; -50 30; 20 -30; 0 0"),
             (P["mint"], 0.35, 1.0, 120, "0 0; 50 -30; -20 -10; 0 0")]
    out = [f'<g clip-path="url(#{clip_id})" filter="url(#blur)">']
    for i, (c, fx, fy, r, vals) in enumerate(specs):
        out.append(f'<circle class="blob" cx="{w*fx:.0f}" cy="{h*fy:.0f}" r="{r}" fill="{c}">'
                   f'<animateTransform attributeName="transform" type="translate" values="{vals}" '
                   f'dur="{16+i*3}s" repeatCount="indefinite"/></circle>')
    out.append("</g>")
    return "\n".join(out)


BLUR = '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="45"/></filter>'


def frame(w, h, clip_id="frame"):
    return (f'<clipPath id="{clip_id}"><rect width="{w}" height="{h}" rx="28"/></clipPath>',
            f'<rect class="bg line" x=".5" y=".5" width="{w-1}" height="{h-1}" rx="28" stroke-width="1"/>\n'
            + blobs(w, h, clip_id))


# ---------- cabeçalho ----------
def header():
    w, h = 1000, 340
    clip, base = frame(w, h)
    avatar = base64.b64encode((OUT / "avatar.jpg").read_bytes()).decode()

    words = ["ciência de dados", "pipelines de ETL", "machine learning", "NLP", "visualização de dados"]
    n, slot = len(words), 3.2
    dur = n * slot
    size, prefix = 20, "eu trabalho com "
    x0 = 52 + text_w(prefix, size, "mono")
    cw = size * 0.6
    typed = []
    for i, word in enumerate(words):
        full = len(word) * cw
        s = i / n
        kt = [0, s, s + 0.3 / n, s + 0.8 / n, s + 1 / n, 1]
        kt = ";".join(f"{min(k, 1):.4f}" for k in kt)
        widths = f"0;0;{full:.1f};{full:.1f};0;0"
        typed.append(
            f'<clipPath id="t{i}"><rect x="{x0:.1f}" y="230" height="34" width="0">'
            f'<animate attributeName="width" values="{widths}" keyTimes="{kt}" dur="{dur}s" '
            f'repeatCount="indefinite" calcMode="linear"/></rect></clipPath>')
        typed.append(f'<text clip-path="url(#t{i})" class="ink mono" x="{x0:.1f}" y="254" '
                     f'font-size="{size}" font-weight="700">{escape(word)}</text>')
    # o cursor acompanha a palavra que está sendo digitada
    cx_vals, cx_kt = [], []
    for i, word in enumerate(words):
        full = len(word) * cw
        s = i / n
        for k, v in [(s, 0), (s + 0.3 / n, full), (s + 0.8 / n, full), (s + 0.999 / n, 0)]:
            cx_kt.append(f"{k:.4f}")
            cx_vals.append(f"{v:.1f} 0")
    cx_kt.append("1")
    cx_vals.append("0 0")
    cursor = (f'<rect class="accent" x="{x0+2:.1f}" y="236" width="2.5" height="24">'
              f'<animateTransform attributeName="transform" type="translate" values="{";".join(cx_vals)}" '
              f'keyTimes="{";".join(cx_kt)}" dur="{dur}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur=".8s" repeatCount="indefinite"/></rect>')

    morph_a = "M100,10 C150,8 195,45 192,100 C190,155 150,195 100,192 C45,190 8,150 10,100 C12,48 52,12 100,10 Z"
    morph_b = "M100,6 C158,14 190,52 194,104 C196,150 148,190 98,194 C50,196 6,154 8,98 C10,44 44,2 100,6 Z"
    defs = (clip + BLUR
            + '<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="#a58bff"/>'
              '<stop offset=".5" stop-color="#ff8fb8"/><stop offset="1" stop-color="#ffab7a"/>'
              '<animate attributeName="x1" values="0;-.4;0" dur="8s" repeatCount="indefinite"/>'
              '<animate attributeName="x2" values="1;1.4;1" dur="8s" repeatCount="indefinite"/></linearGradient>'
            + f'<clipPath id="morph"><path d="{morph_a}"><animate attributeName="d" values="{morph_a};{morph_b};{morph_a}" '
              'dur="10s" repeatCount="indefinite"/></path></clipPath>'
            + "".join(t for t in typed if t.startswith("<clipPath")))
    body = f"""{base}
<g class="fade" style="animation-delay:.1s">
  <rect class="surface line" x="52" y="44" width="296" height="34" rx="17" stroke-width="1"/>
  <circle cx="72" cy="61" r="9" fill="#6fcf97" opacity=".5"><animate attributeName="r" values="4;11;4" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values=".6;0;0" dur="2s" repeatCount="indefinite"/></circle>
  <circle cx="72" cy="61" r="4" fill="#6fcf97"/>
  <text class="muted sans" x="86" y="66" font-size="14">Aberta a oportunidades em dados</text>
</g>
<text class="ink serif fade" style="animation-delay:.25s" x="52" y="138" font-size="44" font-weight="600">Oi, eu sou a</text>
<text class="serif fade" style="animation-delay:.4s" x="52" y="196" font-size="54" font-weight="600" fill="url(#name)">Mariana Macedo</text>
<g class="fade" style="animation-delay:.6s">
  <text class="muted mono" x="52" y="254" font-size="{size}">{prefix}</text>
  {"".join(t for t in typed if t.startswith("<text"))}
  {cursor}
  <text class="muted sans" x="52" y="300" font-size="15">Ciência da Computação · UFOP  ·  Data Analytics · TerraLab</text>
</g>
<g class="fade" style="animation-delay:.3s">
  <g transform="translate(700,62)">
    <g clip-path="url(#morph)"><rect width="200" height="200" fill="#ffffff"/>
      <image x="6" y="6" width="188" height="188" href="data:image/jpeg;base64,{avatar}" xlink:href="data:image/jpeg;base64,{avatar}" preserveAspectRatio="xMidYMid slice"/></g>
  </g>
  <g><animateTransform attributeName="transform" type="translate" values="0 0;0 -9;0 0" dur="4s" repeatCount="indefinite"/>
    <rect class="surface line" x="636" y="82" width="138" height="34" rx="14" stroke-width="1"/>
    <text class="ink sans" x="650" y="104" font-size="14" font-weight="600">🐍 Python + SQL</text></g>
  <g><animateTransform attributeName="transform" type="translate" values="0 0;0 -9;0 0" dur="4s" begin="-2s" repeatCount="indefinite"/>
    <rect class="surface line" x="822" y="226" width="150" height="34" rx="14" stroke-width="1"/>
    <text class="ink sans" x="836" y="248" font-size="14" font-weight="600">📍 Belo Horizonte</text></g>
</g>"""
    return svg(w, h, body, defs)


# ---------- títulos de seção ----------
def title(eyebrow, heading, color):
    w, h = 1000, 96
    hw = text_w(heading, 34) * 1.02
    body = f"""<text class="accent sans fade" x="4" y="26" font-size="13" font-weight="700" letter-spacing="2.4">{escape(eyebrow.upper())}</text>
<text class="ink serif fade" style="animation-delay:.15s" x="2" y="68" font-size="34" font-weight="600">{escape(heading)}</text>
<path d="M4,84 q 12,-8 24,0 t 24,0 t 24,0 t 24,0 t 24,0" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-dasharray="140" stroke-dashoffset="140">
  <animate attributeName="stroke-dashoffset" values="140;0;0;140" keyTimes="0;.25;.8;1" dur="6s" repeatCount="indefinite"/></path>"""
    return svg(w, h, body)


# ---------- fatos (sobre mim) ----------
def facts():
    items = [("🎓", "Ciência da Computação", "UFOP · 2022 – 2026", "lilac"),
             ("🇦🇹", "Intercâmbio em Industrial Data Science", "Montanuniversität Leoben · 2026", "sky"),
             ("📊", "Data Analytics", "Laboratório TerraLab · atual", "mint"),
             ("🌍", "Inglês avançado", "Idiomas", "peach")]
    w, h = 1000, 176
    out = []
    for i, (ic, t, sub, c) in enumerate(items):
        x, y = (i % 2) * 504, (i // 2) * 92
        out.append(f"""<g class="fade" style="animation-delay:{.1+i*.12:.2f}s">
  <rect class="surface line" x="{x+.5}" y="{y+.5}" width="495" height="80" rx="18" stroke-width="1"/>
  <rect x="{x+18}" y="{y+18}" width="44" height="44" rx="13" fill="{P[c]}"/>
  <text x="{x+40}" y="{y+48}" font-size="21" text-anchor="middle">{ic}</text>
  <text class="ink sans" x="{x+78}" y="{y+37}" font-size="16" font-weight="700">{escape(t)}</text>
  <text class="muted sans" x="{x+78}" y="{y+60}" font-size="14">{escape(sub)}</text>
</g>""")
    return svg(w, h, "\n".join(out))


# ---------- trajetória ----------
def timeline():
    items = [
        ("08/2026 — presente", "Data Analytics", "Laboratório TerraLab · UFOP",
         "Pipelines de ETL em Python e SQL para grandes volumes de dados. Gestão de ambientes com Apache Airflow, Apache Doris e Apache Superset.", "mint"),
        ("02/2026 — 07/2026", "Intercâmbio Acadêmico · Industrial Data Science", "Montanuniversität Leoben · Áustria",
         "Especialização prática em Ciência de Dados Industrial, Machine Learning aplicado e Otimização de Processos.", "sky"),
        ("2024 — 2026", "Vice-Diretora", "Diretório Acadêmico de Ciência da Computação · UFOP",
         "Organização de eventos acadêmicos e workshops técnicos, gestão de equipes e representação estudantil.", "peach"),
        ("2023", "Iniciação Científica · Automação e Pipelines de Dados", "UFOP",
         "Automação de extração, tratamento e integração de dados em Python, com PostgreSQL para estruturação e consultas.", "lilac"),
        ("2019 — 2021", "Técnico em Informática", "Instituto Federal do Norte de Minas Gerais (IFNMG)", "", "butter"),
    ]
    y, out = 0, []
    for i, (when, t, where, desc, c) in enumerate(items):
        lines = wrap(desc, 125) if desc else []
        ch = 92 + len(lines) * 21
        d = f"{.1+i*.15:.2f}"
        txt = "".join(f'<text class="muted sans" x="58" y="{y+102+k*21}" font-size="14">{escape(l)}</text>' for k, l in enumerate(lines))
        out.append(f"""<g class="fade" style="animation-delay:{d}s">
  <rect class="surface line" x="34.5" y="{y+.5}" width="964" height="{ch}" rx="20" stroke-width="1"/>
  <circle cx="12" cy="{y+30}" r="9" fill="{P[c]}" stroke-width="4" class="line"><animate attributeName="r" values="8;10;8" dur="3s" begin="{d}s" repeatCount="indefinite"/></circle>
  <text class="muted sans" x="58" y="{y+30}" font-size="13">{escape(when)}</text>
  <text class="ink sans" x="58" y="{y+54}" font-size="17" font-weight="700">{escape(t)}</text>
  <text class="accent sans" x="58" y="{y+76}" font-size="14" font-weight="600">{escape(where)}</text>
  {txt}
</g>""")
        y += ch + 18
    line = f'<rect x="11" y="20" width="2" height="{y-60}" class="surface" style="fill:#ece6f2"/>'
    return svg(1000, y - 18, line + "\n" + "\n".join(out))


# ---------- cards de projeto ----------
def card(emoji, t, desc, tags, c, delay):
    w, h = 490, 272
    tl = wrap(t, 38)
    dl = wrap(desc, 58)[:3]
    ty = 92
    title_svg = "".join(f'<text class="ink sans" x="26" y="{ty+k*24}" font-size="18" font-weight="700">{escape(l)}</text>' for k, l in enumerate(tl))
    dy = ty + len(tl) * 24 + 4
    desc_svg = "".join(f'<text class="muted sans" x="26" y="{dy+k*21}" font-size="14">{escape(l)}</text>' for k, l in enumerate(dl))
    x, chips = 26, []
    for tg in tags:
        cw = text_w(tg, 12) + 22
        chips.append(f'<rect x="{x}" y="{h-74}" width="{cw:.0f}" height="24" rx="12" fill="{P[c]}"/>'
                     f'<text class="chiptxt sans" x="{x+cw/2:.0f}" y="{h-58}" font-size="12" text-anchor="middle">{escape(tg)}</text>')
        x += cw + 6
    defs = f'<clipPath id="c"><rect width="{w}" height="{h}" rx="22"/></clipPath>'
    body = f"""<g class="fade" style="animation-delay:{delay}s">
<rect class="surface line" x=".5" y=".5" width="{w-1}" height="{h-1}" rx="22" stroke-width="1"/>
<g clip-path="url(#c)"><rect width="{w}" height="6" fill="{P[c]}"><animate attributeName="height" values="6;6;{h};{h};6" keyTimes="0;.6;.7;.9;1" dur="9s" begin="{delay}s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;1;.25;.25;1" keyTimes="0;.6;.7;.9;1" dur="9s" begin="{delay}s" repeatCount="indefinite"/></rect></g>
<text x="26" y="56" font-size="30">{emoji}</text>
{title_svg}
{desc_svg}
{"".join(chips)}
<text class="accent sans" x="26" y="{h-22}" font-size="13" font-weight="600">Ver no GitHub →</text>
</g>"""
    return svg(w, h, body, defs)


PROJECTS = [
    ("bertimbau", "🏳️‍⚧️", "Detecção de discurso transfóbico com BERTimbau",
     "Fine-tuning do BERTimbau para classificar tweets como transfóbicos ou não. 93,1% de acurácia em validação balanceada.",
     ["NLP", "PyTorch", "Transformers"], "rose"),
    ("transcricao", "🎬", "Transcrição de vídeos full-stack",
     "Transcreve áudio e vídeo com upload assíncrono, autenticação, divisão de arquivos grandes e cotas diárias por usuário.",
     ["TypeScript", "Next.js", "Node.js", "Firebase"], "sky"),
    ("mineracao", "⛏️", "Mineração de Dados",
     "Práticas da disciplina de Mineração de Dados: exploração, pré-processamento e modelagem em notebooks.",
     ["Jupyter", "Pandas", "scikit-learn"], "mint"),
    ("ia", "🤖", "Inteligência Artificial",
     "Implementações e exercícios da disciplina de Inteligência Artificial em Python.",
     ["Python", "IA"], "lilac"),
]


# ---------- habilidades ----------
def skills():
    groups = [("📈", "Análise de dados", ["Python", "Pandas", "NumPy", "R", "Estatística", "ETL"], "lilac"),
              ("🧠", "Machine Learning", ["scikit-learn", "PyTorch", "NLP", "TF-IDF"], "mint"),
              ("🗄️", "Dados & SQL", ["SQL", "PostgreSQL", "Modelagem relacional", "Airflow", "Apache Doris"], "sky"),
              ("📊", "Visualização & BI", ["Power BI", "Superset", "Matplotlib", "Jupyter"], "peach"),
              ("⚙️", "Engenharia", ["Git/GitHub", "Docker", "Flask", "REST APIs", "Node.js"], "rose"),
              ("💬", "Linguagens", ["Python", "SQL", "R", "C/C++", "Java", "JavaScript"], "butter")]
    cw, ch, gap = 322, 166, 17
    out = []
    for i, (ic, t, chips, c) in enumerate(groups):
        gx, gy = (i % 3) * (cw + gap), (i // 3) * (ch + gap)
        d = .1 + i * .1
        out.append(f'<g class="fade" style="animation-delay:{d:.1f}s"><rect class="surface line" x="{gx+.5}" y="{gy+.5}" width="{cw}" height="{ch}" rx="20" stroke-width="1"/>'
                   f'<text class="ink sans" x="{gx+20}" y="{gy+36}" font-size="16" font-weight="700">{ic}  {escape(t)}</text>')
        x, y = gx + 20, gy + 54
        for k, chip in enumerate(chips):
            w = text_w(chip, 13) + 24
            if x + w > gx + cw - 14:
                x, y = gx + 20, y + 36
            out.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur="3s" begin="{(i*6+k)*.25:.2f}s" repeatCount="indefinite"/>'
                       f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="28" rx="14" fill="{P[c]}"/>'
                       f'<text class="chiptxt sans" x="{x+w/2:.0f}" y="{y+19}" font-size="13" text-anchor="middle">{escape(chip)}</text></g>')
            x += w + 8
        out.append("</g>")
    return svg(3 * cw + 2 * gap + 1, 2 * ch + gap + 1, "\n".join(out))


# ---------- botões de contato ----------
def button(label, primary=False):
    w = int(text_w(label, 15) + 48)
    h = 46
    if primary:
        style = ('<style>.p{fill:#2f2a3d}.pt{fill:#fdfbf7}@media (prefers-color-scheme: dark){.p{fill:#f2eefb}.pt{fill:#1c1a24}}</style>')
        body = (f'{style}<rect class="p" width="{w}" height="{h}" rx="23"/>'
                f'<text class="pt sans" x="{w/2}" y="29" font-size="15" font-weight="600" text-anchor="middle">{escape(label)}</text>')
    else:
        body = (f'<rect class="surface line" x=".5" y=".5" width="{w-1}" height="{h-1}" rx="22.5" stroke-width="1"/>'
                f'<text class="ink sans" x="{w/2}" y="29" font-size="15" font-weight="600" text-anchor="middle">{escape(label)}</text>')
    return svg(w, h, body)


def contact():
    w, h = 1000, 210
    clip, base = frame(w, h)
    body = f"""{base}
<text class="accent sans fade" x="500" y="64" font-size="13" font-weight="700" letter-spacing="2.4" text-anchor="middle">CONTATO</text>
<text class="ink serif fade" style="animation-delay:.15s" x="500" y="114" font-size="38" font-weight="600" text-anchor="middle">Vamos conversar?</text>
<text class="muted sans fade" style="animation-delay:.3s" x="500" y="156" font-size="16" text-anchor="middle">Estou buscando oportunidades em ciência de dados. Fique à vontade para me chamar!</text>"""
    return svg(w, h, body, clip + BLUR)


def footer():
    w, h = 1000, 60
    dots = "".join(
        f'<circle cx="{410+i*30}" cy="20" r="6" fill="{c}"><animate attributeName="cy" values="20;12;20" dur="1.6s" begin="{i*.15:.2f}s" repeatCount="indefinite"/></circle>'
        for i, c in enumerate(P.values()))
    return svg(w, h, dots + '<text class="muted sans" x="500" y="52" font-size="13" text-anchor="middle">Feito com 💜 por Mariana Macedo</text>')


def main():
    files = {
        "header.svg": header(),
        "titulo-sobre.svg": title("Sobre mim", "Dados, curiosidade e café", P["lilac"]),
        "titulo-trajetoria.svg": title("Trajetória", "Experiência & formação", P["mint"]),
        "titulo-projetos.svg": title("Projetos", "Coisas que eu construí", P["rose"]),
        "titulo-habilidades.svg": title("Habilidades", "Minha caixa de ferramentas", P["sky"]),
        "fatos.svg": facts(),
        "trajetoria.svg": timeline(),
        "habilidades.svg": skills(),
        "contato.svg": contact(),
        "rodape.svg": footer(),
        "btn-email.svg": button("✉️  E-mail", primary=True),
        "btn-linkedin.svg": button("LinkedIn"),
        "btn-portfolio.svg": button("🌐  Portfólio"),
        "btn-curriculo.svg": button("📄  Currículo"),
    }
    for i, (slug, *args) in enumerate(PROJECTS):
        files[f"projeto-{slug}.svg"] = card(*args, delay=f"{.1 + (i % 2) * .15:.2f}")
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"{len(files)} SVGs gerados")


if __name__ == "__main__":
    main()
