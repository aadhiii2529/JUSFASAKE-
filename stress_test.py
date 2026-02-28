import requests
import threading
import time
import sys

BASE_URL = "http://127.0.0.1:5000"

latencies = []

def hammer_status(id, stop_event):
    while not stop_event.is_set():
        try:
            start = time.time()
            r = requests.get(f"{BASE_URL}/api/status", timeout=2)
            lat = time.time() - start
            latencies.append(lat)
            if r.status_code != 200:
                print(f"[{id}] Error: {r.status_code}")
        except Exception as e:
            # print(f"[{id}] Failed: {e}")
            pass
        time.sleep(0.01)

def hammer_video(id, stop_event):
    # MJPEG stream is continuous, so we just read chunks
    try:
        r = requests.get(f"{BASE_URL}/video_feed", stream=True)
        count = 0
        for chunk in r.iter_content(chunk_size=1024):
            if stop_event.is_set():
                break
            count += len(chunk)
            if count > 1024 * 1024: # 1MB read
                # print(f"[{id}] Streamed 1MB")
                count = 0
    except Exception as e:
        print(f"[{id}] Video Failed: {e}")

def stress_test(num_status=10, num_video=2, duration=10):
    print(f"Starting stress test: {num_status} status workers, {num_video} video workers...")
    stop_event = threading.Event()
    threads = []
    
    for i in range(num_status):
        t = threading.Thread(target=hammer_status, args=(f"S{i}", stop_event))
        t.start()
        threads.append(t)
        
    for i in range(num_video):
        t = threading.Thread(target=hammer_video, args=(f"V{i}", stop_event))
        t.start()
        threads.append(t)
        
    time.sleep(duration)
    print("Stopping test...")
    stop_event.set()
    for t in threads:
        t.join()
    
    if latencies:
        avg_lat = sum(latencies) / len(latencies)
        print(f"Test complete. Total Requests: {len(latencies)}")
        print(f"Avg Latency: {avg_lat*1000:.2f}ms")
        print(f"Min Latency: {min(latencies)*1000:.2f}ms")
        print(f"Max Latency: {max(latencies)*1000:.2f}ms")
    else:
        print("No latencies recorded.")

if __name__ == "__main__":
    stress_test(num_status=50, num_video=10, duration=20)
