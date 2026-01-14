#!/bin/bash

# Start FastAPI in the background
echo "Starting FastAPI Service..."
python -m api.main &

# Start Streamlit
echo "Starting Streamlit Dashboard..."
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
