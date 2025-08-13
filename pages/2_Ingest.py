from __future__ import annotations

import tempfile
from pathlib import Path
from datetime import date
import pandas as pd
import streamlit as st

from ui import state
from modules.ingest import ingest


def main():
    state.ensure()
    st.title("Catalog Ingest")

    today = date.today()
    ten_years_ago = date(today.year - 10, today.month, today.day)

    # Sidebar controls (persisted defaults)
    _ing = state.get("Ingest", {})
    catalog_files = st.sidebar.file_uploader("Lightroom .lrcat file(s)", type=["lrcat"], accept_multiple_files=True)
    out_csv = st.sidebar.text_input("Output CSV path", value=_ing.get("out_csv", "data/dataset/sliders.csv"))

    # Ingest criteria options
    flagged = st.sidebar.checkbox("Only flagged images", value=bool(_ing.get("flagged", False)))
    edited = st.sidebar.checkbox("Only edited images", value=bool(_ing.get("edited", False)))
    use_date = st.sidebar.checkbox("Filter by date range", value=bool(_ing.get("use_date", False)))

    if use_date:
        _start_iso = _ing.get("start_date")
        _start_val = date.fromisoformat(_start_iso) if _start_iso else ten_years_ago
        start_date = st.sidebar.date_input(
            "Start date",
            value=_start_val,
            min_value=date(1970, 1, 1),
            max_value=today,
        )

        _end_iso = _ing.get("end_date")
        _end_val = date.fromisoformat(_end_iso) if _end_iso else today
        end_date = st.sidebar.date_input(
            "End date",
            value=_end_val,
            min_value=date(1970, 1, 2),
            max_value=today,
        )

    _color_default = _ing.get("color_label", "Any")
    color_label = st.sidebar.selectbox(
        "Color label",
        options=["Any", "Red", "Yellow", "Green", "Blue", "Purple"],
        index=["Any", "Red", "Yellow", "Green", "Blue", "Purple"].index(
            _color_default if _color_default in ["Any", "Red", "Yellow", "Green", "Blue", "Purple"] else "Any"
        ),
    )

    did_ingest = False
    if st.sidebar.button("Run Ingest"):
        if not catalog_files:
            st.error("Please upload at least one .lrcat file first.")
        else:
            # Build criteria string
            criteria_parts = []
            if flagged:
                criteria_parts.append("flag=flagged")
            if use_date:
                criteria_parts.append(f"datecapt=>={start_date.isoformat()}")
                criteria_parts.append(f"datecapt=<={end_date.isoformat()}")
            # Neither of these work in the LR plug-in; we'll filter locally for edits
            # if edited:
            #     criteria_parts.append("modcount=>0")
            #     criteria_parts.append("extfile=xmp")
            if color_label != "Any":
                # DB names are localized (e.g., Bleu, Rouge); we approximate with numeric codes here
                mapping = {"Red": 1, "Yellow": 2, "Green": 3, "Blue": 4, "Purple": 5}
                criteria_parts.append(f"colorlabel={mapping[color_label]}")
            criteria = ", ".join(criteria_parts)

            all_dfs = []
            for catalog_file in catalog_files:
                with st.spinner(f"Ingesting {catalog_file.name}…"):
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".lrcat")
                    tmp.write(catalog_file.read())
                    tmp.flush()
                    tmp_path = Path(tmp.name)
                    df = ingest(tmp_path, Path(out_csv), criteria)
                    # Locally filter for edited images since </> operators aren't supported for modcount
                    if edited and "modcount" in df.columns:
                        df = df[df["modcount"].astype(int) > 0]
                st.success(f"Ingested {len(df)} records from {catalog_file.name}")
                st.header(catalog_file.name)
                st.dataframe(df)
                all_dfs.append(df)

            # Show combined results
            if len(catalog_files) > 1:
                combined = pd.concat(all_dfs, ignore_index=True)
                st.header("Combined Ingested Data")
                st.dataframe(combined)

    # Always show the current dataset CSV on disk (path from "Output CSV path")
    st.subheader("Current dataset CSV")
    csv_path = Path(out_csv)
    if csv_path.exists():
        # Row count + lightweight preview controls
        try:
            row_ct = pd.read_csv(csv_path, usecols=["name"]).shape[0]
        except Exception:
            row_ct = None
        st.caption(f"Path: `{csv_path}`" + (f" • Rows: **{row_ct}**" if row_ct is not None else ""))
        preview_rows = st.number_input(
            "Rows to preview",
            min_value=5,
            max_value=5000,
            value=200,
            step=50,
            key="ingest_csv_preview_rows",
            help="Quick peek at the CSV that training will use."
        )
        try:
            df_preview = pd.read_csv(csv_path, nrows=int(preview_rows))
            st.dataframe(df_preview, use_container_width=True, height=400)
        except Exception as e:
            st.info(f"Could not read CSV: {e}")
    else:
        st.info("No CSV found at the specified path yet. Run Ingest to create one, or set a valid path.")

    # Persist current Ingest settings
    state.update(
        "Ingest",
        {
            "out_csv": out_csv,
            "flagged": bool(flagged),
            "edited": bool(edited),
            "use_date": bool(use_date),
            "start_date": start_date.isoformat() if use_date else None,
            "end_date": end_date.isoformat() if use_date else None,
            "color_label": color_label,
        },
    )
    state.save_if_changed()


if __name__ == "__main__":
    main()
