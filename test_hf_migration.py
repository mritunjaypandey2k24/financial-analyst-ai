"""
Test script to validate Hugging Face migration
Tests imports and basic configuration without requiring model downloads
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import torch
        print(f"✓ PyTorch imported successfully (version: {torch.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import PyTorch: {e}")
        return False
    
    try:
        import transformers
        print(f"✓ Transformers imported successfully (version: {transformers.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import transformers: {e}")
        return False
    
    try:
        import sentence_transformers
        print(f"✓ Sentence-transformers imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import sentence-transformers: {e}")
        return False
    
    try:
        from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
        print(f"✓ LangChain Hugging Face integration imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import langchain-huggingface: {e}")
        return False
    
    return True

def test_config():
    """Test configuration module"""
    print("\nTesting configuration...")
    
    try:
        import config
        
        # Check required attributes exist
        required_attrs = [
            'EMBEDDING_MODEL', 'LLM_MODEL', 'MODEL_CACHE_DIR',
            'USE_8BIT_QUANTIZATION', 'USE_GPU', 'MAX_NEW_TOKENS',
            'TEMPERATURE', 'BATCH_SIZE', 'DEVICE'
        ]
        
        for attr in required_attrs:
            if not hasattr(config, attr):
                print(f"✗ Missing configuration: {attr}")
                return False
        
        print(f"✓ Configuration loaded successfully")
        print(f"  - Embedding model: {config.EMBEDDING_MODEL}")
        print(f"  - LLM model: {config.LLM_MODEL}")
        print(f"  - Model cache: {config.MODEL_CACHE_DIR}")
        print(f"  - 8-bit quantization: {config.USE_8BIT_QUANTIZATION}")
        print(f"  - GPU enabled: {config.USE_GPU}")
        
        # Check that Google API key config is removed
        if hasattr(config, 'GOOGLE_AI_STUDIO_API_KEY'):
            print("⚠ Warning: GOOGLE_AI_STUDIO_API_KEY still present in config")
        else:
            print("✓ Google AI Studio API key removed from config")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False

def test_module_structure():
    """Test that module structure is correct"""
    print("\nTesting module structure...")
    
    try:
        # Test embeddings module
        from rag_engine import embeddings
        if not hasattr(embeddings, 'EmbeddingGenerator'):
            print("✗ EmbeddingGenerator class not found in embeddings module")
            return False
        print("✓ Embeddings module structure is correct")
        
        # Test vector store module
        from rag_engine import vector_store
        if not hasattr(vector_store, 'RAGEngine'):
            print("✗ RAGEngine class not found in vector_store module")
            return False
        print("✓ Vector store module structure is correct")
        
        # Test agent module
        from agent import financial_agent
        if not hasattr(financial_agent, 'FinancialAnalystAgent'):
            print("✗ FinancialAnalystAgent class not found in agent module")
            return False
        print("✓ Agent module structure is correct")
        
        # Test local LLM module
        from agent import local_llm
        if not hasattr(local_llm, 'LocalLLM'):
            print("✗ LocalLLM class not found in local_llm module")
            return False
        print("✓ Local LLM module structure is correct")
        
        return True
        
    except Exception as e:
        print(f"✗ Module structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that dependencies are correctly specified"""
    print("\nTesting dependencies...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Check for new Hugging Face dependencies
        required_packages = [
            'transformers',
            'torch',
            'sentence-transformers',
            'accelerate',
            'sentencepiece',
            'langchain-huggingface'
        ]
        
        for package in required_packages:
            if package not in requirements:
                print(f"✗ Missing package in requirements.txt: {package}")
                return False
        
        print("✓ All required packages present in requirements.txt")
        
        # Check that Google packages are removed
        deprecated_packages = [
            'langchain-google-genai',
            'google-generativeai'
        ]
        
        for package in deprecated_packages:
            if package in requirements:
                print(f"⚠ Warning: Deprecated package still in requirements.txt: {package}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to check dependencies: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    
    try:
        with open('.env.example', 'r') as f:
            env_example = f.read()
        
        # Check for Hugging Face model configuration
        required_vars = [
            'EMBEDDING_MODEL',
            'LLM_MODEL',
            'MODEL_CACHE_DIR',
            'USE_8BIT_QUANTIZATION',
            'USE_GPU'
        ]
        
        for var in required_vars:
            if var not in env_example:
                print(f"✗ Missing environment variable in .env.example: {var}")
                return False
        
        print("✓ Environment configuration is correct")
        
        # Check that Google API key is removed
        if 'GOOGLE_AI_STUDIO_API_KEY' in env_example:
            print("⚠ Warning: GOOGLE_AI_STUDIO_API_KEY still in .env.example")
        else:
            print("✓ Google AI Studio API key removed from .env.example")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to check environment configuration: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Hugging Face Migration Validation Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Module Structure", test_module_structure),
        ("Dependencies", test_dependencies),
        ("Environment", test_environment)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Migration structure is correct.")
        print("\nNote: Model download and inference tests require internet connection")
        print("and sufficient resources. Run the application to test full functionality.")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
