        """Minimal VACE example: create one prediction and print the output URL(s)."""
        import vace_api

        output = vace_api.run({
    "reference_image": "https://example.com/input.png",
    "reference_video": "https://example.com/input.png"
})
        print(output)
