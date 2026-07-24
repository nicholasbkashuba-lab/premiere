#!/usr/bin/env python3
"""
Premiere Research Institute — static site generator.

Single source of truth for every page. Edit the content below, then run:

    python3 build.py

...and every .html page (plus sitemap.xml / robots.txt) is regenerated in place.
Shared chrome (head, header, footer) lives in one place, so nav/branding stay in
sync across the whole site. Add a blog post = one entry in BLOG_POSTS. Add a
newsletter issue = one entry in NEWSLETTER_ISSUES.
"""
import os, json, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# SITE CONFIG
# ----------------------------------------------------------------------------
SITE = {
    "name": "Premiere Research Institute",
    "base": "https://www.premiereresearchinstitute.com",
    "tagline": "Discover Hope with",
    "phone_display": "(561) 851-9400",
    "phone_href": "+15618519400",
    "addr1": "4631 N. Congress Ave, Suite 200",
    "addr2": "West Palm Beach, FL 33407",
    "maps": "https://maps.google.com/?q=4631+N+Congress+Ave+Suite+200+West+Palm+Beach+FL+33407",
    "map_embed": "https://maps.google.com/maps?q=4631+N+Congress+Ave+Suite+200+West+Palm+Beach+FL+33407&z=15&output=embed",
    "hours": "Monday – Friday · 9:00 AM – 4:30 PM",
}
SOCIAL = {
    "instagram": "https://www.instagram.com/premiereresearchinstitute/",
    "facebook": "https://www.facebook.com/PremiereResearchInstitute",
    "tiktok": "https://www.tiktok.com/@askdrwinner",
}

# Absolute base path the site is served under. This repo previews the site in a
# /premiere/ subfolder of the First Rehab deployment, so all asset/link paths are
# emitted absolute from here (robust to trailing-slash / clean-URL handling).
# When Premiere gets its own domain at the web root, set this to "/".
ROOT = "/"

# Primary nav — (label, href, active-key)
NAV = [
    ("Clinical Trials", "clinical-trials.html", "trials"),
    ("About", "about.html", "about"),
    ("Our Team", "team.html", "team"),
    ("Events", "events.html", "events"),
    ("Blog", "blog/index.html", "blog"),
]

YEAR = 2026  # build year (kept static so rebuilds are deterministic)

# ----------------------------------------------------------------------------
# Small inline SVG icons (kept here so pages stay readable)
# ----------------------------------------------------------------------------
IC_PHONE = ('<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><path fill="currentColor" '
            'd="M6.6 10.8a15.5 15.5 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.24 11.4 11.4 0 0 0 3.6.58 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.4 11.4 0 0 0 .58 3.6 1 1 0 0 1-.24 1z"/></svg>')
IC_ARROW = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M13 6l6 6-6 6"/></svg>')
IC_BACK = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="none" stroke="currentColor" '
           'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M19 12H5M11 6l-6 6 6 6"/></svg>')

def icon_condition(key):
    icons = {
        "alz": '<path d="M24 6c-6 0-9 4-9 9 0 2-2 3-2 6s2 4 2 6c0 5 3 9 9 9"/><path d="M24 6c6 0 9 4 9 9 0 2 2 3 2 6s-2 4-2 6c0 5-3 9-9 9"/><path d="M24 6v30M18 16h4M26 22h4M18 28h5"/>',
        "park": '<path d="M8 30c3-2 4-6 4-10 0-7 5-12 12-12s12 5 12 12c0 4 1 8 4 10"/><path d="M14 34c2 3 6 5 10 5s8-2 10-5"/><circle cx="18" cy="20" r="1.6" fill="currentColor" stroke="none"/><circle cx="30" cy="20" r="1.6" fill="currentColor" stroke="none"/>',
        "mig": '<path d="M6 24h6l3-8 6 18 5-24 5 16 3-2h8"/>',
        "ms": '<path d="M24 6v36M24 12c-4-3-9-2-11 1M24 12c4-3 9-2 11 1M24 22c-5-3-11-1-13 3M24 22c5-3 11-1 13 3M24 32c-4-2-8-1-10 2M24 32c4-2 8-1 10 2"/>',
    }
    return (f'<svg viewBox="0 0 48 48" width="30" height="30"><g fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{icons[key]}</g></svg>')

# ----------------------------------------------------------------------------
# SHARED CHROME
# ----------------------------------------------------------------------------
def esc(s):
    return html.escape(s, quote=True)

def org_schema(p):
    data = {
        "@context": "https://schema.org",
        "@type": ["MedicalOrganization", "MedicalBusiness"],
        "@id": SITE["base"] + "/#organization",
        "name": SITE["name"],
        "url": SITE["base"] + "/",
        "telephone": SITE["phone_display"],
        "medicalSpecialty": "Neurology",
        "description": "Neurological clinical research center conducting trials for Alzheimer's and memory loss, Parkinson's disease, migraine, and multiple sclerosis in West Palm Beach, Florida.",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE["addr1"],
            "addressLocality": "West Palm Beach",
            "addressRegion": "FL",
            "postalCode": "33407",
            "addressCountry": "US",
        },
        "openingHours": "Mo-Fr 09:00-16:30",
        "sameAs": list(SOCIAL.values()),
    }
    return '<script type="application/ld+json">' + json.dumps(data) + '</script>'

def head(p, title, desc, canonical, og_image=None, page_type="website", extra_head=""):
    og_image = og_image or (p + "assets/img/logo-original.jpeg")
    canon = SITE["base"] + "/" + canonical
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<script>document.documentElement.classList.add('js')</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#081726">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{page_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..500&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}assets/css/styles.css">
<link rel="icon" type="image/png" sizes="32x32" href="{p}assets/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="512x512" href="{p}assets/img/favicon-512.png">
<link rel="apple-touch-icon" href="{p}assets/img/apple-touch-icon.png">
{org_schema(p)}
{extra_head}</head>
<body>
"""

def header(p, active=""):
    def _nav_link(label, href, key):
        cls = ' class="is-active"' if key == active else ''
        return f'<a href="{p}{href}"{cls}>{esc(label)}</a>'
    links = "\n      ".join(_nav_link(label, href, key) for label, href, key in NAV)
    return f"""<header class="site-header" id="siteHeader">
  <div class="wrap header-inner">
    <a href="{p}index.html" class="brand" aria-label="Premiere Research Institute — Discover Hope">
      <span class="brand-mark" aria-hidden="true"></span>
      <span class="brand-word">
        <span class="brand-kicker">Discover Hope with</span>
        <strong>Premiere</strong>
        <span class="brand-sub">Research Institute</span>
      </span>
    </a>

    <nav class="nav" id="primaryNav" aria-label="Primary">
      {links}
      <div class="mnav-cta">
        <a href="{p}newsletter.html" class="mnav-extra">Newsletter</a>
        <a href="tel:{SITE['phone_href']}" class="phone-link">{IC_PHONE}<span>{SITE['phone_display']}</span></a>
        <a href="{p}contact.html" class="btn btn-primary">See if you qualify</a>
      </div>
    </nav>

    <div class="header-cta">
      <a href="tel:{SITE['phone_href']}" class="phone-link" aria-label="Call Premiere Research Institute">{IC_PHONE}<span>{SITE['phone_display']}</span></a>
      <a href="{p}contact.html" class="btn btn-primary btn-sm">See if you qualify</a>
    </div>

    <button class="nav-toggle" id="navToggle" aria-label="Open menu" aria-expanded="false" aria-controls="primaryNav">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>
"""

def footer(p):
    ig = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" '
          'fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" '
          'stroke-width="1.8"/><circle cx="17.2" cy="6.8" r="1.2" fill="currentColor"/></svg>')
    fb = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" '
          'd="M14 9V7.5c0-.7.5-1 1.2-1H17V3.5h-2.4C11.9 3.5 11 5 11 7v2H9v3h2v9h3v-9h2.2l.5-3z"/></svg>')
    tk = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" '
          'd="M16.5 3c.3 2 1.6 3.6 3.5 3.9v2.7c-1.3.1-2.6-.3-3.7-1v5.9a5.6 5.6 0 1 1-5.6-5.6c.3 0 .6 0 .9.1v2.8a2.8 2.8 0 1 0 2 2.7V3z"/></svg>')
    return f"""<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <a href="{p}index.html" class="brand brand-footer" aria-label="Premiere Research Institute — Discover Hope">
        <span class="brand-mark" aria-hidden="true"></span>
        <span class="brand-word">
          <span class="brand-kicker">Discover Hope with</span>
          <strong>Premiere</strong>
          <span class="brand-sub">Research Institute</span>
        </span>
      </a>
      <p class="footer-tag">Advancing neurology through clinical research &mdash; in the heart of Palm Beach County.</p>
      <div class="footer-social">
        <a href="{SOCIAL['instagram']}" target="_blank" rel="noopener" aria-label="Premiere Research Institute on Instagram">{ig}</a>
        <a href="{SOCIAL['facebook']}" target="_blank" rel="noopener" aria-label="Premiere Research Institute on Facebook">{fb}</a>
        <a href="{SOCIAL['tiktok']}" target="_blank" rel="noopener" aria-label="Ask Dr. Winner on TikTok">{tk}</a>
      </div>
    </div>

    <nav class="footer-col" aria-label="Site">
      <h4>Explore</h4>
      <a href="{p}clinical-trials.html">Clinical Trials</a>
      <a href="{p}about.html">About</a>
      <a href="{p}team.html">Our Team</a>
      <a href="{p}events.html">Events</a>
      <a href="{p}newsletter.html">Newsletter</a>
      <a href="{p}blog/index.html">Blog</a>
    </nav>

    <div class="footer-col">
      <h4>Visit &amp; contact</h4>
      <a href="{SITE['maps']}" target="_blank" rel="noopener">{SITE['addr1']}<br>{SITE['addr2']}</a>
      <a href="tel:{SITE['phone_href']}">{SITE['phone_display']}</a>
      <span class="footer-plain">Mon&ndash;Fri &middot; 9:00 AM &ndash; 4:30 PM</span>
    </div>

    <div class="footer-col footer-cta-col">
      <h4>Ready to begin?</h4>
      <p class="footer-plain">See if you or a loved one may qualify for a current study.</p>
      <a href="{p}contact.html" class="btn btn-primary btn-sm">See if you qualify</a>
    </div>
  </div>

  <div class="wrap footer-bar">
    <p>&copy; <span id="year">{YEAR}</span> Premiere Research Institute. All rights reserved.</p>
    <p class="footer-fine">Clinical research is voluntary. Nothing on this site is medical advice.
       In an emergency, call 911.</p>
  </div>
