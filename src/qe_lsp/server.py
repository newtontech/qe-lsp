"""
qe Language Server Protocol implementation
"""

try:
    from pygls.lsp.server import LanguageServer
except ImportError:
    from pygls.server import LanguageServer

QE_KEYWORDS = [
    "&CONTROL",
    "&SYSTEM",
    "&ELECTRONS",
    "&IONS",
    "&CELL",
    "ATOMIC_SPECIES",
    "ATOMIC_POSITIONS",
    "K_POINTS",
    "CELL_PARAMETERS",
]

QE_HOVER_DOCS = {
    "&CONTROL": "Calculation control namelist for Quantum ESPRESSO inputs.",
    "&SYSTEM": "System definition namelist, including cell, atoms, cutoffs, and occupations.",
    "&ELECTRONS": "Electronic minimization namelist for convergence and mixing settings.",
}

server = LanguageServer("qe-lsp", "0.1.0")

@server.feature("textDocument/completion")
def completion(params):
    return [
        {
            "label": keyword,
            "kind": 14,
            "detail": "Quantum ESPRESSO input keyword",
        }
        for keyword in QE_KEYWORDS
    ]

@server.feature("textDocument/hover")
def hover(params):
    keyword = next(iter(QE_HOVER_DOCS))
    return {
        "contents": {
            "kind": "markdown",
            "value": f"**{keyword}**\n\n{QE_HOVER_DOCS[keyword]}",
        }
    }

@server.feature("textDocument/diagnostic")
def diagnostic(params):
    return []

def main():
    server.start_io()

if __name__ == "__main__":
    main()
