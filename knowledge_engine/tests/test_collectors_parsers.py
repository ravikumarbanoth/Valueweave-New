import tempfile
import unittest
from pathlib import Path

from knowledge_engine.collectors.base import BaseCollector, CollectorRegistry, FetchResult
from knowledge_engine.collectors.csv_collector import CSVCollector
from knowledge_engine.collectors.json_collector import JSONCollector
from knowledge_engine.collectors.rss_collector import RSSCollector
from knowledge_engine.collectors.xml_collector import XMLCollector
from knowledge_engine.parsers.base import ParseError
from knowledge_engine.parsers.csv_parser import CSVParser
from knowledge_engine.parsers.html_table_parser import HTMLTableParser
from knowledge_engine.parsers.json_parser import JSONParser
from knowledge_engine.parsers.pdf_parser import PDFParser
from knowledge_engine.parsers.rss_parser import RSSParser
from knowledge_engine.parsers.xml_parser import XMLParser


def _write(tmp_dir: str, name: str, content: str) -> str:
    path = Path(tmp_dir) / name
    path.write_text(content, encoding="utf-8")
    return str(path)


class CollectorTest(unittest.TestCase):
    def test_csv_collector_reads_local_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "data.csv", "id,name\n1,Alpha\n")
            result = CSVCollector().fetch(path)
            self.assertTrue(result.ok)
            self.assertIn("Alpha", result.payload)

    def test_collector_returns_error_result_not_exception_for_missing_file(self):
        result = CSVCollector().fetch("/nonexistent/path/data.csv")
        self.assertFalse(result.ok)
        self.assertIsNotNone(result.error)

    def test_supports_detection_by_extension(self):
        self.assertTrue(CSVCollector().supports("data.csv"))
        self.assertFalse(CSVCollector().supports("data.json"))
        self.assertTrue(JSONCollector().supports("data.json"))
        self.assertTrue(XMLCollector().supports("data.xml"))
        self.assertTrue(RSSCollector().supports("feed.rss"))
        self.assertTrue(RSSCollector().supports("https://example.com/blog/feed"))


class CollectorRegistryTest(unittest.TestCase):
    def setUp(self):
        self.registry = CollectorRegistry()
        self.registry.register(CSVCollector())
        self.registry.register(JSONCollector())

    def test_get_by_name(self):
        self.assertIsInstance(self.registry.get("csv_collector"), CSVCollector)

    def test_get_unknown_name_raises(self):
        with self.assertRaises(KeyError):
            self.registry.get("nonexistent")

    def test_autodetect_picks_matching_collector(self):
        self.assertIsInstance(self.registry.autodetect("data.json"), JSONCollector)

    def test_autodetect_raises_when_nothing_matches(self):
        with self.assertRaises(ValueError):
            self.registry.autodetect("data.pdf")

    def test_duplicate_registration_raises(self):
        with self.assertRaises(ValueError):
            self.registry.register(CSVCollector())

    def test_custom_collector_plugin(self):
        class EchoCollector(BaseCollector):
            name = "echo_collector"
            version = "0.0.1"

            def fetch(self, source, **kwargs):
                return FetchResult(payload=source, source_url=source, collector_name=self.name, collector_version=self.version)

        registry = CollectorRegistry()
        registry.register(EchoCollector())
        result = registry.get("echo_collector").fetch("hello")
        self.assertEqual(result.payload, "hello")


class CSVParserTest(unittest.TestCase):
    def test_parses_header_and_rows(self):
        records = CSVParser().parse("id,name\n1,Alpha\n2,Beta\n")
        self.assertEqual(records, [{"id": "1", "name": "Alpha"}, {"id": "2", "name": "Beta"}])

    def test_non_string_payload_raises(self):
        with self.assertRaises(ParseError):
            CSVParser().parse({"not": "a string"})


