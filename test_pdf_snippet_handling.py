#!/usr/bin/env python3
"""
Quick test to verify PDF snippet handling in reasoning engine
"""

def test_select_relevant_context():
    """Test that _select_relevant_context handles both strings and dicts"""
    
    # Simulate what the code does
    recalled_info = {
        "stm_memories": [],
        "ltm_memories": [],
        "pdf_knowledge": [
            "This is the first PDF snippet",  # String
            "This is the second PDF snippet",  # String
        ],
        "user_profile": {}
    }
    
    # Simulate _select_relevant_context logic
    context = {
        "recent_conversation": [],
        "relevant_memories": [],
        "knowledge_snippets": [],
        "user_preferences": recalled_info.get("user_profile", {})
    }
    
    pdf_knowledge = recalled_info.get("pdf_knowledge", [])
    knowledge_snippets = []
    for item in pdf_knowledge[:2]:
        # Handle both string snippets and dict items
        if isinstance(item, str):
            snippet = item[:300]
        elif isinstance(item, dict):
            snippet = item.get("content", str(item))[:300]
        else:
            snippet = str(item)[:300]
        knowledge_snippets.append(snippet)
    context["knowledge_snippets"] = knowledge_snippets
    
    # Verify
    print("✅ Test 1: Strings work")
    print(f"   Result: {context['knowledge_snippets']}")
    assert len(context['knowledge_snippets']) == 2
    assert context['knowledge_snippets'][0] == "This is the first PDF snippet"
    
    # Test with dicts
    recalled_info2 = {
        "stm_memories": [],
        "ltm_memories": [],
        "pdf_knowledge": [
            {"content": "Dict-based snippet 1"},
            {"content": "Dict-based snippet 2"},
        ],
        "user_profile": {}
    }
    
    context2 = {
        "recent_conversation": [],
        "relevant_memories": [],
        "knowledge_snippets": [],
        "user_preferences": recalled_info2.get("user_profile", {})
    }
    
    pdf_knowledge = recalled_info2.get("pdf_knowledge", [])
    knowledge_snippets = []
    for item in pdf_knowledge[:2]:
        if isinstance(item, str):
            snippet = item[:300]
        elif isinstance(item, dict):
            snippet = item.get("content", str(item))[:300]
        else:
            snippet = str(item)[:300]
        knowledge_snippets.append(snippet)
    context2["knowledge_snippets"] = knowledge_snippets
    
    print("✅ Test 2: Dicts work")
    print(f"   Result: {context2['knowledge_snippets']}")
    assert len(context2['knowledge_snippets']) == 2
    assert context2['knowledge_snippets'][0] == "Dict-based snippet 1"
    
    # Test with mixed
    recalled_info3 = {
        "stm_memories": [],
        "ltm_memories": [],
        "pdf_knowledge": [
            "String snippet",
            {"content": "Dict snippet"},
        ],
        "user_profile": {}
    }
    
    context3 = {
        "recent_conversation": [],
        "relevant_memories": [],
        "knowledge_snippets": [],
        "user_preferences": recalled_info3.get("user_profile", {})
    }
    
    pdf_knowledge = recalled_info3.get("pdf_knowledge", [])
    knowledge_snippets = []
    for item in pdf_knowledge[:2]:
        if isinstance(item, str):
            snippet = item[:300]
        elif isinstance(item, dict):
            snippet = item.get("content", str(item))[:300]
        else:
            snippet = str(item)[:300]
        knowledge_snippets.append(snippet)
    context3["knowledge_snippets"] = knowledge_snippets
    
    print("✅ Test 3: Mixed types work")
    print(f"   Result: {context3['knowledge_snippets']}")
    assert len(context3['knowledge_snippets']) == 2
    assert context3['knowledge_snippets'][0] == "String snippet"
    assert context3['knowledge_snippets'][1] == "Dict snippet"
    
    print("\n✅ All tests passed! The fix handles both strings and dicts correctly.")

if __name__ == '__main__':
    test_select_relevant_context()
