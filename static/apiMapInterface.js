
// getendpointurl = 
function getallmapsnapshots() {
            fetch('/')
                .then(response => response.json())
                .then(data => {
                    const banner = document.getElementById('loading-banner');
                    if (data.downloading) {
                        banner.style.display = 'block';
                        // Recheck in 3 seconds
                        setTimeout(checkDownloadStatus, 3000);
                    } else {
                        banner.style.display = 'none';
                    }
                })
                .catch(err => {
                    // Try again in case server temporarily lagged
                    setTimeout(checkDownloadStatus, 5000);
                });
        }