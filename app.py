import gradio as gr
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import build_3d_model, get_cad_code, extract_mld_from_prompt


def prototype_pipeline(description, progress=gr.Progress()):

    progress(0.2, desc="Analyzing requirements...")
    time.sleep(0.3)

    mld = extract_mld_from_prompt(description)

    progress(0.4, desc=f"Generating CAD parameters for {mld} MLD plant...")
    code = get_cad_code(description)

    progress(0.7, desc="Building 3D model...")
    glb_path, stl_path = build_3d_model(code, description)

    progress(1.0, desc="Completed!")

    return glb_path, stl_path


with gr.Blocks(title="AI-WTP Architect", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🌊 AI-WTP Architect  
    ### Hydraulic-Based 3D Water Treatment Plant Generator
    """)

    with gr.Row():

        with gr.Column(scale=1):
            input_text = gr.Textbox(
                label="Engineering Requirements",
                value="Create a complete 100 MLD water treatment plant",
                lines=6
            )

            generate_btn = gr.Button("🚀 GENERATE 3D MODEL", variant="primary")

        with gr.Column(scale=1):

            model_viewer = gr.Model3D(
                label="🔍 Live 3D Preview",
                interactive=True,
                clear_color=[0.02, 0.02, 0.05, 1]
            )

            output_file = gr.File(label="⬇ Download STL")

    generate_btn.click(
        fn=prototype_pipeline,
        inputs=input_text,
        outputs=[model_viewer, output_file]
    )


if __name__ == "__main__":
    os.makedirs("exports", exist_ok=True)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True
    )