</footer>
"""

def mobile_call(p):
    return (f'\n<a class="mobile-call" href="tel:{SITE["phone_href"]}" aria-label="Call Premiere Research Institute">'
            f'{IC_PHONE}<span>Call {SITE["phone_display"]}</span></a>\n')

def page(path, title, desc, canonical, body, active="", og_image=None, page_type="website", extra_head=""):
    p = ROOT  # absolute base — works at any URL depth and regardless of trailing slash
    doc = head(p, title, desc, canonical, og_image, page_type, extra_head)
    doc += header(p, active)
    doc += body.replace("{p}", p)
    doc += footer(p)
    doc += mobile_call(p)
    doc += f'\n<script src="{p}assets/js/main.js" defer></script>\n</body>\n</html>\n'
    out = os.path.join(HERE, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return path

# ----------------------------------------------------------------------------
# REUSABLE CONTENT BLOCKS
# ----------------------------------------------------------------------------
def page_hero(eyebrow, title_html, sub, crumbs):
    crumb_html = " ".join(
        (f'<a href="{{p}}{href}">{esc(label)}</a>' if href else f'<span aria-current="page">{esc(label)}</span>')
        + ('<span class="bc-sep" aria-hidden="true">/</span>' if i < len(crumbs) - 1 else "")
        for i, (label, href) in enumerate(crumbs)
    )
    return f"""  <section class="page-hero">
    <div class="page-hero-bg" aria-hidden="true"></div>
    <div class="wrap">
      <nav class="breadcrumb reveal" aria-label="Breadcrumb">{crumb_html}</nav>
      <p class="eyebrow eyebrow-light reveal"><span class="eyebrow-dot"></span>{esc(eyebrow)}</p>
      <h1 class="page-hero-title reveal">{title_html}</h1>
      <p class="page-hero-sub reveal">{sub}</p>
    </div>
  </section>
"""

def cta_band():
    return """  <section class="section page-cta">
    <div class="page-cta-bg" aria-hidden="true"></div>
    <div class="wrap page-cta-inner">
      <h2 class="on-dark reveal">See if you or a loved one <em>may qualify.</em></h2>
      <p class="section-sub on-dark reveal">It's free, confidential, and there's no obligation &mdash;
         a short conversation is all it takes to begin.</p>
      <div class="page-cta-actions reveal">
        <a href="{p}contact.html" class="btn btn-primary btn-lg">See if you qualify</a>
        <a href="tel:%s" class="btn btn-ghost btn-lg">%s %s</a>
      </div>
    </div>
  </section>
""" % (SITE["phone_href"], IC_PHONE, SITE["phone_display"])

WHY_CARDS = [
    ("01", "Emerging treatments, early", "Access promising therapies years before they're widely available &mdash; when other options are limited, a trial can open a new door."),
    ("02", "Care at no cost", "Study-related exams, testing, and investigational treatment are provided at no charge. Health insurance is not required to take part."),
    ("03", "Expert, close monitoring", "Board-certified neurologists and research staff follow your health closely throughout the study &mdash; often more frequently than routine care."),
    ("04", "Compensation for your time", "Many studies compensate participants for time and travel, recognizing the commitment that research participation asks of you."),
    ("05", "Advancing the science", "Your participation helps bring new treatments to everyone who will need them &mdash; a contribution that outlasts the study itself."),
    ("06", "Always your choice", "Participation is fully voluntary and fully informed. You may ask questions at any time and withdraw whenever you wish, without affecting your regular care."),
]

def why_grid():
    cards = "\n".join(
        f"""        <article class="wcard reveal">
          <div class="wcard-num" aria-hidden="true">{n}</div>
          <h3>{t}</h3>
          <p>{d}</p>
        </article>""" for n, t, d in WHY_CARDS)
    return f"""  <section class="section why">
    <span class="giant-word on-dark-word" aria-hidden="true">Participate</span>
    <div class="why-bg" aria-hidden="true"></div>
    <div class="wrap">
      <div class="section-head center">
        <p class="eyebrow eyebrow-light reveal"><span class="eyebrow-dot"></span>Why participate</p>
        <h2 class="on-dark reveal">More than a trial. A <em>different kind of care.</em></h2>
        <p class="section-sub on-dark reveal">Clinical research offers something standard appointments often can't:
           time, attention, and access to what medicine is about to become.</p>
      </div>
      <div class="why-grid">
{cards}
      </div>
    </div>
  </section>
"""

PROCESS_STEPS = [
    ("Reach out", "Call us or complete the short form. Tell us a little about the condition and symptoms you're facing &mdash; there's no cost and no obligation."),
    ("Pre-screening", "Our coordinators review current studies and ask a few questions by phone to see which trials you may be a fit for."),
    ("Screening visit", "If a study looks like a match, you'll meet our team, review the details fully, and complete a screening evaluation &mdash; questions welcome at every step."),
    ("Participate &amp; be cared for", "Take part with close, ongoing monitoring from neurologists and research staff who know you and your condition throughout the study."),
]

def process_section():
    steps = "\n".join(
        f"""        <li class="step reveal">
          <span class="step-dot" aria-hidden="true">{i+1}</span>
          <div><h3>{t}</h3><p>{d}</p></div>
        </li>""" for i, (t, d) in enumerate(PROCESS_STEPS))
    return f"""  <section class="section process">
    <div class="wrap process-grid">
      <div class="process-intro">
        <p class="eyebrow reveal"><span class="eyebrow-dot"></span>The process</p>
        <h2 class="reveal">From first call to first visit &mdash; <em>simple, and at your pace.</em></h2>
        <p class="lede reveal">Reaching out doesn't commit you to anything. It simply starts a conversation with our
           research team about whether a study might be right for you.</p>
        <a href="{{p}}contact.html" class="btn btn-primary reveal">Start the conversation</a>
      </div>
      <ol class="steps">
{steps}
      </ol>
    </div>
  </section>
