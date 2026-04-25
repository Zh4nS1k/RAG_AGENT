import unittest
from rag_data import parse_adilet_html

class TestAdiletParser(unittest.TestCase):
    def test_parse_simple_html(self):
        html = """
        <article>
            <h3 id="z1">Статья 1. Основные понятия</h3>
            <p>Текст первой статьи.</p>
            <h3 id="z2">Статья 2. Область применения</h3>
            <p>Текст второй статьи.</p>
        </article>
        """
        docs = parse_adilet_html(html, "http://test.com")
        self.assertEqual(len(docs), 2)
        self.assertEqual(docs[0].metadata["article_id"], "z1")
        self.assertIn("Статья 1", docs[0].page_content)

if __name__ == '__main__':
    unittest.main()
