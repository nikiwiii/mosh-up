"""
Verification script to test all 5 Datamoshing modes programmatically.
"""

import os
from generate_test_video import create_sample_video
from datamosh_engine import DatamoshEngine

def run_tests():
    print("=== STARTING DATAMOSH ENGINE VERIFICATION ===")
    sample_a = create_sample_video("test_video_a.mp4", duration_sec=3)
    sample_b = create_sample_video("test_video_b.mp4", duration_sec=3)

    engine = DatamoshEngine()

    modes = [
        ('volcano_melt', {'start_pct': 0, 'end_pct': 100, 'keep_audio': False}),
        ('motion_smear', {'repeat_count': 10, 'frequency': 3, 'keep_audio': False}),
        ('stitch_mosh', {'input_b': sample_b, 'keep_audio': False}),
        ('cyber_glitch', {'corrupt_rate': 0.1, 'intensity': 0.05, 'keep_audio': False}),
        ('flow_drift', {'flow_scale': 2.0, 'decay': 0.8, 'keep_audio': False}),
    ]

    for mode_name, options in modes:
        out_file = f"test_output_{mode_name}.mp4"
        print(f"\n---> Testowanie trybu: {mode_name}...")
        
        def cb(pct, msg):
            print(f"   [{pct}%] {msg}")

        success = engine.process(mode_name, sample_a, out_file, options=options, progress_callback=cb)
        
        if success and os.path.exists(out_file) and os.path.getsize(out_file) > 0:
            print(f" [OK] SUCCESS: {mode_name} wygenerowal plik {out_file} ({os.path.getsize(out_file)} bajtow)")
        else:
            print(f" [FAIL] FAIL: {mode_name} nie utworzyl poprawnego pliku!")
            raise RuntimeError(f"Test nieudany dla {mode_name}")

    print("\n=== WSZYSTKIE TESTY SILNIKA DATAMOSHINGU ZAKOŃCZONE SUKCESEM! ===")

if __name__ == "__main__":
    run_tests()
