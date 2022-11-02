"""
Format a standard Markdown document into blog-ready format
"""
from numpy import vectorize
from collections import namedtuple
from pathlib import Path
from datetime import datetime, timedelta
import re
from types import NoneType
from typing import Union, Any 
import tkinter as tk
from tkinter.filedialog import askopenfilenames
import shutil 

POSTDIR = Path.cwd() / "_posts"
CSS_HEADER_PATH = POSTDIR / "_md_css_header.md"
POSTNAME_PAT = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.*)(?:\.md)$")

FIG_URL = "https://github.com/haganenoneko/haganenoneko.github.io/blob/master/_posts/figs/{date}-figs/{name}?raw=true"

HTML_FIGURE_ENV: str = """
<br>
<figure>
  <center>
    <img 
      src="{figpath}"
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
    r"\!\[(.*)\]\(([^\s]+)(.*)\)\n\*\*(?:(?:Figure|Fig)\.{0,1}\s)(\d)\.\s(.*)\*\*"
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
        post_dir: Path=POSTDIR,
        fig_url_str: str=FIG_URL,
        fig_env: str=HTML_FIGURE_ENV,
        fig_pat: re.Pattern=INLINE_FIGURE_PAT,
        postName_pat: re.Pattern=POSTNAME_PAT,
        cssHeader_path: Path=CSS_HEADER_PATH) -> None:

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
        res = re.match(f"{hashes} [^\n]+", self.text)
        return None if res is None else res.group(0)

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

    def get_fname_plink(self) -> tuple[str]:
        """Create `permalink` that goes in the post header"""

        yyyymm = datetime.strftime(self.postDate, format="%Y/%m")
        
        # index (starting from 1) of the current post for the given day
        self.postDateNum = 1+len(
            list(
                self._postdir.glob(self._postName_pat.pattern)
            )
        )

        plink = f"/posts/{yyyymm}/bp{self.postDateNum}"
        fname = datetime.strftime(self.postDate, format=r"%Y-%m-%d") +\
            f"-bp{self.postDateNum}"

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
            f"date: {datetime.strftime(self.postDate, format=r'%Y-%m-%d')}",
            f"permalink: {plink}",
            f"tags:{tags}",
            "---"
        ])
        
        return fname, header

    def get_css_header(self, fp: Path) -> str:
        with open(fp, 'r', encoding='utf-8') as io:
            return io.read()

    def create_figure_env(
            self,
            figpath: str,
            fignum: int,
            title: str,
            caption: str,
            alt_text='',
            width='100%',
            height='100%',
            ha='middle',
            sep=r'. ') -> str:
        
        return self._fig_env.format(
            figpath=figpath,
            alt_text=alt_text,
            title=title,
            width=width, height=height, ha=ha,
            fignum=fignum, sep=sep, caption=caption
        )

    def format_inline_figures(self, figDir: Path, **figkw) -> str:

        figinfo = [
            (r.start(), r.end(), r.groups()) 
            for r in self._fig_pat.finditer(self.text)
        ]

        newText = ''
        lastInd = 0 

        date_ = datetime.strftime(self.postDate, format=r"%Y-%m-%d")

        for start, end, info in figinfo:
            
            newText += self.text[lastInd:start]
            
            if len(info) == 5:
                alt, fp, title, num, cap = info 
            else:
                alt, fp, num, cap = info 
                title = None 

            fpath = Path(fp)
            if fpath.is_file():
                to_fp = figDir / f"{fpath.stem}{fpath.suffix}"
                shutil.copy(fpath, to_fp)
                assert to_fp.is_file()
                figpath = self._fig_url.format(
                    date=date_, 
                    name=fp.stem
                )
            else:
                figpath = str(fp)

            figtext = self.create_figure_env(
                figpath = figpath,
                fignum = num,
                title = title,
                caption = cap,
                alt_text = alt, 
                **figkw   
            )

            newText += figtext 
            lastInd = end + 1 

        return newText + self.text[lastInd:]

    def format(
        self, 
        fp: Path, 
        date: Union[datetime, str],
        encoding='utf-8', 
        date_fmt: str=r"%Y/%m/%d",
        tags: list[str]=None,
        figkw: dict[str, Any]={}) -> str:

        self.text = self._read(fp, encoding)
        self.postDate = self.get_date(date, fmt=date_fmt)

        figDir = f"{datetime.strftime(self.postDate, r'%Y-%m-%d')}-figs"
        figDir = fp.parent / 'figs' / figDir 
        
        if not figDir.is_dir():
            figDir.mkdir()

        fname, header = self.create_header(date, tags=tags)

        figText = self.format_inline_figures(figDir, **figkw)
        outText = '\n\n'.join([header, self._cssHeader, figText.strip()])
        
        outpath = self._postdir / f"{fname}.md"
        with open(outpath, 'w', encoding=encoding) as io:
            io.write(outText)

        print(f"Wrote text to {fname}")
        return outText 

if __name__ == '__main__':
    fp = open_files()[0]
    mf = MarkdownFormatter()
    mf.format(fp, 'today')
    