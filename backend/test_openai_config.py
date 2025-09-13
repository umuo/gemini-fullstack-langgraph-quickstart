#!/usr/bin/env python3
"""
Test script to verify OpenAI compatible API configuration.
"""
import os
from dotenv import load_dotenv
from src.agent.configuration import Configuration
from langchain_openai import ChatOpenAI

def test_configuration():
    """Test if the configuration is properly set up."""
    load_dotenv()
    
    print("Testing OpenAI Compatible API Configuration...")
    
    # Test configuration loading
    config = Configuration()
    print(f"✓ Configuration loaded successfully")
    print(f"  - Base URL: {config.openai_base_url}")
    print(f"  - Model: {config.query_generator_model}")
    print(f"  - API Key: {'***' + config.openai_api_key[-4:] if config.openai_api_key else 'Not set'}")
    
    if not config.openai_api_key:
        print("❌ OPENAI_API_KEY is not set. Please set it in your .env file.")
        return False
    
    # Test LLM initialization
    try:
        llm = ChatOpenAI(
            model=config.query_generator_model,
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            temperature=0.1,
        )
        print("✓ LLM initialized successfully")
        
        # Test a simple call
        response = llm.invoke("Hello! Please respond with 'Configuration test successful.'")
        print(f"✓ API call successful: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LLM: {e}")
        return False

if __name__ == "__main__":
    success = test_configuration()
    if success:
        print("\n🎉 All tests passed! Your OpenAI compatible API is configured correctly.")
    else:
        print("\n❌ Configuration test failed. Please check your settings.")