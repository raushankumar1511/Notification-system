from django.test import SimpleTestCase

from notifications.services.render import extract_variables, render


class RenderTests(SimpleTestCase):
    def test_substitutes_known_vars(self):
        self.assertEqual(render("Hi {{name}}!", {"name": "Ann"}), "Hi Ann!")

    def test_missing_var_becomes_marker(self):
        self.assertEqual(render("Hi {{name}}!", {}), "Hi [name]!")

    def test_whitespace_in_placeholder(self):
        self.assertEqual(render("{{ name }}", {"name": "X"}), "X")

    def test_stray_braces_do_not_crash(self):
        self.assertEqual(render("100% off {price", {"price": 5}), "100% off {price")

    def test_html_escaping(self):
        out = render("{{v}}", {"v": "<b>x</b>"}, escape_html=True)
        self.assertEqual(out, "&lt;b&gt;x&lt;/b&gt;")

    def test_no_escape_by_default(self):
        self.assertEqual(render("{{v}}", {"v": "<b>"}), "<b>")

    def test_extract_variables_distinct_ordered(self):
        self.assertEqual(
            extract_variables("{{a}} {{b}} {{a}}"), ["a", "b"]
        )
