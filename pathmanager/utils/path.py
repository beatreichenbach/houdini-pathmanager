import glob
import re
from pathlib import Path


def normalize_path(path: str) -> str:
    """Return the path with forward slashes, as required by DCCs."""

    return path.replace('\\', '/')


def find_files(path: str | Path) -> tuple[Path, ...]:
    """Return the files matching a path pattern with Houdini-style sequences."""

    path = Path(path)
    if path.exists():
        return (path,)

    text = str(path)
    try:
        # Common
        re_pattern = re.sub(r'<UDIM>', r'(1\\d{3})', text)

        # Nuke
        re_pattern = re.sub(r'%(UDIM)d', r'(1\\d{3})', re_pattern)
        re_pattern = re.sub(r'%0(\d)d', lambda m: rf'(\d{{{m.group(1)}}})', re_pattern)
        re_pattern = re.sub(r'#+', lambda m: rf'(\d{{{len(m.group())}}})', re_pattern)

        # Houdini
        re_pattern = re.sub(r'\$F(\d)', lambda m: rf'(\d{{{m.group(1)}}})', re_pattern)
        re_pattern = re.sub(r'\$F', lambda m: r'(\d+)', re_pattern)

        re_compile = re.compile(re_pattern)
    except re.error:
        return tuple()

    if re_pattern == text:
        return tuple()

    glob_pattern = re.sub(r'<UDIM>', '*', text)
    glob_pattern = re.sub(r'\$F\d?', '*', glob_pattern)
    glob_pattern = re.sub(r'#+', '*', glob_pattern)
    glob_pattern = re.sub(r'%0\dd', '*', glob_pattern)

    files = [Path(file) for file in glob.glob(glob_pattern) if re_compile.match(file)]
    return tuple(sorted(files))