"""

# Director (feature card + detail page)
LEAD = {
    "mono": "PW", "name": "Paul Winner", "suf": "DO, FAAN, FAHS", "slug": "paul-winner",
    "role": "Senior Director",
    "spec": "Headache Medicine &amp; Neurology",
    "cred": "Senior Director, Premiere Research Institute &middot; Palm Beach Memory Disorder Center &middot; Palm Beach Headache Center",
    "short": "A nationally recognized leader in headache medicine and neurology, directing our research and two specialized Palm Beach centers.",
    "bio": [
        "Dr. Paul Winner is a nationally recognized leader in neurology and headache medicine and the Senior Director of Premiere Research Institute. He also directs the Palm Beach Memory Disorder Center and the Palm Beach Headache Center &mdash; bringing expertise in both cognitive and headache disorders under one roof.",
        "As a Fellow of the American Academy of Neurology (FAAN) and the American Headache Society (FAHS), Dr. Winner has helped guide the clinical development of therapies now used for migraine and neurological disease. He leads Premiere's research with a conviction that shapes everything we do: that the best care and the next breakthrough should live under the same roof.",
        "A frequent speaker and educator, Dr. Winner shares the latest in Alzheimer's care, brain health, and neurological research with patients, caregivers, and communities across the region.",
    ],
    "focus": ["Headache &amp; migraine medicine", "Cognitive &amp; memory disorders", "Clinical research leadership"],
    "facts": [("FAAN", "American Academy of Neurology"), ("FAHS", "American Headache Society"), ("3", "Palm Beach centers directed")],
}

# 4 physician specialists (feature cards + detail pages)
DOCTORS = [
    {"mono": "RS", "name": "Reed Stone", "suf": "MD, FAAN", "slug": "reed-stone",
     "spec": "Neuromuscular Specialties", "role": "Neuromuscular Specialist",
     "short": "Board-certified neurologist focused on the nerve and muscle conditions that affect strength, sensation, and mobility.",
     "bio": [
        "Dr. Reed Stone is a board-certified neurologist whose work centers on neuromuscular medicine &mdash; the disorders that affect the nerves and muscles responsible for strength, sensation, and movement. As a Fellow of the American Academy of Neurology, he brings a careful, evidence-minded approach to both patient care and clinical research.",
        "At Premiere Research Institute, Dr. Stone helps evaluate therapies for neurological conditions, guiding participants through studies with the same attention he brings to the exam room. His focus is on clarity and comfort &mdash; making sure patients and families understand every step.",
     ],
     "focus": ["Neuromuscular disorders", "Nerve &amp; muscle conditions", "Clinical research participation"]},
    {"mono": "AD", "name": "Arnaldo Da Silva", "suf": "MD", "slug": "arnaldo-da-silva",
     "spec": "Migraine &amp; Headache", "role": "Migraine &amp; Headache Specialist",
     "short": "Specialist in migraine and headache medicine, helping guide acute and preventive treatment studies for chronic and episodic patients.",
     "bio": [
        "Dr. Arnaldo Da Silva specializes in migraine and headache medicine &mdash; an area where new therapies have transformed what's possible for patients in recent years. He works closely with people whose lives are disrupted by frequent or severe headache, helping them explore both prevention and relief.",
        "As part of the Premiere Research Institute team, Dr. Da Silva helps guide acute and preventive migraine studies, bringing emerging treatments within reach for the chronic and episodic patients who need them most.",
     ],
     "focus": ["Migraine &mdash; chronic &amp; episodic", "Acute &amp; preventive treatment", "Headache clinical trials"]},
    {"mono": "RC", "name": "Robert Coppola", "suf": "DO", "slug": "robert-coppola",
     "spec": "Cognitive, Memory Loss &amp; MS", "role": "Cognitive &amp; MS Specialist",
     "short": "Specialist in cognitive and memory disorders and multiple sclerosis, from early evaluation through ongoing, attentive care.",
     "bio": [
        "Dr. Robert Coppola focuses on cognitive and memory disorders and multiple sclerosis &mdash; conditions where early evaluation and ongoing, attentive care can make a meaningful difference. He partners with patients and families through diagnosis, treatment, and, when appropriate, research participation.",
        "At Premiere Research Institute, Dr. Coppola contributes to memory and MS studies, helping translate promising science into real options for the people he cares for.",
     ],
     "focus": ["Cognitive &amp; memory disorders", "Multiple sclerosis", "Memory &amp; MS research"]},
    {"mono": "MA", "name": "Michael Alosilla", "suf": "MD", "slug": "michael-alosilla",
     "spec": "Movement Disorders", "role": "Movement-Disorders Specialist",
     "short": "Movement-disorders specialist focused on Parkinson's disease and the related conditions that affect coordination and control.",
     "bio": [
        "Dr. Michael Alosilla is a movement-disorders specialist with a focus on Parkinson's disease and related conditions that affect coordination, balance, and control. He works to help patients maintain function and quality of life as they navigate these diagnoses.",
        "As an investigator at Premiere Research Institute, Dr. Alosilla helps evaluate new therapies for Parkinson's and movement disorders, guiding participants with expertise and care throughout each study.",
     ],
     "focus": ["Parkinson's disease", "Movement disorders", "Parkinson's clinical trials"]},
]

def _photo_path(doc):
    """Convention: assets/team/<slug>.jpg — used automatically when the file exists."""
    p = f"assets/team/{doc['slug']}.jpg"
    return p if os.path.exists(os.path.join(HERE, p)) else None

def _portrait_html(doc, base_cls):
    ph = _photo_path(doc)
    if ph:
        alt = f"{doc['name']}, {doc['suf']}".replace("&amp;", "&")
        return (f'<div class="{base_cls} has-photo">'
                f'<img src="{{p}}{ph}" alt="{esc(alt)}" loading="lazy">'
                f'<span class="ld-ring" aria-hidden="true"></span></div>')
    return (f'<div class="{base_cls}" aria-hidden="true">'
            f'<span class="ld-monogram">{doc["mono"]}</span><span class="ld-ring"></span></div>')

def _tcard_portrait(d):
    ph = _photo_path(d)
    if ph:
        alt = f"{d['name']}, {d['suf']}".replace("&amp;", "&")
        return f'<div class="tcard-portrait has-photo"><img src="{{p}}{ph}" alt="{esc(alt)}" loading="lazy"></div>'
    return f'<div class="tcard-portrait" aria-hidden="true"><span>{d["mono"]}</span></div>'

def render_tcards():
    out = []
    for d in DOCTORS:
        out.append(f"""        <article class="tcard reveal">
          {_tcard_portrait(d)}
          <h3>{d['name']}, <span class="tc-suf">{d['suf']}</span></h3>
          <p class="tc-role">{d['spec']}</p>
          <p>{d['short']}</p>
          <a href="{{p}}team/{d['slug']}.html" class="tcard-more">Read bio {IC_ARROW}</a>
        </article>""")
    return "\n".join(out)

def lead_doctor():
    facts = "\n".join(f"            <li><strong>{a}</strong> {b}</li>" for a, b in LEAD["facts"])
    return f"""      <article class="lead-doctor reveal">
        {_portrait_html(LEAD, "ld-portrait")}
        <div class="ld-body">
          <p class="ld-role">{LEAD['role']}</p>
          <h3>{LEAD['name']}, {LEAD['suf']}</h3>
          <p class="ld-cred">{LEAD['cred']}</p>
          <p>{LEAD['bio'][0]}</p>
          <ul class="ld-facts">
{facts}
          </ul>
          <a href="{{p}}team/{LEAD['slug']}.html" class="link-arrow" style="margin-top:1.4rem">Read Dr. Winner's full bio {IC_ARROW}</a>
        </div>
      </article>
"""

# ----------------------------------------------------------------------------
# HOME PAGE
# ----------------------------------------------------------------------------
def home_body():
    docs = render_tcards()
    rcards = ""
    conds = [
        ("alz", "Alzheimer's &amp; Memory Loss", "From mild cognitive impairment to moderate Alzheimer's, our memory studies test the next generation of disease-modifying and symptom therapies."),
        ("park", "Parkinson's Disease", "Studies targeting motor symptoms, \"off\" time, and the psychosis and daily-living challenges that come with Parkinson's progression."),
        ("mig", "Migraine", "Trials for both the acute treatment of attacks and the prevention of chronic and episodic migraine, including next-generation therapies."),
        ("ms", "Multiple Sclerosis", "Research into therapies that slow progression and protect function for people living with relapsing and progressive forms of MS."),
    ]
    for i, (k, t, d) in enumerate(conds):
        rcards += f"""        <article class="rcard reveal" style="--i:{i}">
          <div class="rcard-glow" aria-hidden="true"></div>
          <div class="rcard-icon" aria-hidden="true">{icon_condition(k)}</div>
          <h3>{t}</h3>
          <p>{d}</p>
          <span class="rcard-tag">Now enrolling</span>
        </article>
"""
    faqs = [
        ("Does it cost anything to participate?", "No. Study-related visits, exams, testing, and the investigational treatment are provided at no cost to you, and health insurance is not required to participate. Many studies also compensate participants for time and travel."),
        ("Is participating in a clinical trial safe?", "Every study we conduct is FDA-regulated and reviewed by an independent ethics board before it begins. You're monitored closely by board-certified neurologists throughout, and the potential benefits and risks are explained in full before you decide anything."),
        ("Will I have to stop seeing my own doctor?", "Not at all. Research participation is designed to work alongside your regular care. With your permission, we're glad to coordinate with your existing physicians."),
        ("What if I change my mind?", "Participation is entirely voluntary. You may ask questions at any time and choose to withdraw from a study whenever you wish, for any reason, without affecting your regular medical care."),
        ("How do I know if I qualify?", "Each study has its own eligibility criteria based on factors like diagnosis, age, and health history. The simplest path is to reach out — our coordinators will ask a few questions and let you know which studies you may be a fit for."),
        ("Will I be given a placebo?", "It depends on the study's design. Whether a trial includes a placebo group, and your chances of receiving it, are explained fully during the informed-consent process before you enroll, so you can decide with a complete picture."),
    ]
    faq_items = "\n".join(
        f"""        <details class="faq-item reveal">
          <summary>{q}<span class="faq-plus" aria-hidden="true"></span></summary>
          <div class="faq-a"><p>{a}</p></div>
        </details>""" for q, a in faqs)

    return f"""<main id="home">

  <section class="hero">
    <canvas class="hero-neural" id="neuralCanvas" aria-hidden="true"></canvas>
    <div class="hero-veil" aria-hidden="true"></div>
    <div class="wrap hero-inner">
      <p class="eyebrow eyebrow-light reveal"><span class="eyebrow-dot"></span>Clinical Research &middot; West Palm Beach, Florida</p>
      <h1 class="hero-title reveal">Tomorrow's neurology,<br><span class="grad-text">in trial today.</span></h1>
      <p class="hero-lede reveal">Premiere Research Institute conducts groundbreaking clinical trials for Alzheimer's,
        Parkinson's, migraine, and multiple sclerosis &mdash; opening the door to emerging treatments,
        expert monitoring, and hope for patients and families.</p>
      <div class="hero-actions reveal">
        <a href="{{p}}contact.html" class="btn btn-primary btn-lg">See if you qualify</a>
        <a href="{{p}}clinical-trials.html" class="btn btn-ghost btn-lg">Explore our research {IC_ARROW}</a>
      </div>
      <dl class="hero-stats reveal">
        <div><dt data-count="4" data-suffix="">0</dt><dd>Neurological focus areas</dd></div>
        <div class="hs-div" aria-hidden="true"></div>
        <div><dt data-count="5" data-suffix="">0</dt><dd>Physician specialists</dd></div>
        <div class="hs-div" aria-hidden="true"></div>
        <div><dt data-prefix="$" data-count="0" data-suffix="">0</dt><dd>Cost to participate</dd></div>
      </dl>
    </div>
    <a href="#trust" class="scroll-cue" aria-label="Scroll down"><span></span></a>
  </section>

  <section class="trust" id="trust" aria-label="Credentials">
    <div class="marquee" aria-hidden="true">
      <div class="marquee-track">
        {"".join('<span>%s</span><i>&bull;</i>' % s for s in (["Board-certified neurologists","Study care at no cost","No insurance required","FDA-regulated trials","Compensation for time &amp; travel","Nationally recognized investigators"]*2))}
      </div>
    </div>
  </section>

  <section class="section about" id="about">
    <div class="wrap about-grid">
      <div class="about-visual reveal">
        <div class="orb-card brain-card">
          <canvas id="brainCanvas" role="img" aria-label="Interactive three-dimensional model of a human brain, rendered as a constellation of glowing connected points"></canvas>
        </div>
      </div>
      <div class="about-copy">
        <p class="eyebrow reveal"><span class="eyebrow-dot"></span>Who we are</p>
        <h2 class="reveal">A research institute devoted <em>entirely to the brain.</em></h2>
        <p class="lede reveal">Our neurologists work at the front lines of clinical research &mdash; testing the
          therapies that become tomorrow's standard of care. We exist for one purpose: to move neuroscience forward
          while giving our neighbors real access to what's next.</p>
        <p class="reveal">Every study we run is reviewed, FDA-regulated, and led by physicians who treat these conditions
          every day. Participants are cared for like patients first and volunteers second &mdash; monitored closely,
          informed fully, and never charged for study-related care.</p>
        <ul class="about-points reveal">
          <li><span class="tick" aria-hidden="true"></span>Physician-led, patient-centered research</li>
          <li><span class="tick" aria-hidden="true"></span>Access to therapies years before they reach pharmacies</li>
          <li><span class="tick" aria-hidden="true"></span>A single location, close to home, in West Palm Beach</li>
        </ul>
        <a href="{{p}}about.html" class="link-arrow reveal">More about our institute {IC_ARROW}</a>
      </div>
    </div>
  </section>

  <section class="section research" id="research">
    <span class="giant-word" aria-hidden="true">Research</span>
    <div class="wrap">
      <div class="section-head center">
        <p class="eyebrow reveal"><span class="eyebrow-dot"></span>Research areas</p>
        <h2 class="reveal">Four conditions. One <em>relentless focus.</em></h2>
        <p class="section-sub reveal">Our active and upcoming studies concentrate on the neurological conditions that
           touch the most families. Explore where you or a loved one might fit.</p>
      </div>
      <div class="research-grid">
{rcards}      </div>
      <div class="section-cta reveal"><a href="{{p}}clinical-trials.html" class="btn btn-outline">View all current studies {IC_ARROW}</a></div>
      <p class="research-foot reveal">Don't see your condition? New studies open frequently.
        <a href="{{p}}contact.html" class="link-arrow inline">Join our registry and we'll reach out when one matches {IC_ARROW}</a></p>
    </div>
  </section>

