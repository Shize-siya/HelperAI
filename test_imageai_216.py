import sys
print(f"Python version: {sys.version}")

try:
    from imageai.Detection import ObjectDetection
    print("ImageAI 2.1.6 import successful!")
    
    detector = ObjectDetection()
    print("ObjectDetection created successfully!")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
