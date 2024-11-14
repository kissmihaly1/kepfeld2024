async function uploadVideo() {
    const videoInput = document.getElementById("videoInput");
    if (videoInput.files.length === 0) {
        alert("Please select a video file first");
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
            throw new Error("Failed to upload video");
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const processedVideo = document.getElementById("processedVideo");
        processedVideo.src = url;
        processedVideo.style.display = "block";
    } catch (error) {
        console.error("Error:", error);
        alert("Error processing video");
    }
}
