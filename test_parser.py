import json
from app.parser import ResumeParser
from app.analyzer import ResumeAnalyzer

print("1. Extracting text from resume...")
parser = ResumeParser()
parsed_data = parser.extract("samples/sample_resume.txt")

print("2. Sending to AI for analysis (this takes ~1 second)...")
analyzer = ResumeAnalyzer()
ai_result = analyzer.analyze(parsed_data["text"])

print("\n" + "="*40)
print("🤖 AI EXTRACTION RESULT:")
print("="*40)

# Print the JSON result nicely formatted
print(json.dumps(ai_result, indent=2))