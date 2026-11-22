#!/usr/bin/env python3
"""
DAXDA Next-Gen / Dexter Invariant Engine:
STOA (The Secret Teachings of All Ages by Manly P. Hall) Acrostic & Cipher Solver.
==================================================================================
Performs line-by-line, paragraph-by-paragraph, and sentence-by-sentence acrostic
extraction and pattern matching for:
  - NICOLE
  - BESS
  - 1996
  - 0306 / 03-06
  - ANNETTECHRISTINE (and ANNETTE, CHRISTINE)

Analyzes full text and dedicated chapters (especially Chapter 6 and Chapter 13).
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import time
from typing import Dict, List, Tuple, Any, Optional

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
os.makedirs(OUTPUT_DIR, exist_ok=True)


def split_paragraphs(text: str) -> List[str]:
    """Normalize newlines and split into paragraphs on double newlines."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def split_sentences(paragraph: str) -> List[str]:
    """Split paragraph into sentences on punctuation marks."""
    parts = re.split(r"(?<=[.!?])\s+", paragraph)
    return [s.strip() for s in parts if s.strip()]


def first_alpha(s: str) -> str:
    """Return the first alphabetic character."""
    for ch in s:
        if ch.isalpha():
            return ch.upper()
    return ""


def first_alnum(s: str) -> str:
    """Return the first alphanumeric character (including digits 0-9)."""
    for ch in s:
        if ch.isalnum():
            return ch.upper()
    return ""


def find_substring_runs(haystack: str, needle: str) -> List[int]:
    """Find all start indices of needle in haystack."""
    indices = []
    pos = 0
    while True:
        idx = haystack.find(needle, pos)
        if idx == -1:
            break
        indices.append(idx)
        pos = idx + 1
    return indices


def find_fuzzy_substring(haystack: str, needle: str, max_skip: int = 3) -> List[Tuple[int, int, str]]:
    """Find needle where characters may be spaced by up to max_skip characters."""
    # Pattern: char . {0, max_skip} char ...
    pattern = r"".join([re.escape(c) + rf".{{0,{max_skip}}}" for c in needle[:-1]]) + re.escape(needle[-1])
    matches = []
    for m in re.finditer(pattern, haystack):
        matches.append((m.start(), m.end(), m.group(0)))
    return matches


