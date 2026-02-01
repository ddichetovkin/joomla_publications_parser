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
        self.author = self._get_author()
        self.title = self.header.h1.text
        self.text_block = self._get_article_text_block()
        self.tags = self._get_tag_list()
        self.image_path, self.image_ext = self._get_image_data()
        self.cover = {"image": f"images/title.{self.image_ext}"} if self.image_path else None
        #self.description = f"{self.title} - Российская коммунистическа партия (большевиков)"
        self.ShowToc = True
        self.TocOpen = True

    def _get_author(self) -> str:
        author = self.header.find("div", class_="article-item-credits_author divider").a.text.strip()
        if author == "Балаев Пётр":
            author = "Петр Балаев"
        return author

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

    def prep_post_header(self) -> str:
        attr_list = ["author", "title", "date", "cover", "tags", "ShowToc", "TocOpen"]
        metadata = {attr:getattr(self, attr) for attr in attr_list}
        file_header = yaml.dump(metadata, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return file_header

def represent_list_in_flow_style(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

def main() -> None:
    publ_list = [str(i) for i in Path(f"../{source_dir}/publications/item").glob("*.html")]
    for publ in publ_list:
        print(publ)
        art = Article(publ)
        md_art = art.convert_to_md()

        yaml.add_representer(list, represent_list_in_flow_style)
        file_header = art.prep_post_header()
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
#%%
publ = "../1957anti.ru/publications/item/1332-golova-professora-vangengejma-saga-o-solovetskom-rasstrele.html"
art = Article(publ)

yaml.add_representer(list, represent_list_in_flow_style)
file_header = art.prep_post_header()
print(file_header)
