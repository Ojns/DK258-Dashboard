import streamlit as st
import pandas as pd
from utils import get_parquet_files
import os

st.title("DK258 Dashboard")

# Initialize session state
if 'selected_batches' not in st.session_state:
    st.session_state.selected_batches = []
if 'uploaded_files_data' not in st.session_state:
    st.session_state.uploaded_files_data = {}

# COMMENTED OUT FILE PATH FUNCTIONALITY - UNCOMMENT FOR LOCAL USE
# ================================================================
# if 'folder_path' not in st.session_state:
#     st.session_state.folder_path = "C:/path/to/parquet/folder"
# if 'data_source_method' not in st.session_state:
#     st.session_state.data_source_method = "File Path"
# 
# @st.cache_data
# def get_parquet_files_cached(folder_path):
#     """Cached wrapper for the utils function"""
#     return get_parquet_files(folder_path)

# Cloud-optimized version - always use File Upload
st.sidebar.success("☁️ **Cloud Environment**")
st.sidebar.info("Optimized for file uploads. Perfect for sharing with colleagues!")

# Show cached files info in sidebar
if st.session_state.uploaded_files_data:
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📦 Cached Uploaded Files:**")
    total_cached_size = 0
    for filename, file_data in st.session_state.uploaded_files_data.items():
        file_size = len(file_data) / 1024 / 1024
        total_cached_size += file_size
        st.sidebar.write(f"📄 {filename} ({file_size:.1f} MB)")
    st.sidebar.caption(f"Total cached: {total_cached_size:.1f} MB")
    
    # Clear cache button
    if st.sidebar.button("🗑️ Clear Cached Files"):
        st.session_state.uploaded_files_data = {}
        st.session_state.selected_batches = []
        st.rerun()

# Always use File Upload method
st.markdown("### 📤 File Upload")
st.info("📤 **File Upload Mode** - Upload your parquet files directly to analyze them.")
st.markdown("*Optimized for easy sharing and collaboration.*")

data_method = "File Upload"

with st.expander("💡 Want to use File Path method locally?", expanded=False):
    st.write("""
    **To enable File Path method for local use:**
    1. Download this app's source code
    2. Uncomment the File Path sections in `Homepage.py` (look for the commented blocks)
    3. Run locally with: `streamlit run Homepage.py`
    
    **Benefits of local File Path method:**
    - 🗂️ Direct access to your file system
    - 🚀 Faster processing of large files
    - 🔒 Complete data privacy (no uploads needed)
    - 💾 No file size limitations
    """)

st.markdown("---")

# COMMENTED OUT FILE PATH METHOD - UNCOMMENT FOR LOCAL USE
# ========================================================
# if data_method == "File Path":
#     st.markdown("### 📁 Folder Path Method")
#     
#     # Show if we have cached uploads available
#     if st.session_state.uploaded_files_data:
#         st.success(f"💾 You have {len(st.session_state.uploaded_files_data)} cached uploaded files available if you switch back to File Upload method.")
#     
#     folder_path = st.text_input(
#         "Enter or paste the path to your data folder containing parquet files:",
#         value=st.session_state.folder_path,
#         key="folder_path_input",
#         placeholder="e.g., C:/Data/ParquetFiles or /Users/username/data"
#     )
# 
#     # Update session state when folder path changes
#     if folder_path != st.session_state.folder_path:
#         st.session_state.folder_path = folder_path
#         # Clear selected batches when folder changes
#         if folder_path != "C:/path/to/parquet/folder":
#             st.session_state.selected_batches = []
# 
#     # Get parquet files from the folder
#     parquet_files = get_parquet_files_cached(folder_path) if folder_path else []
# 
#     if parquet_files:
#         st.success(f'✅ Found {len(parquet_files)} parquet files!')
#         
#         with st.expander("View all files", expanded=False):
#             for f in parquet_files:
#                 st.write(f"📄 {f}")
#         
#         # Filter selected batches to only include files that still exist
#         valid_selected_batches = [f for f in st.session_state.selected_batches if f in parquet_files]
#         if valid_selected_batches != st.session_state.selected_batches:
#             st.session_state.selected_batches = valid_selected_batches
#         
#         selected_batches = st.multiselect(
#             "Select files to analyze:",
#             options=parquet_files,
#             default=st.session_state.selected_batches,
#             key="batch_selector_path"
#         )
#         
#         # Update session state with current selections
#         st.session_state.selected_batches = selected_batches
# 
#         if selected_batches:
#             st.write("**You selected:**")
#             for f in selected_batches:
#                 st.write(f"✅ {f}")
#             
#             st.info("📊 Go to the **Viewer** page to see your data in tabs!")
#         else:
#             st.info("Please select files to analyze")
#             
#     elif folder_path and folder_path != "C:/path/to/parquet/folder":
#         if os.path.exists(folder_path):
#             st.warning("⚠️ No parquet files found in this folder.")
#             st.info(f"Looking for files with .parquet extension in: `{folder_path}`")
#         else:
#             st.error("❌ The specified folder does not exist.")
#             st.info("Please check the path and make sure the folder exists.")
#     else:
#         st.info("👆 Please enter the path to your data folder above.")
#         
#         with st.expander("💡 Path Examples", expanded=False):
#             st.write("""
#             **Windows examples:**
#             - `C:\\Users\\YourName\\Documents\\Data`
#             - `D:\\Projects\\ParquetFiles`
#             
#             **Mac/Linux examples:**
#             - `/Users/yourname/Documents/data`
#             - `/home/username/projects/data`
#             
#             **Tips:**
#             - Use forward slashes (/) or double backslashes (\\\\)
#             - Make sure the folder contains .parquet files
#             - The path should be absolute (full path from root)
#             """)

