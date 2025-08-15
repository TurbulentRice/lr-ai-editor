from __future__ import annotations

from pathlib import Path
import streamlit as st
import altair as alt

import pandas as pd
import time

from ui import state
from ui.components import build_preview_table, render_grouped_slider_selector, build_training_overview, PREVIEW_EXTS, render_training_run
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

    # We want to know when the job is running
    is_training = st.session_state.get("train_run_active", False)

    # Show most recent training run (persisted)
    last_run_persisted = state.get("TrainLastRun")
    if (not is_training) and last_run_persisted:
        render_training_run(last_run_persisted, default_chart_expanded=False)

    # Sidebar inputs with persisted defaults
    _tr = state.get("Train", {})
    csv_path = st.sidebar.text_input("CSV path", value=_tr.get("csv_path", "data/dataset/sliders.csv"))
    previews_dir = st.sidebar.text_input("Previews directory path", value=_tr.get("previews_dir", "data/previews"))
    out_model = st.sidebar.text_input("Output model path", value=_tr.get("out_model", "data/models/model.pt"))
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
        st.rerun()

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

    # If a training run has been requested, run it now (before data views) so progress sits near the top
    if st.session_state.get("train_run_active", False):
        with st.spinner("Training model…"):
            t0 = time.perf_counter()
            model, losses, slider_cols = run_train_model(
                csv_path, previews_dir, out_model, epochs, batch_size, effective_sliders
            )
            t1 = time.perf_counter()
        duration_s = max(0.0, t1 - t0)
        # st.session_state["slider_cols"] = slider_cols  # preserve the exact training order for inference
        st.success(f"Training complete. Trained on {len(slider_cols)} sliders.")

        # Training metrics -----------------------------------------------------
        # Compute dataset size actually used (row-based usable) to estimate throughput
        try:
            usable_df, _, _counts = build_training_overview(csv_path, previews_dir, effective_sliders, limit=0)
            samples_used = int(len(usable_df))
        except Exception:
            samples_used = None
        epochs_run = int(len(losses))
        initial_loss = float(losses[0]) if losses else float("nan")
        final_loss = float(losses[-1]) if losses else float("nan")
        loss_drop = (initial_loss - final_loss) if (losses and initial_loss == initial_loss) else None
        loss_drop_pct = (100.0 * loss_drop / initial_loss) if (loss_drop is not None and initial_loss) else None

        # Metrics row (Duration, Epochs, Samples used, Final loss w/ delta)
        m1, m2, m3, m4 = st.columns(4)
        # Duration pretty format
        mins, secs = divmod(int(round(duration_s)), 60)
        m1.metric("Duration", f"{mins:02d}:{secs:02d}")
        m2.metric("Epochs", epochs_run)
        if samples_used is not None:
            m3.metric("Samples used", samples_used)
        else:
            m3.metric("Samples used", "–")
        if loss_drop is not None and loss_drop_pct is not None:
            m4.metric("Final loss", f"{final_loss:,.0f}", delta=f"-{loss_drop:,.0f} ({loss_drop_pct:.1f}%)")
        else:
            m4.metric("Final loss", f"{final_loss:,.0f}")

        # Approx throughput caption
        if samples_used and duration_s > 0:
            total_images = samples_used * max(1, epochs_run)
            throughput = total_images / duration_s
            st.caption(f"Approx. throughput: {throughput:.1f} images/sec")

        # Loss chart with labels ----------------------------------------------
        loss_df = pd.DataFrame({"epoch": list(range(1, len(losses)+1)), "loss": losses})
        chart = (
            alt.Chart(loss_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("epoch:Q", title="Epoch"),
                y=alt.Y("loss:Q", title="Training Loss", scale=alt.Scale(zero=False))
            )
            .properties(title="Training Loss per Epoch")
        )
        st.altair_chart(chart, use_container_width=True)

        # Compact slider list (collapsed)
        with st.expander("Sliders used", expanded=False):
            st.code(", ".join(slider_cols))

        run_summary = {
            "model_path": out_model,
            "duration_s": duration_s,
            "epochs_run": epochs_run,
            "samples_used": samples_used,
            "losses": losses,
            "slider_cols": slider_cols,
        }
        st.session_state["train_last_run"] = run_summary
        state.update("TrainLastRun", run_summary)
        state.save_if_changed()

        # Clear the flag so expanders reopen next render
        st.session_state["train_run_active"] = False

    # CSV data preview expander
    with st.expander("CSV slider data", expanded=True):
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

    # Combined CSV/Preview summary of what will actually be used
    with st.expander("Training data summary", expanded=True):
        try:
            # full CSV (no row limit) for accurate metrics
            usable_df, missing_df, counts = build_training_overview(csv_path, previews_dir, effective_sliders, limit=0)

            # Build an index of all preview files (recursive) and count
            prev_dir_path = Path(previews_dir)
            preview_paths = []
            if prev_dir_path.exists():
                for ext in PREVIEW_EXTS:
                    preview_paths.extend(prev_dir_path.rglob(f"*{ext}"))
            previews_ct = len(preview_paths)
            usable_stems = counts.get("usable_distinct_stems", counts.get("usable", 0))

            # Metrics: keep it simple and consistent
            m1, m2, m3 = st.columns(3)
            m1.metric("Total usable", usable_stems)
            m2.metric("Rows in CSV", counts.get("total", 0))
            m3.metric("Previews", previews_ct)

            # Thumbnail grid for usable rows (show first 24)
            st.caption("Usable previews (first 24)")
            # Build a mapping from stem/name to an actual preview path (reuse the list we built above)
            name_map = {p.name.lower(): p for p in preview_paths}
            stem_map = {p.stem.lower(): p for p in preview_paths}

            filenames = [str(x) for x in usable_df["filename"].tolist()]
            resolved = []
            for fn in filenames:
                key_name = Path(fn).name.lower()
                key_stem = Path(fn).stem.lower()
                p = name_map.get(key_name) or stem_map.get(key_stem)
                if p is not None:
                    resolved.append((fn, p))
                if len(resolved) >= 24:
                    break

            if not resolved:
                st.info("No matching preview files found to display.")
            else:
                n_cols = 6
                rows = (len(resolved) + n_cols - 1) // n_cols
                for r in range(rows):
                    cols = st.columns(n_cols)
                    for c in range(n_cols):
                        i = r * n_cols + c
                        if i < len(resolved):
                            fn, p = resolved[i]
                            with cols[c]:
                                st.image(str(p), caption=Path(fn).name, use_container_width=True)

            if counts.get("missing", 0) > 0:
                show_missing = st.checkbox(
                    "Show missing previews (in CSV but file not found)",
                    value=False,
                    key="train_show_missing_previews",
                    help="These rows are in your CSV but the preview file was not found in the selected previews directory.",
                )
                if show_missing:
                    st.dataframe(missing_df, use_container_width=True, height=200)
        except FileNotFoundError:
            st.info("CSV not found. Set a valid CSV path above.")
        except Exception as e:
            st.warning(f"Could not summarize CSV: {e}")

    # Train
    if st.sidebar.button("Train Model"):
        if not effective_sliders:
            st.error("Select at least one slider or group before training.")
        else:
            st.session_state["train_run_active"] = True
            st.rerun()


if __name__ == "__main__":
    main()
