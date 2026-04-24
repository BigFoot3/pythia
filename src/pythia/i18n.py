from __future__ import annotations

from typing import Literal

Lang = Literal["fr", "en"]

MESSAGES: dict[str, dict[str, dict[str, str]]] = {
    "en": {
        "llms_txt_present": {
            "PASS": "llms.txt found and accessible",
            "FAIL": "llms.txt not found or empty",
            "SKIP": "Could not check llms.txt",
        },
        "llms_full_txt_present": {
            "PASS": "llms-full.txt found and accessible",
            "WARN": "llms-full.txt not found (optional but recommended)",
        },
        "robots_ai_bots": {
            "PASS": "No AI bots blocked in robots.txt",
            "WARN": "robots.txt not found — cannot verify bot policies",
            "FAIL": "One or more AI bots are blocked in robots.txt",
        },
        "sitemap_accessible": {
            "PASS": "Sitemap found and accessible",
            "FAIL": "No accessible sitemap found",
        },
        "jsonld_present_valid": {
            "PASS": "Valid JSON-LD block found",
            "WARN": "JSON-LD block found but contains invalid JSON",
            "FAIL": "No JSON-LD structured data found",
        },
        "single_h1": {
            "PASS": "Exactly one H1 found",
            "WARN": "Multiple H1 headings found",
            "FAIL": "No H1 heading found",
        },
        "heading_hierarchy": {
            "PASS": "Heading hierarchy is sequential",
            "FAIL": "Heading hierarchy contains level gaps",
        },
        "title_length": {
            "PASS": "Title length is within 30–65 characters",
            "WARN": "Title present but length is outside 30–65 characters",
            "FAIL": "No <title> tag found",
        },
        "meta_description": {
            "PASS": "Meta description length is within 70–160 characters",
            "WARN": "Meta description present but length is outside 70–160 characters",
            "FAIL": "No meta description found",
        },
        "opengraph_minimal": {
            "PASS": "All required OpenGraph tags found",
            "WARN": "Some OpenGraph tags are missing",
            "FAIL": "No OpenGraph tags found",
        },
        "generic_headings": {
            "PASS": "No generic headings detected",
            "WARN": "Generic headings detected in H2–H6",
            "FAIL": "Generic H1 or too many generic headings",
        },
        "faq_pattern": {
            "PASS": "FAQ structure detected",
            "WARN": "No FAQ structure found",
        },
        "eeat_signals": {
            "PASS": "Author and publication date detected",
            "WARN": "Only one E-E-A-T signal found (author or date)",
            "FAIL": "No author or publication date detected",
        },
        "structured_content": {
            "PASS": "Structured content found (lists or tables)",
            "FAIL": "No structured content found (no lists or tables)",
        },
    },
    "fr": {
        "llms_txt_present": {
            "PASS": "llms.txt trouvé et accessible",
            "FAIL": "llms.txt introuvable ou vide",
            "SKIP": "Impossible de vérifier llms.txt",
        },
        "llms_full_txt_present": {
            "PASS": "llms-full.txt trouvé et accessible",
            "WARN": "llms-full.txt introuvable (optionnel mais recommandé)",
        },
        "robots_ai_bots": {
            "PASS": "Aucun bot IA bloqué dans robots.txt",
            "WARN": "robots.txt introuvable — impossible de vérifier",
            "FAIL": "Un ou plusieurs bots IA sont bloqués dans robots.txt",
        },
        "sitemap_accessible": {
            "PASS": "Sitemap trouvé et accessible",
            "FAIL": "Aucun sitemap accessible trouvé",
        },
        "jsonld_present_valid": {
            "PASS": "Bloc JSON-LD valide trouvé",
            "WARN": "Bloc JSON-LD présent mais JSON invalide",
            "FAIL": "Aucune donnée structurée JSON-LD trouvée",
        },
        "single_h1": {
            "PASS": "Exactement un H1 trouvé",
            "WARN": "Plusieurs balises H1 détectées",
            "FAIL": "Aucun H1 trouvé",
        },
        "heading_hierarchy": {
            "PASS": "Hiérarchie des titres séquentielle",
            "FAIL": "La hiérarchie des titres contient des sauts de niveau",
        },
        "title_length": {
            "PASS": "Longueur du titre dans la plage 30–65 caractères",
            "WARN": "Titre présent mais hors plage 30–65 caractères",
            "FAIL": "Balise <title> absente",
        },
        "meta_description": {
            "PASS": "Meta description dans la plage 70–160 caractères",
            "WARN": "Meta description présente mais hors plage 70–160 caractères",
            "FAIL": "Aucune meta description trouvée",
        },
        "opengraph_minimal": {
            "PASS": "Tous les tags OpenGraph requis présents",
            "WARN": "Certains tags OpenGraph manquants",
            "FAIL": "Aucun tag OpenGraph trouvé",
        },
        "generic_headings": {
            "PASS": "Aucun titre générique détecté",
            "WARN": "Titres génériques détectés dans H2–H6",
            "FAIL": "H1 générique ou trop de titres génériques",
        },
        "faq_pattern": {
            "PASS": "Structure FAQ détectée",
            "WARN": "Aucune structure FAQ trouvée",
        },
        "eeat_signals": {
            "PASS": "Auteur et date de publication détectés",
            "WARN": "Un seul signal E-E-A-T trouvé (auteur ou date)",
            "FAIL": "Aucun auteur ni date de publication détectés",
        },
        "structured_content": {
            "PASS": "Contenu structuré trouvé (listes ou tableaux)",
            "FAIL": "Aucun contenu structuré trouvé (pas de listes ni tableaux)",
        },
    },
}


def get_message(check_name: str, status: str, lang: Lang = "en") -> str:
    return MESSAGES.get(lang, MESSAGES["en"]).get(check_name, {}).get(
        status, f"{check_name}: {status}"
    )
