from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from datetime import datetime

source_dir = "publications"
target_dir = "content"

class Article:
    def __init__(self ,path: str):
        self.path = path
        self.soup = self._get_soup()
        self.header = self.soup.article.header
        self.date = datetime.strftime(datetime.strptime(self.header.date.text.strip(), "%d.%m.%Y"), "%Y-%m-%d")
        self.author = self.header.find("div", class_="article-item-credits_author divider").a.text.strip()
        self.title = self.header.h1.text
        self.text_block = self._get_article_text_block()
        self.new_path_name = self._get_new_path_name()
        self.tag_list = self._get_tag_list()
        self.image_path = self.soup.find("div", class_="article-item-image").img["src"]

    def _get_tag_list(self):
        return self.soup.article.footer.find("div", class_="article-item-tags").text.strip("\n").split("\n")

    def _get_new_path_name(self):
        return "-".join(Path(self.path).stem.split("-")[1:])

    def _get_soup(self):
        with open(self.path, "r") as file:
            html_str = file.read()
        soup = BeautifulSoup(html_str, "lxml")
        return soup

    def _get_article_text_block(self):
        return self.soup.article.find("div", class_="article-item-text")

    def convert_to_md(self):
        markdown = md(
            str(self.text_block),
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
    l = [(k, v) for k, v in vars(art).items() if k not in ["text_block"]]
    for i in l:
        print(i)
    print("path:", art.path)

    return None
#%%
main()
