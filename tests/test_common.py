import zlib
import pytest
import xml.etree.ElementTree as ET

from common.helpers import (
    decode_xmp_blob,
    parse_xmp,
    custom_crs_parse_xmp,
    build_xmp,
    CRS_NS,
    RDF_NS,
)

def test_decode_xmp_blob_valid():
    # Create a simple XML string and compress it with zlib, with a 4-byte header prefix
    original_xml = "<root><child>value</child></root>"
    compressed = zlib.compress(original_xml.encode("utf-8"))
    # Prepend arbitrary 4 bytes to simulate Lightroom header
    blob = b"\x00\x01\x02\x03" + compressed

    decoded = decode_xmp_blob(blob)
    assert original_xml in decoded
    assert decoded.startswith("<root>")
    assert "</root>" in decoded


def test_decode_xmp_blob_invalid():
    # Pass random bytes that do not contain a valid zlib stream
    invalid_blob = b"not-a-valid-zlib-stream"
    decoded = decode_xmp_blob(invalid_blob)
    # Should catch exception and return empty string
    assert decoded == ""


@pytest.mark.skipif(
    not hasattr(parse_xmp, "__call__"),
    reason="python-xmp-toolkit not installed"
)
def test_parse_xmp_minimal():
    # Construct a minimal XMP packet that python-xmp-toolkit can parse
    xmp_str = """<x:xmpmeta xmlns:x="adobe:ns:meta/">
      <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description rdf:about=""
          xmlns:dc="http://purl.org/dc/elements/1.1/"
          xmlns:xmp="http://ns.adobe.com/xap/1.0/"
          dc:format="image/dng"
          xmp:CreatorTool="Adobe Photoshop Lightroom Classic 14.1.1 (Macintosh)">
        </rdf:Description>
      </rdf:RDF>
    </x:xmpmeta>"""
    parsed = parse_xmp(xmp_str)
    print(parsed)
    # Expect that keys like 'dc:creator' appear in the dict
    assert any("dc:format" in key for key in parsed['http://purl.org/dc/elements/1.1/'])
    assert any("xmp:CreatorTool" in key for key in parsed['http://ns.adobe.com/xap/1.0/'])


def test_custom_crs_parse_xmp_flat_attributes_and_elements():
    # Build an XMP string with CRS attributes and child elements
    xmp_str = f"""
    <x:xmpmeta xmlns:x="adobe:ns:meta/"
               xmlns:crs="{CRS_NS}"
               xmlns:rdf="{RDF_NS}">
      <rdf:RDF>
        <rdf:Description crs:Exposure2012="0.50">
          <crs:ToneCurvePV2012>
            <rdf:Seq>
              <rdf:li>0,0</rdf:li>
              <rdf:li>255,255</rdf:li>
            </rdf:Seq>
          </crs:ToneCurvePV2012>
        </rdf:Description>
      </rdf:RDF>
    </x:xmpmeta>
    """
    result = custom_crs_parse_xmp(xmp_str)
    # Should extract the attribute Exposure2012
    assert result.get("Exposure2012") == "0.50"
    # Should extract ToneCurvePV2012 sequence as a list
    assert isinstance(result.get("ToneCurvePV2012"), list)
    assert "0,0" in result["ToneCurvePV2012"]
    assert "255,255" in result["ToneCurvePV2012"]


def test_build_xmp_and_parse_roundtrip():
    # Given a simple slider dict, build XMP and parse to ensure tags exist
    slider_dict = {"Exposure2012": 0.75, "Contrast2012": 1.25}
    xmp_xml = build_xmp(slider_dict)

    # Parse the returned XML to ensure structure
    root = ET.fromstring(xmp_xml)

    # Navigate to rdf:Description under xmpmeta → rdf:RDF
    ns = {"x": "adobe:ns:meta/", "rdf": RDF_NS, "crs": CRS_NS}
    desc = root.find(".//rdf:Description", ns)
    assert desc is not None

    # Each slider key should appear as a child in the CRS namespace
    for key, val in slider_dict.items():
        elem = desc.find(f"crs:{key}", ns)
        assert elem is not None, f"Missing element for {key}"
        # Text should match formatted float
        assert elem.text == f"{val:.4f}"