{why_grid()}
{process_section()}
  <section class="statband" aria-label="By the numbers">
    <div class="wrap statband-grid">
      <div class="reveal"><span class="stat-n" data-count="5" data-suffix="">0</span><span class="stat-l">Physician specialists</span></div>
      <div class="reveal"><span class="stat-n" data-count="4" data-suffix="">0</span><span class="stat-l">Neurological focus areas</span></div>
      <div class="reveal"><span class="stat-n" data-prefix="$" data-count="0" data-suffix="">0</span><span class="stat-l">Cost to participate</span></div>
      <div class="reveal"><span class="stat-n" data-count="100" data-suffix="%">0</span><span class="stat-l">Study care covered</span></div>
    </div>
  </section>

  <section class="section team" id="team">
    <span class="giant-word" aria-hidden="true">Our Team</span>
    <div class="wrap">
      <div class="section-head center">
        <p class="eyebrow reveal"><span class="eyebrow-dot"></span>Our team</p>
        <h2 class="reveal">Led by neurologists who treat these conditions <em>every day.</em></h2>
        <p class="section-sub reveal">Research at Premiere is directed by physicians recognized nationally for their
           work in cognitive and neurological care.</p>
      </div>
{lead_doctor()}      <div class="team-grid">
{docs}
      </div>
      <div class="section-cta reveal"><a href="{{p}}team.html" class="btn btn-outline">Meet the full team {IC_ARROW}</a></div>
    </div>
  </section>

  <section class="section mission">
    <div class="wrap mission-inner">
      <svg class="quote-mark" viewBox="0 0 48 48" width="56" height="56" aria-hidden="true"><path fill="currentColor" d="M20 34H8V22c0-7 4-11 12-12v5c-4 1-6 3-6 7h6v12zm20 0H28V22c0-7 4-11 12-12v5c-4 1-6 3-6 7h6v12z"/></svg>
      <blockquote class="reveal">The best care and the next breakthrough should live <em>under the same roof</em>. That belief is why
        we exist &mdash; to give our neighbors in Palm Beach County a real seat at the frontier of neurology.</blockquote>
      <p class="mission-attr reveal">The mission of Premiere Research Institute</p>
    </div>
  </section>

{events_section(home=True)}
{newsletter_section(home=True)}
  <section class="section faq" id="faq">
    <span class="giant-word" aria-hidden="true">Questions</span>
    <div class="wrap faq-grid">
      <div class="faq-intro">
        <p class="eyebrow reveal"><span class="eyebrow-dot"></span>Common questions</p>
        <h2 class="reveal">What to know <em>before you volunteer.</em></h2>
        <p class="lede reveal">Have a question we haven't answered? Our team is glad to talk it through &mdash; no pressure,
           no obligation.</p>
        <a href="tel:{SITE['phone_href']}" class="btn btn-outline reveal">{IC_PHONE} Call {SITE['phone_display']}</a>
      </div>
      <div class="faq-list">
{faq_items}
      </div>
    </div>
  </section>

{enroll_section()}
</main>
"""

# ----------------------------------------------------------------------------
# SHARED SECTIONS used on home + dedicated pages
# ----------------------------------------------------------------------------
def events_section(home=False):
    return f"""  <section class="section events" id="events">
    <span class="giant-word" aria-hidden="true">Community</span>
    <div class="wrap events-grid">
      <div class="events-intro">
        <p class="eyebrow reveal"><span class="eyebrow-dot"></span>Community &amp; events</p>
        <h2 class="reveal">Bringing brain-health science <em>to the community.</em></h2>
        <p class="lede reveal">Beyond the clinic, Dr. Paul Winner and our team speak at programs across the region &mdash;
          sharing the latest in Alzheimer's care, brain health, and neurological research with the patients,
          caregivers, and organizations who need it most.</p>
        <ul class="events-list reveal">
          <li><span class="ev-ic" aria-hidden="true"><svg viewBox="0 0 24 24" width="19" height="19"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M3 5h18v13H8l-5 4z"/></svg></span><div><strong>Educational talks</strong><span>Accessible presentations on memory, migraine, and movement disorders.</span></div></li>
          <li><span class="ev-ic" aria-hidden="true"><svg viewBox="0 0 24 24" width="19" height="19"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M16 20a4 4 0 0 0-8 0M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8M21 20a3 3 0 0 0-5-2.2M18.5 12a3 3 0 0 0 0-6M3 20a3 3 0 0 1 5-2.2M5.5 12a3 3 0 0 1 0-6"/></svg></span><div><strong>Caregiver &amp; support programs</strong><span>Guidance and resources for families navigating a new diagnosis.</span></div></li>
          <li><span class="ev-ic" aria-hidden="true"><svg viewBox="0 0 24 24" width="19" height="19"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 21c5-4.5 8-8 8-11a8 8 0 1 0-16 0c0 3 3 6.5 8 11z"/><circle cx="12" cy="10" r="2.6"/></svg></span><div><strong>Community events</strong><span>Partnering with local organizations to advance brain-health awareness.</span></div></li>
        </ul>
        <p class="events-note reveal">Upcoming talks are announced through our newsletter and social channels.</p>
      </div>
      <div class="invite-card reveal">
        <form class="invite-form" id="inviteForm" novalidate>
          <h3>Invite Dr. Paul Winner to speak</h3>
          <p class="ef-sub">For your community group, organization, or next event.</p>
          <div class="field-row">
            <div class="field"><label for="iv-first">First name</label><input id="iv-first" name="first" type="text" autocomplete="given-name" required></div>
            <div class="field"><label for="iv-last">Last name</label><input id="iv-last" name="last" type="text" autocomplete="family-name" required></div>
          </div>
          <div class="field-row">
            <div class="field"><label for="iv-phone">Phone</label><input id="iv-phone" name="phone" type="tel" autocomplete="tel" required></div>
            <div class="field"><label for="iv-email">Email</label><input id="iv-email" name="email" type="email" autocomplete="email" required></div>
          </div>
          <div class="field"><label for="iv-event">Tell us about the event</label><textarea id="iv-event" name="event" rows="3" placeholder="Audience, date, location, and topic of interest" required></textarea></div>
          <button type="submit" class="btn btn-primary btn-block">Submit request</button>
          <div class="ef-success" id="ivSuccess" hidden>
            <div class="ef-check" aria-hidden="true"><svg viewBox="0 0 24 24" width="34" height="34"><path fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" d="m4 12 5 5 11-11"/></svg></div>
            <h3>Request received.</h3>
            <p>Thank you &mdash; our team will follow up about Dr. Winner's availability. You can also reach us at <a href="tel:{SITE['phone_href']}">{SITE['phone_display']}</a>.</p>
          </div>
        </form>
      </div>
    </div>
  </section>
"""

def newsletter_section(home=False):
    return f"""  <section class="section newsletter" id="newsletter">
    <span class="giant-word" aria-hidden="true">Insights</span>
    <div class="wrap news-grid">
      <div class="news-signup reveal">
        <p class="eyebrow"><span class="eyebrow-dot"></span>Stay connected</p>
        <h2>Brain-healthy insights, <em>right in your inbox.</em></h2>
        <p class="section-sub">Join our newsletter for updates on clinical trials, educational programs,
           and resources designed to support you and your family.</p>
        <form class="news-form" id="newsForm" novalidate>
          <div class="news-fields">
            <div class="field"><label for="nl-first">First name</label><input id="nl-first" name="first" type="text" autocomplete="given-name" required></div>
            <div class="field"><label for="nl-last">Last name</label><input id="nl-last" name="last" type="text" autocomplete="family-name" required></div>
            <div class="field"><label for="nl-email">Email</label><input id="nl-email" name="email" type="email" autocomplete="email" required></div>
          </div>
          <button type="submit" class="btn btn-primary btn-lg">Sign up</button>
          <p class="news-success" id="nlSuccess" hidden><span aria-hidden="true">&#10003;</span> You're subscribed &mdash; watch your inbox for our next issue.</p>
        </form>
      </div>
      <aside class="special-edition reveal">
        <div class="se-glow" aria-hidden="true"></div>
        <div class="se-tag">Special Edition</div>
        <h3>Written by Dr. Paul Winner &amp; his expert team</h3>
        <p>In-depth articles on advanced Alzheimer's care, brain health, and the latest research &mdash;
           with practical insights and expert guidance for families.</p>
        <a href="{{p}}newsletter.html" class="se-link" aria-label="Read the Special Edition Newsletter">
          <span class="se-doc" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M6 2h8l4 4v16H6z"/><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M14 2v4h4M9 13h6M9 17h6M9 9h2"/></svg></span>
          <span class="se-meta"><strong>Special Edition Newsletter</strong><em>Read the latest issue</em></span>
          <svg class="se-arrow" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M13 6l6 6-6 6"/></svg>
        </a>
      </aside>
    </div>
  </section>
