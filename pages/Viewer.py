import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.title("Data Viewer")

@st.cache_data
def load_parquet_from_bytes(file_bytes, filename):
    """Load parquet file from bytes data"""
    try:
        return pd.read_parquet(io.BytesIO(file_bytes))
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return None

# Check if we have uploaded files and selected files
if 'uploaded_files_data' not in st.session_state or not st.session_state.uploaded_files_data:
    st.warning("⚠️ No files uploaded!")
    st.info("Please go to the **Homepage** first and upload some parquet files.")
    st.stop()

if 'selected_batches' not in st.session_state or not st.session_state.selected_batches:
    st.warning("⚠️ No files selected!")
    st.info("Please go to the **Homepage** first and select some parquet files to view here.")
    st.stop()

# Get the selected files from session state
selected_batches = st.session_state.selected_batches
uploaded_files_data = st.session_state.uploaded_files_data

# Verify all selected files are still available
missing_files = [f for f in selected_batches if f not in uploaded_files_data.keys()]
if missing_files:
    st.error(f"❌ Some selected files are no longer available: {missing_files}")
    st.info("Please go back to the **Homepage** and re-upload your files.")
    st.stop()

st.success(f"📁 Viewing {len(selected_batches)} uploaded files")

# Display current selections with option to modify
with st.expander("Current Selection", expanded=False):
    st.write("**Selected files:**")
    for f in selected_batches:
        file_size = len(uploaded_files_data[f]) / 1024 / 1024  # MB
        st.write(f"-- {f} ({file_size:.1f} MB)")
    st.info("💡 Go back to **Homepage** to change your selection")

st.markdown("---")

# Create tabs based on selected files
tab_names = [f.replace('.parquet', '') for f in selected_batches]
tabs = st.tabs(tab_names)

