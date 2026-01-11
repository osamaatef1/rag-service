"""
LLM service for generating responses using various providers.
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class LLMService:
    """Service for generating responses using LLM."""

    def __init__(self):
        """Initialize LLM based on configuration."""
        self.provider = settings.LLM_PROVIDER
        self.llm = self._initialize_llm()

        logger.info(f"LLM service initialized with provider: {self.provider}")

    def _initialize_llm(self):
        """Initialize the appropriate LLM based on provider setting."""
        if self.provider == "openai":
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                temperature=0.7
            )

        elif self.provider == "anthropic":
            return ChatAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.ANTHROPIC_MODEL,
                temperature=0.7
            )

        elif self.provider == "ollama":
            return Ollama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL,
                temperature=0.7
            )

        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_response(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response using the LLM with context.

        Args:
            query: User's question
            context_documents: Retrieved relevant documents
            system_prompt: Optional custom system prompt

        Returns:
            Generated response text
        """
        try:
            # Build context from documents
            context_text = self._build_context(context_documents)

            # Default system prompt
            if not system_prompt:
                system_prompt = """You are a helpful AI assistant. Answer the user's question based on the provided context.
If the context doesn't contain enough information to answer the question, say so clearly.
Be concise and accurate in your responses."""

            # Build the prompt
            prompt = f"""Context information:
{context_text}

Question: {query}

Answer based on the context provided above:"""

            # Generate response based on provider
            if self.provider in ["openai", "anthropic"]:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=prompt)
                ]
                response = self.llm.invoke(messages)
                return response.content

            else:  # ollama
                full_prompt = f"{system_prompt}\n\n{prompt}"
                response = self.llm.invoke(full_prompt)
                return response

        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise

    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved documents.

        Args:
            documents: List of document dictionaries with content and metadata

        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})

            # Add source information if available
            source_info = ""
            if "filename" in metadata:
                source_info = f" (Source: {metadata['filename']})"
            elif "source" in metadata:
                source_info = f" (Source: {metadata['source']})"

            context_parts.append(f"[{i}]{source_info}\n{content}")

        return "\n\n".join(context_parts)

    async def generate_response_stream(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ):
        """
        Generate a streaming response (for future streaming support).

        Args:
            query: User's question
            context_documents: Retrieved relevant documents
            system_prompt: Optional custom system prompt

        Yields:
            Response chunks
        """
        # Placeholder for streaming implementation
        # This requires async LLM clients
        response = self.generate_response(query, context_documents, system_prompt)
        yield response


# Global LLM service instance
llm_service = LLMService()