"""

def enroll_section():
    return f"""  <section class="section enroll" id="enroll">
    <div class="wrap enroll-grid">
      <div class="enroll-info">
        <p class="eyebrow eyebrow-light reveal"><span class="eyebrow-dot"></span>See if you qualify</p>
        <h2 class="on-dark reveal">Take the <em>first step</em> today.</h2>
        <p class="section-sub on-dark reveal">Share a few details and our research team will reach out to talk through
           the studies that may be right for you. It's free, confidential, and there's no obligation.</p>
        <ul class="contact-lines reveal">
          <li><span class="ci" aria-hidden="true">{IC_PHONE}</span><div><span class="ci-label">Call the research team</span><a href="tel:{SITE['phone_href']}">{SITE['phone_display']}</a></div></li>
          <li><span class="ci" aria-hidden="true"><svg viewBox="0 0 24 24" width="20" height="20"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M12 21c5-4.5 8-8 8-11a8 8 0 1 0-16 0c0 3 3 6.5 8 11z"/><circle cx="12" cy="10" r="2.6" fill="currentColor" stroke="none"/></svg></span><div><span class="ci-label">Visit us</span><a href="{SITE['maps']}" target="_blank" rel="noopener">{SITE['addr1']}<br>{SITE['addr2']}</a></div></li>
          <li><span class="ci" aria-hidden="true"><svg viewBox="0 0 24 24" width="20" height="20"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M12 7v5l3.5 2"/></svg></span><div><span class="ci-label">Hours</span><span class="ci-plain">{SITE['hours']}</span></div></li>
        </ul>
      </div>
      <div class="enroll-card reveal">
        <form class="enroll-form" id="enrollForm" novalidate>
          <h3>Request a call back</h3>
          <p class="ef-sub">All fields are kept confidential.</p>
          <div class="field"><label for="ef-name">Full name</label><input id="ef-name" name="name" type="text" autocomplete="name" required></div>
          <div class="field-row">
            <div class="field"><label for="ef-phone">Phone</label><input id="ef-phone" name="phone" type="tel" autocomplete="tel" required></div>
            <div class="field"><label for="ef-email">Email</label><input id="ef-email" name="email" type="email" autocomplete="email"></div>
          </div>
          <div class="field"><label for="ef-area">Area of interest</label>
            <div class="select-wrap">
              <select id="ef-area" name="area">
                <option value="" selected disabled>Choose a research area</option>
                <option>Alzheimer's &amp; Memory Loss</option><option>Parkinson's Disease</option>
                <option>Migraine</option><option>Multiple Sclerosis</option><option>Not sure / another condition</option>
              </select>
              <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6"/></svg>
            </div>
          </div>
          <div class="field"><label for="ef-msg">Anything you'd like us to know? <span class="opt">(optional)</span></label><textarea id="ef-msg" name="message" rows="3"></textarea></div>
          <button type="submit" class="btn btn-primary btn-block btn-lg">Request my call back</button>
          <p class="ef-fine">By submitting, you agree to be contacted about clinical research opportunities. This form
             does not collect medical records and is not a medical emergency line &mdash; for emergencies, call 911.</p>
          <div class="ef-success" id="efSuccess" hidden>
            <div class="ef-check" aria-hidden="true"><svg viewBox="0 0 24 24" width="34" height="34"><path fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" d="m4 12 5 5 11-11"/></svg></div>
            <h3>Thank you &mdash; we've got it.</h3>
            <p>A member of our research team will reach out soon. If you'd like to talk sooner, call us at <a href="tel:{SITE['phone_href']}">{SITE['phone_display']}</a>.</p>
          </div>
        </form>
      </div>
    </div>
  </section>
"""

# ----------------------------------------------------------------------------
# CLINICAL TRIALS PAGE
# ----------------------------------------------------------------------------
TRIALS = [
    ("alz", "Alzheimer's &amp; Memory Loss",
     "From mild cognitive impairment through moderate Alzheimer's disease, our memory studies evaluate the next generation of disease-modifying and symptom-focused therapies — including treatments aimed at the changes in thinking, memory, and behavior that families notice most.",
     ["Adults experiencing memory changes or a diagnosis of MCI or Alzheimer's", "Caregivers seeking new options when standard treatments feel limited", "Those interested in emerging disease-modifying therapies"]),
    ("park", "Parkinson's Disease",
     "Our movement-disorder studies focus on the symptoms that shape daily life with Parkinson's — motor fluctuations and \"off\" time, tremor and stiffness, and the mood, sleep, and cognitive changes that can accompany the disease as it progresses.",
     ["Adults living with Parkinson's disease at various stages", "People experiencing \"off\" time or symptom fluctuations", "Those exploring therapies beyond their current regimen"]),
    ("mig", "Migraine",
     "We conduct trials for both the acute treatment of migraine attacks and the prevention of chronic and episodic migraine — evaluating next-generation therapies designed to reduce how often attacks strike and how much they take from your life.",
     ["Adults with frequent episodic or chronic migraine", "People seeking better prevention or faster acute relief", "Those whose current treatments aren't enough"]),
    ("ms", "Multiple Sclerosis",
     "Our multiple sclerosis research investigates therapies that aim to slow progression, reduce relapses, and protect neurological function for people living with relapsing and progressive forms of MS.",
     ["Adults with relapsing or progressive MS", "People interested in emerging disease-modifying therapies", "Those seeking close neurological monitoring"]),
]

def trials_body():
    blocks = ""
    for i, (k, title, desc, who) in enumerate(TRIALS):
        who_html = "\n".join(f"            <li><span class=\"tick\" aria-hidden=\"true\"></span>{w}</li>" for w in who)
        blocks += f"""  <section class="section trial-detail{' alt' if i % 2 else ''}" id="{k}">
    <div class="wrap trial-grid">
      <div class="trial-visual reveal" aria-hidden="true">
        <div class="trial-icon">{icon_condition(k)}</div>
        <span class="rcard-tag">Now enrolling</span>
      </div>
      <div class="trial-copy">
        <h2 class="reveal">{title}</h2>
        <p class="lede reveal">{desc}</p>
        <p class="trial-who-label reveal">Studies here may be right for:</p>
        <ul class="about-points reveal">
{who_html}
        </ul>
        <a href="{{p}}contact.html" class="btn btn-primary reveal">See if you qualify</a>
      </div>
    </div>
  </section>
