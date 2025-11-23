from flask import Flask, request, jsonify, render_template
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})

def create_disk_plot(sequence, algo_name):
    if not sequence:
        return ""

    fig, ax = plt.subplots(figsize=(8, 4))
    
    y_coords = np.arange(len(sequence))
    
    ax.plot(sequence, y_coords, marker='o', linestyle='-', color='purple')
    
    for x, y in zip(sequence, y_coords):
        ax.annotate(f'{x}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)

    ax.invert_yaxis()
    
    ax.set_xlabel("Cylinder Number")
    ax.set_ylabel("Order of Service")
    ax.set_title(f"Disk Scheduling: {algo_name}")
    ax.grid(True, linestyle='--', alpha=0.6)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig) 
    
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return plot_base64

def fcfs(requests, head):
    sequence = [head]
    cost = 0
    new_head = head
    count = 0

    for request in requests:
        sequence.append(request)
        cost += abs(new_head - request)
        if new_head != request:
            count += 1
        new_head = request

    average_cost = cost / count if count > 0 else 0.0
    
    return {
        "sequence": sequence,
        "total_movements": cost,
        "average_movements": round(average_cost, 2)
    }

def sstf(requests_original, head):
    requests = requests_original.copy()
    current_head = head
    cost = 0
    count = 0
    sequence = [current_head]
    
    while requests:
        shortest_seek = float('inf')
        next_request = -1
        next_request_index = -1

        for i, request in enumerate(requests):
            seek_time = abs(current_head - request)
            if seek_time < shortest_seek:
                shortest_seek = seek_time
                next_request = request
                next_request_index = i

        cost += shortest_seek
        if current_head != next_request:
            count += 1
        current_head = next_request
        sequence.append(current_head)
            
        requests.pop(next_request_index)

    average_cost = cost / count if count > 0 else 0.0

    return {
        "sequence": sequence,
        "total_movements": cost,
        "average_movements": round(average_cost, 2)
    }

def get_scan_sequence_and_cost(requests, head, is_descending_first):
    requests.append(head)
    requests.sort()
    
    cost = 0
    new_head = head
    count = 0
    sequence = [head]
    
    try:
        head_loc_index = requests.index(head)
    except ValueError:
        return [head], 0, 0 

    
    if is_descending_first:
        for i in range(head_loc_index - 1, -1, -1):
            request = requests[i]
            cost += abs(new_head - request)
            if new_head != request:
                count += 1
            new_head = request
            sequence.append(new_head)
        
        for i in range(head_loc_index + 1, len(requests)):
            request = requests[i]
            cost += abs(new_head - request)
            if new_head != request:
                count += 1
            new_head = request
            sequence.append(new_head)
    else:
        for i in range(head_loc_index + 1, len(requests)):
            request = requests[i]
            cost += abs(new_head - request)
            if new_head != request:
                count += 1
            new_head = request
            sequence.append(new_head)

        for i in range(head_loc_index - 1, -1, -1):
            request = requests[i]
            cost += abs(new_head - request)
            if new_head != request:
                count += 1
            new_head = request
            sequence.append(new_head)
            
    return sequence, cost, count

def scan(requests_original, head, is_descending_first):
    sequence, cost, count = get_scan_sequence_and_cost(requests_original, head, is_descending_first)
    average_cost = cost / count if count > 0 else 0.0
    
    return {
        "sequence": sequence,
        "total_movements": cost,
        "average_movements": round(average_cost, 2)
    }

def cscan(requests_original, head, is_descending_first):
    requests = requests_original.copy()
    requests.append(head)
    requests.sort()
    
    cost = 0
    new_head = head
    count = 0
    sequence = [head]
    
    try:
        head_loc_index = requests.index(head)
    except ValueError:
        return {"sequence": [head], "total_movements": 0, "average_movements": 0.0}
        
    
    if is_descending_first:
        for i in range(head_loc_index - 1, -1, -1):
            request = requests[i]
            cost += abs(new_head - request)
            if new_head != request:
                count += 1
            new_head = request
            sequence.append(new_head)
        
        for i in range(len(requests) - 1, head_loc_index, -1):
            request = requests[i]
            cost += abs(new_head - request)
            if new_head != request:
                count += 1
            new_head = request
            sequence.append(new_head)
            
    else:
        for i in range(head_loc_index + 1, len(requests)):
            request = requests[i]
            cost += abs(new_head - request)
            if new_head != request:
                count += 1
            new_head = request
            sequence.append(new_head)

        for i in range(head_loc_index):
            request = requests[i]
            cost += abs(new_head - request)
            if new_head != request:
                count += 1
            new_head = request
            sequence.append(new_head)

    average_cost = cost / count if count > 0 else 0.0
    
    return {
        "sequence": sequence,
        "total_movements": cost,
        "average_movements": round(average_cost, 2)
    }


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/visualize', methods=['POST', 'OPTIONS'])
def schedule():

    # 1. Handle preflight OPTIONS request (important)
    if request.method == 'OPTIONS':
        response = jsonify({"message": "OK"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200

    # 2. Handle POST request
    try:
        data = request.get_json(force=True)
        # Convert everything to string first
        head_str = str(data.get('CurrentHeadPosition', '')).strip()
        total_tracks_str = str(data.get('TotalNumberOfTracks', '')).strip()
        speed_per_track_str = str(data.get('SpeedPerTrackMs', '')).strip()
        requests_str = str(data.get('RequestQueue', ''))

        algorithm_name = data.get("Algorithm", "")
        direction = data.get("Direction", "")

        head = int(head_str) if head_str.isdigit() else 0
        total_tracks = int(total_tracks_str) if total_tracks_str.isdigit() else 200
        speed_per_track = int(speed_per_track_str) if speed_per_track_str.isdigit() else 10

        # Parse request list
        requests = [int(r.strip()) for r in requests_str.split(',') if r.strip().isdigit()]

        # Direction check
        algorithm_name = data.get("Algorithm", "")
        direction = data.get("Direction", data.get("DirectionOfHeadMovement", "")).capitalize()

        is_descending_first = (direction == 'Left')

        if algorithm_name in ['FCFS', 'FCFS (First-Come, First-Served)']:
            results = fcfs(requests, head)
        elif algorithm_name in ['SSTF', 'SSTF (Shortest Seek Time First)']:
            results = sstf(requests, head)
        elif algorithm_name in ['SCAN', 'SCAN (Elevator)']:
            results = scan(requests, head, is_descending_first)
        elif algorithm_name in ['C-SCAN', 'C-SCAN (Circular SCAN)']:
            results = cscan(requests, head, is_descending_first)
        else:
            return jsonify({"error": f"Unknown algorithm selected: {algorithm_name}"}), 400


        total_seek_time_ms = results['total_movements'] * speed_per_track

        plot_base64 = create_disk_plot(results['sequence'], algorithm_name)

        response = {
            "algorithm_results": results,
            "total_seek_time_ms": total_seek_time_ms,
            "plot_image": f"data:image/png;base64,{plot_base64}"
        }

        return jsonify(response)

    except Exception as e:
        print(f"Final Crash Traceback: {e}")
        return jsonify({"error": f"Internal Server Error: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0' ,port=8088)