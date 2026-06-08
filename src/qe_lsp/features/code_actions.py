"""Code actions provider for Quantum ESPRESSO input files.

Provides quick fixes for common QE input errors: unclosed namelists, unknown
keywords (with typo correction), invalid enum values, casing fixes, missing
required namelists, and deprecated keyword replacements.  Each code action
produces a minimal TextEdit that preserves surrounding formatting.
"""

from __future__ import annotations

from typing import Optional

from lsprotocol.types import (
    CodeAction,
    CodeActionKind,
    Diagnostic,
    Position,
    Range,
    TextEdit,
    WorkspaceEdit,
)

from ..parser import normalize_value, parse_qe_input
from ..features.lint import (
    DEPRECATED_KEYWORDS,
    KNOWN_PARAMETERS,
    VALID_NAMELISTS,
    RULE_DEPRECATED_KEYWORD,
    RULE_INCONSISTENT_SETTINGS,
    RULE_INVALID_KEYWORD_VALUE,
    RULE_MISSING_ATOMIC_POSITIONS,
    RULE_MISSING_ATOMIC_SPECIES,
    RULE_MISSING_CONTROL_CALC,
    RULE_MISSING_REQUIRED_SECTION,
    RULE_MISSING_SYSTEM_ECUTWFC,
    RULE_ORPHAN_PARAMETER,
    RULE_UNKNOWN_KEYWORD,
    RULE_UNKNOWN_NAMELIST,
)

# ------------------------------------------------------------------
# Typo correction table: common misspellings -> correct keyword
# ------------------------------------------------------------------

_KEYWORD_TYPOS: dict[str, str] = {
    "calulation": "calculation",
    "calcualtion": "calculation",
    "calculaton": "calculation",
    "calculatin": "calculation",
    "calculatio": "calculation",
    "clculation": "calculation",
    "ecutwcf": "ecutwfc",
    "ecutwf": "ecutwfc",
    "ecutrhow": "ecutrho",
    "ecutrh": "ecutrho",
    "ecutrbo": "ecutrho",
    "cutwfc": "ecutwfc",
    "ibrav": "ibrav",
    "ibrve": "ibrav",
    "ibarv": "ibrav",
    "occupations": "occupations",
    "ocupations": "occupations",
    "occupaton": "occupations",
    "occupations": "occupations",
    "smearing": "smearing",
    "smaring": "smearing",
    "smereing": "smearing",
    "smering": "smearing",
    "degauss": "degauss",
    "degaus": "degauss",
    "degausse": "degauss",
    "diagonalisation": "diagonalization",
    "diagonalizaton": "diagonalization",
    "diagionalization": "diagonalization",
    "daigonalization": "diagonalization",
    "mixng_beta": "mixing_beta",
    "mixing_bta": "mixing_beta",
    "mixing_betta": "mixing_beta",
    "conv_trh": "conv_thr",
    "conv_thrs": "conv_thr",
    "conv_thrsh": "conv_thr",
    "ntyp": "ntyp",
    "nty": "ntyp",
    "nat": "nat",
    "nbnd": "nbnd",
    "nband": "nbnd",
    "nbrav": "ibrav",
    "pseudo_dir": "pseudo_dir",
    "psuedo_dir": "pseudo_dir",
    "pseuso_dir": "pseudo_dir",
    "outdier": "outdir",
    "otudir": "outdir",
    "outrdir": "outdir",
    "restart_mdoe": "restart_mode",
    "restart_mod": "restart_mode",
    "cell_dynamics": "cell_dynamics",
    "cell_dyanmics": "cell_dynamics",
    "cell_dynmaics": "cell_dynamics",
    "cell_dofree": "cell_dofree",
    "cell_dofre": "cell_dofree",
    "ion_dynmaics": "ion_dynamics",
    "ion_dyanmics": "ion_dynamics",
}

# ------------------------------------------------------------------
# Namelist casing fixes: common casing mistakes -> correct form
# ------------------------------------------------------------------