"""
    title_html = 'Neurological studies <span class="grad-text">now enrolling.</span>'
    body = page_hero(
        "Current clinical trials", title_html,
        "Joining a neurological clinical trial can open the door to new treatments, expert care, and close monitoring "
        "when standard options feel limited &mdash; while helping advance research that may improve care for others.",
        [("Home", "index.html"), ("Clinical Trials", None)])
    body += f"""  <section class="section trials-intro">
    <div class="wrap trials-intro-inner">
      <div class="reveal">
        <p class="eyebrow"><span class="eyebrow-dot"></span>What we study</p>
        <h2>Four conditions, one relentless focus.</h2>
      </div>
      <p class="lede reveal">Our active and upcoming studies concentrate on the neurological conditions that touch the
         most families in Palm Beach County. Every trial is FDA-regulated, reviewed by an independent ethics board,
         and led by board-certified neurologists &mdash; with study-related care provided at no cost to participants.</p>
    </div>
  </section>
{blocks}{why_grid()}{process_section()}{cta_band()}"""
    return f"<main>\n{body}</main>\n"

# ----------------------------------------------------------------------------
# ABOUT PAGE
# ----------------------------------------------------------------------------
def about_body():
    body = page_hero(
        "About us", 'A research institute devoted <span class="grad-text">entirely to the brain.</span>',
        "Our physicians work at the frontier of neurology — testing the therapies that become "
        "tomorrow's standard of care, right here in West Palm Beach.",
        [("Home", "index.html"), ("About", None)])
    body += f"""  <section class="section about-story">
    <div class="wrap about-story-grid">
      <div class="reveal">
        <p class="eyebrow"><span class="eyebrow-dot"></span>Our story</p>
        <h2>Where the best care and the next breakthrough share one roof.</h2>
      </div>
      <div class="about-story-body reveal">
        <p>Premiere Research Institute is built on a simple conviction held by our neurologists:
           that the patients they treat every day deserve a real seat at the frontier of medicine. Under the direction
           of Dr. Paul Winner, our team conducts clinical trials for the neurological conditions that affect the most
           families &mdash; Alzheimer's and memory loss, Parkinson's disease, migraine, and multiple sclerosis.</p>
        <p>Every study we run is FDA-regulated and reviewed by an independent ethics board before it begins. Participants
           are cared for as patients first and volunteers second &mdash; monitored closely by board-certified neurologists,
           informed fully at every step, and never charged for study-related care. It's research with a human center.</p>
        <p>We're proud to do this work in one place, close to home, alongside the Palm Beach Memory Disorder Center and
           the Palm Beach Headache Center &mdash; so that expert care and emerging science are never more than one visit apart.</p>
      </div>
    </div>
  </section>

  <section class="statband" aria-label="By the numbers">
    <div class="wrap statband-grid">
      <div class="reveal"><span class="stat-n" data-count="5" data-suffix="">0</span><span class="stat-l">Physician specialists</span></div>
      <div class="reveal"><span class="stat-n" data-count="4" data-suffix="">0</span><span class="stat-l">Neurological focus areas</span></div>
      <div class="reveal"><span class="stat-n" data-prefix="$" data-count="0" data-suffix="">0</span><span class="stat-l">Cost to participate</span></div>
      <div class="reveal"><span class="stat-n" data-count="100" data-suffix="%">0</span><span class="stat-l">Study care covered</span></div>
    </div>
  </section>
{why_grid()}{process_section()}
  <section class="section mission">
    <div class="wrap mission-inner">
      <svg class="quote-mark" viewBox="0 0 48 48" width="56" height="56" aria-hidden="true"><path fill="currentColor" d="M20 34H8V22c0-7 4-11 12-12v5c-4 1-6 3-6 7h6v12zm20 0H28V22c0-7 4-11 12-12v5c-4 1-6 3-6 7h6v12z"/></svg>
      <blockquote class="reveal">The best care and the next breakthrough should live <em>under the same roof</em>. That belief is why
        we exist &mdash; to give our neighbors in Palm Beach County a real seat at the frontier of neurology.</blockquote>
      <p class="mission-attr reveal">The mission of Premiere Research Institute</p>
    </div>
  </section>
{cta_band()}"""
    return f"<main>\n{body}</main>\n"

# ----------------------------------------------------------------------------
# TEAM PAGE
# ----------------------------------------------------------------------------
def team_body():
    docs = render_tcards()
    staff = [
        ("Physician Investigators", "Board-certified neurologists serving as principal and sub-investigators across our Alzheimer's, Parkinson's, migraine, and MS studies."),
        ("Research Coordinators", "Dedicated study coordinators who guide you from first call through every visit — your consistent point of contact and advocate."),
        ("Clinical &amp; Regulatory Staff", "Experienced staff ensuring every study meets rigorous safety, ethical, and FDA-regulated standards from start to finish."),
    ]
    staff_html = "\n".join(
        f"""        <article class="scard reveal"><h3>{t}</h3><p>{d}</p></article>""" for t, d in staff)
    body = page_hero(
        "Our team", 'Neurologists who treat these <span class="grad-text">conditions every day.</span>',
        "Research at Premiere is directed by physicians recognized nationally for their work in cognitive and "
        "neurological care — and supported by coordinators who treat you like family.",
        [("Home", "index.html"), ("Our Team", None)])
    body += f"""  <section class="section team">
    <span class="giant-word" aria-hidden="true">Our Team</span>
    <div class="wrap">
{lead_doctor()}      <div class="team-grid">
{docs}
      </div>
    </div>
  </section>

  <section class="section staff">
    <div class="wrap">
      <div class="section-head center">
        <p class="eyebrow reveal"><span class="eyebrow-dot"></span>Behind every study</p>
        <h2 class="reveal">A team that treats you like family.</h2>
      </div>
      <div class="staff-grid">
{staff_html}
      </div>
    </div>
  </section>
{cta_band()}"""
    return f"<main>\n{body}</main>\n"

# ----------------------------------------------------------------------------
# EVENTS PAGE
# ----------------------------------------------------------------------------
def events_body():
    body = page_hero(
        "Community & events", 'Bringing brain-health <span class="grad-text">science to you.</span>',
        "Dr. Paul Winner and our team speak at programs across the region &mdash; and we'd be glad to bring that "
        "expertise to your community group, organization, or next event.",
        [("Home", "index.html"), ("Events", None)])
    body += events_section()
    body += f"""  <section class="section news-cross">
    <div class="wrap news-cross-inner reveal">
      <div>
        <h2>Never miss an event.</h2>
        <p class="section-sub">Upcoming talks and programs are announced first through our newsletter and social channels.</p>
      </div>
      <a href="{{p}}newsletter.html" class="btn btn-primary">Subscribe for updates {IC_ARROW}</a>
    </div>
  </section>
{cta_band()}"""
    return f"<main>\n{body}</main>\n"

# ----------------------------------------------------------------------------
# NEWSLETTER PAGE
# ----------------------------------------------------------------------------
NEWSLETTER_ISSUES = [
    ("Special Edition — 2026", "Advanced Alzheimer's care, brain health, and the latest research from Dr. Paul Winner and his team.", "#"),
]

def _issue_card(title, desc, link):
    doc_ic = ('<span class="issue-doc" aria-hidden="true"><svg viewBox="0 0 24 24" width="24" height="24">'
              '<path fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" d="M6 2h8l4 4v16H6z"/>'
              '<path fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" d="M14 2v4h4M9 13h6M9 17h6M9 9h2"/></svg></span>')
    meta = f'<span class="issue-meta"><strong>{title}</strong><em>{desc}</em></span>'
    if link and link != "#":
        arrow = ('<svg class="se-arrow" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
                 '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M13 6l6 6-6 6"/></svg>')
        return f'        <a href="{link}" class="issue-card reveal">\n          {doc_ic}\n          {meta}\n          {arrow}\n        </a>'
    # no real URL yet — render a non-interactive card so it doesn't look like a broken link
    return f'        <div class="issue-card is-pending reveal">\n          {doc_ic}\n          {meta}\n          <span class="issue-soon">Coming soon</span>\n        </div>'

def newsletter_body():
    issues = "\n".join(_issue_card(title, desc, link) for title, desc, link in NEWSLETTER_ISSUES)
    perks = [
        ("Clinical trial updates", "Be first to hear when new studies open for Alzheimer's, Parkinson's, migraine, and MS."),
        ("Brain-healthy tips", "Practical, physician-informed guidance on memory, headache, and healthy aging."),
        ("Educational programs", "Invitations to talks, caregiver support programs, and community events."),
    ]
    perks_html = "\n".join(
        f"""        <li class="reveal"><span class="tick" aria-hidden="true"></span><div><strong>{t}</strong><span>{d}</span></div></li>""" for t, d in perks)
    body = page_hero(
        "Newsletter", 'Brain-healthy insights, <span class="grad-text">right in your inbox.</span>',
        "Stay connected with the latest news, events, and brain-healthy tips — updates on clinical trials, "
        "educational programs, and resources designed to support you and your family.",
        [("Home", "index.html"), ("Newsletter", None)])
    body += f"""  <section class="section newsletter">
    <div class="wrap news-grid">
      <div class="news-signup reveal">
        <p class="eyebrow"><span class="eyebrow-dot"></span>Subscribe today</p>
        <h2>Join our email newsletter.</h2>
        <p class="section-sub">It's free, and you can unsubscribe anytime. We'll never share your information.</p>
        <form class="news-form" id="newsForm" novalidate>
          <div class="news-fields">
            <div class="field"><label for="nl-first">First name</label><input id="nl-first" name="first" type="text" autocomplete="given-name" required></div>
            <div class="field"><label for="nl-last">Last name</label><input id="nl-last" name="last" type="text" autocomplete="family-name" required></div>
            <div class="field"><label for="nl-email">Email</label><input id="nl-email" name="email" type="email" autocomplete="email" required></div>
          </div>
          <button type="submit" class="btn btn-primary btn-lg">Sign up</button>
          <p class="news-success" id="nlSuccess" hidden><span aria-hidden="true">&#10003;</span> You're subscribed &mdash; watch your inbox for our next issue.</p>
        </form>
        <ul class="perks-list">
{perks_html}
        </ul>
      </div>
      <aside class="special-edition reveal">
        <div class="se-glow" aria-hidden="true"></div>
        <div class="se-tag">Special Edition</div>
        <h3>Written by Dr. Paul Winner &amp; his expert team</h3>
        <p>Explore our special-edition newsletters &mdash; in-depth articles on advanced Alzheimer's care, brain health,
           and the latest research, with practical insights and expert guidance to help you navigate memory and
           neurological concerns.</p>
        <div class="issue-list">
{issues}
        </div>
        <p class="issue-note">New issues are added here as they're published.</p>
      </aside>
    </div>
  </section>
{cta_band()}"""
    return f"<main>\n{body}</main>\n"

# ----------------------------------------------------------------------------
# CONTACT PAGE
# ----------------------------------------------------------------------------
def contact_body():
    body = page_hero(
        "Contact", 'Reach our <span class="grad-text">research team.</span>',
        "Share a few details and our research team will reach out to talk through the studies that may be right for "
        "you. It's free, confidential, and there's no obligation.",
        [("Home", "index.html"), ("Contact", None)])
    body += enroll_section()
    body += f"""  <section class="section map-section">
    <div class="wrap">
      <div class="section-head center">
        <p class="eyebrow reveal"><span class="eyebrow-dot"></span>Visit us</p>
        <h2 class="reveal">In the heart of West Palm Beach.</h2>
        <p class="section-sub reveal">{SITE['addr1']}, {SITE['addr2']} &middot; {SITE['hours']}</p>
      </div>
      <div class="map-embed reveal">
        <iframe src="{SITE['map_embed']}" title="Map to Premiere Research Institute" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
      </div>
    </div>
  </section>
