from pipeline.preprocessing.denoise import denoise_image

input_path = "uploads/133826299539863636.jpg"
output_path = "processed/denoised_test.jpg"

denoise_image(input_path, output_path)

print("Denoising completed!")
print("Saved to:", output_path)