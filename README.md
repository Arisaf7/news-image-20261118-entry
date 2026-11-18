# news-image-20261118

[![make.fun](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/c/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Arisaf7/news-image-20261118-entry/rank.svg)](https://make.fun/c/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Arisaf7/news-image-20261118-entry/reward.svg)](https://make.fun/c/news-image-20261118)

make.fun entry for the **news-image-20261118** competition ($250): a program
that draws one image summing up the world news of Wednesday, 18 November
2026 — the U.S. sinking five Iranian oil tankers as the Gulf war escalated,
Ukraine's second-night strike on the Kerch Bridge, the UN's winter warning
for Gaza, COP31's decisive phase, and Israel's government talks — and writes
it to `/output/entry.png`.

## Run

```sh
python3 main.py
```

`main.py` is pure Python 3 standard library: it draws the graphic with a
built-in 5x7 bitmap font and encodes the PNG with `zlib`. No network, no
randomness, no timestamps — two runs write identical bytes.

The output directory is `$MAKEFUN_OUTPUT_DIR` (default `/output`).

## Layout

- Masthead: "THE WORLD IN ONE DAY — WEDNESDAY, 18 NOVEMBER 2026"
- Lead story: U.S. destroys five Iranian tankers; Iran hits back; Brent
  crude above $100 a barrel
- Ukraine, Gaza, COP31, Israel — one block each
- Also today: Quad leaders in Manila, the An-12 crash in Kemerovo, Robert
  Pattinson named the new James Bond

Sources: Al Jazeera, AP, Reuters, CENTCOM, United Nations.
