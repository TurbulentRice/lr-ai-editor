# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def build_xmp(sliders: dict) -> str:
    """
    Tiny XML builder - creates a Lightroom-compatible DevelopSettings fragment.
    Extend as needed for more sliders!
    """
    slider_tags = "\n    ".join(
        f'<crs:{k}>{v:.4f}</crs:{k}>' for k, v in sliders.items()
    )
    return f"""<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/"
           xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
       xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/">
    {slider_tags}
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""