# Create content for each tab
for i, (tab, filename) in enumerate(zip(tabs, selected_batches)):
    with tab:
        st.write(f"**Dataset:** `{filename}`")
        
        try:
            # Load data from uploaded bytes
            original_df = load_parquet_from_bytes(uploaded_files_data[filename], filename)
            
            if original_df is None:
                continue
                
            # Initialize filtered dataframe
            df = original_df.copy()
            
            # LINE GRAPH SECTION
            st.subheader("📈 Line Graph")
            
            # Get numeric columns for plotting
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            datetime_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # Check if index is datetime
            index_is_datetime = pd.api.types.is_datetime64_any_dtype(df.index)
            
            if numeric_columns:
                # Create two columns for plot controls
                plot_col1, plot_col2 = st.columns(2)
                
                with plot_col1:
                    # Y-axis selection (numeric columns)
                    selected_y_columns = st.multiselect(
                        "Select columns to plot (Y-axis):",
                        options=numeric_columns,
                        default=numeric_columns[:3] if len(numeric_columns) >= 3 else numeric_columns,
                        key=f"y_columns_{i}"
                    )
                
                with plot_col2:
                    # X-axis selection
                    x_axis_options = []
                    x_axis_labels = []
                    
                    if index_is_datetime:
                        x_axis_options.append("index")
                        x_axis_labels.append("Index (datetime)")
                    
                    for col in datetime_columns:
                        x_axis_options.append(col)
                        x_axis_labels.append(f"{col} (datetime)")
                    
                    # Add numeric columns as potential x-axis
                    for col in numeric_columns:
                        x_axis_options.append(col)
                        x_axis_labels.append(f"{col} (numeric)")
                    
                    if x_axis_options:
                        selected_x = st.selectbox(
                            "Select X-axis:",
                            options=x_axis_options,
                            format_func=lambda x: dict(zip(x_axis_options, x_axis_labels)).get(x, x),
                            index=0,
                            key=f"x_axis_{i}"
                        )
                    else:
                        selected_x = None
                        st.warning("No suitable columns found for X-axis")
                
                # Plot the graph if we have valid selections
                if selected_y_columns and selected_x is not None:
                    try:
                        # Prepare the data for plotting
                        plot_df = df.copy()
                        
                        # Handle x-axis data
                        if selected_x == "index":
                            x_data = plot_df.index
                            x_title = "Index"
                        else:
                            x_data = plot_df[selected_x]
                            x_title = selected_x
                        
                        # Create the plot
                        fig = go.Figure()
                        
                        # Add a line for each selected y column
                        for y_col in selected_y_columns:
                            fig.add_trace(go.Scatter(
                                x=x_data,
                                y=plot_df[y_col],
                                mode='lines',
                                name=y_col,
                                line=dict(width=2)
                            ))
                        
                        # Update layout
                        fig.update_layout(
                            title=f"Line Graph for {filename} ({len(plot_df):,} points)",
                            xaxis_title=x_title,
                            yaxis_title="Values",
                            hovermode='x unified',
                            showlegend=True,
                            height=500
                        )
                        
                        # Display the plot
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # DATETIME RANGE SLIDER - BELOW THE GRAPH
                        if isinstance(original_df.index, pd.DatetimeIndex):
                            st.markdown("---")
                            st.write("**📅 Filter by Time Range:**")
                            
                            time_range = st.select_slider(
                                "Adjust the time range and the graph will update:",
                                options=original_df.index,
                                value=(original_df.index.min(), original_df.index.max()),
                                format_func=lambda x: x.strftime('%Y-%m-%d %H:%M') if hasattr(x, 'strftime') else str(x),
                                key=f"time_range_{i}"
                            )
                            
                            # Check if time range has changed from full range
                            if time_range != (original_df.index.min(), original_df.index.max()):
                                # Filter data based on selected time range
                                df_filtered = original_df.loc[time_range[0]:time_range[1]]
                                
                                # Show filtering info
                                st.info(f"🔍 Time filter active: Showing {len(df_filtered):,} of {len(original_df):,} total rows ({len(df_filtered)/len(original_df)*100:.1f}%)")
                                
                                # Update the plot with filtered data
                                if selected_x == "index":
                                    filtered_x_data = df_filtered.index
                                else:
                                    filtered_x_data = df_filtered[selected_x]
                                
                                # Create updated plot
                                fig_filtered = go.Figure()
                                
                                for y_col in selected_y_columns:
                                    fig_filtered.add_trace(go.Scatter(
                                        x=filtered_x_data,
                                        y=df_filtered[y_col],
                                        mode='lines',
                                        name=y_col,
                                        line=dict(width=2)
                                    ))
                                
                                fig_filtered.update_layout(
                                    title=f"Line Graph for {filename} - Filtered ({len(df_filtered):,} points)",
                                    xaxis_title=x_title,
                                    yaxis_title="Values",
                                    hovermode='x unified',
                                    showlegend=True,
                                    height=500
                                )
                                
                                # Replace the original plot
                                st.plotly_chart(fig_filtered, use_container_width=True, key=f"filtered_plot_{i}")
                                
                                # Update df for the rest of the displays
                                df = df_filtered
                                
                            else:
                                st.success("📊 Showing full time range")
                        
                        # Show some stats about the plotted data
                        with st.expander(f"Plot Statistics", expanded=False):
                            stats_df = df[selected_y_columns].describe()
                            st.dataframe(stats_df, use_container_width=True)
                            
                    except Exception as plot_error:
                        st.error(f"❌ Could not create plot: {plot_error}")
                        st.info("This might be due to data format issues or missing values.")
                
                elif not selected_y_columns:
                    st.info("Please select at least one column to plot on the Y-axis.")
                    
            else:
                st.warning("⚠️ No numeric columns found for plotting.")
                st.info("The dataset needs numeric columns to create line graphs.")
            
            st.markdown("---")
            
            # DATASET INFORMATION
            st.subheader("📊 Dataset Information")
            
            # Show basic info about the dataset
            col1, col2, col3 = st.columns(3)
            with col1:
                if len(df) != len(original_df):
                    st.metric("Rows (filtered)", len(df))
                    st.caption(f"Total: {len(original_df):,}")
                else:
                    st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                if hasattr(df.index, 'min') and hasattr(df.index, 'max'):
                    try:
                        if len(df) != len(original_df):
                            date_range = f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}"
                            st.write(f"**Date Range (filtered):** {date_range}")
                            original_range = f"{original_df.index.min().strftime('%Y-%m-%d')} to {original_df.index.max().strftime('%Y-%m-%d')}"
                            st.caption(f"Full range: {original_range}")
                        else:
                            date_range = f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}"
                            st.write(f"**Date Range:** {date_range}")
                    except:
                        st.write("**Index Type:** Non-datetime")
                else:
                    st.write("**Index Type:** Non-datetime")
            
            st.markdown("---")
            
            # Display column info
            with st.expander(f"Column Information ({len(df.columns)} columns)", expanded=False):
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes,
                    'Non-null Count': df.count(),
                    'Null Count': df.isnull().sum()
                })
                st.dataframe(col_info, use_container_width=True)
            
            # Display the dataframe
            st.subheader("Data Preview")
            if len(df) != len(original_df):
                st.caption(f"Showing filtered data ({len(df):,} of {len(original_df):,} rows)")
            st.dataframe(df, use_container_width=True)
            
        except Exception as e:
            st.error(f'❌ Could not process {filename}: {e}')
            st.info("Please check if the file is a valid parquet file.")
