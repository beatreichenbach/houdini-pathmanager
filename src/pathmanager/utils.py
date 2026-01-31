import glob
import os
import re


def title(text: str) -> str:
    text = re.sub(r'([a-z0-9])([A-Z])', r'\g<1> \g<2>', text).replace('_', ' ').title()
    return text


def find_files(path: str) -> tuple[str, ...]:
    if os.path.exists(path):
        return (path,)

    try:
        re_pattern = re.sub(r'<UDIM>', r'(1\\d{3})', path)
        re_pattern = re.sub(r'%(UDIM)d', r'(1\\d{3})', re_pattern)
        re_pattern = re.sub(r'%0(\d)d', lambda m: f'(\d{{{m.group(1)}}})', re_pattern)
        re_pattern = re.sub(r'#+', lambda m: f'(\d{{{len(m.group())}}})', re_pattern)
        re_pattern = re.sub(r'\$F(\d)', lambda m: f'(\d{{{m.group(1)}}})', re_pattern)
        re_pattern = re.sub(r'\$F', lambda m: f'(\d+)', re_pattern)
        re_compile = re.compile(re_pattern)
    except re.error:
        return tuple()

    if re_pattern == path:
        return tuple()

    glob_pattern = re.sub(r'<UDIM>', '*', path)
    glob_pattern = re.sub(r'\$F\d?', '*', glob_pattern)
    glob_pattern = re.sub(r'#+', '*', glob_pattern)
    glob_pattern = re.sub(r'%0\dd', '*', glob_pattern)

    all_files = glob.glob(glob_pattern)
    files = [file for file in all_files if re_compile.match(file)]

    return tuple(sorted(files))
