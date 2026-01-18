from pathlib import Path
import yaml
import shutil
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from datetime import datetime

source_dir = "1957anti.ru"
target_dir = "posts"

class Article:
    def __init__(self ,path: str):
        self.path = path
        self.soup = self._get_soup()
        self.new_path_name = self._get_new_path_name()
        self.header = self.soup.article.header
        self.date = datetime.strftime(datetime.strptime(self.header.date.text.strip(), "%d.%m.%Y"), "%Y-%m-%d")
        self.author = self.header.find("div", class_="article-item-credits_author divider").a.text.strip()
        self.title = self.header.h1.text
        self.text_block = self._get_article_text_block()
        self.tags = self._get_tag_list()
        self.image_path, self.image_ext = self._get_image_data()
        self.cover = {"image": f"images/{self.new_path_name}.{self.image_ext}"} if self.image_path else None
        self.description = f"{self.title} - Российская коммунистическа партия (большевиков)"

    def _get_image_data(self):
        image_dom = self.soup.find("div", class_="article-item-image")
        if not image_dom:
            return None, None
        image_path = image_dom.img["src"]
        image_ext = image_path.split(".")[-1]
        return image_path, image_ext

    def _get_tag_list(self):
        tag_info = self.soup.article.footer.find("div", class_="article-item-tags")
        if not tag_info:
            return []
        return tag_info.text.strip("\n").split("\n")

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
    publ_list = [str(i) for i in Path(f"../{source_dir}/publications/item").glob("*.html")]
    #path = publ_list[0]
    for publ in publ_list:
        print(publ)
        art = Article(publ)
        md_art = art.convert_to_md()
        #l = [(k, v) for k, v in vars(art).items() if k not in ["text_block"]]
        #for i in l:
        #    print(i)

        metadata = {k:getattr(art,k) for k in ["author", "title", "description", "date", "cover", "tags"]}
        file_header = yaml.dump(metadata, allow_unicode=True, default_flow_style=False)
        full_art_str = f"---\n{file_header}\n---\n{md_art}"

        post_dir_str = f"{target_dir}/{art.new_path_name}"
        Path(post_dir_str).mkdir(parents=True, exist_ok=True)

        if art.cover:
            Path(f"{post_dir_str}/images").mkdir(parents=True, exist_ok=True)
            shutil.copy2(art.image_path.replace("../..", f"../{source_dir}"), f"{post_dir_str}/{art.cover['image']}")

        Path(f"{post_dir_str}/index.md").write_text(full_art_str)
    return None
#%%
main()