"""
    return f"<main>\n{body}</main>\n"

# ----------------------------------------------------------------------------
# BLOG
# ----------------------------------------------------------------------------
BLOG_POSTS = [
    {
        "slug": "living-well-with-parkinsons-movement",
        "title": "Living Well with Parkinson's: Everyday Movement Strategies",
        "category": "Movement Disorders",
        "tint": "violet",
        "date": "2026-07-22",
        "read": "6 min read",
        "excerpt": "A Parkinson's diagnosis changes a lot — but daily habits still matter. Here are gentle, practical ways many people stay active and engaged.",
        "body": [
            ("p", "A diagnosis of Parkinson's disease can feel overwhelming, but it doesn't erase the many things you can do to support your health day to day. While every person's experience is different, movement, routine, and a strong care team are themes that come up again and again."),
            ("h2", "Movement is medicine — within reason"),
            ("p", "Regular physical activity is widely encouraged for people with Parkinson's, and many find that staying active helps with mobility, balance, and mood. What that looks like varies from person to person &mdash; walking, stretching, dance, tai chi, and physical therapy are all commonly recommended. The right plan for you is a conversation to have with your physician or a physical therapist who knows your situation."),
            ("h2", "Small adjustments at home"),
            ("p", "Simple changes can make daily life smoother: removing loose rugs and clutter to reduce fall risk, adding good lighting, using chairs with firm arms, and giving yourself extra time for tasks that have become harder. These aren't signs of giving up &mdash; they're smart ways to protect your energy and independence."),
            ("h2", "Build a care team"),
            ("p", "Parkinson's is best managed by a team. Alongside a neurologist, that may include physical, occupational, and speech therapists, plus the family and friends who support you. Keeping notes on your symptoms &mdash; when they're better or worse, and how medications are working &mdash; helps your care team fine-tune your plan over time."),
            ("h2", "Where research fits in"),
            ("p", "Clinical trials continue to explore new therapies for the motor and non-motor symptoms of Parkinson's. For some people, participating offers access to emerging treatments and close monitoring; for all who take part, it helps move the science forward. Whether research is right for you is worth discussing with your care team."),
            ("p", "This article is for general education and is not medical advice. Always talk with your physician before changing your activity or treatment. To ask about Parkinson's research at Premiere Research Institute, call (561) 851-9400."),
        ],
    },
    {
        "slug": "caring-for-a-loved-one-with-memory-loss",
        "title": "Caring for a Loved One with Memory Loss: Where to Begin",
        "category": "Caregiving",
        "tint": "amber",
        "date": "2026-07-18",
        "read": "6 min read",
        "excerpt": "Becoming a caregiver is rarely something we plan for. If someone you love is facing memory loss, here's a gentle place to start.",
        "body": [
            ("p", "When a spouse, parent, or friend begins to struggle with memory, the people closest to them often become caregivers before they ever use that word. It can be tender, tiring, and deeply meaningful work &mdash; and you don't have to figure it out all at once."),
            ("h2", "Lean on structure and routine"),
            ("p", "Predictable routines can ease anxiety for someone with memory changes. Keeping meals, activities, and sleep on a steady schedule, writing down important information, and simplifying choices can all help the day feel more manageable for both of you."),
            ("h2", "Communicate with patience"),
            ("p", "Short, clear sentences, a calm tone, and a little extra time go a long way. When memory falters, meeting your loved one where they are &mdash; rather than correcting every detail &mdash; often reduces frustration on both sides. Connection matters more than getting the facts exactly right."),
            ("h2", "Take care of yourself, too"),
            ("p", "Caregiver burnout is real, and caring for yourself isn't selfish &mdash; it's what makes sustained caregiving possible. Accept help when it's offered, protect a little time for yourself, and remember that asking for support is a sign of strength, not failure."),
            ("h2", "You're not alone"),
            ("p", "Support groups, community programs, and educational resources exist precisely because so many families walk this road. Connecting with others who understand can bring both practical tips and real comfort."),
            ("h2", "Consider a professional evaluation"),
            ("p", "If memory changes are new or worsening, a conversation with a physician is a good next step. Many causes of memory change are treatable, and when an evaluation points toward a condition like Alzheimer's, earlier answers open more options &mdash; including access to clinical research."),
            ("p", "This article is for general education and is not medical advice. For guidance specific to your loved one, speak with a qualified clinician. To ask about memory and Alzheimer's research at Premiere Research Institute, call (561) 851-9400."),
        ],
    },
    {
        "slug": "what-to-expect-clinical-trial",
        "title": "What to Expect When You Join a Clinical Trial",
        "category": "Clinical Research",
        "tint": "teal",
        "date": "2026-07-15",
        "read": "5 min read",
        "excerpt": "Curious about clinical research but unsure how it works? Here's a plain-language walk through every step — from the first phone call to your final visit.",
        "body": [
            ("p", "If you've been told that standard treatments have limits, or you simply want to help move medicine forward, a clinical trial can feel like a big unknown. It doesn't have to be. Here's what participating in neurological research at Premiere Research Institute actually looks like, step by step."),
            ("h2", "It starts with a conversation"),
            ("p", "Reaching out never commits you to anything. When you call or complete our form, a research coordinator asks a few questions about your health and the symptoms you're facing. This pre-screening simply helps us see which current studies you might be a fit for &mdash; there's no cost and no pressure."),
            ("h2", "Informed consent comes first"),
            ("p", "If a study looks like a match, you'll meet our team for a screening visit. Before anything else, we walk you through the study in full: what it involves, how long it lasts, the potential benefits and risks, and whether it includes a placebo group. This is called informed consent, and it exists to make sure your decision is a fully informed one. You can ask any question, take the information home, and say no at any time."),
            ("h2", "Care that often exceeds routine visits"),
            ("p", "During a study, participants are monitored closely by board-certified neurologists and research staff &mdash; frequently more often than a typical appointment schedule allows. Study-related exams, testing, and the investigational treatment are provided at no cost, health insurance is not required, and many studies compensate participants for their time and travel."),
            ("h2", "You're always in control"),
            ("p", "Participation is voluntary from beginning to end. You may withdraw at any time, for any reason, without affecting your regular medical care. And with your permission, we're glad to coordinate with your existing physicians so your research participation fits smoothly alongside the care you already receive."),
            ("h2", "The bigger picture"),
            ("p", "Every person who volunteers helps bring new treatments closer for everyone who will need them. It's a contribution that outlasts the study itself &mdash; and, for many participants, a chance to access tomorrow's therapies today."),
        ],
    },
    {
        "slug": "memory-changes-normal-aging-vs-warning-signs",
        "title": "Memory Changes: Normal Aging vs. Warning Signs",
        "category": "Brain Health",
        "tint": "violet",
        "date": "2026-07-08",
        "read": "6 min read",
        "excerpt": "Forgetting a name is common. But how do you tell everyday forgetfulness from something worth discussing with a doctor? A gentle, practical guide.",
        "body": [
            ("p", "Almost everyone misplaces keys or blanks on a name now and then &mdash; and most of the time, that's simply a normal part of aging. But families often wonder where ordinary forgetfulness ends and a warning sign begins. Knowing the difference can bring peace of mind, and, when it matters, earlier answers."),
            ("h2", "What normal aging can look like"),
            ("p", "It's common to occasionally forget an appointment and remember it later, walk into a room and lose your train of thought, or take a bit longer to recall a word. These moments are usually about speed and attention, not the loss of the memory itself. Day-to-day independence stays intact."),
            ("h2", "Changes worth discussing with a doctor"),
            ("p", "Some patterns deserve a professional conversation. Examples include memory loss that disrupts daily life, difficulty completing familiar tasks, losing track of dates or seasons, trouble following a conversation, misplacing items and being unable to retrace steps, or noticeable changes in mood, judgment, or personality &mdash; especially when a spouse, adult child, or close friend is the one who notices."),
            ("h2", "Why earlier is better"),
            ("p", "Talking with a physician early doesn't mean assuming the worst. Many causes of memory change are treatable &mdash; from sleep, medication, thyroid, and mood issues to vitamin levels. When an evaluation does point toward a condition like mild cognitive impairment or Alzheimer's disease, an earlier diagnosis opens more options, including access to clinical research."),
            ("h2", "A note for caregivers"),
            ("p", "If you're the one noticing changes in someone you love, you're not overreacting by asking questions. Write down specific examples and bring them to an appointment &mdash; concrete observations help clinicians far more than general worry."),
            ("p", "This article is for general education and isn't a substitute for medical advice. If you have concerns about memory, speak with your physician. To ask about memory and Alzheimer's research at Premiere Research Institute, call our team at (561) 851-9400."),
        ],
    },
    {
        "slug": "migraine-prevention-everyday-management",
        "title": "Migraine 101: Prevention and Everyday Management",
        "category": "Headache & Migraine",
        "tint": "amber",
        "date": "2026-06-27",
        "read": "5 min read",
        "excerpt": "Migraine is more than a bad headache. Here are practical, everyday strategies that many people find helpful — and when it's worth seeking specialized care.",
        "body": [
            ("p", "Migraine is a neurological condition, not just a severe headache &mdash; and for the millions who live with it, the goal is often twofold: fewer attacks, and faster relief when one strikes. While every person is different, a few everyday strategies are widely recommended by headache specialists."),
            ("h2", "Know your patterns"),
            ("p", "Keeping a simple headache diary &mdash; noting when attacks happen, how long they last, and what came before them &mdash; can reveal patterns and possible triggers over time. Common triggers include irregular sleep, skipped meals, dehydration, stress, and certain sensory inputs, though triggers vary widely from person to person."),
            ("h2", "Build steady daily habits"),
            ("p", "Consistency tends to help: regular sleep and wake times, staying hydrated, eating at regular intervals, and moving your body most days. Because sudden changes can be their own trigger, gradual, steady routines usually serve people better than dramatic swings."),
            ("h2", "Acute vs. preventive approaches"),
            ("p", "Broadly, migraine care falls into two categories: acute treatment, aimed at stopping an attack that's already underway, and preventive treatment, aimed at reducing how often attacks occur in the first place. Which approach &mdash; or combination &mdash; fits you is a conversation to have with a clinician, ideally one experienced in headache medicine."),
            ("h2", "When to seek specialized care"),
            ("p", "It's worth seeing a specialist if attacks are frequent, disabling, changing in pattern, or not well controlled by your current approach. A headache-focused evaluation can help clarify the diagnosis and open the door to newer options, including next-generation preventive and acute therapies."),
            ("p", "This article is general education, not medical advice. Any severe, sudden, or unusual headache &mdash; especially the \"worst headache of your life\" &mdash; warrants urgent medical attention. To ask about migraine research at Premiere Research Institute, call (561) 851-9400."),
        ],
    },
]

TINTS = {
    "teal": "linear-gradient(135deg,#123b63,#0a8b93)",
    "violet": "linear-gradient(135deg,#123b63,#6d5efc)",
    "amber": "linear-gradient(135deg,#123b63,#c9772a)",
}

def _fmt_date(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%B %-d, %Y")

def blog_index_body():
    cards = ""
    for post in BLOG_POSTS:
        grad = TINTS.get(post["tint"], TINTS["teal"])
        cards += f"""        <article class="blog-card reveal">
          <a href="{{p}}blog/{post['slug']}.html" class="blog-card-link">
            <span class="blog-card-media" style="background:{grad}" aria-hidden="true"><span class="blog-card-mark"></span></span>
            <span class="blog-card-body">
              <span class="blog-tag">{esc(post['category'])}</span>
              <h3>{esc(post['title'])}</h3>
              <p>{esc(post['excerpt'])}</p>
              <span class="blog-meta">{_fmt_date(post['date'])} &middot; {esc(post['read'])}</span>
            </span>
          </a>
        </article>
