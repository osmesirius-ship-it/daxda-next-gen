# DA13 GPU Docker Desktop Checklist

Use this checklist when running the DA13 validator on a Windows machine with NVIDIA hardware and Docker Desktop.

## 1. Confirm the GPU is visible to Windows

Run this in PowerShell:

```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, Status
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
```

Expected result:

- A real NVIDIA card name such as `NVIDIA GeForce RTX 3090`
- A working driver version shown by `nvidia-smi`
- `Status: OK`

## 2. Confirm Docker Desktop is running

Check:

```powershell
docker --version
docker info
```

If this fails, start Docker Desktop and wait until the engine is ready.

## 3. Enable NVIDIA Container Toolkit

Install the NVIDIA Container Toolkit for Docker Desktop and make sure the GPU is exposed to Linux containers.

Required steps:

- Install the NVIDIA driver
- Install the NVIDIA Container Toolkit
- Restart Docker Desktop
- Confirm GPU visibility from inside a container:

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

## 4. Start the DA13 GPU service

At the repo root:

```bash
docker compose -f docker-compose.da13.yml up --build -d
```

Then verify health:

```bash
curl http://localhost:8000/healthz
```

## 5. Submit a validation job

Use the built-in client:

```bash
python tools/da13_client.py --url http://localhost:8000 --key da13-public-renter
```

Or a custom admin key:

```bash
python tools/da13_client.py --url http://localhost:8000 --key da13-admin-renter
```

## 6. Common failure modes

- `docker: Error response from daemon: could not select device driver with capabilities: [[gpu]]`
  - NVIDIA Container Toolkit is not installed or Docker Desktop is not restarted.
- `nvidia-smi` fails inside container
  - Docker Desktop GPU access is not enabled for the current session.
- `Microsoft Basic Display Adapter`
  - Windows is not exposing the real GPU to the current environment.
- `HTTP 403`
  - The API key is missing or invalid.

## 7. Production key rotation

Set custom keys via environment variables:

```yaml
environment:
  DA13_API_KEYS: "client-one:validator,client-two:admin"
```

Use the key that matches the role you need:

- `validator` for validation jobs
- `admin` for scaling and cluster control
