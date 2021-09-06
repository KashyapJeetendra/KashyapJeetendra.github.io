import os
from datetime import datetime
import re
from requests import get


highlight_js = get(
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.2.0/highlight.min.js"
    ).content.decode()


xml = """
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{}
</urlset>
"""


with open("_code/minified.css", "r") as f:
    style_css = f.read()

with open("_code/highlight.css", "r") as f:
    hightlight_css = f.read()

with open("_code/header.html", "r") as f:
    header = f.read().replace("/* style */", style_css + hightlight_css)

with open("_code/footer.html", "r") as f:
    footer = f.read().replace("// highlight", highlight_js)


def convert_date(timestamp):
    parsed_date = datetime.utcfromtimestamp(int(timestamp))
    return (
        parsed_date.strftime('%B %d, %Y'),
        parsed_date.strftime('%Y-%m-%d')
    )


def process_code(page_content):

    match = re.findall("<c-(.*?)>", page_content)

    if match:

        for language in match:
            page_content = page_content.replace(
                f"<c-{language}>",
                f"""<pre><code class='language-{language}'>"""
            ).replace(
                "<c>",
                "</code></pre>"
            )

    return page_content


pages = []


for page in os.listdir("_code/pages"):
    page_loc = f"_code/pages/{page}"
    with open(page_loc,"r") as f:
        page_content = process_code(f.read())

    heading =  page.split('.')[0]
    new_page_loc = page.replace(' ','-').lower()
    page_m_time, t = convert_date(os.path.getmtime(page_loc))
    pages.append({
        "loc": new_page_loc,
        "m_time": page_m_time,
        "heading": heading,
        "xml_time": t
    })

    with open(f"blog/{new_page_loc}","w") as f:
        f.write(f"""
        {header.replace("<!-- title -->",heading)}
        <article>
        <header>
        <h1>{heading}</h1>
        <time datetime="{t}">{page_m_time}</time>
        </header>
        {page_content}
        </article>
        {footer}
        """)

with open(f"blog/index.html","w") as f:

    li = ""
    urls = ""

    for page in pages:

        urls += f"""
        <url>
            <loc>https://www.jkashyap.com/blog/{page["loc"]}</loc>
            <lastmod>{page["xml_time"]}</lastmod>
        </url>
        """

        li += f"""
        <li>
        <a href="{page["loc"]}">
        <header>
        <h2>{page["heading"]}</h2>
        <time>{page["m_time"]}</time>
        </header>
        </a>
        </li>
        """

    f.write(f"""
    {header.replace("<!-- title -->", "Jeetendra Kashyap Blog")}
    {li}
    {footer}
    """)

with open("sitemap.xml","w") as f:
    f.write(xml.format(urls))
