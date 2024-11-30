const setProgressSpinnerElements = () => {
    const progressSpinnerElement = document.getElementById('progressSpinner');
    const mainContainerElement = document.getElementById('mainContainer');
    if (progressSpinnerElement) {
        // Jelenítsük meg a progress spinner-t
        progressSpinnerElement.style.display = 'block';
    }
    if (mainContainerElement) {
        // A háttér legyen blur, miközben az egérrel ne lehessen kattintani.
        mainContainerElement.style.filter = "blur(3px)";
        mainContainerElement.style.pointerEvents = "none";
    }
}

const removeProgressSpinnerElements = () => {
    const progressSpinnerElement = document.getElementById('progressSpinner');
    const mainContainerElement = document.getElementById('mainContainer');
    if (progressSpinnerElement) {
        // Tüntessük el a progress spinner-t
        progressSpinnerElement.style.display = 'none';
    }
    if (mainContainerElement) {
        // A háttér kerüljön visszaállításra az eredeti állapotára.
        mainContainerElement.style.filter = "";
        mainContainerElement.style.pointerEvents = "";
    }
}

const renderVideoDiv = () => {
    const videoDisplayerElement = document.getElementsByClassName('videoDisplayer');
    const htmlElement = document.getElementsByTagName("html");
    if (htmlElement[0]) {
        htmlElement[0].style.height = "auto";
    }
    if (videoDisplayerElement[0]) {
        videoDisplayerElement[0].style.display = "block";
    }
}

const handleSpeedThresholdChanges = () => {
    const thresholdValue = document.getElementById('speed_threshold').value;
    const thresholdLabel = document.getElementById('speed_threshold_label');
    const labelText = `Speed threshold (${thresholdValue}):`;
    thresholdLabel.textContent = labelText;
}

const handlePositionThresholdChanges = () => {
    const thresholdValue = document.getElementById('position_threshold').value;
    const thresholdLabel = document.getElementById('position_threshold_label');
    const labelText = `Position threshold (${thresholdValue}):`;
    thresholdLabel.textContent = labelText;
}

const handleTimeThresholdChanges = () => {
    const thresholdValue = document.getElementById('time_threshold').value;
    const thresholdLabel = document.getElementById('time_threshold_label');
    const labelText = `Time threshold (${thresholdValue}):`;
    thresholdLabel.textContent = labelText;
}

const handleStationaryThresholdChanges = () => {
    const thresholdValue = document.getElementById('stationary_threshold').value;
    const thresholdLabel = document.getElementById('stationary_threshold_label');
    const labelText = `Stationary threshold (${thresholdValue}):`;
    thresholdLabel.textContent = labelText;
}

const getFormData = () => {
    const videoInput = document.getElementById('videoFile');
    const speedThresholdValue = document.getElementById('speed_threshold').value;
    const positionThresholdValue = document.getElementById('position_threshold').value;
    const timeThresholdValue = document.getElementById('time_threshold').value;
    const stationaryThresholdValue = document.getElementById('stationary_threshold').value;
    const formData = new FormData();

    // Ellenőrizd, hogy van-e fájl kiválasztva
    if (videoInput.files.length === 0) {
        alert("Please select a video file!");
        return;
    }

    // Add hozzá a kiválasztott fájlt a formData-hoz
    formData.append('video', videoInput.files[0]);
    formData.append('speed_threshold', speedThresholdValue);
    formData.append('position_threshold', positionThresholdValue);
    formData.append('time_threshold', timeThresholdValue);
    formData.append('stationary_threshold', stationaryThresholdValue);
    return formData;
}

const uploadVideo = () => {
    const formData = getFormData();
    if (!formData) {
        return;
    }

    // Jelenítsük meg a progress bar-t.
    setProgressSpinnerElements();

    // AJAX kérés küldése Fetch API-val
    fetch('/process-video', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        const data = response.json();

        data.then(result => {
            const videoUrl = result.video_url;
            const videoHtmlElement = document.getElementById('processedVideo');
            videoHtmlElement.style.display = 'block';
            videoHtmlElement.src = videoUrl;
            const number = result.number;
            
            if(number) {
                const numberDivElement = document.getElementById('number');
                const numberSpanElement = document.getElementById('numberOfCars');

                numberDivElement.style.display = "block";
                numberSpanElement.textContent = number;
            }
        }).finally(() => {
            removeProgressSpinnerElements();
            renderVideoDiv();
        });
    }) 
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while uploading.');
    }).finally(() => removeProgressSpinnerElements());
}

