from pathlib import Path
import json, html
R=Path(__file__).parent
E=lambda v: html.escape(str(v if v is not None else ''),quote=True)
def read(path): return json.loads((R/path).read_text(encoding='utf-8'))
def records(folder):
    return sorted((d for f in (R/folder).glob('*.json') if (d:=json.loads(f.read_text(encoding='utf-8'))).get('published',True)),key=lambda d:d.get('order',999))
projects=records('content/projects'); galleries=records('content/galleries'); site=read('content/site.json')
def image(path,label):
    path=str(path or '').lstrip('/')
    return f'<img src="{E(path)}" alt="{E(label)}" loading="lazy">' if path else f'<span class="placeholder">[ {E(label)} ]</span>'
def project(d,i):
    slug=E(d['slug']);title=E(d['title'])
    return f'''<article class="project"><a class="project-visual" href="#project/{slug}"><span class="num">{i:02d} / WORK</span>{image(d.get('cover'),d['title']+' — Project image')}{('<span class="music-cover-data" hidden>'+E(json.dumps([d.get('cover'),*(d.get('gallery') or [])]))+'</span>') if d.get('slug')=='music-videos' else ''}</a><div class="project-info"><div><span class="small">{E(d.get('category'))}</span><h3><a href="#project/{slug}">{title}</a></h3><p>{E(d.get('summary'))}</p></div><div><div class="project-meta"><span>{E(d.get('roles'))}</span><span>{E(d.get('year'))}</span></div><p><a class="link" href="#project/{slug}">Explore project ↗</a></p></div></div></article>'''
def gallery(d,i,n):
    slug=E(d['slug']);title=E(d['title']);cover=d.get('cover')
    img=image(cover,d['title']) if cover else f'<span class="carousel-placeholder">[ {title} ]</span>'
    return f'''<a class="carousel-slide" href="#gallery/{slug}" aria-label="Explore {title}"><div class="carousel-image">{img}<span class="carousel-overlay">VIEW SERIES ↗</span></div><div class="carousel-caption"><span>{i:02d} / {n:02d} &nbsp; {title}</span><span>↗</span></div></a>'''
featured=[p for p in projects if p.get('slug') in ('window-shopper','medusa')]
others=[p for p in projects if p.get('slug') not in ('window-shopper','medusa')]
payload=json.dumps({'projects':projects,'galleries':galleries,'site':site},ensure_ascii=False).replace('<','\\u003c')
s=(R/'template.html').read_text(encoding='utf-8')
for a,b in {'<!--FEATURED-PROJECTS-->':''.join(project(p,i) for i,p in enumerate(featured,1)),
            '<!--OTHER-PROJECTS-->':''.join(project(p,i) for i,p in enumerate(others,len(featured)+1)),
            '<!--GALLERIES-->':''.join(gallery(g,i,len(galleries)) for i,g in enumerate(galleries,1)),
            '<!--SITE-DATA-->':payload,
            '<!--EMAIL-->':E(site.get('email')),
            '<!--ABOUT-->':E(site.get('about')),
            '<!--INTRO-->':E(site.get('intro')),
            '<!--HERO-IMAGE-->':image(site.get('hero_image') or next((x.get('cover') for x in projects if x.get('slug')=='window-shopper'),''),'Featured film still'),
            '<!--ABOUT-COVER-->':image(site.get('about_cover'),'Portrait of Kim-Fabio') if site.get('about_cover') else '<span class="about-portrait-placeholder">YOUR PORTRAIT / ADD IN PAGES CMS</span>'}.items():
    if a not in s and a!='<!--INTRO-->': raise RuntimeError('Template marker missing: '+a)
    s=s.replace(a,b)
(R/'index.html').write_text(s,encoding='utf-8')
print(f'Built index.html: {len(projects)} projects, {len(galleries)} galleries')

# Rechtliche Seiten: Texte müssen vor Veröffentlichung individuell geprüft und ergänzt werden.
legal=read('content/legal.json')
def lines(v):
    return '<br>'.join(E(x) for x in str(v or '').replace('\\n','\n').splitlines())
def section(title,body):
    return f'<section class="legal-section"><h2>{E(title)}</h2>{body}</section>'
