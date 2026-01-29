"""
Test suite for response_cleaner module

Tests all cleaning functions with various inputs including edge cases
and real-world examples.
"""

import pytest
from backend.response_cleaner import (
    remove_citations,
    remove_markdown_formatting,
    remove_hashtags,
    remove_asterisk_emphasis,
    normalize_spacing,
    clean_response
)


class TestRemoveCitations:
    """Test citation removal functionality."""
    
    def test_single_citation(self):
        text = "This is a fact[1] about something."
        expected = "This is a fact about something."
        assert remove_citations(text) == expected
    
    def test_multiple_consecutive_citations(self):
        text = "This is a fact[1][2][3] about something."
        expected = "This is a fact about something."
        assert remove_citations(text) == expected
    
    def test_citations_with_spaces(self):
        text = "This is a fact[1] [2] about something."
        expected = "This is a fact about something."
        assert remove_citations(text) == expected
    
    def test_citations_at_end(self):
        text = "This is a fact.[1][2]"
        expected = "This is a fact."
        assert remove_citations(text) == expected
    
    def test_no_citations(self):
        text = "This is a fact about something."
        assert remove_citations(text) == text
    
    def test_real_world_example(self):
        text = "Three fundamental principles for beginner chess openings are: control the center[1][2], develop your minor pieces[3], and castle for king safety[4]."
        expected = "Three fundamental principles for beginner chess openings are: control the center, develop your minor pieces, and castle for king safety."
        assert remove_citations(text) == expected


class TestRemoveMarkdownFormatting:
    """Test markdown formatting removal."""
    
    def test_bold_double_asterisk(self):
        text = "This is **bold** text."
        expected = "This is bold text."
        assert remove_markdown_formatting(text) == expected
    
    def test_bold_double_underscore(self):
        text = "This is __bold__ text."
        expected = "This is bold text."
        assert remove_markdown_formatting(text) == expected
    
    def test_italic_single_asterisk(self):
        text = "This is *italic* text."
        expected = "This is italic text."
        assert remove_markdown_formatting(text) == expected
    
    def test_headers(self):
        text = "### This is a header\nSome content"
        expected = "This is a header\nSome content"
        assert remove_markdown_formatting(text) == expected
    
    def test_multiple_header_levels(self):
        text = "# Header 1\n## Header 2\n### Header 3"
        expected = "Header 1\nHeader 2\nHeader 3"
        assert remove_markdown_formatting(text) == expected
    
    def test_inline_code(self):
        text = "Use the `function()` to do this."
        expected = "Use the function() to do this."
        assert remove_markdown_formatting(text) == expected
    
    def test_markdown_links(self):
        text = "Check out [this link](https://example.com) for more."
        expected = "Check out this link for more."
        assert remove_markdown_formatting(text) == expected
    
    def test_mixed_formatting(self):
        text = "**Bold** and *italic* and `code`."
        expected = "Bold and italic and code."
        assert remove_markdown_formatting(text) == expected


class TestRemoveHashtags:
    """Test hashtag removal."""
    
    def test_single_hashtag(self):
        text = "This is #important information."
        # clean_response will normalize the double space
        result = clean_response(text)
        assert '#important' not in result
        assert 'This is information.' == result
    
    def test_multiple_hashtags(self):
        text = "This is #important and #urgent information."
        result = clean_response(text)
        assert '#important' not in result
        assert '#urgent' not in result
        assert 'This is and information.' == result
    
    def test_hashtag_at_start(self):
        text = "#Important: Read this carefully."
        result = clean_response(text)
        assert '#Important' not in result
        assert ': Read this carefully.' == result
    
    def test_no_hashtags(self):
        text = "This is normal text."
        assert remove_hashtags(text) == text


class TestRemoveAsteriskEmphasis:
    """Test asterisk emphasis removal."""
    
    def test_single_asterisk_emphasis(self):
        text = "I am *really* happy to help."
        expected = "I am really happy to help."
        assert remove_asterisk_emphasis(text) == expected
    
    def test_double_asterisk_emphasis(self):
        text = "I am **really** happy to help."
        expected = "I am really happy to help."
        assert remove_asterisk_emphasis(text) == expected
    
    def test_triple_asterisk_emphasis(self):
        text = "I am ***really*** happy to help."
        expected = "I am really happy to help."
        assert remove_asterisk_emphasis(text) == expected
    
    def test_standalone_asterisks(self):
        text = "This is * a test * with asterisks."
        expected = "This is a test with asterisks."
        assert remove_asterisk_emphasis(text) == expected


class TestNormalizeSpacing:
    """Test spacing normalization."""
    
    def test_multiple_spaces(self):
        text = "This  has   multiple    spaces."
        expected = "This has multiple spaces."
        assert normalize_spacing(text) == expected
    
    def test_multiple_newlines(self):
        text = "Paragraph 1\n\n\n\nParagraph 2"
        expected = "Paragraph 1\n\nParagraph 2"
        assert normalize_spacing(text) == expected
    
    def test_trailing_spaces(self):
        text = "Line with trailing spaces   \nNext line"
        expected = "Line with trailing spaces\nNext line"
        assert normalize_spacing(text) == expected
    
    def test_leading_spaces(self):
        text = "   Leading spaces on this line"
        expected = "Leading spaces on this line"
        assert normalize_spacing(text) == expected
    
    def test_preserve_paragraph_breaks(self):
        text = "Paragraph 1\n\nParagraph 2"
        expected = "Paragraph 1\n\nParagraph 2"
        assert normalize_spacing(text) == expected


