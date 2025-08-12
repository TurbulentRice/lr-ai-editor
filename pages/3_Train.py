from __future__ import annotations

from pathlib import Path
import streamlit as st

from ui import state
from ui.components import build_preview_table, render_grouped_slider_selector
from modules.train import train_model, SLIDER_NAME_MAP


@st.cache_resource
def run_train_model(
    csv_path: str,
    previews_dir: str,
    out_model_path: str,
    epochs: int = 5,
    batch_size: int = 32,
    selected_sliders: list[str] | None = None,
):
    return train_model(csv_path, previews_dir, out_model_path, epochs, batch_size, selected_sliders)


def main():
    state.ensure()
    st.title("Model Training")

    # Sidebar inputs with persisted defaults
    _tr = state.get("Train", {})
    csv_path = st.sidebar.text_input("CSV path", value=_tr.get("csv_path", "data/dataset/sliders.csv"))
    previews_dir = st.sidebar.text_input("Previews directory path", value=_tr.get("previews_dir", "data/previews"))
    out_model = st.sidebar.text_input("Output model path", value=_tr.get("out_model", "model.pt"))
    epochs = st.sidebar.number_input("Epochs", min_value=1, value=int(_tr.get("epochs", 5)))
    batch_size = st.sidebar.number_input("Batch size", min_value=1, value=int(_tr.get("batch_size", 16)))

    # Grouped slider selection
    all_sliders = list(SLIDER_NAME_MAP.keys())
    selected_groups_default = _tr.get("selected_groups", None)
    selected_sliders_default = _tr.get("selected_sliders", None)
    selected_groups, selected_sliders, effective_sliders, groups_map = render_grouped_slider_selector(
        all_sliders,
        selected_groups_default=selected_groups_default,
        selected_sliders_default=selected_sliders_default,
        sidebar=True,
        groups_key="train_groups_sel",
        sliders_key="train_sliders_sel",
        restrict_to_groups=True,
    )

    # Reset selections to defaults (all groups, all sliders)
    if st.sidebar.button("Reset selections"):
        all_groups_list = sorted(groups_map.keys(), key=lambda g: (g != "primary", g))
        st.session_state["train_groups_sel"] = all_groups_list
        st.session_state["train_sliders_sel"] = [s for g in all_groups_list for s in groups_map[g]]
        # Persist and rerun
        state.update("Train", {
            "selected_groups": st.session_state["train_groups_sel"],
            "selected_sliders": st.session_state["train_sliders_sel"],
        })
        state.save_if_changed()
        st.experimental_rerun()

    # Persist current Train settings
    state.update(
        "Train",
        {
            "csv_path": csv_path,
            "previews_dir": previews_dir,
            "out_model": out_model,
            "epochs": int(epochs),
            "batch_size": int(batch_size),
            "selected_groups": selected_groups,
            "selected_sliders": selected_sliders,
        },
    )
    state.save_if_changed()

    # Data preview expander
    with st.expander("Preview included sliders", expanded=True):
        preview_rows = st.number_input(
            "Rows to preview",
            min_value=5,
            max_value=1000,
            value=100,
            step=5,
            help="For large CSVs, keep this modest for responsiveness.",
            key="train_preview_rows",
        )
        live_preview = st.checkbox(
            "Live preview (auto-update)",
            value=True,
            help="If enabled, the table updates automatically when you change slider selection.",
            key="train_live_preview",
        )

        if live_preview:
            try:
                preview_df = build_preview_table(csv_path, effective_sliders, preview_rows)
                st.dataframe(preview_df, use_container_width=True)
            except FileNotFoundError:
                st.info("CSV not found. Set a valid CSV path above.")
            except Exception as e:
                st.warning(f"Could not build preview: {e}")
        else:
            apply_clicked = st.button("Apply", key="train_preview_apply")
            if apply_clicked:
                try:
                    st.session_state["train_preview_df"] = build_preview_table(csv_path, effective_sliders, preview_rows)
                except Exception as e:
                    st.session_state["train_preview_df"] = None
                    st.warning(f"Could not build preview: {e}")
            if st.session_state.get("train_preview_df") is not None:
                st.dataframe(st.session_state["train_preview_df"], use_container_width=True)
            else:
                st.info("Choose sliders and click Apply to preview.")

    # Train
    if st.sidebar.button("Train Model"):
        if not effective_sliders:
            st.error("Select at least one slider or group before training.")
        else:
            with st.spinner("Training model…"):
                model, losses, slider_cols = run_train_model(
                    csv_path, previews_dir, out_model, epochs, batch_size, effective_sliders
                )
            st.session_state["slider_cols"] = slider_cols  # preserve the exact training order for inference
            st.success(f"Training complete. Trained on {len(slider_cols)} sliders.")
            st.write("Sliders used (in order):", slider_cols)
            st.line_chart(losses)


if __name__ == "__main__":
    main()