def legal_page(title,subtitle,body):
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{E(title)} — Kim-Fabio</title><style>
:root{{--paper:#f1efe9;--ink:#171715;--red:#d22c22}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 Arial,Helvetica,sans-serif}}a{{color:inherit}}header{{padding:17px 3.2%;border-bottom:1px solid var(--ink);display:flex;justify-content:space-between;gap:20px;align-items:center}}header a{{font-size:13px;font-weight:800;text-decoration:none}}main{{max-width:880px;padding:8vw 3.2% 100px;margin:auto}}h1{{font-size:clamp(52px,9vw,110px);line-height:.9;letter-spacing:-.07em;text-transform:uppercase;margin:22px 0 28px}}.eyebrow{{font-size:11px;letter-spacing:.12em;text-transform:uppercase}}.legal-section{{padding:26px 0;border-top:1px solid #bdbab2}}h2{{font-size:20px;line-height:1.2;margin:0 0 14px}}p{{margin:0 0 14px;overflow-wrap:anywhere}}.notice{{border-left:4px solid var(--red);padding:14px 20px;background:#e7e2d8;margin-bottom:38px}}footer{{background:#1c1c1a;color:#fff;padding:32px 3.2%;display:flex;gap:22px;flex-wrap:wrap;font-size:12px}}footer a{{color:#fff}}
</style></head><body><header><a href="index.html#home">KIM-FABIO<span style="color:var(--red)">.</span></a><a href="index.html#home">← Back to portfolio</a></header><main><div class="eyebrow">Legal / {E(subtitle)}</div><h1>{E(title)}<span style="color:var(--red)">.</span></h1><div class="notice"><strong>Vor Veröffentlichung prüfen:</strong> Diese Seite enthält Vorlagen und gegebenenfalls Platzhalter. Angaben in Pages CMS vervollständigen und Datenschutzhinweise an die tatsächlich eingesetzten Dienste anpassen.</div>{body}</main><footer><a href="index.html#home">Portfolio</a><a href="impressum.html">Impressum</a><a href="datenschutz.html">Datenschutz</a></footer></body></html>"""
name=legal.get('operator_name','[VOLLSTÄNDIGER NAME]')
address=legal.get('address','[LADUNGSFÄHIGE ANSCHRIFT]')
mail=legal.get('email','[E-MAIL-ADRESSE]')
operator=f'<p><strong>{E(name)}</strong><br>{lines(address)}</p><p>E-Mail: <a href="mailto:{E(mail)}">{E(mail)}</a></p>'
if legal.get('phone'):operator+=f'<p>Telefon: {E(legal["phone"])}</p>'
if legal.get('vat_id'):operator+=f'<p>Umsatzsteuer-Identifikationsnummer: {E(legal["vat_id"])}</p>'
if legal.get('register'):operator+=f'<p>Registerangaben: {E(legal["register"])}</p>'
if legal.get('extra_imprint'):operator+=f'<p>{lines(legal["extra_imprint"])}</p>'
imprint=section('Angaben gemäß § 5 DDG',operator)+section('Hinweis', '<p>Je nach Rechtsform, Tätigkeit und Inhalt können zusätzliche Pflichtangaben erforderlich sein. Bitte vor Veröffentlichung prüfen.</p>')
(R/'impressum.html').write_text(legal_page('Impressum','Anbieterkennzeichnung',imprint),encoding='utf-8')
privacy=(section('1. Verantwortliche Person',operator)+
 section('2. Hosting und technische Zugriffsdaten',f'<p>Diese Website wird voraussichtlich über {E(legal.get("hosting_provider") or "GitHub Pages (GitHub, Inc., USA)")} bereitgestellt. Beim Aufruf können technisch erforderliche Daten wie IP-Adresse, Datum und Uhrzeit, aufgerufene Ressourcen sowie Browserinformationen verarbeitet werden, um die Website auszuliefern und die Sicherheit zu gewährleisten. Rechtsgrundlage ist regelmäßig Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an einem sicheren und funktionsfähigen Webauftritt). Umfang, Speicherfristen und mögliche Übermittlungen in Drittländer sind anhand der aktuellen Hostingbedingungen zu prüfen.</p><p>Weitere Informationen: <a href="https://docs.github.com/de/site-policy/privacy-policies/github-general-privacy-statement">GitHub Datenschutzhinweise</a>.</p>')+
 section('3. Schriftarten', '<p>Diese Website bindet derzeit Schriftarten von Google Fonts über eine externe Verbindung zu fonts.googleapis.com ein. Dabei kann Ihre IP-Adresse an Google übermittelt werden. <strong>Vor der Veröffentlichung sollte diese externe Einbindung aus Datenschutzgründen geprüft und möglichst durch lokal bereitgestellte Schriftarten ersetzt werden.</strong></p>')+
 section('4. Kontaktaufnahme', '<p>Bei einer Kontaktaufnahme per E-Mail werden die übermittelten Daten zur Bearbeitung Ihrer Anfrage verarbeitet. Rechtsgrundlage ist je nach Anlass Art. 6 Abs. 1 lit. b oder lit. f DSGVO. Die Daten werden nur so lange aufbewahrt, wie dies für die Bearbeitung beziehungsweise gesetzliche Aufbewahrungspflichten erforderlich ist.</p>')+
 section('5. Externe Links und Videos', '<p>Diese Website verlinkt gegebenenfalls auf externe Plattformen wie YouTube oder Vimeo. Beim Anklicken eines externen Links gelten die Datenschutzbestimmungen des jeweiligen Anbieters. Soweit zukünftig Videos direkt eingebettet oder weitere Dienste eingesetzt werden, muss diese Erklärung entsprechend ergänzt und eine mögliche Einwilligungspflicht geprüft werden.</p>')+
 section('6. Cookies und Analyse', '<p>Der aktuell geprüfte Website-Code enthält kein eigenes Analyse- oder Werbetracking und setzt selbst keine nicht notwendigen Cookies. Dies muss nach jeder technischen Erweiterung erneut überprüft werden. Für nicht notwendige Cookies oder vergleichbare Zugriffe kann eine vorherige Einwilligung erforderlich sein.</p>')+
 section('7. Ihre Rechte', '<p>Sie haben nach Maßgabe der DSGVO insbesondere Rechte auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit sowie Widerspruch. Außerdem besteht ein Beschwerderecht bei einer zuständigen Datenschutzaufsichtsbehörde. Zur Wahrnehmung Ihrer Rechte kontaktieren Sie bitte die oben genannte Person.</p>'))
if legal.get('additional_privacy'):privacy+=section('8. Weitere Hinweise',f'<p>{lines(legal["additional_privacy"])}</p>')
(R/'datenschutz.html').write_text(legal_page('Datenschutz','Datenschutzerklärung',privacy),encoding='utf-8')
print('Built impressum.html and datenschutz.html')
