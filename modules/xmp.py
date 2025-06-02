import xml.etree.ElementTree as ET
import zlib
from libxmp import XMPMeta
from libxmp.utils import object_to_dict

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

# Namespace for Camera Raw settings in XMP
CRS_NS = "http://ns.adobe.com/camera-raw-settings/1.0/"
# Namespace for RDF sequences
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

# ---------------------------------------------------------------------------- #
# XMP Decoding
# ---------------------------------------------------------------------------- #
def decode_xmp_blob(xmp_blob: bytes) -> str:
    """
    Decode a Lightroom XMP BLOB from the catalog into a UTF-8 XML string.
    Only work for bytes, not strings. 
    """
    # zlib-decompress the raw bytes (skip any leading header)
    try:
        # Some Lightroom XMP BLOBs include a 4-byte header before the actual zlib data.
        header_index = xmp_blob.find(b'\x78\x9c')
        to_decompress = xmp_blob[header_index:] if header_index != -1 else xmp_blob
        xml_bytes = zlib.decompress(to_decompress)
        return xml_bytes.decode("utf-8", errors="replace")
    except (zlib.error, UnicodeDecodeError) as _e:
        print(f' ==> FAILED to decode xmp blob: {_e}')
        return ""

# ---------------------------------------------------------------------------- #
# XMP Parsing
# ---------------------------------------------------------------------------- #
def parse_xmp(xmp_str) -> dict:
    """
    Uses Python XMP Toolkit
    @see https://github.com/python-xmp-toolkit/python-xmp-toolkit/tree/master
    """
    xmp = XMPMeta(xmp_str=xmp_str)
    return object_to_dict(xmp)

def custom_crs_parse_xmp(xmp_str: str) -> dict:
    """
    Custom funciton to parse the decoded XMP string and extract all tags under the Camera Raw namespace.
    Captures namespace-qualified attributes (e.g., crs:Exposure2012) and element text nodes.
    Returns a dict mapping each tag (without namespace) to its text value or attribute value.

    TODO: Either extrapolate or ignore nested attributes
    """
    parsed = {}
    try:
        root = ET.fromstring(xmp_str)

        # First, capture all namespace-qualified attributes on root <rdf:Description> and any child
        for elem in root.iter():
            # Check attributes of each element
            for attr_key, attr_val in elem.attrib.items():
                if attr_key.startswith(f"{{{CRS_NS}}}"):
                    tag_name = attr_key.split("}", 1)[1]
                    parsed[tag_name] = attr_val

        # Next, capture any child elements under Camera Raw namespace.
        for elem in root.iter():
            if elem.tag.startswith(f"{{{CRS_NS}}}"):
                tag_name = elem.tag.split("}", 1)[1]
                # Check if there are any nested <rdf:li> elements beneath this tag
                li_elems = elem.findall(f".//rdf:li", namespaces={"rdf": RDF_NS})
                if li_elems:
                    # Collect all <rdf:li> text values into a list
                    parsed[tag_name] = [li.text for li in li_elems if li.text is not None]
                else:
                    # If no nested list items, use direct text if available
                    if elem.text and elem.text.strip():
                        parsed[tag_name] = elem.text.strip()
    except ET.ParseError as _e:
        print(f' ==> FAILED to parse xmp str: {_e}')
        pass
    return parsed

# ---------------------------------------------------------------------------- #
# XMP Building
# ---------------------------------------------------------------------------- #
def build_xmp(slider_dict: dict[str, float]) -> str:
    rdf = ET.Element("{adobe:ns:meta/}xmpmeta", nsmap={
        None: "adobe:ns:meta/",
        "crs": CRS_NS,
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    })
    desc = ET.SubElement(
        ET.SubElement(rdf, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF")
        , "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
    for k, v in slider_dict.items():
        ET.SubElement(desc, f"{{{CRS_NS}}}{k}").text = f"{v:.4f}"
    return ET.tostring(rdf, xml_declaration=True, encoding="utf-8").decode()
