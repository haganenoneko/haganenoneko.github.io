from pathlib import Path
from datetime import datetime, timedelta
import re
from types import NoneType
from typing import Union

POSTDIR = Path.cwd() / "_posts"
CSS_HEADER_PATH = POSTDIR / "_md_css_header.md"
POSTNAME_PAT = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.*)(?:\.md)$")
HTML_FIGURE_ENV: str = """
<br>
<figure>
  <center>
    <img 
      src="https://github.com/haganenoneko/haganenoneko.github.io/blob/master/_posts/figs/{date}-figs/{figpath}?raw=true"
      alt="{alt_text}"
      title="{title}" width="{width}" height="{height}"
      style="horizontal-align:{ha}"
    />
  </center>
  <figcaption>
    <b> Fig. {fignum}{sep}{title} </b>
    <br>
    <p> {caption} </p>
  </figcaption>
</figure>
<br>
"""
INLINE_FIGURE_PAT = re.compile(
    r"\!\[([\w\s]+)\]\((.*)\)\n(?:\*\*){0,1}(Figure|Fig)\s(\d+)\.[^\w]{0,2}([^\*]+)(?:\*\*){0,2}"
)


def find_title(txt: str, level=1) -> Union[NoneType, str]:
    res = re.match(r"\#"*level + r"\s[^\n]+", txt)
    if res is None:
        return None
    else:
        return res.group(0)


def get_title(txt: str) -> str:
    if title is None:
        for i in range(1, 4):
            title = find_title(txt, level=i)
            if title:
                break
    if title is None:
        raise Exception("No title was found.")


def get_date(date: Union[str, datetime, NoneType], fmt="%Y/%m/%d") -> datetime:
    if isinstance(date, datetime):
        return date
    if date is None or date == 'today':
        return datetime.now()
    if isinstance(date, str):
        if date == 'tomorrow':
            return datetime.now() + timedelta(days=1)
        elif date == 'yesterday':
            return datetime.now() - timedelta(days=1)
        try:
            return datetime.strptime(date, fmt=fmt)
        except:
            raise Exception(f"Could not parse {date} with format {fmt}")

    raise Exception(f"Could not parse {date} as date.")


def get_fname_plink(
        date: datetime,
        postdir=POSTDIR,
        pat=POSTNAME_PAT) -> tuple[str]:
    yyyymm = datetime.strtime(date, fmt="%Y/%m")
    num = len(list(postdir.glob(pat.pattern)))

    plink = f"/posts/{yyyymm}/bp{num}"
    fname = datetime.strftime(date, fmt="%Y-%m-%d") + f"-bp{num}"
    return fname, plink


def create_header(
    txt: str, title: str = None, tags: list[str] = None,
    date: Union[str, datetime, NoneType] = None, date_fmt="%Y/%m/%d",
    postdir=POSTDIR, fname_pat=POSTNAME_PAT,
) -> None:

    title = get_title(txt)
    date = get_date(date, fmt=date_fmt)
    fname, plink = get_fname_plink(date, postdir=postdir, pat=fname_pat)
    tags = '' if tags is None else "\n  - ".join(tags)

    header = f"""---
    title: "{title}"
    date: {datetime.strftime(date, r"%Y-%m-%d")}
    permalink: {plink}
    tags:{tags}
    ---
    """
    return fname, header


def get_css_header(css_header_path: Path = CSS_HEADER_PATH) -> str:
    with open(css_header_path, 'r', encoding='utf-8') as io:
        return io.read()


def create_figure_env(
        figpath: str,
        fignum: int,
        title: str,
        caption: str,
        date: datetime,
        alt_text='',
        width='100%',
        height='100%',
        ha='middle',
        sep=': ', template=HTML_FIGURE_ENV) -> str:

    date_ = datetime.strftime(date, "%Y-%m-%d")
    return template.format(
        date=date_,
        figpath=figpath,
        alt_text=alt_text,
        title=title,
        width=width, height=height, ha=ha,
        fignum=fignum, sep=sep, caption=caption
    )


def find_inline_figures(txt: str, inline_fig_pat=INLINE_FIGURE_PAT) -> None:
    res = inline_fig_pat.findall(txt)
    return res 