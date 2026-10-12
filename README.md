# LawCodex — Maldives (`mv`)

Legislation of the Republic of Maldives as plain Markdown, one file per text, in Dhivehi (the
official language), as published in consolidated form by **MVLaw**, the legislation database of
the Attorney General's Office.

Part of [LawCodex](https://github.com/LawCodex): the laws of every country as Markdown in git.

Retrieved: 2026-10-12. **242 files.**

## Contents

| Category | Directory | Files |
|---|---|---:|
| Constitution of the Republic of Maldives (2008, consolidated with its amendments) | `constitution/` | 1 |
| Laws (ޤާނޫނު), latest consolidation | `laws/<year>/` | 216 |
| Regulations (ގަވާއިދު) listed in the database | `regulations/<year>/` | 25 |
| **Total** | | **242** |

11 of the files carry `status: repealed` (MVLaw gives an abolition date).

## Structure

```
constitution/<mvlaw-id>-<slug>.md
laws/<year>/<mvlaw-id>-<slug>.md          year = date of entry into force (implemented_at)
regulations/<year>/<mvlaw-id>-<slug>.md
```

The `<slug>` is MVLaw's own Latin transliteration of the Dhivehi title (e.g.
`zakaathuge-aanoonu`). The Dhivehi title is in the front matter and the H1.

Front matter: `title`, `identifier` (law number, e.g. `27/2025`), `mvlaw_id`, `type`
(`constitution`, `act`, `regulation`), `jurisdiction`, `language` (`dv`), `date` (entry into force),
`published`, `consolidation` (name of the consolidated version, e.g. "with the seventh amendment"),
`status`, `abolished` (if any), `categories` (MVLaw volume), `source`, `source_pdf` (the original
gazetted PDF), `retrieved`.

Body: the section tree of the consolidation. Chapters (ބާބު) are `##`, articles `###`, deeper
levels `####`. Numbered sub-paragraphs ((ހ), (ށ)...) are paragraphs. Amendment notes recorded by
MVLaw against a provision are kept as `> ` quote lines right after it.

## Not covered

- Texts with no consolidated text in MVLaw (18): the historical constitutions of 1932–1998 and a few
  presidential decrees/notices whose content is only available as a scanned PDF.
- MVLaw states that its database is still being completed ("not all laws in this section may be
  visible yet"): laws not yet loaded in MVLaw are not in this repository. MVLaw listed 261
  legislative texts at retrieval time.
- No English translations: MVLaw publishes Dhivehi only (its English interface lists no texts).
- Other legal documents (decisions, rulings, standards) not listed among the 261 items.

## Sources

- MVLaw, Attorney General's Office of the Maldives — <https://mvlaw.gov.mv/dv/legislations>
  (official; linked from <https://agoffice.gov.mv>). The site is a server-rendered Inertia.js
  application: each page embeds its data as JSON (`<div id="app" data-page="...">`), which the scripts
  read. The JSON API (`/api/v1/...`) requires authentication and was not used.
- robots.txt allows all crawling; no terms restricting reuse were found on the site.

## Licence

Laws of the Maldives are official public texts. This compilation adds no copyrightable content.

## Regenerate

```
pip install -r scripts/requirements.txt
python scripts/mv_fetch.py      # caches pages under ../_raw/mv (1 request/second)
python scripts/mv_convert.py .  # writes the Markdown files
```
