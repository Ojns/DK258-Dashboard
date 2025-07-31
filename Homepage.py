import streamlit as st
import pandas as pd
from utils import get_parquet_files
import os

st.title("DK258 Dashboard")

# Detect if running on Streamlit Cloud
def is_cloud_deployment():
    """Check if app is running on Streamlit Cloud or similar cloud platform"""
    return (
        os.getenv('STREAMLIT_SHARING_MODE') is not None or
        os.getenv('STREAMLIT_SERVER_PORT') is not None or
        'streamlit.app' in os.getenv('HOSTNAME', '') or
        'herokuapp' in os.getenv('HOSTNAME', '') or
        'render' in os.getenv('HOSTNAME', '') or
        os.getenv('DYNO') is not None or  # Heroku
        os.getenv('RENDER') is not None or  # Render
        os.getenv('RAILWAY_STATIC_URL') is not None  # Railway
    )

# Initialize session state
if 'selected_batches' not in st.session_state:
    st.session_state.selected_batches = []
if 'folder_path' not in st.session_state:
    st.session_state.folder_path = "C:/path/to/parquet/folder"
if 'uploaded_files_data' not in st.session_state:
    st.session_state.uploaded_files_data = {}
if 'data_source_method' not in st.session_state:
    # Default based on environment
    st.session_state.data_source_method = "File Upload" if is_cloud_deployment() else "File Path"

@st.cache_data
def get_parquet_files_cached(folder_path):
    """Cached wrapper for the utils function"""
    return get_parquet_files(folder_path)

# Show environment info in sidebar
if not is_cloud_deployment():
    st.sidebar.success("🏠 **Local Environment**")
    st.sidebar.info("You have access to both File Path and File Upload methods.")
    
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
else:
    st.sidebar.success("☁️ **Cloud Environment**")
    st.sidebar.info("Optimized for file uploads. Perfect for sharing with colleagues!")

# Method selection based on environment
st.markdown("### 📂 Data Source")

if is_cloud_deployment():
    st.info("📤 **File Upload Mode** - Upload your parquet files directly to analyze them.")
    st.markdown("*Running in cloud mode - optimized for easy sharing and collaboration.*")
    data_method = "File Upload"
    st.session_state.data_source_method = "File Upload"
    
    with st.expander("💡 Want to run this locally?", expanded=False):
        st.write("""
        **Benefits of running locally:**
        - 🗂️ Direct access to your file system (File Path method)
        - 🚀 Faster processing of large files
        - 🔒 Complete data privacy (no uploads needed)
        - 💾 No file size limitations
        - 💨 Persistent file caching between method switches
        """)
else:
    # Local deployment: show both options
    data_method = st.radio(
        "How would you like to access your parquet files?",
        options=["File Path", "File Upload"],
        index=0 if st.session_state.data_source_method == "File Path" else 1,
        help="File Path: Access files from a folder on your computer\nFile Upload: Upload files directly to the app"
    )
    
    # Update session state when method changes
    if data_method != st.session_state.data_source_method:
        st.session_state.data_source_method = data_method
        st.session_state.selected_batches = []  # Clear selections when switching methods
        # NOTE: We DON'T clear uploaded_files_data anymore - keep them cached!
        st.info(f"🔄 Switched to {data_method} method. Your selections have been cleared, but uploaded files remain cached.")

st.markdown("---")

# FILE PATH METHOD (only available locally)
if data_method == "File Path":
    st.markdown("### 📁 Folder Path Method")
    
    # Show if we have cached uploads available
    if st.session_state.uploaded_files_data:
        st.success(f"💾 You have {len(st.session_state.uploaded_files_data)} cached uploaded files available if you switch back to File Upload method.")
    
    folder_path = st.text_input(
        "Enter or paste the path to your data folder containing parquet files:",
        value=st.session_state.folder_path,
        key="folder_path_input",
        placeholder="e.g., C:/Data/ParquetFiles or /Users/username/data"
    )

    # Update session state when folder path changes
    if folder_path != st.session_state.folder_path:
        st.session_state.folder_path = folder_path
        # Clear selected batches when folder changes
        if folder_path != "C:/path/to/parquet/folder":
            st.session_state.selected_batches = []

    # Get parquet files from the folder
    parquet_files = get_parquet_files_cached(folder_path) if folder_path else []

    if parquet_files:
        st.success(f'✅ Found {len(parquet_files)} parquet files!')
        
        with st.expander("View all files", expanded=False):
            for f in parquet_files:
                st.write(f"📄 {f}")
        
        # Filter selected batches to only include files that still exist
        valid_selected_batches = [f for f in st.session_state.selected_batches if f in parquet_files]
        if valid_selected_batches != st.session_state.selected_batches:
            st.session_state.selected_batches = valid_selected_batches
        
        selected_batches = st.multiselect(
            "Select files to analyze:",
            options=parquet_files,
            default=st.session_state.selected_batches,
            key="batch_selector_path"
        )
        
        # Update session state with current selections
        st.session_state.selected_batches = selected_batches

        if selected_batches:
            st.write("**You selected:**")
            for f in selected_batches:
                st.write(f"✅ {f}")
            
            st.info("📊 Go to the **Viewer** page to see your data in tabs!")
        else:
            st.info("Please select files to analyze")
            
    elif folder_path and folder_path != "C:/path/to/parquet/folder":
        if os.path.exists(folder_path):
            st.warning("⚠️ No parquet files found in this folder.")
            st.info(f"Looking for files with .parquet extension in: `{folder_path}`")
        else:
            st.error("❌ The specified folder does not exist.")
            st.info("Please check the path and make sure the folder exists.")
    else:
        st.info("👆 Please enter the path to your data folder above.")
        
        with st.expander("💡 Path Examples", expanded=False):
            st.write("""**Windows examples:** `C:\\Users\\YourName\\Documents\\Data`
            **Mac/Linux examples:** `/Users/yourname/Documents/data`""")

# FILE UPLOAD METHOD
elif data_method == "File Upload":
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
            **Supported:** `.parquet` files only
            **Features:** Files are cached in memory between method switches
            **Tip:** You can switch to File Path method and return - your uploads will still be here!
            """)

# Show current method and selection summary
st.markdown("---")
st.markdown("### 📋 Current Status")

col1, col2, col3, col4 = st.columns(4)
with col1:
    environment = "☁️ Cloud" if is_cloud_deployment() else "🏠 Local"
    st.metric("Environment", environment)
    
with col2:
    st.metric("Data Source", data_method)
    
with col3:
    file_count = len(st.session_state.selected_batches)
    st.metric("Selected Files", file_count)

with col4:
    cached_count = len(st.session_state.uploaded_files_data)
    st.metric("Cached Uploads", cached_count)

if st.session_state.selected_batches:
    with st.expander("📁 View Selected Files", expanded=False):
        total_size = 0
        for f in st.session_state.selected_batches:
            if data_method == "File Upload" and f in st.session_state.uploaded_files_data:
                file_size = len(st.session_state.uploaded_files_data[f]) / 1024 / 1024
                total_size += file_size
                st.write(f"✅ {f} ({file_size:.1f} MB)")
            else:
                st.write(f"✅ {f}")
        
        if data_method == "File Upload" and total_size > 0:
            st.caption(f"Total size: {total_size:.1f} MB")

# Footer with sharing info for cloud deployment
if is_cloud_deployment():
    st.markdown("---")
    st.markdown("### 🚀 Share This App")
    st.info("""
    **This app is perfect for sharing!** 
    - Send the URL to colleagues to analyze their parquet files
    - No Python installation required
    - Works on any device with a web browser
    - Data is processed securely and not stored permanently
    """)