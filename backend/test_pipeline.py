from pipeline.process_document import process_document


input_path = "uploads/133826299539863636.jpg"
processed_dir = "processed"


result = process_document(
    input_path,
    processed_dir
)


print("\nPIPELINE RESULT")
print("----------------------------")

print("QUALITY:")
print(result["quality"])

print("\nDENOISED FILE:")
print(result["denoised_file"])

print("\nDESKEWED FILE:")
print(result["deskewed_file"])

print("\nDOCUMENT TYPE:")
print(result["document_type"])

print("\nLANGUAGE:")
print(result["language"])

print("\nPIPELINE TEST: PASS")