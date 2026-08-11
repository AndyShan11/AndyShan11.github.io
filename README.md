# Xihang Shan — Personal Academic Homepage

Source for [andyshan11.github.io](https://andyshan11.github.io/).

The site is a lightweight, dependency-free academic portfolio built with semantic HTML, modern CSS, and vanilla JavaScript. It includes:

- responsive one-page research portfolio;
- dark and light themes;
- animated research-network canvas and orbit visual;
- publication filters and direct PDF links;
- research timeline, projects, education, honors, and skills;
- English and Chinese CV downloads;
- reduced-motion and keyboard-accessible behavior;
- Open Graph metadata and JSON-LD profile data.

## Local preview

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Content updates

Edit `index.html` for publications and experience, `styles.css` for design, and `script.js` for interactions. GitHub Pages serves the `main` branch directly.

## Publication media

Run `python tools/generate_publication_figures.py` for static posters. Run
`python tools/generate_publication_animations.py` for the posters plus the
8-second model-process videos. Each scene animates a real method state rather
than adding decorative motion to a static figure.
