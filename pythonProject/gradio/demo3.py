import gradio as gr
import numpy as np


def sepia(input_img):
    sepia_filter = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    sepia_img = input_img.dot(sepia_filter)
    sepia_img /= sepia_img.max()
    return sepia_img


demo = gr.Interface(
    fn=sepia,
    inputs=[gr.Image()],
    outputs=["image"],
)
if __name__ == "__main__":
    demo.launch()