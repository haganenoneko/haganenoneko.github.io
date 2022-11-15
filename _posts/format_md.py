"""
Format a standard Markdown document into blog-ready format
"""
from numpy import vectorize
from collections import namedtuple
"""
Format a standard Markdown document into blog-ready format
"""
from numpy import vectorize
from pathlib import Path
from datetime import datetime, timedelta
import re
from types import NoneType
from typing import Union, Any 
import tkinter as tk
from tkinter.filedialog import askopenfilenames
import shutil , Any
import tkinter as tk
from tkinter.filedialog import askopenfilenames
import shutil

POSTDIR = Path.cwd() / "_posts"
CSS_HEADER_PATH = POSTDIR / "_md_css_header.md"
POSTNAME_PAT = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.*)(?:\.md)$")

FIG_URL = "https://github.com/haganenoneko/haganenoneko.github.io/blob/master/_posts/figs/{date}-figs/{name}?raw=true"


FIG_URL = "https://github.com/haganenoneko/haganenoneko.github.io/blob/master/_posts/figs/{date}-figs/{name}?raw=true"

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


def open_files(initialdir: Path = POSTDIR, **kwargs) -> list[Path]:
    """Open markdown files to process"""
    root = tk.Tk()
    files = askopenfilenames(
        title="Open a Markdown file to process.",
        initialdir=initialdir,
        filetypes=(
            ("Markdown files", "*.md"),
        ), **kwargs
    )
    root.destroy()
    return list(map(Path, files))


class MarkdownFormatter:
    def __init__(
            self,
            post_dir: Path = POSTDIR,
            fig_url_str: str = FIG_URL,
            fig_env: str = HTML_FIGURE_ENV,
            fig_pat: re.Pattern = INLINE_FIGURE_PAT,
            postName_pat: re.Pattern = POSTNAME_PAT,
            cssHeader_path: Path = CSS_HEADER_PATH) -> None:

        self.text: str = None
        self.postDate: datetime = None
        self.postDateNum: int = None

        self._vstrip = vectorize(lambda x: x.strip())

        self._fig_pat = fig_pat
        self._fig_env = fig_env
        self._fig_url = fig_url_str

        self._postdir = post_dir
        self._postName_pat = postName_pat
        self._cssHeader: str = self.get_css_header(cssHeader_path)

    def _read(self, fp: Path, enc: str) -> str:
        with open(fp, 'r', encoding=enc) as io:
            return io.read()

    def find_title(self, level=1) -> Union[NoneType, str]:
        """Looks for a title, but expects it to be at the beginning of the documnet"""

        hashes = "#" * level
        pat = re.compile(f"(?:{hashes}\s)([^\n]+)\n")

        for r in pat.finditer(self.text):
            return r.group(1)

        return None

    def get_title(self, title: str) -> str:
        """Find first heading with largest number of #s"""
        if title is None:
            for i in range(1, 4):
                title = self.find_title(level=i)
                if title:
                    break

        if title is None:
            raise Exception("No title was found.")

        return title

    @staticmethod
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

        return fname, plink

    def create_header(
        self,
        title: str = None,
        tags: list[str] = None,
    ) -> tuple[str, str]:
        """Create header that contains metadata for the blog post"""

        title = self.get_title(title)
        fname, plink = self.get_fname_plink()
        tags = '' if tags is None else "\n  - ".join(tags)

        header = '\n'.join([
            '---',
            f"title: \"{title}\"",
            f"date: {self.postDateStr}",
            f"permalink: {plink}",
            f"tags:{tags}",
            "---"
        ])

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