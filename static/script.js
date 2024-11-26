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
    const videoDisplayerElement = document.getElementsByClassName('videoDisplayer');
    const htmlElement = document.getElementsByTagName("html");

    if (progressSpinnerElement) {
        // Tüntessük el a progress spinner-t
        progressSpinnerElement.style.display = 'none';
    }
    if (mainContainerElement) {
        // A háttér kerüljön visszaállításra az eredeti állapotára.
        mainContainerElement.style.filter = "";
        mainContainerElement.style.pointerEvents = "";
    }
    if (videoDisplayerElement[0]) {
        videoDisplayerElement[0].style.display = "block";
    }
    if (htmlElement[0]) {
        htmlElement[0].style.height = "auto";
    }
}

const uploadVideo = () => {
    const videoInput = document.getElementById('videoFile');
    const formData = new FormData();

    // Ellenőrizd, hogy van-e fájl kiválasztva
    if (videoInput.files.length === 0) {
        alert("Please select a video file!");
        return;
    }

    // Add hozzá a kiválasztott fájlt a formData-hoz
    formData.append('video', videoInput.files[0]);

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
        }).finally(() => removeProgressSpinnerElements());
    }) 
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while uploading.');
    }).finally(() => removeProgressSpinnerElements());
}

