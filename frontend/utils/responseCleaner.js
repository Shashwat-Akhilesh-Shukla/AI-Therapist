/**
 * Frontend Response Cleaner
 * 
 * Mirrors the backend response_cleaner.py functionality to clean
 * LLM responses on the frontend after streaming completes.
 */

export function removeCitations(text) {
    // Remove citation patterns like [1], [2], [1][2], etc.
    text = text.replace(/(\[\d+\])+/g, '');
    text = text.replace(/\[\d+\]\s*/g, '');
    return text;
}

export function removeMarkdownFormatting(text) {
    // Remove headers (###, ##, #) at start of lines
    text = text.replace(/^#{1,6}\s+/gm, '');

    // Remove bold (**text** or __text__)
    text = text.replace(/\*\*(.+?)\*\*/g, '$1');
    text = text.replace(/__(.+?)__/g, '$1');

    // Remove italic (*text* or _text_)
    text = text.replace(/\*([^*]+?)\*/g, '$1');
    text = text.replace(/_([^_]+?)_/g, '$1');

    // Remove inline code (`code`)
    text = text.replace(/`([^`]+?)`/g, '$1');

    // Remove markdown links [text](url)
    text = text.replace(/\[([^\]]+?)\]\([^\)]+?\)/g, '$1');

    return text;
}

export function removeHashtags(text) {
    // Remove hashtags
    text = text.replace(/#\w+/g, '');
    return text;
}

export function removeAsteriskEmphasis(text) {
    // Remove patterns like *word* or **word**
    text = text.replace(/\*+([^*]+?)\*+/g, '$1');

    // Remove standalone asterisks
    text = text.replace(/\s\*+\s/g, ' ');

    return text;
}

export function normalizeSpacing(text) {
    // Replace multiple spaces with single space
    text = text.replace(/[ \t]+/g, ' ');

    // Replace more than 2 consecutive newlines with exactly 2
    text = text.replace(/\n{3,}/g, '\n\n');

    // Remove spaces at start/end of lines
    text = text.replace(/[ \t]+$/gm, '');
    text = text.replace(/^[ \t]+/gm, '');

    // Remove trailing/leading whitespace
    text = text.trim();

    return text;
}

export function cleanResponse(text) {
    if (!text) return text;

    // Apply cleaning operations in order
    text = removeCitations(text);
    text = removeMarkdownFormatting(text);
    text = removeHashtags(text);
    text = removeAsteriskEmphasis(text);
    text = normalizeSpacing(text);

    return text;
}