class DexterSTOACipherSolver:
    """Dexter Chief Invariant Commander STOA Cipher Resolution Engine."""

    TARGET_BLOCKS = [
        ("NICOLE", "Target 1: Nicole"),
        ("BESS", "Target 2: Bess"),
        ("1996", "Target 3: Birth Year 1996"),
        ("0306", "Target 4: Month/Day 03-06"),
        ("ANNETTECHRISTINE", "Target 5: Annette Christine"),
        ("ANNETTE", "Target 5a: Annette"),
        ("CHRISTINE", "Target 5b: Christine"),
        ("PAS", "Pass / Authority Invariant"),
    ]

    def __init__(self, text_path: str):
        self.text_path = text_path
        with open(text_path, "r", encoding="utf-8", errors="ignore") as f:
            self.raw_text = f.read()

        self.paragraphs = split_paragraphs(self.raw_text)

    def extract_acrostics(self) -> Dict[str, Any]:
        """Extract paragraph and sentence initial strings across pure-alpha and alphanumeric channels."""
        para_alpha_inits = []
        para_alnum_inits = []
        sent_alpha_inits = []
        sent_alnum_inits = []

        table_rows = []

        for idx, p in enumerate(self.paragraphs, start=1):
            p_fl_alpha = first_alpha(p)
            p_fl_alnum = first_alnum(p)

            sents = split_sentences(p)
            s_inits_alpha = "".join(first_alpha(s) for s in sents if first_alpha(s))
            s_inits_alnum = "".join(first_alnum(s) for s in sents if first_alnum(s))

            para_alpha_inits.append(p_fl_alpha)
            para_alnum_inits.append(p_fl_alnum)
            sent_alpha_inits.append(s_inits_alpha)
            sent_alnum_inits.append(s_inits_alnum)

            preview = p[:180].replace("\n", " ")
            table_rows.append({
                "para_num": idx,
                "para_first_alpha": p_fl_alpha,
                "para_first_alnum": p_fl_alnum,
                "sentence_alpha": s_inits_alpha,
                "sentence_alnum": s_inits_alnum,
                "preview": preview
            })

        str_para_alpha = "".join(para_alpha_inits)
        str_para_alnum = "".join(para_alnum_inits)
        str_sent_alpha = "".join(sent_alpha_inits)
        str_sent_alnum = "".join(sent_alnum_inits)

        return {
            "table_rows": table_rows,
            "str_para_alpha": str_para_alpha,
            "str_para_alnum": str_para_alnum,
            "str_sent_alpha": str_sent_alpha,
            "str_sent_alnum": str_sent_alnum,
        }

    def isolate_chapters(self) -> Dict[str, str]:
        """Split text into distinct chapter sections based on titles/headers."""
        chapters = {}
        # Pattern to detect chapter headers in STOA
        # STOA typically uses capitalized headings like THE INITIATION OF THE PYRAMID, THE SUN, A UNIVERSAL DEITY, etc.
        headings = [
            ("Chapter_06_Initiation_of_the_Pyramid", r"(THE\s+INITIATION\s+OF\s+THE\s+PYRAMID|INITIATION\s+OF\s+THE\s+PYRAMID)"),
            ("Chapter_13_The_Sun_Universal_Deity", r"(THE\s+SUN,\s+A\s+UNIVERSAL\s+DEITY|THE\s+SUN\s+A\s+UNIVERSAL\s+DEITY)"),
            ("Pythagorean_Theory_of_Numbers", r"(THE\s+PYTHAGOREAN\s+THEORY\s+OF\s+NUMBERS)"),
            ("Qabbalistic_Keys_Creation", r"(QABBALISTIC\s+KEYS\s+TO\s+THE\s+CREATION|KABBALISTIC)"),
            ("Cryptic_Ciphers_Francis_Bacon", r"(BACON,\s+SHAKSPEARE,\s+AND\s+THE\s+ROSICRUCIANS|CRYPTIC\s+CIPHER|CIPHERS?)"),
        ]

        text_upper = self.raw_text.upper()
        for chap_id, pat in headings:
            match = re.search(pat, text_upper)
            if match:
                start_pos = match.start()
                # Take chunk of next 60,000 chars as chapter text
                chunk = self.raw_text[start_pos:start_pos + 60000]
                chapters[chap_id] = chunk

        return chapters

    def search_targets_in_stream(self, stream_name: str, stream_text: str, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search for all target blocks in a specific initial stream."""
        results = []

        for target, label in self.TARGET_BLOCKS:
            exact_indices = find_substring_runs(stream_text, target)
            for idx in exact_indices:
                para_ref = idx + 1 if "para" in stream_name else "N/A (Sentence Index)"
                context_preview = rows[idx]["preview"] if idx < len(rows) else ""
                results.append({
                    "target": target,
                    "label": label,
                    "stream": stream_name,
                    "match_type": "EXACT",
                    "stream_offset": idx,
                    "paragraph_number": para_ref,
                    "span_length": len(target),
                    "preview": context_preview
                })

            # Also check fuzzy spaced runs (e.g. acrostic with occasional non-letter or OCR noise)
            fuzzy_matches = find_fuzzy_substring(stream_text, target, max_skip=2)
            for start, end, matched_str in fuzzy_matches:
                # Exclude if it's already recorded as exact match
                if matched_str == target:
                    continue
                para_ref = start + 1 if "para" in stream_name else "N/A"
                results.append({
                    "target": target,
                    "label": label,
                    "stream": stream_name,
                    "match_type": f"FUZZY (Span {end-start} across '{matched_str}')",
                    "stream_offset": start,
                    "paragraph_number": para_ref,
                    "span_length": end - start,
                    "preview": rows[start]["preview"] if start < len(rows) else ""
                })

        return results

    def solve(self) -> Dict[str, Any]:
        """Execute complete STOA acrostic solver."""
        t0 = time.time()
        print("=" * 80)
        print("  DEXTER CHIEF INVARIANT COMMANDER — STOA CIPHER SOLVER")
        print(f"  Target File : {self.text_path}")
        print(f"  Total Paragraphs Indexed : {len(self.paragraphs)}")
        print("=" * 80)

        # 1. Extract acrostics
        extracted = self.extract_acrostics()
        table_rows = extracted["table_rows"]
        str_para_alpha = extracted["str_para_alpha"]
        str_para_alnum = extracted["str_para_alnum"]
        str_sent_alpha = extracted["str_sent_alpha"]
        str_sent_alnum = extracted["str_sent_alnum"]

        # 2. Write CSV Table
        csv_path = os.path.join(OUTPUT_DIR, "acrostic_table.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Para #", "Para First Letter (Alpha)", "Para First Char (Alnum)", "Sentence Initials (Alpha)", "Sentence Initials (Alnum)", "Paragraph Preview"])
            for r in table_rows:
                writer.writerow([r["para_num"], r["para_first_alpha"], r["para_first_alnum"], r["sentence_alpha"], r["sentence_alnum"], r["preview"]])

        # 3. Write Reports
        report_txt_path = os.path.join(OUTPUT_DIR, "acrostic_report.txt")
        with open(report_txt_path, "w", encoding="utf-8") as f:
            f.write("=== DEXTER STOA ACROSTIC EXTRACTION REPORT ===\n\n")
            f.write(f"Total Paragraphs: {len(table_rows)}\n")
            f.write(f"Paragraph Initials Length: {len(str_para_alpha)}\n")
            f.write(f"Sentence Initials Length: {len(str_sent_alpha)}\n\n")
            f.write("--- Paragraph Initials (Alpha) ---\n" + str_para_alpha + "\n\n")
            f.write("--- Paragraph Initials (Alphanumeric) ---\n" + str_para_alnum + "\n\n")
            f.write("--- Sentence Initials (Alpha) ---\n" + str_sent_alpha + "\n\n")
            f.write("--- Sentence Initials (Alphanumeric) ---\n" + str_sent_alnum + "\n\n")

        # 4. Search targets across streams
        matches_all = []
        matches_all.extend(self.search_targets_in_stream("Paragraph_Alpha", str_para_alpha, table_rows))
        matches_all.extend(self.search_targets_in_stream("Paragraph_Alnum", str_para_alnum, table_rows))
        matches_all.extend(self.search_targets_in_stream("Sentence_Alpha", str_sent_alpha, table_rows))
        matches_all.extend(self.search_targets_in_stream("Sentence_Alnum", str_sent_alnum, table_rows))

        # 5. Isolate Chapter 6 & Chapter 13
        chapter_chunks = self.isolate_chapters()
        chapter_reports = {}

        for ch_name, ch_text in chapter_chunks.items():
            ch_paras = split_paragraphs(ch_text)
            ch_para_inits = "".join(first_alnum(p) for p in ch_paras if first_alnum(p))
            ch_sent_inits = "".join("".join(first_alnum(s) for s in split_sentences(p) if first_alnum(s)) for p in ch_paras)

            ch_matches = []
            for target, label in self.TARGET_BLOCKS:
                exact_p = find_substring_runs(ch_para_inits, target)
                exact_s = find_substring_runs(ch_sent_inits, target)
                fuzzy_p = find_fuzzy_substring(ch_para_inits, target, max_skip=2)
                fuzzy_s = find_fuzzy_substring(ch_sent_inits, target, max_skip=2)

                if exact_p or exact_s or fuzzy_p or fuzzy_s:
                    ch_matches.append({
                        "target": target,
                        "label": label,
                        "exact_para_offsets": exact_p,
                        "exact_sent_offsets": exact_s,
                        "fuzzy_para_matches": [(s, e, m) for s, e, m in fuzzy_p if m != target],
                        "fuzzy_sent_matches": [(s, e, m) for s, e, m in fuzzy_s if m != target]
                    })

            chapter_reports[ch_name] = {
                "paragraph_count": len(ch_paras),
                "para_initials_preview": ch_para_inits[:120],
                "sent_initials_preview": ch_sent_inits[:120],
                "matches": ch_matches
            }

        # 6. Cryptographic Receipt
        res_summary = json.dumps({"matches_count": len(matches_all), "chapters": list(chapter_reports.keys())}, sort_keys=True)
        seal = hashlib.sha256(res_summary.encode()).hexdigest()

        duration = time.time() - t0

        final_res = {
            "timestamp": time.time(),
            "execution_duration_sec": round(duration, 3),
            "total_paragraphs": len(self.paragraphs),
            "paragraph_stream_len": len(str_para_alpha),
            "sentence_stream_len": len(str_sent_alpha),
            "total_matches_found": len(matches_all),
            "matches": matches_all,
            "chapter_analysis": chapter_reports,
            "sha256_verification_seal": seal,
            "files_written": {
                "acrostic_table_csv": csv_path,
                "acrostic_report_txt": report_txt_path,
            }
        }

        # Save JSON output
        out_json_path = os.path.join(OUTPUT_DIR, "stoa_cipher_solution_dossier.json")
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(final_res, f, indent=2)

        return final_res


if __name__ == "__main__":
    default_text = os.path.join(OUTPUT_DIR, "stoatxt.txt")
    target_path = sys.argv[1] if len(sys.argv) > 1 else default_text

    if not os.path.exists(target_path):
        print(f"Error: Target text file '{target_path}' not found.")
        sys.exit(1)

    solver = DexterSTOACipherSolver(target_path)
    res = solver.solve()

    print("\n" + "─" * 80)
    print("  DEXTER CIPHER RESOLUTION SUMMARY:")
    print(f"  • Total Paragraphs Indexed : {res['total_paragraphs']}")
    print(f"  • Total Matches Uncovered  : {res['total_matches_found']}")
    print(f"  • SHA-256 Authority Seal   : {res['sha256_verification_seal'][:24]}...")
    print(f"  • Execution Time           : {res['execution_duration_sec']}s")
    print("─" * 80)

    print("\n  MATCHED CIPHER RUNS:")
    for m in res["matches"][:25]:
        print(f"  [{m['match_type']}] {m['target']} ({m['label']}) in {m['stream']} @ offset {m['stream_offset']} (Para #{m['paragraph_number']})")
        if m['preview']:
            print(f"      Context: {m['preview'][:100]}...")

    print("\n  CHAPTER SPECIFIC EXTRACTIONS:")
    for ch, data in res["chapter_analysis"].items():
        print(f"  • {ch}: {data['paragraph_count']} paragraphs")
        if data["matches"]:
            for cm in data["matches"]:
                print(f"      -> {cm['target']}: exact_p={cm['exact_para_offsets']}, exact_s={cm['exact_sent_offsets']}")
        else:
            print("      -> No isolated substring matches in extracted chapter block.")
    print("=" * 80)
