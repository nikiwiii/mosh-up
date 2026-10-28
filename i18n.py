"""
Internationalization (i18n) module for MoshUp Studio.
Supports English ('en', default) and Polish ('pl').
"""

TRANSLATIONS = {
    'en': {
        # App Title & About
        'app_title': 'MoshUp Studio',
        'about_title': 'About MoshUp Studio',
        'about_heading': '<h3>MoshUp Studio</h3>',
        'about_desc': '<p>Modern desktop application for video datamoshing powered by PySide6 and FFmpeg.</p>',
        'about_modes_title': '<p><b>Datamosh Modes:</b></p>',
        'about_mode_volcano': '<li><b>Volcano Melt</b>: Removes keyframes (I-Frames) in a selected time window</li>',
        'about_mode_smear': '<li><b>Endless Motion Smear</b>: Duplicates delta frames (P-Frames)</li>',
        'about_mode_stitch': '<li><b>Stitch Mosh</b>: Transfers motion vectors from Video B onto the last frame of Video A</li>',
        'about_mode_cyber': '<li><b>Cyber Glitch</b>: Corrupts delta frame motion bits directly</li>',
        'about_mode_flow': '<li><b>Flow Drift</b>: Organic pixel drift calculated using Farneback optical flow</li>',
        'about_mode_rgb': '<li><b>RGB Channel Split</b>: Splits color channels (R, G, B) with temporal delay and spatial shift</li>',
        'about_mode_audio': '<li><b>Audio Reactive</b>: Syncs datamosh vector smears, keyframe drops, and chromatic shocks directly to music beats and audio frequencies</li>',

        # Navigation Rail
        'nav_step_1': '1. Upload Video',
        'nav_step_2': '2. Effects & Parameters',
        'nav_step_3': '3. Rendering',
        'nav_step_4': '4. Video Preview',
        'nav_lang_tooltip': 'Switch language (EN / PL)',
        'nav_reset_tooltip': 'Reset parameters to default state',
        'nav_info_tooltip': 'About MoshUp',

        # Step 1: Upload Page
        'step1_title': 'Step 1: Upload Video File',
        'step1_subtitle': 'Drag and drop a video file to serve as the base for datamoshing effects and vector corruptions.',
        'drop_title': 'Drag and drop video file here',
        'drop_subtitle': 'or browse from your computer\nSupported formats: MP4, MOV, MKV, AVI, WEBM',
        'btn_browse_file': '  Choose video file from disk...',
        'source_preview_title': 'Source Video Preview',
        'file_info_title': 'File Information',
        'badge_loaded_success': '✓ File loaded successfully',
        'tech_params_title': 'Technical Parameters',
        'meta_filename': 'File Name:',
        'meta_duration': 'Duration:',
        'meta_resolution': 'Resolution:',
        'meta_fps': 'Frame Rate (FPS):',
        'meta_filesize': 'File Size:',
        'btn_replace_video': '  Change video file...',
        'step1_hint_empty': 'Select a video file to proceed to effects configuration.',
        'step1_hint_loaded': 'Video ready. Click Next to configure datamoshing effects.',
        'btn_next_effects': '  Next: Choose Effects',

        # Video Player
        'player_no_video': 'No video loaded',
        'player_read_error': 'Video read error',
        'player_file_not_found': 'File not found',
        'btn_play': '  Play',
        'btn_pause': '  Pause',

        # Step 2: Effects Page
        'step2_title': 'Step 2: Effects & Parameters Configuration',
        'step2_subtitle': 'Choose a distortion mode and fine-tune datamosh algorithm parameters.',
        'tab_volcano': 'Volcano Melt',
        'tab_smear': 'Motion Smear',
        'tab_stitch': 'Stitch Mosh',
        'tab_cyber': 'Cyber Glitch',
        'tab_flow': 'Flow Drift',
        'tab_rgb': 'RGB Split',
        'tab_audio': 'Audio Reactive',

        # Mode Descriptions
        'desc_volcano': 'Removes keyframes (I-Frames) in the specified time range. Motion vectors deform the previous static picture, melting objects seamlessly.',
        'desc_smear': 'Duplicates delta frames (P-Frames), infinitely extending motion vectors and creating vibrant pixel smears.',
        'desc_stitch': 'Joins two video files. The initial keyframe of Video B is cut out, allowing motion from clip B to animate the last frame of clip A.',
        'desc_cyber': 'Injects random byte corruptions directly into P-Frame motion vectors, generating digital cyberpunk glitch-art artifacts.',
        'desc_flow': 'Calculates optical flow vectors between frames and drifts accumulated screen pixels organically.',
        'desc_rgb': 'Splits color components (Red, Green, Blue) with temporal lag and spatial offset, creating analog VHS chromatic aberration.',
        'desc_audio': 'Analyzes audio beats, basslines, and frequency energy to trigger vector smears, keyframe drops, or digital glitches in sync with the rhythm.',

        # Mode Parameters
        'group_time_window': 'Effect Time Window',
        'lbl_time_start': 'Start Time:',
        'lbl_time_end': 'End Time:',
        'btn_from_cursor': '  From Player',
        'ts_format_hint': 'Format: MM:SS (e.g. 00:05 or 01:20)',
        'ts_valid_hint': 'Valid range: {start} to {end} [Duration: {duration:.1f} s]',
        'ts_error_start_range': 'Start time must be within [0, {duration:.1f}s]',
        'ts_error_end_range': 'End time must be greater than start and within [0, {duration:.1f}s]',
        'ts_error_format': 'Invalid format! Use MM:SS (e.g. 00:15)',

        'group_smear_params': 'Vector Smear Parameters',
        'lbl_repeat_count': 'Repeat Count:',
        'lbl_frequency': 'Frequency (every Nth frame):',

        'group_stitch_params': 'Second Video File (Video B)',
        'btn_select_b': '  Choose Video B...',
        'lbl_no_b_selected': 'No second video file selected',

        'group_cyber_params': 'Bit Corruption Settings',
        'lbl_corrupt_rate': 'Corruption Rate (% of P-frames):',
        'lbl_corrupt_intensity': 'Byte Swap Intensity:',

        'group_flow_params': 'Optical Flow Parameters (Farneback)',
        'lbl_flow_scale': 'Flow Scale:',
        'lbl_trail_decay': 'Trail Decay:',

        'group_rgb_params': 'RGB Channel Split Parameters',
        'lbl_rgb_delay': 'Frame Lag (Temporal Delay):',
        'lbl_rgb_shift': 'Optical Shift (px):',
        'lbl_rgb_direction': 'Shift Direction:',
        'rgb_dir_horizontal': 'Horizontal',
        'rgb_dir_diagonal': 'Diagonal',
        'rgb_dir_vertical': 'Vertical',
        'lbl_rgb_jitter': 'VHS Scanline Jitter (%):',

        'group_audio_params': 'Audio-Reactive Datamosh Settings',
        'lbl_audio_source': 'Audio Track Source:',
        'audio_src_video': 'Source Video Audio Track',
        'audio_src_custom': 'Custom External Audio File (MP3 / WAV / AAC)',
        'btn_choose_audio': '  Choose Audio File...',
        'lbl_no_custom_audio': 'Using audio from video',
        'lbl_reaction_mode': 'Reaction Mode:',
        'reaction_smear': 'Beat Motion Smear (Vector Stretch on Bass)',
        'reaction_melt': 'Beat Drop Melt (Drop Keyframes on Beats)',
        'reaction_glitch': 'Cyber Glitch Rhythm (Bit Corruption on Beats)',
        'reaction_rgb': 'Chromatic Beat Pulse (Aberration Shockwave)',
        'reaction_hybrid': 'Full Audio Chaos (Smear + Glitch Burst)',
        'lbl_audio_band': 'Frequency Trigger Band:',
        'band_bass': 'Bass / Kick Drums (20 - 180 Hz)',
        'band_rms': 'Full Volume / Transients & Peaks',
        'band_high': 'Snare / High Frequencies (2 - 10 kHz)',
        'lbl_audio_sensitivity': 'Beat Sensitivity / Threshold:',
        'lbl_audio_intensity': 'Glitch Burst Intensity:',

        # Fast Draft inline
        'btn_fast_draft': '  3s Preview',
        'fast_draft_tooltip': 'Generate 3-second preview with current parameters',
        'fast_draft_refresh': 'Refresh preview',
        'fast_draft_close': 'Close preview',

        # Export & Audio
        'group_export_settings': 'Export Settings',
        'chk_keep_audio': 'Preserve original audio track',
        'btn_change_out': '  Change output name/folder...',
        'lbl_auto_out': 'Automatic output filename',
        'btn_step2_back': '  Back to Video Selection',
        'btn_step2_next': '  Next: Export & Render',

        # Step 3: Render Page
        'step3_title': 'Step 3: Export & Rendering',
        'step3_subtitle': 'Review render configuration summary and launch the Datamosh processing engine.',
        'summary_hdr': 'Render Task Summary',
        'tile1_title': '1. SOURCE VIDEO',
        'tile2_title': '2. DATAMOSH EFFECT',
        'tile3_title': '3. AUDIO & STREAM',
        'tile4_title': '4. OUTPUT FILE',
        'tile_dir_label': 'Folder: {folder}',
        'tile_audio_on': 'Audio: Preserved',
        'tile_audio_off': 'Audio: Muted',
        'btn_start_mosh': '  START MOSHING',
        'status_ready': 'Status: Ready to start',
        'status_processing': 'Status: Processing ({pct}%)',
        'status_in_progress': 'Status: Processing in progress...',
        'status_success': 'Status: Finished successfully!',
        'status_error': 'Status: Error occurred',
        'console_title': 'Console',
        'console_placeholder': 'FFmpeg engine log stream...',
        'console_ready': 'MoshUp Studio ready.',
        'btn_step3_back': '  Back to Parameters',
        'btn_step3_next': '  Next: Video Preview',

        # Step 4: Preview Page
        'step4_title': 'Step 4: Final Video Preview',
        'step4_subtitle': 'Play the rendered video, compare with the original, or open output files on disk.',
        'btn_toggle_effect': '  Effect',
        'btn_toggle_source': '  Original',
        'lbl_location': 'File Location:',
        'lbl_no_output_file': 'No generated file',
        'btn_open_system_player': '  Play in System Player',
        'btn_open_folder': '  Open Folder with File',
        'btn_tweak_params': '  Adjust Parameters',
        'btn_new_project': '  Load New Video',
        'btn_step4_back': '  Back to Rendering',
        'btn_step4_restart': '  New Project',
        'tag_viewing_result': 'Viewing: Generated Datamosh File',
        'tag_viewing_source': 'Viewing: Original Video File (Before Effect)',

        # Dialogs & Notifications
        'dialog_reset_title': 'Reset Parameters',
        'dialog_reset_heading': '<h3>Do you want to reset all parameters to defaults?</h3>',
        'dialog_reset_info': 'All loaded video files, modified effect parameters, generated previews, and rendering states will be restored to default startup values.',
        'btn_reset_all': '  Reset Everything',
        'btn_cancel': '  Cancel',

        'dialog_new_project_title': 'New Project',
        'dialog_new_project_msg': 'Do you want to reset the current project and load a new video?',

        'dialog_no_video_title': 'No Video File',
        'dialog_no_video_msg': 'Please select a video file in Step 1 first!',
        'dialog_no_video_b_title': 'Missing Second Video',
        'dialog_no_video_b_msg': 'Please select Video B for Stitch Mosh mode before generating preview!',
        'dialog_ts_error_title': 'Time Range Error',
        'dialog_ts_error_msg': 'Please fix the time range in Volcano Melt tab before proceeding!',
        'dialog_no_output_title': 'No Rendered File',
        'dialog_no_output_msg': 'Render the video in Step 3 first to view the preview!',
        'dialog_draft_error_title': 'Fast Draft Error',
        'dialog_draft_error_msg': 'Failed to generate 3-second preview:\n\n{err}',
        'dialog_render_error_title': 'Processing Error',
        'dialog_render_error_msg': 'An error occurred during the datamosh process:\n\n{err}',
        'dialog_no_audio_title': 'No Audio Track Found',
        'dialog_no_audio_msg': 'The video has no audio stream and no custom audio file was selected. Please choose an audio file or select a video with sound!',

        'file_dialog_select_a': 'Select Video File A',
        'file_dialog_select_b': 'Select Video File B',
        'file_dialog_select_audio': 'Select External Audio File',
        'file_dialog_audio_filter': 'Audio Files (*.mp3 *.wav *.aac *.m4a *.flac *.ogg);;All Files (*.*)',
        'file_dialog_save_output': 'Save Datamosh Output Video',
        'file_dialog_video_filter': 'Video files (*.mp4 *.avi *.mov *.mkv *.webm);;All files (*.*)',
        'file_dialog_save_filter': 'MP4 Video (*.mp4);;AVI Video (*.avi)',

        # Logs
        'log_task_start': "Starting task: mode '{mode}' -> {output}",
        'log_success': 'Success: Output video saved to {path}',
        'log_error': 'Error: {err}',
        'log_video_a_loaded': 'Loaded Video A: {path}',
        'log_video_b_loaded': 'Loaded Video B: {path}',
        'log_reset_done': 'Reset application parameters to initial state.',
    },

    'pl': {
        # App Title & About
        'app_title': 'MoshUp Studio',
        'about_title': 'O programie MoshUp Studio',
        'about_heading': '<h3>MoshUp Studio</h3>',
        'about_desc': '<p>Nowoczesne studio do zaawansowanego zniekształcania wideo (Datamoshing) oparte na PySide6 i FFmpeg.</p>',
        'about_modes_title': '<p><b>Tryby zniekształceń:</b></p>',
        'about_mode_volcano': '<li><b>Volcano Melt</b>: Usuwanie klatek kluczowych (I-Frames) w zadanym oknie czasowym</li>',
        'about_mode_smear': '<li><b>Endless Motion Smear</b>: Powielanie klatek delta (P-Frames)</li>',
        'about_mode_stitch': '<li><b>Stitch Mosh</b>: Przenoszenie ruchu z drugiego klipu (Video B) na klatkę z Video A</li>',
        'about_mode_cyber': '<li><b>Cyber Glitch</b>: Bezpośrednie uszkadzanie bitów wektorów ruchu</li>',
        'about_mode_flow': '<li><b>Flow Drift</b>: Organiczny dryf pikseli obliczany metodą przepływu optycznego</li>',
        'about_mode_rgb': '<li><b>RGB Channel Split</b>: Rozszczepianie kanałów barwnych (Red, Green, Blue) z opóźnieniem czasowym i przesunięciem przestrzennym</li>',
        'about_mode_audio': '<li><b>Audio Reactive</b>: Synchronizuje impulsy zniekształceń, smugi wektorów i aberrację chromatyczną z rytmem i basem muzyki</li>',

        # Navigation Rail
        'nav_step_1': '1. Wczytaj wideo',
        'nav_step_2': '2. Efekty i parametry',
        'nav_step_3': '3. Renderowanie',
        'nav_step_4': '4. Podgląd wideo',
        'nav_lang_tooltip': 'Zmień język (PL / EN)',
        'nav_reset_tooltip': 'Resetuj parametry do stanu początkowego',
        'nav_info_tooltip': 'Informacje o MoshUp',

        # Step 1: Upload Page
        'step1_title': 'Krok 1: Wczytaj plik wideo',
        'step1_subtitle': 'Przeciągnij i upuść plik wideo, który posłuży jako baza dla zniekształceń i efektów datamoshingu.',
        'drop_title': 'Przeciągnij i upuść plik wideo tutaj',
        'drop_subtitle': 'lub wybierz plik z dysku komputera\nObsługiwane formaty: MP4, MOV, MKV, AVI, WEBM',
        'btn_browse_file': '  Wybierz plik wideo z dysku...',
        'source_preview_title': 'Podgląd wideo źródłowego',
        'file_info_title': 'Informacje o pliku',
        'badge_loaded_success': '✓ Plik załadowany pomyślnie',
        'tech_params_title': 'Parametry techniczne',
        'meta_filename': 'Nazwa pliku:',
        'meta_duration': 'Czas trwania:',
        'meta_resolution': 'Rozdzielczość:',
        'meta_fps': 'Klatkaż (FPS):',
        'meta_filesize': 'Rozmiar:',
        'btn_replace_video': '  Zmień plik wideo...',
        'step1_hint_empty': 'Wybierz plik wideo, aby przejść do konfiguracji efektów.',
        'step1_hint_loaded': 'Wideo gotowe. Kliknij Dalej, aby skonfigurować efekty datamosh.',
        'btn_next_effects': '  Dalej: Wybierz efekty',

        # Video Player
        'player_no_video': 'Brak załadowanego wideo',
        'player_read_error': 'Błąd odczytu wideo',
        'player_file_not_found': 'Nie można odnaleźć pliku',
        'btn_play': '  Odtwórz',
        'btn_pause': '  Wstrzymaj',

        # Step 2: Effects Page
        'step2_title': 'Krok 2: Wybór efektu i parametrów',
        'step2_subtitle': 'Wybierz tryb zniekształceń klatek i dostosuj parametry algorytmu datamosh.',
        'tab_volcano': 'Volcano Melt',
        'tab_smear': 'Motion Smear',
        'tab_stitch': 'Stitch Mosh',
        'tab_cyber': 'Cyber Glitch',
        'tab_flow': 'Flow Drift',
        'tab_rgb': 'RGB Split',
        'tab_audio': 'Audio Reactive',

        # Mode Descriptions
        'desc_volcano': 'Usuwa klatki kluczowe (I-Frames) w zadanym oknie czasowym. Wektory ruchu deformatują poprzedni statyczny obraz, tworząc płynne topnienie obiektów.',
        'desc_smear': 'Duplikuje klatki delta (P-Frames), powodując wielokrotne powtarzanie wektorów ruchu i charakterystyczne smugi pikseli.',
        'desc_stitch': 'Łączy dwa pliki wideo. Początkowa klatka kluczowa wideo B zostaje wycięta, przez co ruch z drugiego klipu ożywia ostatnią klatkę pierwszego wideo.',
        'desc_cyber': 'Wstrzykuje losowe uszkodzenia bajtów bezpośrednio do wektorów klatek różnicowych (P-Frames), generując cyfrowe zakłócenia w stylu glitch-art.',
        'desc_flow': 'Oblicza wektory przepływu optycznego pomiędzy klatkami i deformuje zakumulowane piksele na ekranie w organiczny, płynny sposób.',
        'desc_rgb': 'Rozszczepia składowe barwne (czerwony, zielony, niebieski) z opóźnieniem czasowym i przesunięciem przestrzennym, tworząc hipnotyzujące tęczowe smugi ruchu oraz analogowy efekt aberracji chromatycznej VHS.',
        'desc_audio': 'Analizuje pasma częstotliwości i uderzenia w ścieżce dźwiękowej, wyzwalając rozmazywanie wektorów, usuwanie klatek kluczowych lub zniekształcenia bitów dokładnie w rytm muzyki.',

        # Mode Parameters
        'group_time_window': 'Przedział czasowy efektu',
        'lbl_time_start': 'Czas początkowy (Start):',
        'lbl_time_end': 'Czas końcowy (Koniec):',
        'btn_from_cursor': '  Z pozycji odtwarzacza',
        'ts_format_hint': 'Format: MM:SS (np. 00:05 lub 01:20)',
        'ts_valid_hint': 'Prawidłowy przedział: {start} do {end} [Długość okna: {duration:.1f} s]',
        'ts_error_start_range': 'Czas początkowy musi mieścić się w przedziale [0, {duration:.1f}s]',
        'ts_error_end_range': 'Czas końcowy musi być większy niż start i mieścić się w przedziale [0, {duration:.1f}s]',
        'ts_error_format': 'Nieprawidłowy format! Użyj formatu MM:SS (np. 00:15)',

        'group_smear_params': 'Parametry rozmycia wektorów',
        'lbl_repeat_count': 'Liczba powtórzeń (Repeat Count):',
        'lbl_frequency': 'Częstotliwość (co N-tą klatkę):',

        'group_stitch_params': 'Drugi plik wideo (Wideo B)',
        'btn_select_b': '  Wybierz wideo B...',
        'lbl_no_b_selected': 'Nie wybrano drugiego pliku wideo',

        'group_cyber_params': 'Ustawienia uszkodzeń bitowych',
        'lbl_corrupt_rate': 'Wskaźnik korupcji (% klatek P):',
        'lbl_corrupt_intensity': 'Intensywność zamiany bajtów:',

        'group_flow_params': 'Parametry przepływu optycznego (Farneback)',
        'lbl_flow_scale': 'Skala przepływu (Flow Scale):',
        'lbl_trail_decay': 'Zanikanie śladu (Trail Decay):',

        'group_rgb_params': 'Parametry rozszczepienia kanałów RGB',
        'lbl_rgb_delay': 'Opóźnienie klatek (Lag czasowy):',
        'lbl_rgb_shift': 'Przesunięcie optyczne (px):',
        'lbl_rgb_direction': 'Kierunek przesunięcia:',
        'rgb_dir_horizontal': 'Poziomy (Horizontal)',
        'rgb_dir_diagonal': 'Ukośny (Diagonal)',
        'rgb_dir_vertical': 'Pionowy (Vertical)',
        'lbl_rgb_jitter': 'Zakłócenia linii VHS (Jitter %):',

        'group_audio_params': 'Ustawienia reakcji na dźwięk',
        'lbl_audio_source': 'Źródło ścieżki audio:',
        'audio_src_video': 'Ścieżka dźwiękowa z pliku wideo',
        'audio_src_custom': 'Własny plik audio (MP3 / WAV / AAC)',
        'btn_choose_audio': '  Wybierz plik audio...',
        'lbl_no_custom_audio': 'Używany dźwięk z wideo',
        'lbl_reaction_mode': 'Tryb reakcji:',
        'reaction_smear': 'Beat Motion Smear (Rozciąganie wektorów na basie)',
        'reaction_melt': 'Beat Drop Melt (Usuwanie klatek na uderzeniach)',
        'reaction_glitch': 'Cyber Glitch Rhythm (Rytmiczne zniekształcenia bitów)',
        'reaction_rgb': 'Chromatic Beat Pulse (Aberracja chromatyczna i wstrząs)',
        'reaction_hybrid': 'Full Audio Chaos (Maksymalny mosh: Smear + Glitch)',
        'lbl_audio_band': 'Pasmo wyzwalania:',
        'band_bass': 'Basy / Stopa perkusji (20 - 180 Hz)',
        'band_rms': 'Pełna głośność / Skoki amplitudy',
        'band_high': 'Werbel / Tony wysokie (2 - 10 kHz)',
        'lbl_audio_sensitivity': 'Czułość detekcji uderzeń:',
        'lbl_audio_intensity': 'Intensywność impulsu glitch:',

        # Fast Draft inline
        'btn_fast_draft': '  Podgląd 3s',
        'fast_draft_tooltip': 'Generuj 3-sekundowy podgląd z bieżącymi parametrami',
        'fast_draft_refresh': 'Odśwież podgląd',
        'fast_draft_close': 'Zamknij podgląd',

        # Export & Audio
        'group_export_settings': 'Ustawienia eksportu',
        'chk_keep_audio': 'Zachowaj oryginalną ścieżkę dźwiękową wideo',
        'btn_change_out': '  Zmień nazwę/folder zapisu...',
        'lbl_auto_out': 'Automatyczna nazwa pliku wyjściowego',
        'btn_step2_back': '  Wróć do wyboru wideo',
        'btn_step2_next': '  Dalej: Eksport i Renderowanie',

        # Step 3: Render Page
        'step3_title': 'Krok 3: Eksport i Renderowanie',
        'step3_subtitle': 'Szczegółowe zestawienie parametrów renderowania oraz uruchomienie silnika Datamosh.',
        'summary_hdr': 'Podsumowanie zadania renderingu',
        'tile1_title': '1. PLIK ŹRÓDŁOWY',
        'tile2_title': '2. EFEKT DATAMOSH',
        'tile3_title': '3. AUDIO I STRUMIEŃ',
        'tile4_title': '4. PLIK WYJŚCIOWY',
        'tile_dir_label': 'Katalog: {folder}',
        'tile_audio_on': 'Dźwięk: Zachowany',
        'tile_audio_off': 'Dźwięk: Wyciszony',
        'btn_start_mosh': '  ROZPOCZNIJ MOSHING',
        'status_ready': 'Status: Gotowy do uruchomienia',
        'status_processing': 'Status: Przetwarzanie ({pct}%)',
        'status_in_progress': 'Status: Przetwarzanie w toku...',
        'status_success': 'Status: Zakończono sukcesem!',
        'status_error': 'Status: Wystąpił błąd',
        'console_title': 'Konsola',
        'console_placeholder': 'Strumień logów z silnika FFmpeg...',
        'console_ready': 'MoshUp Studio gotowe.',
        'btn_step3_back': '  Wróć do parametrów',
        'btn_step3_next': '  Dalej: Podgląd gotowego wideo',

        # Step 4: Preview Page
        'step4_title': 'Krok 4: Podgląd gotowego wideo',
        'step4_subtitle': 'Odtwórz wyrenderowane wideo, porównaj je z oryginałem lub otwórz plik na dysku.',
        'btn_toggle_effect': '  Efekt',
        'btn_toggle_source': '  Oryginał',
        'lbl_location': 'Lokalizacja pliku:',
        'lbl_no_output_file': 'Brak wygenerowanego pliku',
        'btn_open_system_player': '  Odtwórz w odtwarzaczu systemowym',
        'btn_open_folder': '  Otwórz folder z plikiem',
        'btn_tweak_params': '  Zmień parametry',
        'btn_new_project': '  Wczytaj nowe wideo',
        'btn_step4_back': '  Wróć do renderowania',
        'btn_step4_restart': '  Nowy projekt',
        'tag_viewing_result': 'Oglądasz: Wygenerowany plik Datamosh',
        'tag_viewing_source': 'Oglądasz: Oryginalny plik wideo (Przed efektem)',

        # Dialogs & Notifications
        'dialog_reset_title': 'Resetowanie parametrów',
        'dialog_reset_heading': '<h3>Czy chcesz zresetować parametry do stanu początkowego?</h3>',
        'dialog_reset_info': 'Wszystkie wczytane pliki wideo, zmodyfikowane parametry efektów, wygenerowane podglądy oraz stan renderowania zostaną przywrócone do stanu zerowego (uruchomienia).',
        'btn_reset_all': '  Zresetuj wszystko',
        'btn_cancel': '  Anuluj',

        'dialog_new_project_title': 'Nowy projekt',
        'dialog_new_project_msg': 'Czy chcesz zresetować bieżący projekt i wczytać nowe wideo?',

        'dialog_no_video_title': 'Brak pliku wideo',
        'dialog_no_video_msg': 'Wybierz najpierw plik wideo w kroku 1!',
        'dialog_no_video_b_title': 'Brak drugiego wideo',
        'dialog_no_video_b_msg': 'Wybierz plik Wideo B dla trybu Stitch Mosh przed wygenerowaniem podglądu!',
        'dialog_ts_error_title': 'Błąd zakresu czasu',
        'dialog_ts_error_msg': 'Popraw przedział czasu w zakładce Volcano Melt przed startem!',
        'dialog_no_output_title': 'Brak wygenerowanego pliku',
        'dialog_no_output_msg': 'Najpierw wyrenderuj wideo w kroku 3, aby zobaczyć podgląd!',
        'dialog_draft_error_title': 'Błąd szybkiego podglądu',
        'dialog_draft_error_msg': 'Nie udało się wygenerować wycinka:\n\n{err}',
        'dialog_render_error_title': 'Błąd przetwarzania',
        'dialog_render_error_msg': 'Wystąpił błąd podczas procesu datamosh:\n\n{err}',
        'dialog_no_audio_title': 'Brak ścieżki dźwiękowej',
        'dialog_no_audio_msg': 'Wideo nie posiada dźwięku i nie wybrano własnego pliku audio. Wybierz plik dźwiękowy lub użyj wideo z dźwiękiem!',

        'file_dialog_select_a': 'Wybierz plik wideo A',
        'file_dialog_select_b': 'Wybierz plik wideo B',
        'file_dialog_select_audio': 'Wybierz zewnętrzny plik audio',
        'file_dialog_audio_filter': 'Pliki audio (*.mp3 *.wav *.aac *.m4a *.flac *.ogg);;Wszystkie pliki (*.*)',
        'file_dialog_save_output': 'Zapisz wyjściowy film Datamosh',
        'file_dialog_video_filter': 'Pliki wideo (*.mp4 *.avi *.mov *.mkv *.webm);;Wszystkie pliki (*.*)',
        'file_dialog_save_filter': 'MP4 Video (*.mp4);;AVI Video (*.avi)',

        # Logs
        'log_task_start': "Rozpoczynanie zadania: tryb '{mode}' -> {output}",
        'log_success': 'Sukces: Gotowy film zapisano w {path}',
        'log_error': 'Błąd: {err}',
        'log_video_a_loaded': 'Wczytano wideo A: {path}',
        'log_video_b_loaded': 'Wczytano wideo B: {path}',
        'log_reset_done': 'Zresetowano parametry aplikacji do stanu początkowego.',
    }
}

_current_lang = 'en'


def set_language(lang: str):
    global _current_lang
    if lang in TRANSLATIONS:
        _current_lang = lang


def get_language() -> str:
    return _current_lang


def tr(key: str, **kwargs) -> str:
    """Translates a key into current language with optional string formatting."""
    dict_lang = TRANSLATIONS.get(_current_lang, TRANSLATIONS['en'])
    text = dict_lang.get(key, TRANSLATIONS['en'].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
