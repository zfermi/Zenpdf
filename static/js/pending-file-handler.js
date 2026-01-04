/**
 * Pending File Handler
 * Handles PDF files uploaded from the homepage and transferred to tool pages
 */
(function () {
    'use strict';

    const pendingFile = sessionStorage.getItem('pendingPdfFile');
    if (!pendingFile) return;

    try {
        const fileData = JSON.parse(pendingFile);
        // Clear the storage immediately to prevent re-use
        sessionStorage.removeItem('pendingPdfFile');

        // Convert base64 back to File object
        const byteString = atob(fileData.data.split(',')[1]);
        const mimeType = fileData.type || 'application/pdf';
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        const blob = new Blob([ab], { type: mimeType });
        const file = new File([blob], fileData.name, { type: mimeType });

        // Wait for DOM to be ready
        const handlePendingFile = function () {
            // Try different common selectors for file inputs and forms
            const fileInput = document.getElementById('file') ||
                document.getElementById('pdf-file') ||
                document.querySelector('input[type="file"][accept=".pdf"]');

            const uploadLabel = document.getElementById('upload-label') ||
                document.querySelector('.upload-area');

            const form = document.getElementById('split-form') ||
                document.getElementById('merge-form') ||
                document.getElementById('compress-form') ||
                document.getElementById('rotate-form') ||
                document.getElementById('pdf2word-form') ||
                document.querySelector('form[enctype="multipart/form-data"]');

            if (fileInput && form) {
                // Create a DataTransfer to set files
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;

                // Update UI if upload label exists
                if (uploadLabel) {
                    const uploadText = uploadLabel.querySelector('.upload-text');
                    const uploadHint = uploadLabel.querySelector('.upload-hint');

                    if (uploadText) {
                        uploadText.textContent = file.name;
                    }
                    if (uploadHint) {
                        const fileSize = (file.size / (1024 * 1024)).toFixed(2);
                        uploadHint.textContent = `${fileSize} MB - Ready to process`;
                    }
                }

                // Auto-submit the form after a brief delay
                setTimeout(() => {
                    form.submit();
                }, 500);
            }
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', handlePendingFile);
        } else {
            handlePendingFile();
        }

    } catch (e) {
        console.error('Error processing pending file:', e);
        sessionStorage.removeItem('pendingPdfFile');
    }
})();
