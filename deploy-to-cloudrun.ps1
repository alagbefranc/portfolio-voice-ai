# Google Cloud Run Deployment Script for Voice AI Agent

# Check if user is logged in to gcloud
Write-Host "Checking Google Cloud authentication..." -ForegroundColor Yellow
gcloud auth list

# Get or set project ID
$PROJECT_ID = Read-Host "Enter your Google Cloud Project ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "Enabling required Google Cloud APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Set variables
$SERVICE_NAME = "voice-ai-agent"
$REGION = "us-central1"  # You can change this to your preferred region
$IMAGE = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Build and push Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow

# Read environment variables from .env file
if (Test-Path .env) {
    Write-Host "Reading environment variables from .env file..." -ForegroundColor Yellow
    $envVars = @{}
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $envVars[$matches[1]] = $matches[2]
        }
    }
    
    # Build environment variables string for Cloud Run
    $envString = ""
    foreach ($key in $envVars.Keys) {
        if ($envString -ne "") { $envString += "," }
        $envString += "$key=$($envVars[$key])"
    }
    
    # Deploy with environment variables
    gcloud run deploy $SERVICE_NAME `
        --image $IMAGE `
        --platform managed `
        --region $REGION `
        --memory 4Gi `
        --cpu 2 `
        --timeout 3600 `
        --min-instances 0 `
        --max-instances 10 `
        --set-env-vars $envString `
        --allow-unauthenticated
} else {
    Write-Host "No .env file found. Deploying without environment variables." -ForegroundColor Red
    Write-Host "You'll need to set them manually in the Cloud Console." -ForegroundColor Red
    
    gcloud run deploy $SERVICE_NAME `
        --image $IMAGE `
        --platform managed `
        --region $REGION `
        --memory 4Gi `
        --cpu 2 `
        --timeout 3600 `
        --min-instances 0 `
        --max-instances 10 `
        --allow-unauthenticated
}

# Get the service URL
Write-Host "`nGetting service URL..." -ForegroundColor Yellow
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format "value(status.url)"
Write-Host "Your Voice AI Agent is deployed at: $SERVICE_URL" -ForegroundColor Green

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Note: The agent will connect to LiveKit Cloud automatically when it receives events." -ForegroundColor Cyan
