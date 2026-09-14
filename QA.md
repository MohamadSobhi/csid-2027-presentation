# Validation record

Validation performed on 2026-09-14 against the supplied matching PPTX.

- 40/40 PowerPoint exports visually inspected in contact sheets.
- 40/40 browser slide screenshots inspected in Chrome, compared to the PowerPoint exports.
- All exported images verified as 3840 x 2160 PNG.
- Source SHA-256 matches its pre-conversion hash; original PPTX was never saved or overwritten.
- Foreground labels on slide 33 initially disappeared beneath video. Fixed through a PowerPoint-derived transparent foreground layer and visually rechecked.
- Both original MP4s decoded and played in Chrome: slide 33 reached 8.3 seconds; slide 14 reached 22.7 seconds, with readyState 4 and no media errors.
- Tested Right, Space, Page Down, Left, Page Up, Home, End, overview opening and selecting slide 20, browser back/forward and refresh, and click/pointer-swipe navigation.
- Ordinary Chrome viewport: 1539 x 744; centered 16:9 canvas approximately 1323.10 x 744.24.
- In-app Chromium geometry at 1920 x 1080: canvas approximately 1920.61 x 1080.34.
- In-app Chromium geometry at 2560 x 1440: canvas approximately 2560.00 x 1440.00.
- In-app Chromium geometry at 3840 x 2160: canvas approximately 3840.61 x 2160.34.
- Subpixel rounding is below one CSS pixel. Original 16:9 aspect ratio retained.
- Browser screenshot tools could not reliably capture requested high-resolution viewports. These checks establish layout geometry, not complete high-resolution visual certification.
- Automated fullscreen was rejected with "Fullscreen is unavailable in this browser context." The implementation uses the standard Fullscreen API; a successful manual fullscreen test remains necessary.
- Connected Microsoft Edge browser was unavailable. Edge testing remains outstanding.
- Native video control behavior after the final control-handler correction, notes-popup behavior, and physical touch hardware remain partially unverified.
- No quantitative pixel-difference certification was performed for browser screenshots.
- No external assets/CDNs are used. Local HTTP viewing and media playback succeeded. Network-disconnected operation follows from the all-local architecture but was not tested by disabling the machine's network.
- Relative paths are used throughout. No live GitHub Pages deployment exists to test, and nested-path deployment was not independently exercised.
- Original PowerPoint timing is intentionally not replayed. Transitions are recorded for 36 slides; timing trees occur on 14, 33 and 34.
- Some browser captures showed transient stale pixels during rapid navigation; settled slide 33 was rechecked after the foreground fix. Full-frame high-resolution pixel comparison remains outstanding.

## Deployment

The requested repository was created as private. Its Pages settings say: "Upgrade or make this repository public to enable Pages." Repository visibility was not changed. `.nojekyll` and the static root layout support future deployment from `main` / `/(root)` when authorized and eligible.
