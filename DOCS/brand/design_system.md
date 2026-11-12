# Design System

## Tokens

Source of truth:

- `src/app/theme/tokens.py`
- `src/app/theme/map_palette.py`

Primary semantic tokens:

- Backgrounds: `bg`, `surface`, `surface_alt`
- Text: `text`, `text_muted`, `on_primary`
- Action: `primary`, `primary_hover`, `primary_pressed`
- Feedback: `success`, `warning`, `danger`, `info`
- Structure: `border`, `focus_ring`
- Navigation: `sidebar_bg`, `sidebar_text`, `sidebar_active`

## Typography Scale

- Caption: 12 px
- Body: 14 px
- Label strong: 16 px
- Section title: 20 px
- Page title: 28 px

## Spacing and Shape

- Spacing grid: 4, 8, 12, 16, 24, 32
- Radius: 6, 10, 14
- Min hit target: 32 px

## Component Specs

Reusable components in `src/app/widgets/components.py`:

- `PageHeader`: title + subtitle + optional actions
- `Card`: bordered content container
- `MetricTile`: label + value emphasis
- `StatusChip`: state text + icon cue
- `Banner`: info/warning/error/success message

Button variants (QSS dynamic property):

- `primary`
- `danger`
- default secondary

## Map and Algorithm Palette

Map states (color + non-color cue):

- wall (cross hatch)
- free (center dot)
- unknown (diagonal hatch)
- door (stripe)
- explored (dot)
- frontier (diamond)
- route (polyline)
- cleaned (circle)
- robot (label R)
- start (label S)

Algorithms (CVD-safe categorical mapping):

- BFS, DFS, UCS, Greedy, A*, IDDFS in `ALGORITHM_COLORS`

## Theming Engine

- Entry point: `apply_theme(app, mode)` in `src/app/theme/engine.py`
- Enforces Fusion style
- Builds complete `QPalette` including Active/Inactive/Disabled
- Sets Qt color scheme where API exists
- Applies generated QSS from `src/app/theme/stylesheet.py`
- Sets Windows immersive title bar mode when available
