
## Liquidity Dashboard

An interactive dashboard for visualizing and analyzing liquidity data from multiple sources, built with Streamlit and containerized for easy deployment.

---

### Project Structure

```
├── Dockerfile                # Container build instructions
├── requirements.txt          # Python dependencies
├── streamlit_app.py          # Main Streamlit app entry point
├── src/                      # Source code (data fetchers, UI components, config)
├── data/                     # Static data files
├── plots/                    # Generated plots
├── docs/                     # Documentation
```

---

## Quick Start (Docker)

### Prerequisites
- [Docker](https://www.docker.com/get-started) installed

### Build the Docker image
```sh
docker build -t liquidity-dashboard .
```

### Run the app
```sh
docker run -p 8501:8501 liquidity-dashboard
```
Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Local Development (Optional)

If you prefer to run locally (without Docker):

1. Create a virtual environment and activate it:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the app:
   ```sh
   streamlit run streamlit_app.py
   ```

---

## Configuration

- App configuration is managed in `src/config.py` and `src/common/config.py`.
- Data sources and update logic are in `src/fetch_*.py` and `src/components/`.

---

## Data Sources

- See `docs/DATA-SOURCES.md` for details on data origins and update instructions.
- Static data is in `data/`.

---

## Distribution & Deployment

1. **Build the Docker image** as above.
2. **Test locally** to ensure the app runs as expected.
3. **Push to a container registry** (e.g., Docker Hub, GitHub Container Registry, Azure Container Registry):
   ```sh
   docker tag liquidity-dashboard yourrepo/liquidity-dashboard:latest
   docker push yourrepo/liquidity-dashboard:latest
   ```
4. **Deploy** using your preferred container orchestration (Kubernetes, Azure Web Apps, etc.).

---

## .dockerignore (Recommended)

Create a `.dockerignore` file to exclude unnecessary files from the image:
```
__pycache__/
*.pyc
.git/
docs/
plots/
venv/
```

---

## Troubleshooting

- If you see file permission errors, ensure the container user has access to `data/` and `plots/`.
- For networking issues, confirm port 8501 is open and not in use.

---

## Contributing

Pull requests are welcome! Please see `docs/AGENTS.md` for agent-related contributions and `docs/REQUIREMENTS_REPORT.md` for dependency details.

---

## License

MIT License (see LICENSE file).
