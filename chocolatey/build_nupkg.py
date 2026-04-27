#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manually build a Chocolatey .nupkg (zip with NuGet bookkeeping)."""
import uuid
import zipfile
from pathlib import Path

PKG_ID = "tokenmix-cli"
VERSION = "0.1.0"
NUSPEC = "tokenmix-cli.nuspec"
TOOLS_DIR = "tools"
OUTPUT = f"{PKG_ID}.{VERSION}.nupkg"

guid = uuid.uuid4().hex

ctypes = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />
  <Default Extension="psmdcp" ContentType="application/vnd.openxmlformats-package.core-properties+xml" />
  <Default Extension="nuspec" ContentType="application/octet" />
  <Default Extension="ps1" ContentType="application/octet" />
  <Default Extension="txt" ContentType="application/octet" />
</Types>
"""

rels = f"""<?xml version="1.0" encoding="utf-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Type="http://schemas.microsoft.com/packaging/2010/07/manifest" Target="/{NUSPEC}" Id="R1" />
  <Relationship Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="/package/services/metadata/core-properties/{guid}.psmdcp" Id="R2" />
</Relationships>
"""

psmdcp = f"""<?xml version="1.0" encoding="utf-8"?>
<coreProperties xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.openxmlformats.org/package/2006/metadata/core-properties">
  <dc:creator>TokenMix</dc:creator>
  <dc:description>CLI for TokenMix - one API key for 155+ LLMs</dc:description>
  <dc:identifier>{PKG_ID}</dc:identifier>
  <version>{VERSION}</version>
  <keywords>tokenmix ai llm openai gpt claude gemini deepseek chatbot cli rust</keywords>
  <dc:title>TokenMix CLI</dc:title>
  <lastModifiedBy>Manual</lastModifiedBy>
</coreProperties>
"""

with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(NUSPEC, NUSPEC)
    for f in sorted(Path(TOOLS_DIR).iterdir()):
        zf.write(str(f), f"tools/{f.name}")
    zf.writestr("[Content_Types].xml", ctypes)
    zf.writestr("_rels/.rels", rels)
    zf.writestr(f"package/services/metadata/core-properties/{guid}.psmdcp", psmdcp)

print(f"Created {OUTPUT}")
