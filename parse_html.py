from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md

source_dir = "publications"

class Article:
    def __init__(self ,path: str):
        self.path = path
        self.soup = self._get_soup()
        self.article_text_block = self._get_article()

    def _get_soup(self):
        with open(self.path, "r") as file:
            html_str = file.read()
        soup = BeautifulSoup(html_str, "lxml")
        return soup

    def get_paragraph_list(self):
        item_list = self.article.find_all(True, recursive=False)
        return item_list

    def _get_article(self):
        return self.soup.article.find("div", class_="article-item-text")

    def convert_to_md(self):
        markdown = md(
            str(self.article_text_block),
            heading_style="ATX",      # # Заголовок, а не =========
            strip=["script", "style", "nav", "footer"],  # удалим ненужное
            # convert=['h1', 'h2', 'p', 'ul', 'ol', 'blockquote', 'a', 'strong', 'em', 'pre', 'code', 'img']
        )
        return markdown
#%%

def main() -> None:
    publ_list = [str(i) for i in Path(source_dir).glob("*.html") if i.stem.startswith("2444-")]
    path = publ_list[0]
    art = Article(path)
    md_art = art.convert_to_md()
    print(md_art)
    return None
#%%
main()