class TestCleanResponse:
    """Test the main clean_response function with comprehensive examples."""
    
    def test_empty_string(self):
        assert clean_response("") == ""
    
    def test_none_input(self):
        assert clean_response(None) == None
    
    def test_clean_text_unchanged(self):
        text = "This is clean, natural text that should remain unchanged."
        assert clean_response(text) == text
    
    def test_real_world_chess_example(self):
        """Test with the actual example from the uploaded image."""
        text = """**Three fundamental principles for beginner chess openings are: control the center (with moves like 1.e4 or 1.d4), develop your minor pieces (knights and bishops) early, and castle for king safety within the first 5-8 moves.[1][2]** These "golden rules" maximize piece mobility, restrict your opponent, and protect your king—avoiding common mistakes like flank pawn moves (e.g., 1.h4).[1] ### Recommended Beginner Opening: Italian Game (White pieces) This simple sequence controls the center, develops pieces, and prepares castling. Play as White against 1...e5:[2][4] 1. **e4** (pawn to e4: claims center).[1][3] 2. **Nf3** (knight to f3: attacks e5, develops piece).[2][4] 3. **Bc4** (bishop to c4: targets f7 weak spot, develops).[4] **Full first four moves example (Italian Game):** 1.e4 e5 2.Nf3 Nc6 3.Bc4 (opponent often plays 3...Nf6 or 3...Bc5; follow with 4.d3 or 0-0 to castle).[1][4] ### For Black: Sicilian Defense (aggressive response to 1.e4) If your opponent plays 1.e4, the *c5* (challenges center indirectly).[4] Practice on sites like Chess.com, starting with 1.e4 as Bobby Fischer recommended for its central control.[3] These moves work against stronger players if you understand the ideas.[1]"""
        
        result = clean_response(text)
        
        # Should not contain citations
        assert '[1]' not in result
        assert '[2]' not in result
        assert '[3]' not in result
        assert '[4]' not in result
        
        # Should not contain markdown bold
        assert '**' not in result
        
        # Should not contain markdown headers
        assert '###' not in result
        
        # Should still contain the actual content
        assert 'Three fundamental principles' in result
        assert 'Italian Game' in result
        assert 'Sicilian Defense' in result
    
    def test_therapeutic_response_with_formatting(self):
        """Test cleaning a therapeutic response with various formatting."""
        text = """**I hear that you're feeling overwhelmed.**[1] It's completely normal to feel this way when dealing with stress.[2][3] 

### Coping Strategies:
- *Deep breathing* exercises
- **Mindfulness** meditation
- Regular exercise

#selfcare #mentalhealth

Remember, you're not alone in this journey."""
        
        result = clean_response(text)
        
        # Should be clean
        assert '[1]' not in result
        assert '**' not in result
        assert '###' not in result
        assert '#selfcare' not in result
        assert '*' not in result
        
        # Should preserve content
        assert 'I hear that you' in result
        assert 'Coping Strategies' in result
        assert 'Deep breathing' in result
    
    def test_mixed_formatting_comprehensive(self):
        """Test with all types of formatting mixed together."""
        text = "**Bold text**[1] with *italic*[2] and ### headers and #hashtags and `code`[3][4]."
        result = clean_response(text)
        
        # Should be completely clean
        assert '**' not in result
        assert '*' not in result
        assert '[' not in result
        assert ']' not in result
        assert '###' not in result
        assert '#hashtags' not in result
        assert '`' not in result
        
        # Should preserve actual words
        assert 'Bold text' in result
        assert 'italic' in result
        assert 'headers' in result
        assert 'code' in result
    
    def test_preserve_natural_punctuation(self):
        """Ensure natural punctuation is preserved."""
        text = "Hello! How are you? I'm doing well. Let's talk."
        result = clean_response(text)
        assert result == text
    
    def test_preserve_numbers_in_text(self):
        """Ensure numbers in natural text are preserved."""
        text = "I have 3 apples and 5 oranges. That's 8 fruits total."
        result = clean_response(text)
        assert result == text


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_only_citations(self):
        text = "[1][2][3]"
        assert clean_response(text) == ""
    
    def test_only_markdown(self):
        text = "**bold** *italic* `code`"
        expected = "bold italic code"
        assert clean_response(text) == expected
    
    def test_only_hashtags(self):
        text = "#tag1 #tag2 #tag3"
        result = clean_response(text)
        assert '#' not in result
    
    def test_very_long_text(self):
        """Test with a longer text to ensure performance."""
        text = "This is a sentence. " * 100 + "[1][2][3]"
        result = clean_response(text)
        assert '[1]' not in result
        assert result.count('This is a sentence.') == 100
    
    def test_unicode_characters(self):
        """Ensure unicode characters are preserved."""
        text = "Hello 世界! This is a test with émojis 😊 and accénts."
        result = clean_response(text)
        assert '世界' in result
        assert '😊' in result
        assert 'émojis' in result
        assert 'accénts' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
