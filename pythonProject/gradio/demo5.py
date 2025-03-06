import gradio as gr

def generate_fake_image(prompt, seed, initial_image=None):
    return f"Used seed: {seed}", "https://dummyimage.com/600x400/000/fff&text=Fake+Image"

demo = gr.Interface(
    fn=generate_fake_image,
    inputs=["text"],
    outputs=["text", "image"],
    additional_inputs=[
        gr.Slider(0,1000),
        "image"
    ]
)

demo.launch()