# FILE UPLOAD METHOD - ACTIVE
st.markdown("### 📤 File Upload Method")

# Show cached files info if we have them
if st.session_state.uploaded_files_data:
    cached_count = len(st.session_state.uploaded_files_data)
    total_cached_size = sum(len(data) for data in st.session_state.uploaded_files_data.values()) / 1024 / 1024
    st.success(f"💾 You have {cached_count} files cached in memory ({total_cached_size:.1f} MB total)")

# File uploader
uploaded_files = st.file_uploader(
    "Choose parquet files to analyze:",
    type=['parquet'],
    accept_multiple_files=True,
    help="Select one or more .parquet files from your computer. Previously uploaded files are cached and will remain available."
)

# Handle newly uploaded files
if uploaded_files:
    st.success(f'✅ {len(uploaded_files)} file(s) uploaded successfully!')
    
    # Merge new files with existing cached files
    new_files = {}
    file_names = []
    
    for uploaded_file in uploaded_files:
        file_names.append(uploaded_file.name)
        new_files[uploaded_file.name] = uploaded_file.getvalue()
    
    # Update session state - merge with existing files
    st.session_state.uploaded_files_data.update(new_files)
    
    # Show what was just uploaded
    st.write("**Just uploaded:**")
    for name in file_names:
        file_size = len(new_files[name]) / 1024 / 1024  # MB
        st.write(f"📄 {name} ({file_size:.1f} MB)")
    
    # Clear previous selections since we have new files
    st.session_state.selected_batches = []

# Show file selection interface if we have files (either newly uploaded or cached)
if st.session_state.uploaded_files_data:
    current_file_names = list(st.session_state.uploaded_files_data.keys())
    
    # If no files were just uploaded, show info about cached files
    if not uploaded_files:
        st.info("📋 Showing your cached uploaded files. Upload new files above to add more.")
        st.write("**Available files:**")
        for name in current_file_names:
            file_size = len(st.session_state.uploaded_files_data[name]) / 1024 / 1024  # MB
            st.write(f"📄 {name} ({file_size:.1f} MB)")
    
    # Filter selected batches to only include files that are currently available
    valid_selected_batches = [f for f in st.session_state.selected_batches if f in current_file_names]
    if valid_selected_batches != st.session_state.selected_batches:
        st.session_state.selected_batches = valid_selected_batches
    
    # File selection
    st.markdown("---")
    selected_batches = st.multiselect(
        "Select files to analyze:",
        options=current_file_names,
        default=st.session_state.selected_batches,
        key="batch_selector_upload"
    )
    
    # Update session state with current selections
    st.session_state.selected_batches = selected_batches

    if selected_batches:
        st.write("**You selected:**")
        for f in selected_batches:
            file_size = len(st.session_state.uploaded_files_data[f]) / 1024 / 1024  # MB
            st.write(f"✅ {f} ({file_size:.1f} MB)")
        
        st.info("📊 Go to the **Viewer** page to see your data in tabs!")
    else:
        st.info("Please select files to analyze from your available files.")

else:
    st.info("👆 Please upload your parquet files above to get started.")
    
    with st.expander("ℹ️ What files can I upload?", expanded=False):
        st.write("""
        **Supported file format:**
        - `.parquet` files only
        
        **File requirements:**
        - Files should contain tabular data
        - Preferably with datetime index or datetime columns for time series visualization
        - Numeric columns for plotting line graphs
        
        **File size limits:**
        - Maximum file size depends on your platform
        - For large files, consider downloading and running this app locally
        
        **Tips:**
        - You can upload multiple files at once by holding Ctrl/Cmd while selecting
        - Each file will appear as a separate tab in the Viewer
        - File names will be used as tab names (without .parquet extension)
        - Files are cached in memory during your session
        """)

# Show current status
st.markdown("---")
st.markdown("### 📋 Current Status")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Environment", "☁️ Cloud")
    
with col2:
    file_count = len(st.session_state.selected_batches)
    st.metric("Selected Files", file_count)

with col3:
    cached_count = len(st.session_state.uploaded_files_data)
    st.metric("Cached Files", cached_count)

if st.session_state.selected_batches:
    with st.expander("📁 View Selected Files", expanded=False):
        total_size = 0
        for f in st.session_state.selected_batches:
            if f in st.session_state.uploaded_files_data:
                file_size = len(st.session_state.uploaded_files_data[f]) / 1024 / 1024
                total_size += file_size
                st.write(f"✅ {f} ({file_size:.1f} MB)")
        
        if total_size > 0:
            st.caption(f"Total size: {total_size:.1f} MB")

# Footer with sharing info
st.markdown("---")
st.markdown("### 🚀 Share This App")
st.info("""
**This app is perfect for sharing!** 
- Send the URL to colleagues to analyze their parquet files
- No Python installation required
- Works on any device with a web browser
- Data is processed securely and not stored permanently
""")
