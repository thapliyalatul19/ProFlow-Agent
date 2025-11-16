"""
ProFlow - Test Agent
Simple agent to verify ADK installation and setup
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set environment variables for Vertex AI
os.environ['GOOGLE_CLOUD_PROJECT'] = os.getenv('GOOGLE_CLOUD_PROJECT', 'proflow-agent-capstone')
os.environ['GOOGLE_CLOUD_LOCATION'] = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

import vertexai
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

def test_basic_setup():
    """Test basic environment setup"""
    print("=" * 60)
    print("🚀 ProFlow - Testing ADK Setup")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Checking Environment Variables...")
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION')
    
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT not set!")
        return False
    
    print(f"✅ Project ID: {project_id}")
    print(f"✅ Location: {location}")
    
    # Initialize Vertex AI
    print("\n🔧 Initializing Vertex AI...")
    try:
        vertexai.init(project=project_id, location=location)
        print("✅ Vertex AI initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize Vertex AI: {e}")
        return False
    
    # Create a simple agent
    print("\n📦 Creating test agent...")
    try:
        agent = LlmAgent(
            model=Gemini(model="gemini-2.5-flash-lite"),
            name="test_agent",
            description="A simple test agent to verify ProFlow setup",
            instruction="You are a helpful test agent. Respond briefly and enthusiastically."
        )
        print("✅ Agent created successfully!")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return False
    
    # Test with direct Gemini call instead
    print("\n🤖 Testing Gemini API...")
    try:
        from google.genai import types
        from vertexai.generative_models import GenerativeModel
        
        model = GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content("Say 'ProFlow setup is working!' in an enthusiastic way.")
        
        print("\n💬 Gemini Response:")
        print("-" * 60)
        print(response.text)
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        print("\nPlease ensure:")
        print("1. You've run: gcloud auth application-default login")
        print("2. Vertex AI API is enabled")
        return False
    
    print("\n✅ SUCCESS! Your environment is ready!")
    print("🎉 ProFlow setup is complete!")
    print("\n📊 Configuration Summary:")
    print(f"   Project: {project_id}")
    print(f"   Location: {location}")
    print(f"   Model: gemini-2.5-flash-lite")
    print("\n🚀 Ready to build ProFlow agents!")
    
    return True

if __name__ == "__main__":
    success = test_basic_setup()
    exit(0 if success else 1)
