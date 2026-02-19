import gradio as gr
import os
from core.generator import build_3d_model


# ===============================
# Generate Function
# ===============================

def generate_model(user_prompt):

    try:
        # Build model
        glb_path, stl_path = build_3d_model({}, user_prompt)

        print("Generated GLB:", glb_path)
        print("Generated STL:", stl_path)
        print("GLB Exists:", os.path.exists(glb_path))
        print("STL Exists:", os.path.exists(stl_path))

        if not os.path.exists(glb_path):
            return None, None, "❌ GLB file not generated"

        return glb_path, stl_path, "✅ Model Generated Successfully"

    except Exception as e:
        print("ERROR:", str(e))
        return None, None, f"❌ Error: {str(e)}"


# ===============================
# Gradio UI
# ===============================

with gr.Blocks() as demo:

    gr.Markdown("## 🏗️ AI WTP Architect")

    prompt_input = gr.Textbox(
        label="Enter Plant Capacity (e.g. 100 MLD)",
        placeholder="Example: 150 MLD WTP"
    )

    generate_btn = gr.Button("Generate")

    status = gr.Textbox(label="Status")

    model_output = gr.Model3D(label="3D Preview")
    file_output = gr.File(label="Download STL")

    generate_btn.click(
        fn=generate_model,
        inputs=prompt_input,
        outputs=[model_output, file_output, status]
    )


# ===============================
# Launch
# ===============================

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
