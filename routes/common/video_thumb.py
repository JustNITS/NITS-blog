import cv2
def create_thumbnail(current_dir, video_path):
    time_sec = 5
    output_image_path = video_path.replace('.mp4', '_thumbnail.jpg')
    print(current_dir + video_path)
    cap = cv2.VideoCapture(current_dir + video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps
    if time_sec > duration:
        print(f"Requested time {time_sec}s exceeds video length ({duration:.2f}s). Using {duration / 2:.2f}s instead.")
        time_sec = duration / 2

    cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
    success, frame = cap.read()

    if success:
        thumbnail = cv2.resize(frame, (320, 180))
        cv2.imwrite(current_dir + output_image_path, thumbnail)
        print("Thumbnail saved at", output_image_path)
    else:
        print("Failed to capture frame")

    cap.release()
    print("Video capture released at ", output_image_path)
    return output_image_path

