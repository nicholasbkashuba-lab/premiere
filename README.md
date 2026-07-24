# Premiere Research Institute — Website

A bespoke, fully responsive marketing site for **Premiere Research Institute**, a neurological
clinical-research center in West Palm Beach, FL. Static HTML/CSS/JS with a small Python generator —
no framework, no runtime dependencies.

## Architecture
- **`build.py` is the single source of truth.** It generates every `.html` page (plus `sitemap.xml`
  and `robots.txt`) from shared components, so the header, footer, nav, and branding stay in sync
  across the whole site. Edit `build.py`, then run:
  ```bash
  python3 build.py
  ```
- **Preview locally:**
  ```bash
  python3 -m http.server 8010   # → http://localhost:8010
  ```
- Commit & push → Vercel (or any static host) serves this repo at the web root.

## Pages
Home · Clinical Trials · About · Our Team · Events · Newsletter · Contact · Blog (index + posts).
Each page passes a unique `<title>`, meta description, canonical URL, Open Graph tags, and
`MedicalOrganization` JSON-LD (built in `build.py`). All page URLs land in `sitemap.xml`.

## Adding content
- **New blog post** → add one dict to `BLOG_POSTS` in `build.py` (slug, title, category, tint,
  date, read, excerpt, and a `body` list of `("h2"|"p", text)` tuples), then rebuild. The post page,
  the blog index card, and "keep reading" cross-links are generated automatically.
- **New newsletter issue** → add one tuple to `NEWSLETTER_ISSUES` and rebuild.
- **New study / condition** → edit `TRIALS` (detail page) and the `conds` list in `home_body()`.
- **Team change** → edit `DOCTORS` (and `lead_doctor()` for the director).
- **FAQ / process / benefits** → edit `FAQ`, `PROCESS_STEPS`, `WHY_CARDS`.

## Design language ("neural")
- **Palette:** midnight navy · synapse **teal → violet** gradient · warm amber · warm paper neutrals.
- **Type:** Fraunces (editorial display serif) + Inter (UI/body).
- **Signature elements:** interactive neural-network canvas hero (pointer-reactive, reduced-motion &
  off-screen aware), gradient headlines, scroll reveals, count-up stats, pulsing "Now enrolling"
  tags, single-open FAQ accordion, glassmorphism form cards, tinted blog cards with the tree-brain
  watermark. Accessible focus states, semantic landmarks, aria labels; responsive down to mobile
  with a slide-in menu.

## Brand assets
Built from the client-provided logo (`assets/img/logo-original.jpeg` — the "Discover Hope with"
tree-brain mark). The tree mark was isolated from its white background into a transparent alpha PNG
(`mark-mask.png`) used as a CSS mask, so it recolors via `currentColor`: cream/white over dark
sections, slate on the light scrolled header. Favicons/apple-touch icon are the mark on a midnight
rounded square. The "Discover Hope with" tagline is kept in the lockup.

## Facts used
- **4631 N. Congress Ave, Suite 200, West Palm Beach, FL 33407** · **(561) 851-9400** · Mon–Fri 9:00 AM–4:30 PM
- **Team:** Paul Winner, DO, FAAN, FAHS (Senior Director); Reed Stone, MD, FAAN; Arnaldo Da Silva, MD;
  Robert Coppola, DO; Michael Alosilla, MD
- **Social:** instagram.com/premiereresearchinstitute · facebook.com/PremiereResearchInstitute · tiktok.com/@askdrwinner

All body copy is original (written for this build), carrying the same information as the current
site. No clinical claims, patient testimonials, or credentials were invented; blog posts are general
education with disclaimers, not medical advice.

## To go live — owner hand-offs
1. **Wire the forms.** Enroll, invite-to-speak, and newsletter forms validate and show a success
   state client-side only. In `assets/js/main.js` (marked `NOTE:`), POST `new FormData(form)` to an
   email/CRM endpoint (FormSubmit, Formspree, or a Supabase table) before showing success. The
   newsletter form should post to your email provider (Mailchimp, Constant Contact, etc.).
2. **Newsletter issues.** Point each `NEWSLETTER_ISSUES` entry's link at the real PDF/article URL.
3. **Real photography.** Doctor portraits use elegant monogram avatars by design — swap in headshots
   when available (`assets/team/` + update `DOCTORS`).
4. **Domain / OG image / analytics.** This standalone repo serves the site at the web root, so
   `build.py` emits absolute asset/link paths from `ROOT = "/"`. Set `SITE["base"]` to the real domain
   for canonical/OG URLs, add a wide `og:image`, and drop in an analytics tag if desired.
