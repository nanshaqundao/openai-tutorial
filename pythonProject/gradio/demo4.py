import gradio as gr


def calculation(num1, operation, num2):
    if operation == "add":
        return num1 + num2
    elif operation == "subtract":
        return num1 - num2
    elif operation == "multiply":
        return num1 * num2
    elif operation == "divide":
        return num1 / num2


demo = gr.Interface(
    fn=calculation,
    inputs=[
        "number",
        gr.Radio(["add", "subtract", "multiply", "divide"]),
        "number"
    ],
    outputs="number",
    live=True,
    examples=[
        [45, "add", 5],
        [3.14, "multiply", 2],
        [100, "divide", 4],
        [10, "subtract", 7],
    ],
    title="Calculation",
    description="Perform a calculation on two numbers",
)

demo.launch()