class JSONParserTest(unittest.TestCase):
    def test_parses_top_level_list(self):
        records = JSONParser().parse('[{"id": "1"}, {"id": "2"}]')
        self.assertEqual(len(records), 2)

    def test_parses_already_decoded_list(self):
        records = JSONParser().parse([{"id": "1"}])
        self.assertEqual(records, [{"id": "1"}])

    def test_auto_locates_single_list_valued_key(self):
        records = JSONParser().parse({"results": [{"id": "1"}], "meta": {"count": 1}})
        self.assertEqual(records, [{"id": "1"}])

    def test_records_path_disambiguates(self):
        payload = {"data": {"items": [{"id": "1"}]}}
        records = JSONParser().parse(payload, records_path="data.items")
        self.assertEqual(records, [{"id": "1"}])

    def test_single_object_becomes_one_record(self):
        records = JSONParser().parse({"id": "1", "name": "solo"})
        self.assertEqual(records, [{"id": "1", "name": "solo"}])

    def test_invalid_json_string_raises(self):
        with self.assertRaises(ParseError):
            JSONParser().parse("{not valid json")

    def test_ambiguous_multiple_lists_raises(self):
        with self.assertRaises(ParseError):
            JSONParser().parse({"a": [{"id": "1"}], "b": [{"id": "2"}]})


class XMLParserTest(unittest.TestCase):
    def test_auto_detects_repeated_record_element(self):
        xml = "<root><record><a>1</a><b>x</b></record><record><a>2</a><b>y</b></record></root>"
        records = XMLParser().parse(xml)
        self.assertEqual(records, [{"a": "1", "b": "x"}, {"a": "2", "b": "y"}])

    def test_explicit_record_tag(self):
        xml = "<root><item><a>1</a></item></root>"
        records = XMLParser().parse(xml, record_tag="item")
        self.assertEqual(records, [{"a": "1"}])

    def test_attributes_become_at_prefixed_keys(self):
        xml = '<root><record id="r1"><a>1</a></record><record id="r2"><a>2</a></record></root>'
        records = XMLParser().parse(xml)
        self.assertEqual(records[0]["@id"], "r1")

    def test_malformed_xml_raises(self):
        with self.assertRaises(ParseError):
            XMLParser().parse("<root><unclosed>")

    def test_no_repeated_element_raises(self):
        with self.assertRaises(ParseError):
            XMLParser().parse("<root><a>1</a><b>2</b></root>")


class RSSParserTest(unittest.TestCase):
    def test_parses_rss_items(self):
        rss = """<rss><channel>
            <item><title>First</title><link>https://example.com/1</link></item>
            <item><title>Second</title><link>https://example.com/2</link></item>
        </channel></rss>"""
        records = RSSParser().parse(rss)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["title"], "First")
        self.assertEqual(records[0]["link"], "https://example.com/1")

    def test_parses_atom_entries_with_href_link(self):
        atom = """<feed xmlns="http://www.w3.org/2005/Atom">
            <entry><title>Only</title><link href="https://example.com/only"/></entry>
        </feed>"""
        records = RSSParser().parse(atom)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["link"], "https://example.com/only")

    def test_no_entries_raises(self):
        with self.assertRaises(ParseError):
            RSSParser().parse("<rss><channel><title>Empty feed</title></channel></rss>")


class HTMLTableParserTest(unittest.TestCase):
    def test_parses_simple_table(self):
        html = """<html><body><table>
            <tr><th>id</th><th>name</th></tr>
            <tr><td>1</td><td>Alpha</td></tr>
            <tr><td>2</td><td>Beta</td></tr>
        </table></body></html>"""
        records = HTMLTableParser().parse(html)
        self.assertEqual(records, [{"id": "1", "name": "Alpha"}, {"id": "2", "name": "Beta"}])

    def test_no_table_raises(self):
        with self.assertRaises(ParseError):
            HTMLTableParser().parse("<html><body><p>no tables here</p></body></html>")

    def test_table_index_selects_correct_table(self):
        html = """<table><tr><th>a</th></tr><tr><td>1</td></tr></table>
                  <table><tr><th>b</th></tr><tr><td>2</td></tr></table>"""
        records = HTMLTableParser().parse(html, table_index=1)
        self.assertEqual(records, [{"b": "2"}])

    def test_header_only_table_raises(self):
        with self.assertRaises(ParseError):
            HTMLTableParser().parse("<table><tr><th>a</th></tr></table>")


class PDFParserTest(unittest.TestCase):
    def test_is_an_explicit_placeholder(self):
        with self.assertRaises(NotImplementedError):
            PDFParser().parse(b"%PDF-1.4 ...")


if __name__ == "__main__":
    unittest.main()
