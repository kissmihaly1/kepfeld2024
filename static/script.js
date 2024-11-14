async function uploadVideo() {
    const videoInput = document.getElementById("videoInput");
    if (videoInput.files.length === 0) {
        alert("Please select a video file first.");
        return;
    }

    const formData = new FormData();
    formData.append("video", videoInput.files[0]);

    try {
        const response = await fetch("/process-video", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Failed to upload and process video");
        }

        const data = await response.json();
        const videoUrl = data.video_url;

        const processedVideo = document.getElementById("processedVideo");
        processedVideo.src = videoUrl;
        processedVideo.style.display = "block";
        processedVideo.play();
    } catch (error) {
        console.error("Error:", error);
        alert("Error processing video");
    }
}
