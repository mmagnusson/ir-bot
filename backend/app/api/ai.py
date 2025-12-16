"""
AI Service Wrapper
Handles interaction with LLM (local or API)
"""

from typing import Optional
import os
from anthropic import Anthropic


class AIService:
    """Wrapper for AI/LLM interactions"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI service
        Can use Claude API, local model, or any LLM provider
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            # In production, you might fall back to a local model here
            print("Warning: No API key provided. AI features will be limited.")

    def generate_response(self, system_prompt: str, user_prompt: str,
                         model: str = "claude-3-5-sonnet-20241022") -> str:
        """
        Generate AI response with controlled prompts

        Args:
            system_prompt: System instructions for the AI
            user_prompt: User query/request
            model: Model to use (default: Claude 3.5 Sonnet)

        Returns:
            AI-generated response text
        """
        if not self.client:
            return self._generate_fallback_response(user_prompt)

        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            # Extract text from response
            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            return response_text

        except Exception as e:
            print(f"Error calling AI service: {e}")
            return self._generate_fallback_response(user_prompt)

    def _generate_fallback_response(self, user_prompt: str) -> str:
        """
        Generate a basic response when AI is unavailable
        This ensures the system can still function without AI
        """
        return """AI service is currently unavailable.

WHAT WE KNOW:
- Incident has been logged and is awaiting analysis
- Manual investigation procedures should be followed

WHAT WE NEED TO DETERMINE:
- Please refer to your organization's IR playbook for this incident type

RECOMMENDED NEXT INVESTIGATIVE STEPS:
1. Review the incident details manually
2. Follow standard operating procedures for this incident type
3. Consult with senior IR team members if needed
4. Document all findings and actions taken

Note: AI-assisted analysis is temporarily unavailable. Please proceed with manual analysis.
"""

    def test_connection(self) -> bool:
        """Test if AI service is available"""
        if not self.client:
            return False

        try:
            # Simple test call
            self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False
