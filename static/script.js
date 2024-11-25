function uploadVideo() {
    const videoInput = document.getElementById('videoFile');
    const formData = new FormData();

    // Ellenőrizd, hogy van-e fájl kiválasztva
    if (videoInput.files.length === 0) {
        alert("Please select a video file!");
        return;
    }

    // Add hozzá a kiválasztott fájlt a formData-hoz
    formData.append('video', videoInput.files[0]);

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
        });
    }) 
    .then(data => {
        console.log('Success');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while uploading.');
    });
}

