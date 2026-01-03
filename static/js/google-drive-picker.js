/**
 * Google Drive Picker Integration for ZenPDF
 * Allows users to select PDF files from their Google Drive
 */

// Configuration - these will be injected from server
const GOOGLE_API_KEY = 'AIzaSyDmel8WVno1fm4UzNCf4PlToI1CcAS7Qso';
const GOOGLE_CLIENT_ID = '934576760552-3fr03nm0mjijhj48ig0sokpmc71sp8qe.apps.googleusercontent.com';
const GOOGLE_APP_ID = '934576760552';
const SCOPES = 'https://www.googleapis.com/auth/drive.readonly';

let pickerApiLoaded = false;
let oauthToken = null;
let googleDriveCallback = null;

/**
 * Load the Google API client library
 */
function loadGoogleApi() {
    return new Promise((resolve, reject) => {
        if (window.gapi) {
            resolve();
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'https://apis.google.com/js/api.js';
        script.onload = () => {
            gapi.load('client:picker', {
                callback: () => {
                    pickerApiLoaded = true;
                    resolve();
                },
                onerror: reject
            });
        };
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

/**
 * Load Google Identity Services for authentication
 */
function loadGoogleIdentity() {
    return new Promise((resolve, reject) => {
        if (window.google && window.google.accounts) {
            resolve();
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

/**
 * Authenticate with Google
 */
async function authenticateGoogle() {
    await loadGoogleIdentity();
    
    return new Promise((resolve, reject) => {
        const tokenClient = google.accounts.oauth2.initTokenClient({
            client_id: GOOGLE_CLIENT_ID,
            scope: SCOPES,
            callback: (response) => {
                if (response.error) {
                    reject(response);
                } else {
                    oauthToken = response.access_token;
                    resolve(response.access_token);
                }
            },
        });
        tokenClient.requestAccessToken({ prompt: 'consent' });
    });
}

/**
 * Create and show the Google Drive Picker
 */
function createPicker(callback) {
    googleDriveCallback = callback;
    
    const picker = new google.picker.PickerBuilder()
        .addView(new google.picker.DocsView()
            .setMimeTypes('application/pdf')
            .setMode(google.picker.DocsViewMode.LIST))
        .setOAuthToken(oauthToken)
        .setDeveloperKey(GOOGLE_API_KEY)
        .setAppId(GOOGLE_APP_ID)
        .setCallback(pickerCallback)
        .setTitle('Select a PDF from Google Drive')
        .build();
    
    picker.setVisible(true);
}

/**
 * Handle picker selection
 */
async function pickerCallback(data) {
    if (data[google.picker.Response.ACTION] === google.picker.Action.PICKED) {
        const doc = data[google.picker.Response.DOCUMENTS][0];
        const fileId = doc[google.picker.Document.ID];
        const fileName = doc[google.picker.Document.NAME];
        const fileSize = doc[google.picker.Document.SIZE_BYTES] || 0;
        
        console.log('Selected file:', fileName, fileId);
        
        // Download the file content
        try {
            showLoadingState(`Downloading ${fileName} from Google Drive...`);
            
            const response = await fetch(
                `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`,
                {
                    headers: {
                        'Authorization': `Bearer ${oauthToken}`
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error('Failed to download file from Google Drive');
            }
            
            const blob = await response.blob();
            const file = new File([blob], fileName, { type: 'application/pdf' });
            
            hideLoadingState();
            
            if (googleDriveCallback) {
                googleDriveCallback(file);
            }
        } catch (error) {
            console.error('Error downloading from Google Drive:', error);
            hideLoadingState();
            alert('Failed to download file from Google Drive. Please try again or upload directly.');
        }
    }
}

/**
 * Main function to open Google Drive picker
 */
async function openGoogleDrivePicker(callback) {
    try {
        showLoadingState('Connecting to Google Drive...');
        
        await loadGoogleApi();
        
        if (!oauthToken) {
            await authenticateGoogle();
        }
        
        hideLoadingState();
        createPicker(callback);
        
    } catch (error) {
        console.error('Google Drive error:', error);
        hideLoadingState();
        alert('Failed to connect to Google Drive. Please try again.');
    }
}

/**
 * UI helper functions
 */
function showLoadingState(message) {
    // Create or update loading overlay
    let overlay = document.getElementById('gdrive-loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'gdrive-loading-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;
        overlay.innerHTML = `
            <div style="
                background: #1a1f2e;
                padding: 2rem;
                border-radius: 12px;
                text-align: center;
                color: white;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    border: 3px solid #667eea;
                    border-top-color: transparent;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 1rem;
                "></div>
                <p id="gdrive-loading-text">${message}</p>
            </div>
            <style>
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            </style>
        `;
        document.body.appendChild(overlay);
    } else {
        overlay.style.display = 'flex';
        document.getElementById('gdrive-loading-text').textContent = message;
    }
}

function hideLoadingState() {
    const overlay = document.getElementById('gdrive-loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * Helper to set file from Google Drive in a form's file input
 */
function setFileFromGoogleDrive(file, fileInputId, uploadLabelId) {
    const fileInput = document.getElementById(fileInputId);
    const uploadLabel = document.getElementById(uploadLabelId);
    
    // Create a DataTransfer to set the file
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;
    
    // Update UI
    if (uploadLabel) {
        const fileName = file.name;
        const fileSize = (file.size / (1024 * 1024)).toFixed(2);
        const textSpan = uploadLabel.querySelector('.upload-text');
        const hintSpan = uploadLabel.querySelector('.upload-hint');
        if (textSpan) textSpan.textContent = fileName;
        if (hintSpan) hintSpan.textContent = `${fileSize} MB (from Google Drive)`;
    }
    
    // Trigger change event
    fileInput.dispatchEvent(new Event('change', { bubbles: true }));
}

// Export for use
window.GoogleDrivePicker = {
    open: openGoogleDrivePicker,
    setFile: setFileFromGoogleDrive
};
