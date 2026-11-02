# Calm Edge

Source of https://calm-edge.github.io: free trading calculators, guides, and the marketing engine
for [Trading Journal AI](https://kallas8.gumroad.com/l/axltbh).

- `site/`: static site (Markdown articles, calculators, templates). `python site/build.py out/`
- `marketing/content/`: video scripts and post texts for every channel (`bank.py` writes `videos/*.json`)
- `marketing/video/`: vertical video renderer (app screenshots, captions, neural voice) and Pinterest pins
- `marketing/schedule.json`: approved posts with date and time; `publish.yml` posts them, `published.json` records the links

Educational content. Nothing here is financial advice.
