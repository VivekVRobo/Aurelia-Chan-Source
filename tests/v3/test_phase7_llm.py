#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurelia Cognitive OS V3 - Phase 7 Local LLM Tests
===================================================
Tests the model adapter, context compiler, reasoning interface, and response renderer.
"""

import sys
sys.path.insert(0, 'C:\\Users\\vivek\\Desktop\\Aurelia-Chan')

from aurelia.llm.model_adapter import ModelAdapter, ModelConfig, ModelProvider, ModelCapability
from aurelia.llm.context_compiler import ContextCompiler, CompiledContext, ContextScope
from aurelia.llm.reasoning_interface import ReasoningInterface, ReasoningRequest, ReasoningResponse, ReasoningTask
from aurelia.llm.response_renderer import ResponseRenderer, RenderedResponse, ResponseStyle, ResponseTone
from aurelia.cognition.contracts import MeaningFrame, ResponsePlan, DialogueAct, Intent, EntityRef


def test_model_adapter():
    """Test model adapter."""
    print("Testing Model Adapter...")
    
    adapter = ModelAdapter()
    
    # Test model registration
    config = ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name="llama2",
        api_endpoint="http://localhost:11434",
        capabilities=[ModelCapability.CHAT, ModelCapability.COMPLETION]
    )
    
    adapter.register_model("test_model", config)
    assert "test_model" in adapter.models
    assert adapter.default_model == "test_model"
    
    # Test default model setting
    adapter.set_default_model("test_model")
    assert adapter.default_model == "test_model"
    
    # Test model retrieval
    retrieved = adapter.get_model("test_model")
    assert retrieved.model_name == "llama2"
    
    # Test listing Ollama models (will fail if Ollama not running, but that's OK)
    available_models = adapter.list_ollama_models()
    assert isinstance(available_models, list)
    
    # Test default initialization
    adapter.initialize_default_ollama_models()
    assert len(adapter.models) >= 1  # Should have at least the placeholder
    
    print("  Model Adapter: PASS")
    return True


def test_context_compiler():
    """Test context compiler."""
    print("Testing Context Compiler...")
    
    compiler = ContextCompiler()
    
    # Create test meaning frame
    meaning_frame = MeaningFrame(
        dialogue_act=DialogueAct.CAREER_ADVICE,
        intents=[Intent(type="career_guidance", confidence=0.9)],
        subject=EntityRef(type="user", value="current_user"),
        target_role=EntityRef(type="job_role", value="Director"),
        raw_text="How can I become a Director?",
        confidence=0.9
    )
    
    # Test context compilation
    compiled = compiler.compile_context(
        meaning_frame=meaning_frame,
        scope=ContextScope.SESSION
    )
    
    assert compiled.user_message == "How can I become a Director?"
    assert compiled.system_context is not None
    assert compiled.metadata["scope"] == "session"
    
    # Test formatting for LLM
    formatted = compiler.format_for_llm(compiled)
    assert "USER MESSAGE:" in formatted
    assert "How can I become a Director?" in formatted
    
    # Test context optimization
    long_context = "A" * 5000
    optimized = compiler.optimize_context_length(long_context)
    assert len(optimized) <= compiler.max_context_length
    
    print("  Context Compiler: PASS")
    return True


def test_reasoning_interface():
    """Test reasoning interface."""
    print("Testing Reasoning Interface...")
    
    interface = ReasoningInterface()
    
    # Test reasoning request creation
    request = interface.create_reasoning_request(
        task=ReasoningTask.INFERENCE,
        context="User has 5 years of experience in project management.",
        question="What role might be suitable for this user?",
        constraints=["Focus on executive roles", "Consider leadership experience"]
    )
    
    assert request.task == ReasoningTask.INFERENCE
    assert len(request.constraints) == 2
    
    # Test prompt formatting
    prompt = interface.format_prompt(request)
    assert "inference" in prompt.lower() or "infer" in prompt.lower()
    assert "5 years" in prompt
    
    # Test response parsing
    mock_response = "Based on the evidence, I conclude that the user is ready for senior management roles. My reasoning is that 5 years of experience demonstrates proven capability. Confidence: 0.8"
    
    parsed = interface.parse_response(mock_response, ReasoningTask.INFERENCE)
    assert parsed.task == ReasoningTask.INFERENCE
    assert parsed.conclusion is not None
    assert parsed.confidence >= 0.0
    
    # Test different reasoning tasks
    for task in ReasoningTask:
        task_request = interface.create_reasoning_request(
            task=task,
            context="Test context",
            question="Test question"
        )
        task_prompt = interface.format_prompt(task_request)
        assert task_prompt is not None
        assert len(task_prompt) > 0
    
    print("  Reasoning Interface: PASS")
    return True


def test_response_renderer():
    """Test response renderer."""
    print("Testing Response Renderer...")
    
    renderer = ResponseRenderer()
    
    # Create test response plan
    response_plan = ResponsePlan(
        intent="Provide career guidance",
        claims=["Strategic thinking is important for Director role"],
        recommendations=["Develop strategic planning skills", "Seek executive mentorship"],
        uncertainty=["Timeline may vary based on opportunities"],
        questions=["What specific strategic skills are most important?"],
        tone="professional"
    )
    
    # Test response rendering
    rendered = renderer.render_response(
        response_plan=response_plan,
        style=ResponseStyle.PROFESSIONAL,
        tone=ResponseTone.CONFIDENT
    )
    
    assert rendered.content is not None
    assert len(rendered.content) > 0
    assert rendered.style == ResponseStyle.PROFESSIONAL
    assert rendered.tone == ResponseTone.CONFIDENT
    assert len(rendered.sections) > 0
    
    # Test persona application
    test_content = "This is good advice."
    persona_content = renderer._apply_persona(test_content)
    assert persona_content is not None
    # Professional language should be applied
    assert len(persona_content) > 0
    
    print("  Response Renderer: PASS")
    return True


def test_llm_integration():
    """Test integration between LLM components."""
    print("Testing LLM Integration...")
    
    # Create all LLM components
    adapter = ModelAdapter()
    compiler = ContextCompiler()
    interface = ReasoningInterface()
    renderer = ResponseRenderer()
    
    # Initialize model adapter
    adapter.initialize_default_ollama_models()
    
    # Create meaning frame
    meaning_frame = MeaningFrame(
        dialogue_act=DialogueAct.CAREER_ADVICE,
        intents=[Intent(type="career_guidance", confidence=0.9)],
        subject=EntityRef(type="user", value="current_user"),
        target_role=EntityRef(type="job_role", value="Director"),
        raw_text="What skills do I need to become a Director?",
        confidence=0.9
    )
    
    # Compile context
    compiled = compiler.compile_context(meaning_frame, scope=ContextScope.SESSION)
    
    # Create reasoning request
    reasoning_request = interface.create_reasoning_request(
        task=ReasoningTask.INFERENCE,
        context=compiler.format_for_llm(compiled),
        question="What skills are needed for Director role?"
    )
    
    # Format prompt
    prompt = interface.format_prompt(reasoning_request)
    assert prompt is not None
    assert "Director" in prompt or "skills" in prompt
    
    # Test rendering with response plan
    response_plan = ResponsePlan(
        intent="Provide career guidance",
        claims=["Strategic thinking is important for Director role", "Executive communication is essential"],
        recommendations=["Develop strategic planning capabilities", "Improve executive communication"],
        uncertainty=["Timeline may vary based on opportunities"],
        questions=["What specific strategic skills are most important?"],
        tone="professional"
    )
    
    rendered = renderer.render_response(response_plan)
    assert rendered.content is not None
    assert len(rendered.content) > 0
    
    print("  LLM Integration: PASS")
    return True


def main():
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 7 LOCAL LLM TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_model_adapter,
        test_context_compiler,
        test_reasoning_interface,
        test_response_renderer,
        test_llm_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 70)
    print("    TEST RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print()
        print("SUCCESS: All Phase 7 Local LLM tests passed!")
        print()
        print("Local LLM system ready:")
        print("  - Model Adapter (Ollama integration, unified interface)")
        print("  - Context Compiler (structured to natural language)")
        print("  - Reasoning Interface (structured prompts, response parsing)")
        print("  - Response Renderer (persona application, natural language generation)")
        print()
        print("PHASE 7 COMPLETE!")
        print()
        print("Next: Phase 8 - Character Intelligence (Affect engine, Expression policy, Aurelia state, Persona renderer)")
    else:
        print()
        print("FAILURE: Some tests failed. Please fix the issues.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()