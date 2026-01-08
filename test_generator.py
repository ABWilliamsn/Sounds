#!/usr/bin/env python3
"""
Simple test script to verify the sound generator functionality.
This is NOT a Home Assistant test - it's a standalone verification.
"""
import sys
import os
import tempfile

# Add the custom_components path to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'ambient_sound_synthesizer'))

from sound_generator import AmbientSoundGenerator


def test_sound_generation():
    """Test generating each sound type."""
    print("Testing Ambient Sound Generator...")
    print("-" * 50)
    
    generator = AmbientSoundGenerator()
    sound_types = ["white", "pink", "brown", "rain", "wind", "fan"]
    intensities = ["low", "medium", "high"]
    
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Temporary directory: {tmpdir}\n")
        
        # Test each sound type with medium intensity
        for sound_type in sound_types:
            filename = f"test_{sound_type}.wav"
            output_path = os.path.join(tmpdir, filename)
            
            print(f"Generating {sound_type} sound... ", end="", flush=True)
            
            try:
                success = generator.generate_and_save(
                    sound_type=sound_type,
                    intensity="medium",
                    duration=2,  # Short duration for testing
                    output_path=output_path
                )
                
                if success and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"✓ Success! ({file_size:,} bytes)")
                else:
                    print("✗ Failed!")
                    return False
                    
            except Exception as e:
                print(f"✗ Error: {e}")
                return False
        
        print("\n" + "-" * 50)
        print("All sound types generated successfully!")
        print("\nTesting different intensities for white noise...")
        
        # Test intensities
        for intensity in intensities:
            filename = f"test_white_{intensity}.wav"
            output_path = os.path.join(tmpdir, filename)
            
            print(f"  {intensity}: ", end="", flush=True)
            
            success = generator.generate_and_save(
                sound_type="white",
                intensity=intensity,
                duration=1,
                output_path=output_path
            )
            
            if success:
                print("✓")
            else:
                print("✗")
                return False
        
        print("\n" + "-" * 50)
        print("✓ All tests passed!")
        return True


if __name__ == "__main__":
    try:
        success = test_sound_generation()
        sys.exit(0 if success else 1)
    except ImportError as e:
        print(f"Error importing dependencies: {e}")
        print("\nPlease install required packages:")
        print("  pip install numpy scipy")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
