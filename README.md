# CSID 2027 presentation

A static, fidelity-first browser presentation of Mohamad Sobhi's supplied CSID PowerPoint. The scientific content and original PPTX are not edited. All 40 slides are rendered by desktop Microsoft PowerPoint as lossless 3840 x 2160 PNG images.

## Source and requirements

The matching source on the authoring machine is:

`D:\PhD_ENSAM\CSID_Comité de suivi individuel\PhD CSID Presentation_Mohamad Sobhi 2027.pptx`

The path originally supplied in the request used different folder separators and does not exist on this machine. The local, ignored `source.local.json` points to the matching file above. The PPTX is deliberately excluded from Git.

Regeneration requires Windows, Microsoft PowerPoint, Python 3.10+, and the original fonts installed on the rendering machine:

```powershell
python -m pip install -r requirements.txt
```

Viewing requires only a modern browser and a local static HTTP server. There are no CDNs, runtime package dependencies, analytics, or external fonts.

## Local viewing

```powershell
cd D:\Projects\csid-2027-presentation
python -m http.server 8000 --bind 127.0.0.1
```

Open http://localhost:8000. Internet access is unnecessary. Direct `file://` viewing is not supported because metadata is loaded with fetch.

## Regeneration

After editing and saving the source PowerPoint, run:

```powershell
python D:\Projects\csid-2027-presentation\tools\build_presentation.py
```

On another machine, specify the source once per build or set `CSID_PPTX`:

```powershell
python tools/build_presentation.py --source "C:\path\presentation.pptx"
```

The script inspects Open XML, follows presentation slide order, extracts embedded media and notes, exports 4K slides and overview thumbnails through PowerPoint COM, and creates foreground layers above videos where needed. It builds in a temporary project directory and replaces only generated `slides`, `assets`, and `data` directories after successful rendering. Application code and Git configuration remain intact. Removed slides/media are removed from generated output. Do not store hand-authored assets inside those generated directories. A SHA-256 check verifies that the source file has not changed.

To publish an updated repository after regeneration:

```powershell
git add slides assets data
git commit -m "Update presentation from PowerPoint"
git push origin main
```

## Architecture

- `index.html`: clean audience presentation canvas.
- `css/presentation.css`: viewport fitting, transient controls, overview grid.
- `js/presentation.js`: navigation, bounded neighboring-image preload, media and separate notes window.
- `slides/`: lossless 4K PowerPoint exports.
- `slides/thumbs/`: small WebP overview thumbnails.
- `assets/video/`: original embedded MP4 files.
- `assets/images/`: original video posters and PowerPoint-rendered foreground layers.
- `data/slides.json`: dimensions, ordered slides, media rectangles, foreground assets and source text.
- `data/notes.json`: notes keyed by one-based slide number.
- `data/source-analysis.json`: source hash, font inventory, package element counts, media and timing inventory.
- `tools/build_presentation.py`: reproducible conversion pipeline.

The slide stays at its original aspect ratio and is never cropped or stretched. A dark background fills unused viewport space. The current image is decoded before display; adjacent slides and the next two are preloaded. Distant overview images are lazy-loaded. URLs use `#slide-N`, including on refresh and browser back/forward navigation.

## Controls

| Input | Action |
| --- | --- |
| Right, Space, Page Down | Next slide |
| Left, Page Up | Previous slide |
| Home / End | First / last slide |
| F | Toggle fullscreen |
| O | Toggle overview |
| Escape | Close overview or leave browser fullscreen |
| N | Open separate presenter notes window |
| Click/tap left quarter | Previous slide |
| Click/tap elsewhere | Next slide |
| Swipe left/right | Next/previous slide |

Hover a video to reveal its native playback controls. Playback requires user interaction; nothing autoplays with sound. Media pauses when leaving its slide. Keyboard shortcuts defer to focused native media controls and buttons.

## Media and notes

Two original MP4s are preserved on slides 14 and 33, at normalized PowerPoint rectangles. Slide 33's foreground labels are preserved above the video using a transparent raster layer derived from PowerPoint renders. No separate embedded audio objects were found; any audio inside the videos remains intact. Browser video support depends on the original codecs.

Notes exist on slides 32, 36 and 37. They are never inserted into the audience document. Press N only on the presenter's display, and share only the audience window. Notes are separate files, not access-controlled secrets: anyone with access to a deployed static site could request its notes JSON.

## GitHub Pages

Repository: https://github.com/MohamadSobhi/csid-2027-presentation

Visibility: **private**. The account's Pages settings currently report: **"Upgrade or make this repository public to enable Pages."** No public deployment or visibility change has been made.

The project is ready for branch-based Pages deployment using `main` and `/(root)`, with `.nojekyll` and relative asset URLs. Once an eligible plan or explicitly approved visibility change is in place, go to repository Settings > Pages, choose Deploy from a branch, select main and /(root), and save. A private repository does not by itself guarantee a private Pages website. Review the intended audience before enabling publication.

## Fidelity and limitations

Slides are faithful PowerPoint raster exports, not editable HTML reconstructions. Embedded charts/diagrams/tables/equations are preserved visually. No native chart or Office Math objects were detected; scientific graphics also occur as images. Native PowerPoint animation timelines on slides 14, 33 and 34 and transitions on 36 slides are not replayed in HTML. Videos remain interactive. Original wording, clipped source content, page-number inconsistencies and dates are retained.

Font inventory includes direct slide fonts such as Gill Sans MT, Arial, Verdana, Aptos, Aptos Display, Times New Roman, NPIGol, NPIBaran, Sans Serif Collection, AkayaTelivigala, Rockwell Nova Extra Bold and Circular Std Book Italic; theme definitions add further fonts listed in source-analysis.json. Browser fonts do not affect raster slide text. Regeneration on a different machine may substitute unavailable fonts.

Three hyperlink-click elements were found, associated with media actions; no normal navigable hyperlink overlays were extracted. Visible URL text remains visually unchanged.

Current media extraction handles embedded media with direct shape transforms. Newly introduced grouped, rotated, cropped or externally linked media require additional validation. External media links cause the build to fail rather than silently discard playback.

## QA and browser support

All 40 source renders and all 40 browser slides were visually inspected. The slide 33 foreground-label issue was corrected and rechecked. Chrome navigation, overview selection, URL history/refresh and both MP4 playback streams were exercised. The ordinary Chrome viewport was 1539 x 744. Additional viewport geometry checks use the in-app Chromium browser.

The connected Edge browser is unavailable. Automated Chrome fullscreen was rejected by the browser context, so successful interactive fullscreen is not certified. High-resolution screenshot capture has tool limitations; see QA.md for the precise validation status. Touch/swipe is implemented but has not been validated on physical touch hardware. No deployed Pages site exists to test.
