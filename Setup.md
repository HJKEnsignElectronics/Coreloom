### Step 3: Set Up the Python Environment
Open your terminal or command prompt and navigate to your `coreloom` folder. It is best practice to use a virtual environment.

**1. Navigate to the folder:**
```bash
cd path/to/coreloom
```

**2. Create a virtual environment:**
```bash
python -m venv venv
```

**3. Activate the virtual environment:**
*   **Windows:** `venv\Scripts\activate`
*   **Mac/Linux:** `source venv/bin/activate`
*(You should see `(venv)` appear at the start of your terminal prompt).*

**4. Install the dependencies:**
```bash
pip install -r requirements.txt
```

### Step 4: Run the CoreLoom Server
With the environment activated and Docker running, start the FastAPI server:

```bash
python main.py
```

**You should see output like this:**
```text
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Connected to Docker Daemon successfully.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 5: Test the System via the API Dashboard
FastAPI automatically generates a beautiful, interactive UI for testing your API. 

1. Open your web browser and go to: **http://localhost:8000/docs**
2. You will see the **CoreLoom API** dashboard with all the endpoints.

#### How to test the full lifecycle:

**A. Register a User**
1. Find the `POST /register` endpoint and click **Try it out**.
2. Paste this JSON into the Request body:
   ```json
   {
     "username": "testuser",
     "password": "securepassword123"
   }
   ```
3. Click **Execute**. You will get a `200` success response.

**B. Log In**
1. Find the `POST /login` endpoint and click **Try it out**.
2. *⚠️ Important:* This endpoint uses Form Data, **not** JSON. Do not paste JSON. Instead, type `testuser` in the `username` field and `securepassword123` in the `password` field.
3. Click **Execute**. 
4. Copy the long string of text from the `access_token` field in the response (it will look like `eyJhbGci...`).

**C. Authorize your Session**
1. Scroll to the very top of the `/docs` page and click the green **Authorize** 🔒 button.
2. Paste your copied token into the "Value" box.
3. Click **Authorize**, then close the box. *(Now, all subsequent requests will be securely tied to your user).*

**D. Allocate Resources (Spin up a Virtual Core)**
1. Find the `POST /allocate` endpoint and click **Try it out**.
2. Paste this JSON to request 40% compute and 50% ROM:
   ```json
   {
     "rom_percent": 50,
     "compute_percent": 40,
     "task_description": "Neural network training batch"
   }
   ```
3. Click **Execute**. 
4. Look at the response! CoreLoom has successfully calculated the density, synthesized virtual cores, and the Docker daemon has spun up an isolated container. You will see a `container_id` (e.g., `a1b2c3d4e5f6`).

**E. Check Telemetry (The Collector)**
1. Find the `GET /telemetry/{container_id}` endpoint.
2. Click **Try it out**.
3. Paste the `container_id` you got from the previous step into the `container_id` field.
4. Click **Execute**. You will see real-time CPU and memory usage of your newly created virtual core!

### Troubleshooting
*   **"Cannot connect to Docker daemon"**: Docker Desktop is not running. Open it, wait for it to say "Engine running", and try again.
*   **"Port 8000 is already in use"**: Another app is using port 8000. Open `main.py`, change `port=8000` to `port=8001`, and restart.
*   **Container fails to start**: Ensure you have pulled the base image. Run `docker pull alpine:latest` in your terminal just to be safe.

You are now running a fully functional, containerized, distributed compute virtualization framework!
