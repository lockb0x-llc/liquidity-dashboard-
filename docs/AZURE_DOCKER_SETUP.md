# Azure App Service Docker Configuration

Since you are switching from a code-based deployment to a Docker container deployment, you need to update your App Service configuration in the Azure Portal.

## Prerequisite
Ensure the `deploy-docker.yml` workflow has successfully run at least once on GitHub. This will push the container image to your GitHub Container Registry (GHCR).

## Steps

1.  **Navigate to your App Service** in the [Azure Portal](https://portal.azure.com).
2.  In the left sidebar, under **Settings**, click on **Deployment Center**.
3.  **Source Settings**:
    *   **Source**: Select `Container Registry` (NOT GitHub Actions, as we want Azure to just pull the image we built).
    *   **Registry Source**: Select `GitHub Container Registry` (if available) or `Private Registry`.
        *   *If "Private Registry" is chosen:*
            *   **Server URL**: `https://ghcr.io`
            *   **Username**: Your GitHub username.
            *   **Password**: You will need a GitHub Personal Access Token (PAT) with `read:packages` scope.
            *   **Image and Tag**: `ghcr.io/<your-username>/liquidity-dashboard:latest`

    > **Preferred Method**: If you see an option to specific "GitHub Actions" as the build provider, you can try that, but often the most stable method for containers is to let GitHub Actions build/push (which we just set up) and tell Azure to just "Run" that image.

4.  **Save** the settings.

## Environment Variables
Don't forget to verify your **Environment Variables** are still set correctly under **Settings > Environment variables**.
- `PORT` is usually automatically handled, but Streamlit runs on `8501` by default. We set the Dockerfile to expose 8501.
- You might need to add an app setting: `WEBSITES_PORT` = `8501` to tell Azure which port to route traffic to.

## Troubleshooting
- If the app doesn't load, check the **Log Stream** in Azure.
- Ensure the container image is actually public or you have provided the correct credentials if it's private. (GHCR images are private by default usually, so "Private Registry" with PAT is safest).
