import src.core.video_control as VideoControl

VideoControl.list_open_window_names()
window_name = "Krteček.mp4 - VLC media player"
VideoControl.start_playing_video(window_name)