_NAMELIST_CASING: dict[str, str] = {
    "&control": "&CONTROL",
    "&system": "&SYSTEM",
    "&electrons": "&ELECTRONS",
    "&ions": "&IONS",
    "&cell": "&CELL",
    "&Control": "&CONTROL",
    "&System": "&SYSTEM",
    "&Electrons": "&ELECTRONS",
    "&Ions": "&IONS",
    "&Cell": "&CELL",
}


class CodeActionProvider:
    """Provides code actions (quick fixes) for Quantum ESPRESSO input files.

    Quick fixes are generated for the highest-volume diagnostics emitted by
    the lint and validation pipelines.  Each action is deterministic and
    produces a minimal workspace edit.
    """

    def get_code_actions(
        self,
        source: str,
        diagnostics: list[Diagnostic],
    ) -> list[CodeAction]:
        """Return code actions for the given source and diagnostics.

        Parameters
        ----------
        source:
            Full text of the document.
        diagnostics:
            Currently-published diagnostics to attach quick fixes to.
        """
        actions: list[CodeAction] = []

        for diagnostic in diagnostics:
            action = self._action_for_diagnostic(source, diagnostic)
            if action is not None:
                actions.append(action)

        actions.extend(self._general_actions(source))
        return actions

    # ------------------------------------------------------------------
    # Diagnostic-tied actions
    # ------------------------------------------------------------------

    def _action_for_diagnostic(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> Optional[CodeAction]:
        """Dispatch a single diagnostic to the appropriate fix generator."""
        code = str(diagnostic.code) if diagnostic.code else ""
        message = diagnostic.message.lower()

        # Unclosed namelist
        if "unclosed namelist" in message:
            return self._fix_unclosed_namelist(source, diagnostic)

        # Unknown namelist -> casing fix
        if code == RULE_UNKNOWN_NAMELIST:
            return self._fix_namelist_casing(source, diagnostic)

        # Unknown keyword -> typo correction
        if code == RULE_UNKNOWN_KEYWORD:
            return self._fix_unknown_keyword(source, diagnostic)

        # Invalid enum value -> suggest closest valid value
        if code == RULE_INVALID_KEYWORD_VALUE:
            return self._fix_invalid_value(source, diagnostic)

        # Deprecated keyword -> replace with modern alternative
        if code == RULE_DEPRECATED_KEYWORD:
            return self._fix_deprecated_keyword(source, diagnostic)

        # Duplicate parameter -> remove the duplicate line
        if "duplicate parameter" in message:
            return self._fix_duplicate_parameter(source, diagnostic)

        # mixing_beta above 0.7 -> lower to 0.7
        if "mixing_beta above 0.7" in message:
            return self._fix_mixing_beta(source, diagnostic)

        # ecutrho too low -> set to recommended ratio
        if "ecutrho should normally be at least" in message:
            return self._fix_ecutrho_ratio(source, diagnostic)

        # Orphan parameter outside namelist -> remove it
        if code == RULE_ORPHAN_PARAMETER:
            return self._fix_orphan_parameter(source, diagnostic)

        # Missing required sections -> add skeleton
        if code in (
            RULE_MISSING_REQUIRED_SECTION,
            RULE_MISSING_CONTROL_CALC,
            RULE_MISSING_SYSTEM_ECUTWFC,
            RULE_MISSING_ATOMIC_SPECIES,
            RULE_MISSING_ATOMIC_POSITIONS,
        ):
            return self._fix_missing_section(source, diagnostic, code)

        # Inconsistent settings
        if code == RULE_INCONSISTENT_SETTINGS:
            return self._fix_inconsistent_setting(source, diagnostic)

        return None

    # ------------------------------------------------------------------
    # Individual fix generators
    # ------------------------------------------------------------------

    def _fix_unclosed_namelist(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> CodeAction:
        """Add a closing '/' for an unclosed namelist."""
        lines = source.split("\n")
        line_num = diagnostic.range.start.line

        # Find the first blank line after the namelist start, or EOF
        insert_line = line_num + 1
        while insert_line < len(lines) and lines[insert_line].strip():
            insert_line += 1

        if insert_line >= len(lines):
            insert_pos = Position(
                line=len(lines) - 1,
                character=len(lines[-1]),
            )
            new_text = "\n/"
        else:
            insert_pos = Position(line=insert_line, character=0)
            new_text = "/\n"

        return CodeAction(
            title="Add '/' to close namelist",
            kind=CodeActionKind.QuickFix,
            diagnostics=[diagnostic],
            edit=WorkspaceEdit(
                changes={
                    "document": [
                        TextEdit(
                            range=Range(start=insert_pos, end=insert_pos),
                            new_text=new_text,
                        )
                    ]
                }
            ),
        )

    def _fix_namelist_casing(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> Optional[CodeAction]:
        """Fix namelist name casing (e.g. &control -> &CONTROL)."""
        line_num = diagnostic.range.start.line
        lines = source.split("\n")
        if line_num >= len(lines):
            return None

        line = lines[line_num]
        raw_name = line.strip().split()[0] if line.strip() else ""
        lower_name = raw_name.lower()
        upper_name = raw_name.upper()

        # Already valid (e.g. truly unknown, not just a casing issue)
        if upper_name in {n.upper() for n in VALID_NAMELISTS}:
            correct = None
            for valid in VALID_NAMELISTS:
                if valid.upper() == upper_name:
                    correct = valid
                    break
            if correct is not None and raw_name != correct:
                return self._make_replacement(
                    diagnostic, line_num, 0, len(raw_name), correct,
                    title=f"Change '{raw_name}' to '{correct}'",
                )
        return None

    def _fix_unknown_keyword(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> Optional[CodeAction]:
        """Suggest a typo correction for an unknown keyword."""
        message = diagnostic.message
        # Extract the keyword name from messages like:
        #   "Unknown keyword 'foo' in &CONTROL."
        keyword = ""
        if "'" in message:
            parts = message.split("'")
            if len(parts) >= 2:
                keyword = parts[1].lower()

        if not keyword:
            return None

        suggestion = self._find_closest_keyword(keyword)
        if suggestion is None:
            return None

        line_num = diagnostic.range.start.line
        col = diagnostic.range.start.character

        return self._make_replacement(
            diagnostic,
            line_num,
            col,
            len(keyword),
            suggestion,
            title=f"Replace '{keyword}' with '{suggestion}'",
        )

    def _fix_invalid_value(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> Optional[CodeAction]:
        """Suggest the closest valid enum value for an invalid keyword value."""
        message = diagnostic.message
        line_num = diagnostic.range.start.line
        lines = source.split("\n")
        if line_num >= len(lines):
            return None

        line = lines[line_num]

        # Extract the keyword name from the diagnostic range
        col_start = diagnostic.range.start.character
        col_end = diagnostic.range.end.character
        keyword = line[col_start:col_end].strip().lower()

        # Try extracting from message: "Invalid value 'foo' for 'bar'."
        if "'" in message:
            parts = message.split("'")
            # Keyword is at index 3 (fourth segment): for 'bar'
            if len(parts) >= 4:
                keyword = parts[3].lower()

        # Extract the current invalid value
        from ..parser import ASSIGNMENT_RE

        match = ASSIGNMENT_RE.search(line)
        if not match:
            return None

        raw_value = match.group(2).strip().strip("'\"")
        value_start = match.start(2)
        value_len = len(match.group(2))

        # Find valid values from message: "Valid: a, b, c."
        valid_values: set[str] = set()
        if "valid: " in message.lower():
            idx = message.lower().rfind("valid: ")
            values_str = message[idx + 7:].rstrip(".")
            valid_values = {v.strip().strip("'\"") for v in values_str.split(",")}

        if not valid_values:
            return None

        suggestion = self._closest_match(raw_value.lower(), valid_values)
        if suggestion is None:
            return None

        return self._make_replacement(
            diagnostic,
            line_num,
            value_start,
            value_len,
            f"'{suggestion}'",
            title=f"Change '{raw_value}' to '{suggestion}'",
        )

    def _fix_deprecated_keyword(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> Optional[CodeAction]:
        """Remove or flag deprecated keywords."""
        message = diagnostic.message
        # Extract keyword name
        keyword = ""
        if "'" in message:
            parts = message.split("'")
            if len(parts) >= 2:
                keyword = parts[1].lower()

        if not keyword:
            return None

        line_num = diagnostic.range.start.line
        lines = source.split("\n")
        if line_num >= len(lines):
            return None

        # Offer to remove the deprecated line
        start_pos = Position(line=line_num, character=0)
        end_pos = Position(line=line_num + 1, character=0)

        return CodeAction(
            title=f"Remove deprecated keyword '{keyword}'",
            kind=CodeActionKind.QuickFix,
            diagnostics=[diagnostic],
            edit=WorkspaceEdit(
                changes={
                    "document": [
                        TextEdit(
                            range=Range(start=start_pos, end=end_pos),
                            new_text="",
                        )
                    ]
                }
            ),
        )

    def _fix_duplicate_parameter(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> Optional[CodeAction]:
        """Remove a duplicate parameter line."""
        line_num = diagnostic.range.start.line
        lines = source.split("\n")
        if line_num >= len(lines):
            return None

        start_pos = Position(line=line_num, character=0)
        end_pos = Position(line=line_num + 1, character=0)

        return CodeAction(
            title="Remove duplicate parameter",
            kind=CodeActionKind.QuickFix,
            diagnostics=[diagnostic],
            edit=WorkspaceEdit(
                changes={
                    "document": [
                        TextEdit(
                            range=Range(start=start_pos, end=end_pos),
                            new_text="",
                        )
                    ]
                }
            ),
        )

    def _fix_mixing_beta(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> Optional[CodeAction]:
        """Lower mixing_beta to 0.7."""
        line_num = diagnostic.range.start.line
        lines = source.split("\n")
        if line_num >= len(lines):
            return None

        line = lines[line_num]
        from ..parser import ASSIGNMENT_RE

        match = ASSIGNMENT_RE.search(line)
        if not match:
            return None

        value_start = match.start(2)
        value_len = len(match.group(2))

        return self._make_replacement(
            diagnostic,
            line_num,
            value_start,
            value_len,
            "0.7",
            title="Set mixing_beta to 0.7",
        )

    def _fix_ecutrho_ratio(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> Optional[CodeAction]:
        """Adjust ecutrho to the recommended minimum ratio."""
        message = diagnostic.message
        line_num = diagnostic.range.start.line
        lines = source.split("\n")
        if line_num >= len(lines):
            return None

        line = lines[line_num]
        from ..parser import ASSIGNMENT_RE

        match = ASSIGNMENT_RE.search(line)
        if not match:
            return None

        value_start = match.start(2)
        value_len = len(match.group(2))

        # Parse the ratio from the diagnostic message
        ratio = 4
        for token in message.split():
            if token.endswith("x") and token[:-1].isdigit():
                ratio = int(token[:-1])
                break

        # Find ecutwfc from parsed input
        parsed = parse_qe_input(source)
        system = parsed.namelists.get("&SYSTEM", {})
        ecutwfc_param = system.get("ecutwfc")
        if ecutwfc_param is None:
            return None

        from ..parser import parse_number

        ecutwfc_val = parse_number(ecutwfc_param.value)
        if ecutwfc_val is None:
            return None

        recommended = ratio * ecutwfc_val
        # Format to match the precision of the original
        new_value = f"{recommended:.1f}"

        return self._make_replacement(
            diagnostic,
            line_num,
            value_start,
            value_len,
            new_value,
            title=f"Set ecutrho to {new_value} ({ratio}x ecutwfc)",
        )

    def _fix_orphan_parameter(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> Optional[CodeAction]:
        """Remove an orphan parameter line that is outside any namelist."""
        line_num = diagnostic.range.start.line
        lines = source.split("\n")
        if line_num >= len(lines):
            return None

        start_pos = Position(line=line_num, character=0)
        end_pos = Position(line=line_num + 1, character=0)

        return CodeAction(
            title="Remove orphan parameter",
            kind=CodeActionKind.QuickFix,
            diagnostics=[diagnostic],
            edit=WorkspaceEdit(
                changes={
                    "document": [
                        TextEdit(
                            range=Range(start=start_pos, end=end_pos),
                            new_text="",
                        )
                    ]
                }
            ),
        )

    def _fix_missing_section(
        self,
        source: str,
        diagnostic: Diagnostic,
        code: str,
    ) -> Optional[CodeAction]:
        """Add a skeleton for a missing required section."""
        message = diagnostic.message

        if code == RULE_MISSING_REQUIRED_SECTION:
            if "&CONTROL" in message:
                return self._add_skeleton(
                    diagnostic,
                    "&CONTROL\n  calculation = 'scf'\n/\n\n",
                    "Add &CONTROL namelist skeleton",
                )
            if "&SYSTEM" in message:
                return self._add_skeleton(
                    diagnostic,
                    "&SYSTEM\n  ibrav = 1\n  ecutwfc = 60.0\n/\n\n",
                    "Add &SYSTEM namelist skeleton",
                )
            return None

        if code == RULE_MISSING_CONTROL_CALC:
            return self._add_after_namelist(
                source,
                diagnostic,
                "&CONTROL",
                "\n  calculation = 'scf'",
                "Add 'calculation' to &CONTROL",
            )

        if code == RULE_MISSING_SYSTEM_ECUTWFC:
            return self._add_after_namelist(
                source,
                diagnostic,
                "&SYSTEM",
                "\n  ecutwfc = 60.0",
                "Add 'ecutwfc' to &SYSTEM",
            )

        if code == RULE_MISSING_ATOMIC_SPECIES:
            return self._append_skeleton(
                source,
                diagnostic,
                "\nATOMIC_SPECIES\n  ! element mass pseudo_file\n",
                "Add ATOMIC_SPECIES card skeleton",
            )

        if code == RULE_MISSING_ATOMIC_POSITIONS:
            return self._append_skeleton(
                source,
                diagnostic,
                "\nATOMIC_POSITIONS {crystal}\n  ! element x y z\n",
                "Add ATOMIC_POSITIONS card skeleton",
            )

        return None

    def _fix_inconsistent_setting(
        self,
        source: str,
        diagnostic: Diagnostic,
    ) -> Optional[CodeAction]:
        """Add missing namelists/cards required by calculation type."""
        message = diagnostic.message

        if "&IONS" in message and "recommended" in message:
            return self._append_skeleton(
                source,
                diagnostic,
                "\n&IONS\n  ion_dynamics = 'bfgs'\n/\n",
                "Add &IONS namelist skeleton",
            )

        if "&CELL" in message and "required" in message:
            return self._append_skeleton(
                source,
                diagnostic,
                "\n&CELL\n  cell_dynamics = 'bfgs'\n  press = 0.0\n/\n",
                "Add &CELL namelist skeleton",
            )

        if "nbnd" in message:
            return self._add_after_namelist(
                source,
                diagnostic,
                "&SYSTEM",
                "\n  nbnd = 8",
                "Add 'nbnd' to &SYSTEM",
            )

        return None

    # ------------------------------------------------------------------
    # General (non-diagnostic) actions
    # ------------------------------------------------------------------

    def _general_actions(self, source: str) -> list[CodeAction]:
        """Actions not tied to any specific diagnostic."""
        return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _find_closest_keyword(self, unknown: str) -> Optional[str]:
        """Find the closest matching valid keyword by typo table then edit distance."""
        if len(unknown) < 2:
            return None

        # Exact typo table match
        if unknown in _KEYWORD_TYPOS:
            return _KEYWORD_TYPOS[unknown]

        # Edit-distance search across all known parameters
        all_keywords: set[str] = set()
        for params in KNOWN_PARAMETERS.values():
            all_keywords.update(params)

        best_match: Optional[str] = None
        best_score = 0.0

        for kw in all_keywords:
            score = self._similarity_score(unknown, kw)
            if score > best_score and score > 0.6:
                best_score = score
                best_match = kw

        return best_match

    @staticmethod
    def _similarity_score(s1: str, s2: str) -> float:
        """Levenshtein-based similarity score in [0, 1]."""
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        if len(s2) == 0:
            return 1.0 if len(s1) == 0 else 0.0

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1.lower() != c2.lower())
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        distance = previous_row[-1]
        max_len = max(len(s1), len(s2))
        return 1.0 - (distance / max_len)

    def _closest_match(self, value: str, candidates: set[str]) -> Optional[str]:
        """Return the closest candidate to *value* by Levenshtein similarity."""
        best: Optional[str] = None
        best_score = 0.0
        for c in candidates:
            score = self._similarity_score(value, c)
            if score > best_score:
                best_score = score
                best = c
        return best if best_score > 0.3 else None

    @staticmethod
    def _make_replacement(
        diagnostic: Diagnostic,
        line: int,
        col_start: int,
        col_end_offset: int,
        new_text: str,
        title: str,
    ) -> CodeAction:
        """Create a CodeAction that replaces a span on a single line."""
        return CodeAction(
            title=title,
            kind=CodeActionKind.QuickFix,
            diagnostics=[diagnostic],
            edit=WorkspaceEdit(
                changes={
                    "document": [
                        TextEdit(
                            range=Range(
                                start=Position(line=line, character=col_start),
                                end=Position(
                                    line=line, character=col_start + col_end_offset
                                ),
                            ),
                            new_text=new_text,
                        )
                    ]
                }
            ),
        )

    @staticmethod
    def _add_skeleton(
        diagnostic: Diagnostic,
        skeleton_text: str,
        title: str,
    ) -> CodeAction:
        """Add a skeleton at the beginning of the document."""
        pos = Position(line=0, character=0)
        return CodeAction(
            title=title,
            kind=CodeActionKind.QuickFix,
            diagnostics=[diagnostic],
            edit=WorkspaceEdit(
                changes={
                    "document": [
                        TextEdit(
                            range=Range(start=pos, end=pos),
                            new_text=skeleton_text,
                        )
                    ]
                }
            ),
        )

    @staticmethod
    def _add_after_namelist(
        source: str,
        diagnostic: Diagnostic,
        namelist_name: str,
        parameter_text: str,
        title: str,
    ) -> Optional[CodeAction]:
        """Add a parameter line after the opening of a namelist."""
        lines = source.split("\n")
        for i, line in enumerate(lines):
            if line.strip().upper().startswith(namelist_name):
                # Insert after the namelist header line
                insert_pos = Position(line=i + 1, character=0)
                return CodeAction(
                    title=title,
                    kind=CodeActionKind.QuickFix,
                    diagnostics=[diagnostic],
                    edit=WorkspaceEdit(
                        changes={
                            "document": [
                                TextEdit(
                                    range=Range(start=insert_pos, end=insert_pos),
                                    new_text=parameter_text + "\n",
                                )
                            ]
                        }
                    ),
                )
        return None

    @staticmethod
    def _append_skeleton(
        source: str,
        diagnostic: Diagnostic,
        skeleton_text: str,
        title: str,
    ) -> CodeAction:
        """Append a skeleton at the end of the document."""
        lines = source.split("\n")
        if not lines:
            pos = Position(line=0, character=0)
        else:
            last_line = lines[-1]
            pos = Position(line=len(lines) - 1, character=len(last_line))

        return CodeAction(
            title=title,
            kind=CodeActionKind.QuickFix,
            diagnostics=[diagnostic],
            edit=WorkspaceEdit(
                changes={
                    "document": [
                        TextEdit(
                            range=Range(start=pos, end=pos),
                            new_text=skeleton_text,
                        )
                    ]
                }
            ),
        )


__all__ = ["CodeActionProvider"]