"""
    body = page_hero(
        "Insights & resources", 'The Premiere <span class="grad-text">Research blog.</span>',
        "Plain-language articles on clinical research, brain health, and living well with neurological conditions "
        "— from the team at Premiere Research Institute.",
        [("Home", "index.html"), ("Blog", None)])
    body += f"""  <section class="section blog-index">
    <div class="wrap">
      <div class="blog-grid">
{cards}      </div>
    </div>
  </section>
{newsletter_section()}"""
    return f"<main>\n{body}</main>\n"

def blog_post_body(post):
    grad = TINTS.get(post["tint"], TINTS["teal"])
    parts = []
    for tag, text in post["body"]:
        if tag == "h2":
            parts.append(f"      <h2>{text}</h2>")
        else:
            parts.append(f"      <p>{text}</p>")
    article = "\n".join(parts)
    idx = BLOG_POSTS.index(post)
    more = [q for j, q in enumerate(BLOG_POSTS) if j != idx][:2]
    more_html = ""
    for m in more:
        mg = TINTS.get(m["tint"], TINTS["teal"])
        more_html += f"""        <article class="blog-card reveal">
          <a href="{{p}}blog/{m['slug']}.html" class="blog-card-link">
            <span class="blog-card-media" style="background:{mg}" aria-hidden="true"><span class="blog-card-mark"></span></span>
            <span class="blog-card-body">
              <span class="blog-tag">{esc(m['category'])}</span>
              <h3>{esc(m['title'])}</h3>
              <span class="blog-meta">{_fmt_date(m['date'])} &middot; {esc(m['read'])}</span>
            </span>
          </a>
        </article>
"""
    body = f"""<main>
  <article class="article">
    <header class="article-hero" style="background:{grad}">
      <div class="article-hero-veil" aria-hidden="true"></div>
      <div class="wrap article-hero-inner">
        <nav class="breadcrumb light reveal" aria-label="Breadcrumb"><a href="{{p}}index.html">Home</a><span class="bc-sep">/</span><a href="{{p}}blog/index.html">Blog</a><span class="bc-sep">/</span><span aria-current="page">{esc(post['category'])}</span></nav>
        <span class="blog-tag on-media">{esc(post['category'])}</span>
        <h1 class="reveal">{esc(post['title'])}</h1>
        <p class="article-byline reveal">Premiere Research Institute &middot; {_fmt_date(post['date'])} &middot; {esc(post['read'])}</p>
      </div>
    </header>

    <div class="wrap article-body">
{article}
      <hr class="article-rule">
      <p class="article-disclaimer">This article is provided for general education and is not medical advice.
         Always consult a qualified clinician about your health. In an emergency, call 911.</p>
      <div class="article-cta">
        <div>
          <h3>Questions about our research?</h3>
          <p>Our team is glad to talk it through &mdash; no cost, no obligation.</p>
        </div>
        <a href="{{p}}contact.html" class="btn btn-primary">See if you qualify</a>
      </div>
    </div>
  </article>

  <section class="section blog-more">
    <div class="wrap">
      <div class="section-head"><h2 class="reveal">Keep reading</h2></div>
      <div class="blog-grid">
{more_html}      </div>
    </div>
  </section>
{newsletter_section()}</main>
"""
    return body

# ----------------------------------------------------------------------------
# DOCTOR DETAIL PAGES
# ----------------------------------------------------------------------------
def doctor_page_body(doc):
    bio = "\n".join(f"        <p>{para}</p>" for para in doc["bio"])
    focus = "\n".join(f"          <li><span class=\"tick\" aria-hidden=\"true\"></span>{f}</li>" for f in doc["focus"])
    facts_html = ""
    if doc.get("facts"):
        chips = "\n".join(f"          <li><strong>{a}</strong> {b}</li>" for a, b in doc["facts"])
        facts_html = f'        <ul class="ld-facts doc-facts">\n{chips}\n        </ul>\n'
    role = doc.get("role", doc["spec"])
    title_html = f'{doc["name"]}<span class="dr-suf">, {doc["suf"]}</span>'
    # role data may carry entities (e.g. "Migraine &amp; Headache"); unescape so page_hero's
    # esc() single-escapes it rather than double-escaping to "&amp;amp;"
    body = page_hero(html.unescape(role), title_html, doc["short"],
                     [("Home", "index.html"), ("Our Team", "team.html"), (doc["name"], None)])
    body += f"""  <section class="section doctor">
    <div class="wrap doctor-grid">
      <aside class="doctor-aside reveal">
        {_portrait_html(doc, "doctor-portrait")}
        <p class="ld-role">{role}</p>
        <p class="doctor-spec">{doc['spec']}</p>
        <p class="doctor-focus-label">Focus areas</p>
        <ul class="doc-focus">
{focus}
        </ul>
{facts_html}        <a href="{{p}}contact.html" class="btn btn-primary btn-block">See if you qualify</a>
      </aside>
      <div class="doctor-body reveal">
{bio}
        <a href="{{p}}team.html" class="link-arrow doctor-back">{IC_BACK} Back to our team</a>
      </div>
    </div>
  </section>
{cta_band()}"""
    return f"<main>\n{body}</main>\n"

def not_found_body():
    links = "".join(f'<a href="{{p}}{href}">{esc(label)}</a>' for label, href, key in NAV)
    body = page_hero("Page not found", '404 &mdash; this page has <span class="grad-text">wandered off.</span>',
                     "The page you're looking for may have moved or no longer exists. Let's get you back on track.",
                     [("Home", "index.html"), ("Not found", None)])
    body += f"""  <section class="section notfound">
    <div class="wrap notfound-inner">
      <p class="notfound-label reveal">Try one of these instead</p>
      <nav class="notfound-links reveal" aria-label="Site">{links}<a href="{{p}}contact.html">Contact</a></nav>
      <a href="{{p}}index.html" class="btn btn-primary btn-lg reveal">Back to home</a>
    </div>
  </section>
"""
    return f"<main>\n{body}</main>\n"

# ----------------------------------------------------------------------------
# SITEMAP + ROBOTS
# ----------------------------------------------------------------------------
def build_meta(pages):
    today = f"{YEAR}-07-23"
    urls = ""
    for path in pages:
        loc = SITE["base"] + "/" + ("" if path == "index.html" else path)
        pr = "1.0" if path == "index.html" else ("0.8" if "blog/" not in path else "0.6")
        urls += f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>\n"
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n')
    with open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)
    robots = f"User-agent: *\nAllow: /\n\nSitemap: {SITE['base']}/sitemap.xml\n"
    with open(os.path.join(HERE, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

# ----------------------------------------------------------------------------
# BUILD
# ----------------------------------------------------------------------------
def main():
    pages = []
    pages.append(page("index.html",
        "Premiere Research Institute | Neurological Clinical Trials in West Palm Beach",
        "Premiere Research Institute conducts groundbreaking clinical trials for Alzheimer's, Parkinson's, migraine, and multiple sclerosis in West Palm Beach, FL. Access emerging treatments and expert care at no cost.",
        "", home_body(), active=""))
    pages.append(page("clinical-trials.html",
        "Clinical Trials | Alzheimer's, Parkinson's, Migraine, MS | West Palm Beach",
        "Explore neurological clinical trials now enrolling at Premiere Research Institute in West Palm Beach, FL — Alzheimer's, Parkinson's, migraine, and multiple sclerosis studies at no cost to participants.",
        "clinical-trials.html", trials_body(), active="trials"))
    pages.append(page("about.html",
        "About | Premiere Research Institute | Neurology Research in West Palm Beach",
        "Learn about Premiere Research Institute — a neurological clinical-research center in West Palm Beach, FL, directed by Dr. Paul Winner, advancing Alzheimer's, Parkinson's, migraine, and MS research.",
        "about.html", about_body(), active="about"))
    pages.append(page("team.html",
        "Our Team | Neurologists & Researchers | Premiere Research Institute",
        "Meet the physicians and research team behind Premiere Research Institute in West Palm Beach, FL — led by Dr. Paul Winner, DO, FAAN, FAHS.",
        "team.html", team_body(), active="team"))
    pages.append(page("events.html",
        "Events | Community Talks & Speaking | Premiere Research Institute",
        "Invite Dr. Paul Winner to speak, and discover community programs, caregiver support, and brain-health events from Premiere Research Institute in West Palm Beach, FL.",
        "events.html", events_body(), active="events"))
    pages.append(page("newsletter.html",
        "Newsletter | Brain-Health Insights | Premiere Research Institute",
        "Subscribe to the Premiere Research Institute newsletter for clinical-trial updates, brain-healthy tips, and special-edition articles from Dr. Paul Winner and his team.",
        "newsletter.html", newsletter_body(), active=""))
    pages.append(page("contact.html",
        "Contact | See If You Qualify | Premiere Research Institute",
        "Contact Premiere Research Institute in West Palm Beach, FL to see if you or a loved one may qualify for a neurological clinical trial. Call (561) 851-9400 — free and confidential.",
        "contact.html", contact_body(), active=""))
    pages.append(page("blog/index.html",
        "Blog | Clinical Research & Brain Health | Premiere Research Institute",
        "Plain-language articles on clinical research, brain health, memory, migraine, and living well with neurological conditions from Premiere Research Institute.",
        "blog/index.html", blog_index_body(), active="blog"))
    for post in BLOG_POSTS:
        pages.append(page(f"blog/{post['slug']}.html",
            f"{post['title']} | Premiere Research Institute",
            post["excerpt"],
            f"blog/{post['slug']}.html", blog_post_body(post), active="blog", page_type="article"))
    for doc in [LEAD] + DOCTORS:
        clean = doc["name"] + ", " + doc["suf"]
        pages.append(page(f"team/{doc['slug']}.html",
            f"{clean} | Premiere Research Institute",
            doc["short"].replace("&amp;", "and").replace("&mdash;", "-"),
            f"team/{doc['slug']}.html", doctor_page_body(doc), active="team", page_type="profile"))
    # 404 — generated but deliberately kept out of the sitemap
    page("404.html", "Page Not Found | Premiere Research Institute",
         "The page you're looking for may have moved. Return to Premiere Research Institute.",
         "404.html", not_found_body(), active="")
    build_meta(pages)
    print(f"Built {len(pages)} pages:")
    for p in pages:
        print("  -", p)
    print("  - sitemap.xml\n  - robots.txt")

if __name__ == "__main__":
    main()
